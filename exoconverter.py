import os
import shutil
import sys
import traceback
from metadatahandler import MetadataHandler
from keyb2joypad import Keyb2Joypad
import util
import dosboxconfv6
from zipfile import ZipFile
import TDLindexer
from gamegenerator import GameGenerator


# Main Converter
class ExoConverter:

    def __init__(self, games, cache, scriptDir, collectionVersion, collectionDir, outputDir, conversionType, useLongFolderNames, 
                 useGenreSubFolders, conversionConf, fullnameToGameDir, postProcess, logger):
        self.games = games
        self.cache = cache
        self.scriptDir = scriptDir
        self.collectionVersion = collectionVersion
        self.exoCollectionDir = collectionDir
        self.logger = logger
        self.collectionGamesDir = util.getCollectionGamesDir(collectionDir, collectionVersion)
        self.collectionGamesConfDir = util.getCollectionGamesConfDir(collectionDir, collectionVersion)
        self.outputDir = outputDir
        self.conversionType = conversionType
        self.useLongFolderNames = useLongFolderNames
        self.useGenreSubFolders = useGenreSubFolders
        self.conversionConf = conversionConf
        self.metadataHandler = MetadataHandler(scriptDir, collectionDir, collectionVersion, self.cache, self.logger)
        self.keyb2joypad = Keyb2Joypad(self.scriptDir, self.logger)
        self.fullnameToGameDir = fullnameToGameDir
        self.postProcess = postProcess
        self.defaultDosboxConf = dosboxconfv6.loadDosboxConf(os.path.join(scriptDir, 'data', 'dosbox-0.74-default.conf'), dict())
        self.dosboxPureZip = True if 'dosboxPureZip' in self.conversionConf and self.conversionConf['dosboxPureZip'] is True else False

    # Loops on all games to convert them
    def convertGames(self):
        # Pre-checks
        if len(self.games) == 0:
            self.postProcess()
            return
        if self.conversionType == util.mister and os.path.exists(os.path.join(self.outputDir, 'TDL_VHD')):
            self.logger.log("\nFound a previous MiSTeR conversion in output folder, please move or delete it before processing with a new one\n", self.logger.ERROR)
            self.postProcess()
            return

        self.logger.log("Loading metadatas...")
        self.metadataHandler.parseXmlMetadata()
        if not os.path.exists(os.path.join(self.outputDir, 'downloaded_images')):
            os.mkdir(os.path.join(self.outputDir, 'downloaded_images'))
        if not os.path.exists(os.path.join(self.outputDir, 'manuals')):
            os.mkdir(os.path.join(self.outputDir, 'manuals'))

        self.logger.log("Loading keyb2joypad configurations")
        self.keyb2joypad.load()
        self.logger.log("")

        gamelist = self.metadataHandler.initXml(self.outputDir)

        count = 1
        total = len(self.games)
        errors = dict()

        for game in self.games:
            try:
                self.__convertGame__(game, gamelist, total, count)
            except:
                self.logger.log('  Error %s while converting game %s\n\n' % (sys.exc_info()[0], game),
                                self.logger.ERROR)
                excInfo = traceback.format_exc()
                errors[game] = excInfo

            count = count + 1

        self.metadataHandler.writeXml(self.outputDir, gamelist)

        self.logger.log('\n<--------- Post-conversion --------->')
        self.__postConversion__()

        self.logger.log('\n<--------- Finished Process --------->\n')

        if len(errors.keys()) > 0:
            self.logger.log('\n<--------- Errors rundown --------->', self.logger.ERROR)
            self.logger.log('%i errors were found during process' % len(errors.keys()), self.logger.ERROR)
            self.logger.log('See error log in your outputDir for more info\n', self.logger.ERROR)
            logFile = open(os.path.join(self.outputDir, 'error_log.txt'), 'w')
            for key in list(errors.keys()):
                logFile.write("Found error when processing %s" % key + " :\n")
                logFile.write(errors.get(key))
                logFile.write("\n")
            logFile.close()
        elif os.path.exists(os.path.join(self.outputDir, 'error_log.txt')):
            # Delete log from previous runs
            os.remove(os.path.join(self.outputDir, 'error_log.txt'))

        self.postProcess()

    # Full conversion for a given game    
    def __convertGame__(self, game, gamelist, totalSize, count):
        genre = self.metadataHandler.buildGenre(self.metadataHandler.metadatas.get(game.lower()), self.metadataHandler.fixGenres)
        self.logger.log(">>> %i/%i >>> %s: starting conversion" % (count, totalSize, game))
        metadata = self.metadataHandler.processGame(game, gamelist, genre, self.outputDir, self.useLongFolderNames, self.useGenreSubFolders,
                                                    self.conversionType, self.collectionVersion, self.dosboxPureZip, None, None)

        if (self.conversionType == util.batocera or self.conversionType == util.retrobat) and self.useLongFolderNames:
            gameDir = util.getCleanGameID(metadata,'.pc')
        else:
            gameDir = game + ".pc"
        gGator = GameGenerator(game, gameDir, genre, self.outputDir, self.collectionVersion, self.useLongFolderNames, self.useGenreSubFolders, metadata,
                               self.conversionType, self.conversionConf, self.exoCollectionDir, self.fullnameToGameDir,
                               self.scriptDir, self.keyb2joypad, self.defaultDosboxConf, self.logger)

        if not os.path.exists(gGator.getLocalGameOutputDir()):
            self.__copyGameDataToOutputDir__(gGator)
            gGator.convertGame()
        else:
            self.logger.log("  already converted in output folder")

        # TODO refine and reactivate
        # util.checkMultipleofSameGame(self.useGenreSubFolders, metadata, genre, game, gameDir, self.outputDir, self.logger)
        self.logger.log("")

    # Copy game data from collection to output dir
    def __copyGameDataToOutputDir__(self, gGator):
        # previous method kept for doc purpose
        # automatic Y, F and N to validate answers to exo's install.bat
        # fullscreen = true, output=overlay, aspect=true
        # subprocess.call("cmd /C (echo Y&echo F&echo N) | Install.bat", cwd=os.path.join(self.gamesDosDir, game),
        #                 shell=False)

        # unzip game (xxxx).zip from unzip line in game/install.bat
        # following options should be set in dosbox.conf / actually do it later in converter
        # fullscreen = true, output=overlay, aspect=true
        bats = [os.path.splitext(filename)[0] for filename in
                os.listdir(os.path.join(self.collectionGamesConfDir, gGator.game)) if
                os.path.splitext(filename)[-1].lower() == '.bat' and not os.path.splitext(filename)[0].lower() == 'install'
                and not os.path.splitext(filename)[0].lower() == 'exception']
        gameZip = bats[0] + '.zip'
        # Unzip game
        if gameZip is not None:
            gameZipPath = os.path.join(
                os.path.join(util.getCollectionGamesDir(self.exoCollectionDir, self.collectionVersion)), gameZip)

            # ensure gameZip not 0 bytes, this will trigger a download if it is.
            try:    
                if not os.path.getsize(gameZipPath):
                    self.logger.log("  <WARNING>" + gameZipPath + " is 0 bytes. Removing.",self.logger.WARNING)
                    os.remove(gameZipPath)
            except OSError as error: 
                pass

            # If zip of the game is not found, try to download it
            if not os.path.exists(gameZipPath):
                self.logger.log('  <WARNING> %s not found' % gameZipPath, self.logger.WARNING)
                if self.conversionConf['downloadOnDemand']:
                    # try zip then try torrent
                    downloadZipSuccess = util.downloadZip(gameZip, gameZipPath, self.logger)
                    if not downloadZipSuccess:
                        self.logger.log("  <WARNING> Web download Failed, trying Torrent",self.logger.WARNING)
                        util.downloadTorrent(gameZip, gameZipPath, self.exoCollectionDir, self.logger)
                else:
                    self.logger.log('  <WARNING> Activate Download on demand if you want to download missing games',
                                    self.logger.WARNING)
            self.__unzipGame__(gameZipPath, gGator)
        else:
            self.logger.log(
                "  ERROR while trying to find zip file for " + os.path.join(self.collectionGamesConfDir, gGator.game),
                self.logger.ERROR)
        self.logger.log("  unzipped")

        # Handle game update if it exists
        updateZipPath = os.path.join(util.getCollectionUpdateDir(self.exoCollectionDir, self.collectionVersion),
                                     gameZip)
        if os.path.exists(updateZipPath):
            self.logger.log("  found an update for the game")
            self.__unzipGame__(updateZipPath, gGator)

        # For win3x games, all files / dir / etc in game.pc/game should be moved to game.pc/ and sub game.pc/game deleted
        # do not use getLocalGameDataOutputDir as game data are in subdir at that point
        if gGator.isWin3x():
            # Needs to rename sub game dir first then move content to .pc folder , then delete sub game dir
            subDirTempName = gGator.game + '-tempEDC'
            os.rename(os.path.join(gGator.getLocalGameOutputDir(), gGator.game), os.path.join(gGator.getLocalGameOutputDir(), subDirTempName))
            for gameFile in os.listdir(os.path.join(gGator.getLocalGameOutputDir(), subDirTempName)):
                shutil.move(os.path.join(gGator.getLocalGameOutputDir(), subDirTempName, gameFile), gGator.getLocalGameOutputDir())
            # Check if it's empty !! a subdir might be named the same
            if len(os.listdir(os.path.join(gGator.getLocalGameOutputDir(), subDirTempName))) == 0:
                shutil.rmtree(os.path.join(gGator.getLocalGameOutputDir(), subDirTempName))

    # Unzip game zip
    def __unzipGame__(self, gameZipPath, gGator):
        with ZipFile(gameZipPath, 'r') as zipFile:
            # Extract all the contents of zip file in current directory
            self.logger.log("  unzipping " + gameZipPath)
            zipFile.extractall(path=gGator.getLocalGameOutputDir())
        # Check folder name // !dos folder, if not the same rename it to the !dos one
        unzippedDirs = [file for file in os.listdir(gGator.getLocalGameOutputDir()) if
                        os.path.isdir(os.path.join(gGator.getLocalGameOutputDir(), file))]
        if len(unzippedDirs) == 1 and unzippedDirs[0] != gGator.game and not gGator.isWin3x():
            self.logger.log("  fixing extracted dir %s to !dos name %s" % (unzippedDirs[0], gGator.game))
            os.rename(os.path.join(gGator.getLocalGameOutputDir(), unzippedDirs[0]), os.path.join(gGator.getLocalGameOutputDir(), gGator.game))

    # specific convertion type treatments after converting all games
    def __postConversion__(self):
        # Cleaning for some conversions
        if self.conversionType in [util.esoteric, util.simplemenu, util.mister]:
            self.logger.log('Post cleaning for ' + self.conversionType)
            # Remove gamelist.xml and downloaded_images folder
            if os.path.exists(os.path.join(self.outputDir, 'gamelist.xml')):
                os.remove(os.path.join(self.outputDir, 'gamelist.xml'))
            if os.path.exists(os.path.join(self.outputDir, 'downloaded_images')):
                shutil.rmtree(os.path.join(self.outputDir, 'downloaded_images'))
            if self.conversionType == util.mister:
                # delete empty genres dir
                dirs = [file for file in os.listdir(self.outputDir) if
                        os.path.isdir(os.path.join(self.outputDir, file))
                        and file not in ['games', 'games-data', 'cd', 'floppy', 'manuals', 'bootdisk']]
                gamesDir = os.path.join(self.outputDir, 'games')
                if os.path.exists(gamesDir):
                    for genreDir in dirs:
                        shutil.rmtree(os.path.join(self.outputDir, genreDir))
                    # copy mister zips
                    shutil.copy2(os.path.join(self.scriptDir, 'data', 'mister', '(Manually Added Games).zip'), gamesDir)
                    shutil.copy2(os.path.join(self.scriptDir, 'data', 'mister', '(Utilities and System Files).zip'),
                                 gamesDir)
                    # Call Total DOS Launcher Indexer, delete top level games folder after
                    self.logger.log('Total DOS Indexer for ' + self.conversionType)
                    TDLindexer.index(self.outputDir, self.scriptDir, util.misterCleanNameToGameDir,
                                     self.conversionConf['useDebugMode'],
                                     self.conversionConf['preExtractGames'], self.logger)
                    os.rename(os.path.join(self.outputDir, 'tdlprocessed'), os.path.join(self.outputDir, 'TDL_VHD'))
                    if not self.conversionConf['useDebugMode'] or self.conversionConf['preExtractGames']:
                        shutil.rmtree(os.path.join(self.outputDir, 'games'))
                    # move cd, floppy, boot disk into ao486 folder
                    if not os.path.exists(os.path.join(self.outputDir, "ao486")):
                        os.mkdir(os.path.join(self.outputDir, "ao486"))
                    self.logger.log("  Moving cd folder to tdlprocessed, this might take a while ...")
                    if os.path.exists(os.path.join(self.outputDir, "cd")):
                        shutil.move(os.path.join(self.outputDir, "cd"),
                                    os.path.join(os.path.join(self.outputDir, "ao486")))
                    self.logger.log("  Moving floppy folder to tdlprocessed, this might take a while ...")
                    if os.path.exists(os.path.join(self.outputDir, "floppy")):
                        shutil.move(os.path.join(self.outputDir, "floppy"),
                                    os.path.join(os.path.join(self.outputDir, "ao486")))
                    self.logger.log("  Moving bootdisk folder to tdlprocessed, this might take a while ...")
                    if os.path.exists(os.path.join(self.outputDir, "bootdisk")):
                        shutil.move(os.path.join(self.outputDir, "bootdisk"),
                                    os.path.join(os.path.join(self.outputDir, "ao486")))
                else:
                    self.logger.log(
                        '  Some critical errors seems to have happened during process.\n  Skipping Total Indexer phase',
                        self.logger.ERROR)
                # clean data/distro dir if it exists
                distroUnzippedDir = os.path.join(self.scriptDir, 'data', 'mister', 'distro')
                if os.path.exists(distroUnzippedDir) and os.path.isdir(distroUnzippedDir):
                    shutil.rmtree(distroUnzippedDir)

        elif self.conversionType == util.emuelec:
            self.logger.log('Post cleaning for ' + self.conversionType)
            # move gamelist downloaded_images, manuals
            if os.path.exists(os.path.join(self.outputDir, 'gamelist.xml')):
                shutil.move(os.path.join(self.outputDir, 'gamelist.xml'), os.path.join(self.outputDir, 'pc'))
            if os.path.exists(os.path.join(self.outputDir, 'manuals')):
                shutil.move(os.path.join(self.outputDir, 'manuals'), os.path.join(self.outputDir, 'pc'))
            if os.path.exists(os.path.join(self.outputDir, 'downloaded_images')):
                shutil.move(os.path.join(self.outputDir, 'downloaded_images'), os.path.join(self.outputDir, 'pc'))
            # delete empty genres dir
            dirs = [file for file in os.listdir(self.outputDir) if
                    os.path.isdir(os.path.join(self.outputDir, file)) and file not in ['pc', 'pcdata']]
            for genreDir in dirs:
                shutil.rmtree(os.path.join(self.outputDir, genreDir))
            instructions = open(os.path.join(self.outputDir, 'instructions for emuelec.txt'), 'w')
            instructions.write('The script /emuelec/scripts/emuelecRunEmu.sh must be modified to read the exported configuration files (need to comment/uncomment the relevant RUNTHIS commands)\n')
            instructions.close()
