import os
import shutil
import util
import sys
import traceback
from metadatahandler import MetadataHandler
from zipfile import ZipFile


# noinspection PyBroadException,PyTypeChecker
class AppleIIGSConverter:

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
        [outputGameFile, hiddenOutputGameFiles] = self.__copyGameDataToOutputDir__(game, genre)
        self.metadataHandler.processGame(game, gamelist, genre, self.outputDir, self.useLongFolderNames,
                                         self.useGenreSubFolders, self.conversionType, self.collectionVersion, False, outputGameFile, None)

        for hiddenOutputGameFiles in hiddenOutputGameFiles:
            self.metadataHandler.writeHiddenGamelistEntry(gamelist, hiddenOutputGameFiles, genre, self.useGenreSubFolders)

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
        extractedGameFiles = [file for file in os.listdir(extractedGamePath) if os.path.splitext(file)[-1] in ['.po', '.2mg', '.hdv']]

        if len(extractedGameFiles) == 1:
            gamefile = game + os.path.splitext(extractedGameFiles[0])[-1]
            shutil.move(os.path.join(extractedGamePath, extractedGameFiles[0]), os.path.join(outputDir, gamefile))
            shutil.rmtree(extractedGamePath)
            return [gamefile, []]
        else:
            self.logger.log('  <WARNING> several game files found while converting game %s\n\n' % game, self.logger.WARNING)
            maingamefile = None
            othergamefiles = []
            for extractedGameFile in extractedGameFiles:
                gamefile = game + '(' + ''.join(os.path.splitext(extractedGameFile)[:-1]) + ')' + os.path.splitext(extractedGameFile)[-1]
                shutil.move(os.path.join(extractedGamePath, extractedGameFile), os.path.join(outputDir, gamefile))
                if 'Game' in extractedGameFile:
                    maingamefile = gamefile
                else:
                    othergamefiles.append(gamefile)
            shutil.rmtree(extractedGamePath)
            if maingamefile is not None:
                return [maingamefile, othergamefiles]
            else:
                return [othergamefiles[0], othergamefiles[1:]]

    # Returns local parent output dir of the generated game
    def getLocalGameOutputDir(self, genre):
        return os.path.join(self.outputDir, genre) if self.useGenreSubFolders else self.outputDir
