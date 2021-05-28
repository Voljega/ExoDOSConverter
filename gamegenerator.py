import os
import util
import shutil
import ntpath
import mister
from zipfile import ZipFile
from confconverter import ConfConverter
from mapping import Mapping


# contains all data and conf about generating a given game
class GameGenerator:

    def __init__(self, game, genre, outputDir, collectionVersion, useGenreSubFolders, metadata, conversionType,
                 conversionConf, exoCollectionDir, fullnameToGameDir, scriptDir, keyb2joypad, logger):
        self.game = game
        self.collectionVersion = collectionVersion
        self.genre = genre
        self.outputDir = outputDir
        self.useGenreSubFolders = useGenreSubFolders
        self.metadata = metadata
        self.conversionType = conversionType
        self.exoCollectionDir = exoCollectionDir
        self.logger = logger
        self.fullnameToGameDir = fullnameToGameDir
        self.conversionConf = conversionConf
        self.scriptDir = scriptDir
        self.confConverter = ConfConverter(self)
        self.keyb2joypad = keyb2joypad

    ##### Utils functions ####

    # Checks if collection is win3x or dos
    def isWin3x(self):
        return util.isWin3x(self.collectionVersion)

    # Returns local parent output dir of the generated game
    def getLocalParentOutputDir(self):
        return os.path.join(self.outputDir, self.genre) if self.useGenreSubFolders else self.outputDir

    # returns local game ouput dir of the generated game
    def getLocalGameOutputDir(self):
        return os.path.join(self.getLocalParentOutputDir(), self.game + ".pc")

    # returns local game data output dir of the generated game
    def getLocalGameDataOutputDir(self):
        return self.getLocalGameOutputDir() if self.isWin3x() else os.path.join(
            self.getLocalGameOutputDir(), self.game)

    ################################

    ##### Generation functions #####

    # Converts game
    def convertGame(self):
        self.copyGameFiles()
        self.confConverter.process(self)
        self.postConversion()

    # Copy game files and game dosbox.conf to output dir
    def copyGameFiles(self):
        self.logger.log("  copy dosbox conf")
        # Copy dosbox.conf in game.pc
        shutil.copy2(
            os.path.join(util.getCollectionGamesConfDir(self.exoCollectionDir, self.collectionVersion), self.game,
                         "dosbox.conf"),
            os.path.join(self.getLocalGameDataOutputDir(), "dosbox.conf"))
        # Create blank file with full game name        
        f = open(os.path.join(self.getLocalGameOutputDir(), util.getCleanGameID(self.metadata, '.txt')), 'w',
                 encoding='utf8')
        f.write(self.metadata.desc)
        f.close()
        # Handle first-game-of-a-serie dependencies
        needsFirstGame = {
            'roadware': ['Roadwar 2000 (1987).zip'],  # @mount a .\Games\roadwar -t floppy
            'eob2': ['Eye of the Beholder (1991).zip'],  # mount a .\Games\eob1\ -t floppy
            'bardtal2': ["Bard's Tale 1, The - Tales Of The Unknown (1987).zip"],
            # mount a .\Games\bardtal1 -t floppy
            'bardtal3': ["Bard's Tale 1, The - Tales Of The Unknown (1987).zip",
                         # mount a .\Games\bardtal1 -t floppy
                         "Bard's Tale 2, The - The Destiny Knight (1988).zip"],
            # @mount b .\Games\bardtal2 -t floppy
            'MM2': ['Might and Magic - Book 1 (1986).zip'],  # mount a .\Games\MM1\ -t floppy
            'vengexca': ['Spirit of Excalibur (1990).zip'],  # @mount a .\Games\spirexc -t floppy
            'WC2DLX': ['Wing Commander (1990).zip'],  # mount a .\Games\WC\WING\GAMEDAT\
            'darkdes2': ['Dark Designs I - Grelminars Staff (1990).zip'],  # mount a .\Games\darkdes1 -t floppy
            'whalvoy2': ["Whale's Voyage (1993).zip"]  # @mount e .\Games\whalvoy1\WVCD
        }
        if self.game in needsFirstGame:
            for previousGameZip in needsFirstGame[self.game]:
                # unzip game dependency
                with ZipFile(os.path.join(util.getCollectionGamesDir(self.exoCollectionDir, self.collectionVersion),
                                          previousGameZip), 'r') as zipFile:
                    # Extract all the contents of zip file in current directory
                    self.logger.log("  unzipping previous game" + previousGameZip)
                    zipFile.extractall(
                        path=util.getCollectionGamesDir(self.exoCollectionDir, self.collectionVersion))
                # copy its directory or directory part to the inside of the second game dir
                shutil.move(os.path.join(util.getCollectionGamesDir(self.exoCollectionDir, self.collectionVersion),
                                         self.fullnameToGameDir.get(os.path.splitext(previousGameZip)[0])),
                            os.path.join(self.getLocalGameOutputDir()))

    ######################################

    ###### Post-conversion functions #####

    # Post-conversion operations for a given game for various conversion types
    def postConversion(self):
        if self.conversionType == util.retropie:
            self.postConversionForRetropie()
        elif self.conversionType in [util.esoteric, util.simplemenu]:
            self.postConversionForOpenDingux()
        elif self.conversionType == util.mister:
            self.postConversionForMister()
        elif self.conversionType == util.recalbox:
            self.postConversionForRecalbox()
        elif self.conversionType == util.batocera:
            self.postConversionForBatocera()
        elif self.conversionType == util.emuelec:
            self.postConversionForEmuelec()

    # Post-conversion for Emuelec for a given game
    def postConversionForEmuelec(self):
        self.logger.log("  Emuelec post-conversion")
        # create pcdata and pc subfolders in outputdir
        if not os.path.exists(os.path.join(self.outputDir, 'pcdata')):
            os.mkdir(os.path.join(self.outputDir, 'pcdata'))
        if not os.path.exists(os.path.join(self.outputDir, 'pc')):
            os.mkdir(os.path.join(self.outputDir, 'pc'))
        emuElecDataDir = os.path.join(self.outputDir, 'pcdata', self.genre) if self.useGenreSubFolders \
            else os.path.join(self.outputDir, 'pcdata')
        if not os.path.exists(emuElecDataDir):
            os.mkdir(emuElecDataDir)
        # move *.pc folder to pcdata folder
        shutil.move(os.path.join(self.getLocalGameOutputDir()), emuElecDataDir)
        os.rename(os.path.join(emuElecDataDir, self.game + '.pc'), os.path.join(emuElecDataDir, self.game))
        open(os.path.join(emuElecDataDir, self.game, util.getCleanGameID(self.metadata, '.bat')),'w').close()
        # move *.bat *.map and *.cfg to pc/*.pc folder and rename *.cfg to dosbox-SDL2.conf
        emuelecConfOutputDir = os.path.join(self.outputDir, 'pc', self.genre, self.game + ".pc") \
            if self.useGenreSubFolders else os.path.join(self.outputDir, 'pc', self.game + ".pc")
        if not os.path.exists(emuelecConfOutputDir):
            os.makedirs(emuelecConfOutputDir)
        shutil.move(os.path.join(emuElecDataDir, self.game, 'dosbox.bat'), emuelecConfOutputDir)
        shutil.move(os.path.join(emuElecDataDir, self.game, 'dosbox.cfg'),
                    os.path.join(emuelecConfOutputDir, 'dosbox-SDL2.conf'))
        shutil.copy2(
            os.path.join(emuElecDataDir, self.game, util.getCleanGameID(self.metadata, '.txt')),
            emuelecConfOutputDir)
        if os.path.exists(os.path.join(emuElecDataDir, self.game, 'mapper.map')):
            shutil.move(os.path.join(emuElecDataDir, self.game, 'mapper.map'), emuelecConfOutputDir)
        # modify dosbox-SDL2.conf to add mount c /storage/roms/pcdata/game at the beginning of autoexec.bat
        dosboxCfg = open(os.path.join(emuelecConfOutputDir, 'dosbox-SDL2.conf'), 'a')
        # add mount c at end of dosbox.cfg
        romsFolder = util.getRomsFolderPrefix(self.conversionType, self.conversionConf)
        emuelecGameDir = romsFolder + "/" + self.genre + "/" + self.game if self.useGenreSubFolders else romsFolder + "/" + self.game
        dosboxCfg.write("mount c " + emuelecGameDir + "\n")
        dosboxCfg.write("c:\n")
        # copy all instructions from dosbox.bat to end of dosbox.cfg
        dosboxBat = open(os.path.join(emuelecConfOutputDir, "dosbox.bat"), 'r')  # retroarch dosbox.bat
        for cmdLine in dosboxBat.readlines():
            # needs to get rid of '.pc' in mount instructions
            dosboxCfg.write(cmdLine.replace('.pc',''))
        # delete dosbox.bat
        dosboxCfg.close()
        dosboxBat.close()
        # delete dosbox.bat
        os.remove(os.path.join(emuelecConfOutputDir, "dosbox.bat"))

    # Post-conversion for Recalbox for a given game
    def postConversionForRecalbox(self):
        self.logger.log("  Recalbox post-conversion")
        if 'mapper' in self.conversionConf and self.conversionConf['mapper'] == 'Yes':
            p2kTemplate = open(os.path.join(self.scriptDir, 'data', 'P2K.template.txt'), 'r')
            p2kFile = open(os.path.join(self.getLocalParentOutputDir(), self.game + '.pc.p2k.cfg'), 'w',
                           encoding='utf-8')
            for line in p2kTemplate.readlines():
                p2kFile.write(line.replace('{GameID}', self.metadata.name))
            p2kFile.close()
            p2kTemplate.close()

    def postConversionForBatocera(self):
        self.logger.log("  Batocera post-conversion")
        if 'mapper' in self.conversionConf and self.conversionConf['mapper'] == 'Yes':
            # TODO Remove included padt2.keys when new full generation well tested by users
            Mapping(self.keyb2joypad.gamesConf, util.getCleanGameID(self.metadata, ''), self.getLocalGameOutputDir(),
                    self.conversionConf, self.logger).mapForBatocera()

    # Post-conversion for MiSTeR for a given game
    def postConversionForMister(self):
        self.logger.log("  MiSTer post-conversion")
        # Remove any C: from dosbox.bat, rename to launch.bat, remove dosbox.cfg
        os.remove(os.path.join(self.getLocalGameOutputDir(), 'dosbox.cfg'))
        # Move CDs to cdgames/gamefolder and rename commands
        mister.batsAndMounts(self)
        shutil.move(os.path.join(self.getLocalGameOutputDir(), util.getCleanGameID(self.metadata, '.txt')),
                    os.path.join(self.getLocalGameOutputDir(), '2_About.txt'))
        # Remove unused CDs
        mister.removeUnusedCds(self.game, self.getLocalGameDataOutputDir(), self.logger)
        # Remove any COMMAND.COM and CHOICE.EXE files, as they are not compatible with MiSTeR
        if self.isWin3x:
            tobeRemoved = [file for file in os.listdir(self.getLocalGameOutputDir()) if
                           file.lower() in ['command.com', 'choice.exe']]
            for fileToRemove in tobeRemoved:
                self.logger.log("    remove non-compatible file %s" % fileToRemove)
                os.remove(os.path.join(self.getLocalGameOutputDir(), fileToRemove))
        else:
            tobeRemoved = [file for file in os.listdir(os.path.join(self.getLocalGameDataOutputDir())) if
                           file.lower() in ['command.com', 'choice.exe']]
            for fileToRemove in tobeRemoved:
                self.logger.log("    remove non-compatible file %s" % fileToRemove)
                os.remove(os.path.join(self.getLocalGameDataOutputDir(), fileToRemove))
        # Create about.jpg combining About.txt and pic of the game
        if self.metadata.frontPic is not None:
            cover = os.path.join(self.getLocalGameOutputDir(),
                                 '5_About' + os.path.splitext(self.metadata.frontPic)[-1])
            shutil.move(
                os.path.join(self.outputDir, 'downloaded_images', ntpath.basename(self.metadata.frontPic)), cover)
            aboutTxt = open(os.path.join(self.getLocalGameOutputDir(), '2_About.txt'), 'r', encoding='utf-8')
            mister.text2png(self.scriptDir, aboutTxt.read(), cover,
                            os.path.join(self.getLocalGameOutputDir(), '2_About.jpg'))
            aboutTxt.close()
            os.remove(os.path.join(self.getLocalGameOutputDir(), '2_About.txt'))
            os.remove(os.path.join(self.getLocalGameOutputDir(),
                                   '5_About' + os.path.splitext(self.metadata.frontPic)[-1]))

        misterCleanName = util.getCleanGameID(self.metadata, '').replace('+', '').replace("'", '').replace('µ',
                                                                                                           'mu') \
            .replace('¿', '').replace('é', 'e').replace('á', '').replace('ō', 'o').replace('#', '').replace('½', '') \
            .replace('$', '').replace('à', 'a').replace('&', 'and').replace(',', '')

        util.misterCleanNameToGameDir[misterCleanName] = self.game

        if not os.path.exists(os.path.join(self.outputDir, 'games')):
            os.mkdir(os.path.join(self.outputDir, 'games'))

        if self.conversionConf['preExtractGames']:
            # As the game will be pre-extracted, create empty zip, only containing a warning missing.bat file
            warningBat = open(os.path.join(self.outputDir, 'games', 'missing.bat'), 'w')
            warningBat.write('@echo off\nECHO You have used a pre-extracted games pack but the game data '
                             'files in your games directory are missing or corrupted .\n'
                             'Please regenerate your game data using the ExoDOSConverter,'
                             ' drop the game folder into E:\\GAMES\\GAMENAME and re-launch the game.\n')
            warningBat.close()
            with ZipFile(os.path.join(self.outputDir, 'games', misterCleanName + '.zip'), 'w') as zf:
                zf.write(os.path.join(self.outputDir, 'games', 'missing.bat'), 'missing.bat')
            os.remove(os.path.join(self.outputDir, 'games', 'missing.bat'))
            # Move game.pc folder to games-data
            if not os.path.exists(os.path.join(self.outputDir, 'games-data')):
                os.mkdir(os.path.join(self.outputDir, 'games-data'))
            shutil.move(os.path.join(self.getLocalGameOutputDir()),
                        os.path.join(self.outputDir, 'games-data', misterCleanName))
        else:
            # Zip internal game dir to longgamename.zip
            self.logger.log('    Rezipping game to %s.zip' % misterCleanName)
            shutil.make_archive(os.path.join(self.getLocalParentOutputDir(), misterCleanName), 'zip',
                                self.getLocalGameOutputDir())
            # Delete everything unrelated
            shutil.rmtree(os.path.join(self.getLocalGameOutputDir()))
            # Move archive to games folder
            shutil.move(os.path.join(self.getLocalParentOutputDir(), misterCleanName + '.zip'),
                        os.path.join(self.outputDir, 'games'))

    # Post-conversion for openDingux for a given game
    def postConversionForOpenDingux(self):
        self.logger.log("  opendingux post-conversion")
        openDinguxPicDir = '.previews' if self.conversionType == util.esoteric else '.media'
        # Copy image to opendingux img folder for game.pc
        distPicPath = os.path.join(self.getLocalParentOutputDir(), openDinguxPicDir)
        if not os.path.exists(distPicPath):
            os.mkdir(distPicPath)
        shutil.copy2(self.metadata.frontPic, os.path.join(distPicPath, self.game + '.pc.png'))
        # Resize image
        util.resize(os.path.join(distPicPath, self.game + '.pc.png'))
        # Copy image to opendingux img folder for game.pc/dosbox.bat
        dosboxBatPicPath = os.path.join(self.getLocalGameOutputDir(), openDinguxPicDir)
        if not os.path.exists(dosboxBatPicPath):
            os.mkdir(dosboxBatPicPath)
        shutil.copy2(os.path.join(distPicPath, self.game + '.pc.png'),
                     os.path.join(dosboxBatPicPath, 'dosbox.png'))
        if 'mapper' in self.conversionConf and self.conversionConf['mapper'] == 'Yes':
            # Generate RG350 mapper
            mapper = open(os.path.join(self.getLocalGameOutputDir(), "mapper.map"), 'w')
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

    # Post-conversion for Retropie for a given game
    def postConversionForRetropie(self):
        self.logger.log("  retropie post-conversion")
        dosboxCfg = open(os.path.join(self.getLocalGameOutputDir(), "dosbox.cfg"), 'a')
        # add mount c at end of dosbox.cfg
        romsFolder = util.getRomsFolderPrefix(self.conversionType, self.conversionConf)
        retropieGameDir = romsFolder + "/" + self.genre + "/" + self.game + ".pc" if self.useGenreSubFolders else romsFolder + "/" + self.game + ".pc"
        dosboxCfg.write("mount c " + retropieGameDir + "\n")
        dosboxCfg.write("c:\n")
        # copy all instructions from dosbox.bat to end of dosbox.cfg
        dosboxBat = open(os.path.join(self.getLocalGameOutputDir(), "dosbox.bat"), 'r')  # retroarch dosbox.bat
        for cmdLine in dosboxBat.readlines():
            dosboxCfg.write(cmdLine)
        # delete dosbox.bat
        dosboxCfg.close()
        dosboxBat.close()
        os.remove(os.path.join(self.getLocalGameOutputDir(), "dosbox.bat"))
        # move dosbox.cfg to {game}.conf at top level
        shutil.move(os.path.join(self.getLocalGameOutputDir(), "dosbox.cfg"),
                    os.path.join(self.getLocalParentOutputDir(), util.getCleanGameID(self.metadata, '.conf')))

    ########################################
