import os
import shutil
import subprocess
import sys
import traceback
from confconverter import ConfConverter
from metadatahandler import MetadataHandler
import util
from zipfile import ZipFile, ZIP_DEFLATED


# Main Converter
class ExoDOSConverter:

    def __init__(self, games, cache, collectionDir, gamesDosDir, outputDir, conversionType, useGenreSubFolders, logger):
        self.games = games
        self.cache = cache
        self.exoDosDir = os.path.join(collectionDir, 'eXoDOS')
        self.logger = logger
        self.gamesDosDir = gamesDosDir
        self.outputDir = outputDir
        self.conversionType = conversionType
        self.useGenreSubFolders = useGenreSubFolders
        self.metadataHandler = MetadataHandler(collectionDir, self.cache, self.logger)
        self.confConverter = ConfConverter(self.games, self.exoDosDir, self.outputDir, self.useGenreSubFolders,
                                           self.conversionType, self.logger)

    # Loops on all games to convert them
    def convertGames(self):
        self.logger.log("Loading metadatas...")
        self.metadataHandler.parseXmlMetadata()
        self.logger.log("")
        if not os.path.exists(os.path.join(self.outputDir, 'downloaded_images')):
            os.mkdir(os.path.join(self.outputDir, 'downloaded_images'))
        if not os.path.exists(os.path.join(self.outputDir, 'manuals')):
            os.mkdir(os.path.join(self.outputDir, 'manuals'))

        gamelist = self.metadataHandler.initXml(self.outputDir)

        count = 1
        total = len(self.games)
        errors = dict()

        for game in self.games:
            try:
                self.convertGame(game, gamelist, total, count)
            except:
                self.logger.log('Error %s while converting game %s' % (sys.exc_info()[0], game))
                excInfo = traceback.format_exc()
                errors[game] = excInfo

            count = count + 1

        self.metadataHandler.writeXml(self.outputDir, gamelist)

        # Cleaning for some conversions
        if self.conversionType in [util.esoteric, util.simplemenu, util.mister]:
            self.logger.log('Post cleaning for '+self.conversionType)
            # Remove gamelist.xml and downloaded_images folder    
            if os.path.exists(os.path.join(self.outputDir, 'gamelist.xml')):
                os.remove(os.path.join(self.outputDir, 'gamelist.xml'))
            if os.path.exists(os.path.join(self.outputDir, 'downloaded_images')):
                shutil.rmtree(os.path.join(self.outputDir, 'downloaded_images'))

        self.logger.log('\n<--------- Finished Process --------->')

        if len(errors.keys()) > 0:
            self.logger.log('\n<--------- Errors rundown --------->')
            self.logger.log('%i errors were found during process' % len(errors.keys()))
            self.logger.log('See error log in your outputDir')
            logFile = open(os.path.join(self.outputDir, 'error_log.txt'), 'w')
            for key in list(errors.keys()):
                logFile.write("Found error when processing %s" % key + " :\n")
                logFile.write(errors.get(key))
                logFile.write("\n")
            logFile.close()
        elif os.path.exists(os.path.join(self.outputDir, 'error_log.txt')):
            # Delete log from previous runs
            os.remove(os.path.join(self.outputDir, 'error_log.txt'))

    # Full conversion for a given game    
    def convertGame(self, game, gamelist, total, count):
        genre = self.metadataHandler.buildGenre(self.metadataHandler.metadatas.get(game))
        self.logger.log(">>> %i/%i >>> %s: starting conversion" % (count, total, game))
        metadata = self.metadataHandler.processGame(game, gamelist, genre, self.outputDir, self.useGenreSubFolders,
                                                    self.conversionType)

        localParentOutputDir = os.path.join(self.outputDir, genre) if self.useGenreSubFolders else os.path.join(
            self.outputDir)
        localGameOutputDir = os.path.join(self.outputDir, genre,
                                          game + ".pc") if self.useGenreSubFolders else os.path.join(self.outputDir,
                                                                                                     game + ".pc")
        if not os.path.exists(localGameOutputDir):
            # previous method kept for doc purpose
            # automatic Y, F and N to validate answers to exo's install.bat
            # fullscreen = true, output=overlay, aspect=true
            # subprocess.call("cmd /C (echo Y&echo F&echo N) | Install.bat", cwd=os.path.join(self.gamesDosDir, game),
            #                 shell=False)

            # unzip game (xxxx).zip from unzip line in game/install.bat
            # following options should be set in dosbox.conf / actually do it later in converter
            # fullscreen = true, output=overlay, aspect=true
            self.unzipGame(os.path.join(self.gamesDosDir, game, 'install.bat'), localGameOutputDir, game)
            self.logger.log("  unzipped")

            self.copyGameFiles(game, localGameOutputDir, metadata)
            self.confConverter.process(game, localGameOutputDir, genre)
            self.postConversion(game, genre, localGameOutputDir, localParentOutputDir, metadata)
        else:
            self.logger.log("  already converted in output folder")

        self.logger.log("")

    # Unzip game zip
    def unzipGame(self, gameInstallBat, localGameOutputDir, game):
        installFile = open(gameInstallBat, 'r')
        zipParam = None
        for line in installFile.readlines():
            if line.startswith('unzip "') or line.startswith('unzip -o "'):
                zipParam = line.split('"')[1]
                break
        installFile.close()
        if zipParam is not None:
            with ZipFile(os.path.join(self.exoDosDir, "Games", zipParam), 'r') as zipFile:
                # Extract all the contents of zip file in current directory
                self.logger.log("  unzipping " + zipParam)
                zipFile.extractall(path=localGameOutputDir)
            # Check folder name // !dos folder, if not the same rename it to the !dos one
            unzippedDirs = [file for file in os.listdir(localGameOutputDir) if os.path.isdir(os.path.join(localGameOutputDir, file))]
            if len(unzippedDirs) == 1 and unzippedDirs[0] != game:
                self.logger.log("  fixing extracted dir %s to !dos name %s" % (unzippedDirs[0], game))
                os.rename(os.path.join(localGameOutputDir, unzippedDirs[0]), os.path.join(localGameOutputDir, game))
        else:
            self.logger.log("  ERROR no zip file found in " + gameInstallBat)

    # Copy game files and game dosbox.conf to output dir
    def copyGameFiles(self, game, localGameOutputDir, metadata):
        localGameDataOutputDir = os.path.join(localGameOutputDir, game)
        # self.logger.log("  copy game data")
        # # Copy game files in game.pc/game
        # shutil.copytree(os.path.join(self.exoDosDir, "Games", game), localGameDataOutputDir)
        self.logger.log("  copy dosbox conf")
        # Copy dosbox.conf in game.pc
        shutil.copy2(os.path.join(self.exoDosDir, "Games", "!dos", game, "dosbox.conf"),
                     os.path.join(localGameDataOutputDir, "dosbox.conf"))
        # Create blank file with full game name        
        f = open(os.path.join(localGameOutputDir, util.getCleanGameID(metadata, '.txt')), 'w', encoding='utf8')
        f.write(metadata.desc)
        f.close()

    # Post-conversion operations for a given game for various conversion types
    def postConversion(self, game, genre, localGameOutputDir, localParentOutputDir, metadata):
        if self.conversionType == util.retropie:
            self.postConversionForRetropie(game, genre, localGameOutputDir, localParentOutputDir, metadata)
        elif self.conversionType in [util.esoteric, util.simplemenu]:
            self.postConversionForOpenDingux(game, genre, localGameOutputDir, localParentOutputDir, metadata)
        elif self.conversionType == util.mister:
            self.postConversionForMister(game, genre, localGameOutputDir, localParentOutputDir, metadata)

    # Post-conversion for MiSTeR for a given game
    def postConversionForMister(self, game, genre, localGameOutputDir, localParentOutputDir, metadata):
        self.logger.log("  MiSTer post-conversion")
        # Remove any C: from dosbox.bat, rename to launch.bat, remove dosbox.cfg
        os.remove(os.path.join(localGameOutputDir, 'dosbox.cfg'))
        dosboxBat = open(os.path.join(localGameOutputDir, "dosbox.bat"), 'r')
        launchBat = open(os.path.join(localGameOutputDir, "launch.bat"), 'w')
        lines = dosboxBat.readlines()
        for line in lines:
            if line.lower().rstrip(' \n\r') != 'c:':
                launchBat.write(line)
        launchBat.close()
        dosboxBat.close()
        os.remove(os.path.join(localGameOutputDir, 'dosbox.bat'))
        shutil.move(os.path.join(localGameOutputDir,util.getCleanGameID(metadata, '.txt')),os.path.join(localGameOutputDir,'about.txt'))
        # Move CDs to cdgames/gamefolder
        # Change imgmount iso command to imgset ide10 cdgames/gamefolder/game.iso
        # Include imgset in the outputDir ?
        # Convert imgmount or mount of floppy to imgset fdd0 /floppy/filename.img
        # Create about.jpg combining About.txt and pic of the game + script to run showJPG.exe ?
        # Zip internal game dir to longgamename.zip
        shutil.make_archive(os.path.join(localParentOutputDir, util.getCleanGameID(metadata, '')), 'zip', localGameOutputDir)
        # Delete everything unrelated
        shutil.rmtree(os.path.join(localParentOutputDir,game+'.pc'))

    # Post-conversion for openDingux for a given game
    def postConversionForOpenDingux(self, game, genre, localGameOutputDir, localParentOutputDir, metadata):
        self.logger.log("  opendingux post-conversion")
        openDinguxPicDir = '.previews' if self.conversionType == util.esoteric else '.media'
        # Copy image to opendingux img folder for game.pc
        distPicPath = os.path.join(localParentOutputDir, openDinguxPicDir)
        if not os.path.exists(distPicPath):
            os.mkdir(distPicPath)
        shutil.copy2(metadata.frontPic, os.path.join(distPicPath, game + '.pc.png'))
        # Resize image
        util.resize(os.path.join(distPicPath, game + '.pc.png'))
        # Copy image to opendingux img folder for game.pc/dosbox.bat
        dosboxBatPicPath = os.path.join(localGameOutputDir, openDinguxPicDir)
        if not os.path.exists(dosboxBatPicPath):
            os.mkdir(dosboxBatPicPath)
        shutil.copy2(os.path.join(distPicPath, game + '.pc.png'), os.path.join(dosboxBatPicPath, 'dosbox.png'))
        # Generate RG350 mapper
        mapper = open(os.path.join(localGameOutputDir, "mapper.map"), 'w')
        mapper.write('key_space "key 308"\n')
        mapper.write('key_lshift "key 32"\n')
        mapper.write('key_lctrl "key 304"\n')
        mapper.write('key_lalt "key 306"\n')
        mapper.write('key_esc "key 27"\n')
        mapper.write('key_enter "key 13"\n')
        mapper.write('key_up "key 273"\n')
        mapper.write('key_down "key 274"\n')
        mapper.write('key_right "key 275"\n')
        mapper.write('key_left "key 276"\n')
        mapper.write('key_n "key 9"\n')
        mapper.write('key_y "key 8"\n')
        mapper.close()

    # POst-conversion for Retropie for a given game
    def postConversionForRetropie(self, game, genre, localGameOutputDir, localParentOutputDir, metadata):
        self.logger.log("  retropie post-conversion")
        dosboxCfg = open(os.path.join(localGameOutputDir, "dosbox.cfg"), 'a')
        # add mount c at end of dosbox.cfg
        romsFolder = util.getRomsFolderPrefix(self.conversionType)
        retropieGameDir = romsFolder + "/" + genre + "/" + game + ".pc" if self.useGenreSubFolders else romsFolder + "/" + game + ".pc"
        dosboxCfg.write("mount c " + retropieGameDir + "\n")
        dosboxCfg.write("c:\n")
        # copy all instructions from dosbox.bat to end of dosbox.cfg
        dosboxBat = open(os.path.join(localGameOutputDir, "dosbox.bat"), 'r')  # retroarch dosbox.bat
        for cmdLine in dosboxBat.readlines():
            dosboxCfg.write(cmdLine)
        # delete dosbox.bat
        dosboxCfg.close()
        dosboxBat.close()
        os.remove(os.path.join(localGameOutputDir, "dosbox.bat"))
        # move dosbox.cfg to {game}.conf at top level
        shutil.move(os.path.join(localGameOutputDir, "dosbox.cfg"),
                    os.path.join(localParentOutputDir, util.getCleanGameID(metadata, '.conf')))
        # TODO not needed anymore apparently, to remove in the future
        # generate sh file        
        # shFile = open(os.path.join(gameOutputDir,"launch.sh"),'w')
        # shFile.write("!/bin/bash\n")
        # shFile.write("/opt/retropie/emulators/dosbox/bin/dosbox -conf "+retropieGameDir+"/dosbox.cfg\n")
        # shFile.close()
