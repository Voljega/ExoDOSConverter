import os
import shutil
import util
import sys
import traceback
from metadatahandler import MetadataHandler
from zipfile import ZipFile


# noinspection PyBroadException,PyTypeChecker
class ScummVMConverter:

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
        self.fullnameToGameDir = fullnameToGameDir
        self.postProcess = postProcess

    # Loops on all games to convert them
    def convertGames(self):
        # Pre-checks
        if len(self.games) == 0:
            self.postProcess()
            return
        if self.conversionType == util.mister and os.path.exists(os.path.join(self.outputDir, 'TDL_VHD')):
            self.logger.log(
                "\nFound a previous MiSTeR conversion in output folder, please move or delete it before processing with a new one\n",
                self.logger.ERROR)
            self.postProcess()
            return

        self.logger.log("Loading metadatas...")
        self.metadataHandler.parseXmlMetadata()
        if not os.path.exists(os.path.join(self.outputDir, 'downloaded_images')):
            os.mkdir(os.path.join(self.outputDir, 'downloaded_images'))
        if not os.path.exists(os.path.join(self.outputDir, 'manuals')):
            os.mkdir(os.path.join(self.outputDir, 'manuals'))

        self.logger.log('\n')

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

        # self.logger.log('\n<--------- Post-conversion --------->')
        # self.__postConversion__()

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
        gameMetadata = self.metadataHandler.metadatas.get(game.lower())
        genre = self.metadataHandler.buildGenre(gameMetadata, self.metadataHandler.fixGenres)
        self.logger.log(">>> %i/%i >>> %s: starting conversion" % (count, totalSize, game))
        [game, gamefolders] = self.__copyGameDataToOutputDir__(game, genre)
        for outputgamefolder in gamefolders:
            # TODO needs specific processing for multi folder games
            self.metadataHandler.processGame(game, gamelist, genre, self.outputDir, self.useLongFolderNames,
                                         self.useGenreSubFolders, self.conversionType, self.collectionVersion, False, outputgamefolder, None)

        self.logger.log("")

    # Copy game data from collection to output dir
    def __copyGameDataToOutputDir__(self, game, genre):
        outputDir = self.getLocalGameOutputDir(genre)
        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        bats = [os.path.splitext(filename)[0] for filename in
                os.listdir(os.path.join(self.collectionGamesConfDir, game)) if
                os.path.splitext(filename)[-1].lower() == '.bat' and not os.path.splitext(filename)[
                                                                             0].lower() == 'install'
                and not os.path.splitext(filename)[0].lower() == 'exception']
        gameZip = bats[0] + '.zip'
        # Unzip game
        if gameZip is not None:
            gameZipPath = os.path.join(
                os.path.join(util.getCollectionGamesDir(self.exoCollectionDir, self.collectionVersion)), gameZip)

            # ensure gameZip not 0 bytes, this will trigger a download if it is.
            try:
                if not os.path.getsize(gameZipPath):
                    self.logger.log("  <WARNING>" + gameZipPath + " is 0 bytes. Removing.", self.logger.WARNING)
                    os.remove(gameZipPath)
            except OSError as error:
                pass

            with ZipFile(gameZipPath, 'r') as zipFile:
                # Extract all the contents of zip file in current directory
                self.logger.log("  unzipping " + gameZipPath)
                zipFile.extractall(path=outputDir)

        else:
            self.logger.log(
                "  ERROR while trying to find zip file for " + os.path.join(self.collectionGamesConfDir, game),
                self.logger.ERROR)
        self.logger.log("  unzipped")

        # TODO handle config.txt file and/or the one in util/configs.zip

        extractedGamePath = os.path.join(outputDir, game)
        extractedGameFiles = [file for file in os.listdir(extractedGamePath)]
        extractedGameDirs = list(filter(lambda f: os.path.isdir(os.path.join(extractedGamePath, f)), extractedGameFiles))

        scummvmfolders = []

        if len(extractedGameDirs) == len(extractedGameFiles):
            # Handle multi-platform game
            for d in extractedGameDirs:
                shutil.move(os.path.join(extractedGamePath, d), os.path.join(outputDir))
                scummvmfolders.append(d)
            shutil.rmtree(extractedGamePath)
        else:
            scummvmfolders.append(game)

        for gamefolder in scummvmfolders:
            self.generatescummvmfiles(game, gamefolder, outputDir)

        return [game, scummvmfolders]

    def generatescummvmfiles(self, game, gamefolder, outputdir):
        conffilepath = os.path.join(util.getCollectionGamesConfDir(self.exoCollectionDir, self.collectionVersion), game, game + '.bat')
        conffile = open(conffilepath, 'r', encoding='utf-8')
        scummvmkey = None
        for line in conffile.readlines():
            if game != gamefolder and line.startswith('".\\scmvm\\scummvm.exe"') and gamefolder in line:
                scummvmkey = line.split(' ')[-1].rstrip(' \n\r')
                break
            if game == gamefolder and line.startswith('".\\scmvm\\scummvm.exe"'):
                scummvmkey = line.split(' ')[-1].rstrip(' \n\r')
                break

        if scummvmkey is not None:
            # if 'CD' in gamefolder:
            #     scummvmkey = scummvmkey + '-cd'
            # if 'Windows' in gamefolder:
            #     scummvmkey = scummvmkey + '-win'
            # if 'Amiga' in gamefolder:
            #     scummvmkey = scummvmkey + '-amiga'
            # if 'FM-Towns' in gamefolder:
            #     scummvmkey = scummvmkey + '-fm'
            # if 'Version 2' in gamefolder:
            #     scummvmkey = scummvmkey + '-v2'
            # if 'VGA' in gamefolder:
            #     scummvmkey = scummvmkey + '-vga'
            # if 'EGA' in gamefolder:
            #     scummvmkey = scummvmkey + '-ega'
            # if 'SCI' in gamefolder:
            #     scummvmkey = scummvmkey + '-sci'
            # if 'AGDI' in gamefolder:
            #     scummvmkey = scummvmkey + '-agdi'
            # if 'DELUXE' in gamefolder:
            #     scummvmkey = scummvmkey + '-deluxe'
            # if 'STEAM' in gamefolder:
            #     scummvmkey = scummvmkey + '-steam'
            # if 'IOS' in gamefolder and '-ios' not in scummvmkey:
            #     scummvmkey = scummvmkey + '-ios'

            scummvmkey = scummvmkey + '.scummvm'
            # create scummvm key file
            scummvmkeyfile = os.path.join(outputdir, gamefolder, scummvmkey)
            self.logger.log("  Create key file " + scummvmkeyfile)
            open(scummvmkeyfile, 'w')
        else:
            self.logger.log("  <ERROR> no scummvm key found for " + gamefolder, self.logger.ERROR)

        conffile.close()

    # Returns local parent output dir of the generated game
    def getLocalGameOutputDir(self, genre):
        return os.path.join(self.outputDir, genre) if self.useGenreSubFolders else self.outputDir
