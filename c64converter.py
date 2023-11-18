import os
import shutil
import util
import sys
import traceback
from metadatahandler import MetadataHandler


# noinspection PyBroadException,PyTypeChecker
class C64Converter:

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
        if game == 'H.E.R.O':
            gameMetadata = self.metadataHandler.metadatas.get('h.e.r.o.')
        else:
            gameMetadata = self.metadataHandler.metadatas.get(game.lower())
        genre = self.metadataHandler.buildGenre(gameMetadata, self.metadataHandler.fixGenres)
        self.logger.log(">>> %i/%i >>> %s: starting conversion" % (count, totalSize, game))
        [outputGameFile, hiddenOutputGameFiles] = self.__copyGameDataToOutputDir__(game, genre)
        manualFile = self.__copyManual(game)

        self.metadataHandler.processGame(game, gamelist, genre, self.outputDir, self.useLongFolderNames,
                                         self.useGenreSubFolders, self.conversionType, outputGameFile, manualFile)

        for hiddenOutputGameFiles in hiddenOutputGameFiles:
            self.metadataHandler.writeHiddenGamelistEntry(gamelist, hiddenOutputGameFiles, genre, self.useGenreSubFolders)

        self.logger.log("")

    def __copyManual(self, game):
        outputDir = os.path.join(self.outputDir, 'manuals')
        gamePath = os.path.join(self.collectionGamesDir, game)
        manualFile = game + ' Manual.cbz'
        manualPath = os.path.join(gamePath, manualFile)
        if os.path.exists(manualPath):
            self.logger.log('  Copy manual %s' % manualFile, self.logger.INFO)
            shutil.copy2(manualPath, os.path.join(outputDir, manualFile))
            return manualFile
        return None

    # Copy game data from collection to output dir
    def __copyGameDataToOutputDir__(self, game, genre):
        outputDir = self.getLocalGameOutputDir(genre)
        collectionGamePath = os.path.join(self.collectionGamesDir, game)
        collectionGameFiles = [file for file in os.listdir(collectionGamePath) if os.path.splitext(file)[-1] in ['.crt', '.d64', '.D64', '.d81', '.m3u', '.t64', '.g64', 'tcrt']]

        if not os.path.exists(outputDir):
            os.makedirs(outputDir)

        if len(collectionGameFiles) == 0:
            compilationConversion = self.handleCompilationDisk(game, outputDir, collectionGamePath)
            if compilationConversion is not None:
                return compilationConversion
            else:
                self.logger.log('  <WARNING> no game file found while converting game %s\n\n' % game, self.logger.WARNING)
                self.logger.log('            (most likely a commercial homebrew)\n\n', self.logger.WARNING)
                return [game + '.notfound', []]
        elif len(collectionGameFiles) > 1:
            m3uGameFiles = list(filter(lambda f: os.path.splitext(f)[-1] == '.m3u', collectionGameFiles))
            if len(m3uGameFiles) == 1:
                return self.handleM3U(game, outputDir, collectionGamePath, m3uGameFiles[0])
            else:
                return self.handleMultiDisksWithoutM3U(game, outputDir, collectionGamePath, collectionGameFiles)

        return self.handleSingleDisk(game, outputDir, collectionGamePath, collectionGameFiles[0])

    def handleCompilationDisk(self, game, outputDir, collectionGamePath):
        if os.path.exists(os.path.join(collectionGamePath, game + '.cmd')):
            self.logger.log('  compilation conversion')
            cmdFile = open(os.path.join(collectionGamePath, game + '.cmd'))
            for line in cmdFile.readlines():
                compilationGameFilePath = os.path.join(collectionGamePath, line.replace('"', ''))
                compilationGameFile = compilationGameFilePath.split('\\')[-1]
                outputGameFile = game + os.path.splitext(compilationGameFile)[-1]
                if os.path.exists(compilationGameFilePath):
                    self.logger.log('  Copy %s to %s\n\n' % (compilationGameFile, outputGameFile), self.logger.INFO)
                    shutil.copy2(os.path.join(collectionGamePath, compilationGameFilePath),
                                 os.path.join(outputDir, outputGameFile))
                    return [outputGameFile, []]
            cmdFile.close()
        return None

    def handleM3U(self, game, outputDir, collectionGamePath, m3uFile):
        self.logger.log('  m3u conversion')
        m3uGameFilePath = os.path.join(collectionGamePath, m3uFile)
        m3uGameFile = open(m3uGameFilePath, 'r', encoding='utf-8')
        disks = list(map(lambda d: d.rstrip(' \n\r'), m3uGameFile.readlines()))
        m3uGameFile.close()
        return self.createM3u(collectionGamePath, outputDir, game, disks)

    def handleMultiDisksWithoutM3U(self, game, outputDir, collectionGamePath, collectionGameFiles):
        self.logger.log('  multi disks without m3u conversion')
        # TODO most likely special launch, see cmd in Advanced Dungeons & Dragons - Champions of Krynn
        maingame = 'Game.crt'
        if maingame in collectionGameFiles:
            collectionGameFiles.remove(maingame)
            collectionGameFiles = [maingame] + collectionGameFiles
        return self.createM3u(collectionGamePath, outputDir, game, collectionGameFiles)

    def handleSingleDisk(self, game, outputDir, collectionGamePath, gameFile):
        cmds = [cmd for cmd in os.listdir(collectionGamePath) if os.path.splitext(cmd)[-1] == '.cmd']
        if len(cmds) > 0:
            return self.handleSingleDiskWithCmd(game, outputDir, collectionGamePath, gameFile, cmds)
        else:
            return self.handleSingleDiskWithoutCmd(game, outputDir, collectionGamePath, gameFile)

    def handleSingleDiskWithCmd(self, game, outputDir, collectionGamePath, gameFile, cmds):
        # TODO actually we should use cmd and not m3u for compatibility, however doe not work at the moment on Batocera
        if len(cmds) > 1:
            self.logger.log('  <ERROR> more than one cmd found\n\n', self.logger.ERROR)
        cmd = os.path.join(collectionGamePath, cmds[0])
        cmdFile = open(cmd, 'r', encoding='utf-8')
        lines = list(filter(lambda line: line.strip() != '', list(map(lambda l: l.replace('"','').rstrip(' \n\r'), cmdFile.readlines()))))
        cmdFile.close()
        if len(lines) > 1:
            self.logger.log('  <ERROR> more than one line found in cmd\n\n', self.logger.ERROR)
        cmdline = lines[0].split(':')
        if cmdline[0] != gameFile or len(cmdline) != 2:
            if len(cmdline) == 1:
                return self.handleSingleDiskWithoutCmd(game, outputDir, collectionGamePath, gameFile)
            else:
                self.logger.log('  <ERROR> more than one or no parameter found in cmd\n\n', self.logger.ERROR)
        self.logger.log('  single disk conversion with cmd\n\n')
        m3uOutputGameFilePath = os.path.join(outputDir, game + '.m3u')
        m3uOutputGameFile = open(os.path.join(outputDir, game + '.m3u'), 'w', encoding='utf-8')
        self.logger.log('  Create %s with launch parameter: %s\n\n' % (m3uOutputGameFilePath, cmdline[1]), self.logger.INFO)
        outputGameFile = game + os.path.splitext(gameFile)[-1]
        m3uOutputGameFile.write(outputGameFile + ':' + cmdline[1] + '\n')
        m3uOutputGameFile.close()
        self.logger.log('  copy %s to %s\n\n' % (gameFile, outputGameFile), self.logger.INFO)
        shutil.copy2(os.path.join(collectionGamePath, str(gameFile)), os.path.join(outputDir, outputGameFile))
        return [game + '.m3u', [outputGameFile]]

    def handleSingleDiskWithoutCmd(self, game, outputDir, collectionGamePath, gameFile):
        self.logger.log('  single disk conversion without cmd\n\n')
        outputGameFile = game + os.path.splitext(gameFile)[-1]
        self.logger.log('  copy %s to %s\n\n' % (gameFile, outputGameFile), self.logger.INFO)
        shutil.copy2(os.path.join(collectionGamePath, str(gameFile)), os.path.join(outputDir, outputGameFile))
        return [outputGameFile, []]

    def createM3u(self, collectionGamePath, outputDir, game, disks):
        m3uOutputGameFilePath = os.path.join(outputDir, game + '.m3u')
        m3uOutputGameFile = open(os.path.join(outputDir, game + '.m3u'), 'w', encoding='utf-8')
        self.logger.log('  Create %s\n\n' % m3uOutputGameFilePath, self.logger.INFO)
        hiddenGameFiles = []
        for rawdisk in disks:
            diskandparameter = rawdisk.split(':')
            [disk, parameter] = [diskandparameter[0], None] if len(diskandparameter) == 1 else [diskandparameter[0], diskandparameter[1]]
            outputGameFile = game + ' (' + '.'.join(os.path.splitext(disk)[:-1]) + ')' + os.path.splitext(disk)[-1]
            self.logger.log('  Copy %s to %s\n\n' % (disk, outputGameFile), self.logger.INFO)
            shutil.copy2(os.path.join(collectionGamePath, str(disk)), os.path.join(outputDir, outputGameFile))
            if parameter is None:
                m3uOutputGameFile.write(outputGameFile + '\n')
            else:
                m3uOutputGameFile.write(outputGameFile + ':' + parameter + '\n')
            hiddenGameFiles.append(outputGameFile)
        m3uOutputGameFile.close()
        return [game + '.m3u', hiddenGameFiles]

    # Returns local parent output dir of the generated game
    def getLocalGameOutputDir(self, genre):
        return os.path.join(self.outputDir, genre) if self.useGenreSubFolders else self.outputDir

    # specific convertion type treatments after converting all games
    # def __postConversion__(self):
    #     # Cleaning for some conversions
