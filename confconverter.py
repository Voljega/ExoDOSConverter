import os
from commandhandler import CommandHandler
import util


# Converts dosbox.conf to dosbox.cfg and dosbox.bat, at the moment Batocera/ Recalbox linux flavor
class ConfConverter:

    def __init__(self, games, exoDosDir, outputDir, useGenreSubFolders, conversionType, conversionConf, logger):
        self.games = games
        self.logger = logger
        self.exoDosDir = exoDosDir
        self.outputDir = outputDir
        self.useGenreSubFolders = useGenreSubFolders
        self.conversionType = conversionType
        self.conversionConf = conversionConf
        self.commandHandler = CommandHandler(self.outputDir, self.logger)

    # Handle Parameter in ExpertMod
    def getExpertParam(self, parameter, defaultValue):
        if self.conversionConf['useExpertMode']:
            return self.conversionConf[parameter]
        else:
            return defaultValue

    # Converts exoDos dosbox.conf to dosbox.cfg and dosbox.bat
    def process(self, game, localGameOutputDir, genre):
        self.logger.log("  create dosbox.bat")
        exoDosboxConf = open(os.path.join(localGameOutputDir, game, "dosbox.conf"), 'r')  # original
        retroDosboxCfg = open(os.path.join(localGameOutputDir, "dosbox.cfg"), 'w')  # retroarch dosbox.cfg
        retroDosboxBat = open(os.path.join(localGameOutputDir, "dosbox.bat"), 'w')  # retroarch dosbox.bat

        count = 0
        lines = exoDosboxConf.readlines()
        for cmdline in lines:
            if cmdline.startswith("fullscreen"):
                retroDosboxCfg.write("fullscreen=true\n")
            elif cmdline.startswith("fullresolution"):
                if self.conversionType == util.retrobat:
                    retroDosboxCfg.write(cmdline)
                else:
                    retroDosboxCfg.write("fullresolution=" + self.getExpertParam("fullresolutionCfg", "desktop") + "\n")
            elif cmdline.startswith("output"):
                if self.conversionType == util.retrobat:
                    retroDosboxCfg.write(cmdline)
                else:
                    retroDosboxCfg.write("output=" + self.getExpertParam("outputCfg", "texture") + "\n")
                retroDosboxCfg.write("renderer=" + self.getExpertParam("rendererCfg", "auto") + "\n")
                if self.conversionConf['vsyncCfg']:
                    retroDosboxCfg.write("vsync=true\n")
                else:
                    retroDosboxCfg.write("vsync=false\n")

            # Always write these
            elif cmdline.startswith("aspect"):
                retroDosboxCfg.write("aspect=true\n")
            elif cmdline.startswith("buttonwrap"):
                retroDosboxCfg.write("buttonwrap=false\n")
            elif cmdline.startswith("mapperfile"):
                retroDosboxCfg.write("mapperfile=mapper.map\n")
            elif cmdline.startswith("ultradir"):
                retroDosboxCfg.write(r"ultradir=C:\ULTRASND")
                retroDosboxCfg.write("\n")
            elif cmdline.startswith("[autoexec]"):
                retroDosboxCfg.write(cmdline)
                self.createDosboxBat(lines[count + 1:], retroDosboxBat, retroDosboxCfg, game, localGameOutputDir, genre)
                break
            else:
                retroDosboxCfg.write(cmdline)

            count = count + 1

        exoDosboxConf.close()
        os.remove(os.path.join(localGameOutputDir, game, "dosbox.conf"))
        retroDosboxCfg.close()
        retroDosboxBat.close()

    # Creates dosbox.bat from dosbox.conf [autoexec] part
    def createDosboxBat(self, cmdlines, retroDosboxBat, retroDosboxCfg, game, localGameOutputDir, genre):
        for cmdline in cmdlines:
            # keep conf in dosbox.cfg but comment it
            if self.conversionConf['useDebugMode']:
                retroDosboxCfg.write("# " + cmdline)
            self.convertLine(cmdline, retroDosboxBat, game, localGameOutputDir, genre)

    # Convert command line to dosbox.bat
    def convertLine(self, cmdline, retroDosboxBat, game, localGameOutputDir, genre):
        cutLines = ["cd ..", "cls", "mount c", "#", "exit", "echo off", "echo on"]
        # always remove @
        cmdline = cmdline.lstrip('@ ')

        if self.commandHandler.useLine(cmdline, cutLines):
            if cmdline.lower().startswith("c:"):
                retroDosboxBat.write(cmdline)
                # First add move into game subdir
                retroDosboxBat.write("cd %s\n" % game)
                # remove cd to gamedir as it is already done, but keep others cd
            elif cmdline.lower().startswith("cd "):
                path = self.commandHandler.reducePath(cmdline.rstrip('\n\r ').split(" ")[-1].rstrip('\n\r '), game)
                if path.lower() == game.lower() and not os.path.exists(
                        os.path.join(localGameOutputDir, game, path)):
                    self.logger.log("    cd command: '%s' -> path is game name and no existing subpath, removed"
                                    % cmdline.rstrip('\n\r '))
                else:
                    self.logger.log("    cd command: '%s' -> kept" % cmdline.rstrip('\n\r '))
                    retroDosboxBat.write(cmdline)
            elif cmdline.lower().startswith("imgmount "):
                retroDosboxBat.write(self.commandHandler.handleImgmount(cmdline, game, localGameOutputDir))
                if self.conversionConf['useDebugMode']:
                    retroDosboxBat.write("\npause\n")
                else:
                    retroDosboxBat.write("\n")
            elif cmdline.lower().startswith("mount "):
                retroDosboxBat.write(self.commandHandler.handleMount(cmdline, game, localGameOutputDir, genre,
                                                                     self.useGenreSubFolders, self.conversionType,
                                                                     self.conversionConf))
                if self.conversionConf['useDebugMode']:
                    retroDosboxBat.write("\npause\n")
                else:
                    retroDosboxBat.write("\n")
            elif cmdline.lower().startswith("boot "):
                retroDosboxBat.write(self.commandHandler.handleBoot(cmdline, game, localGameOutputDir, genre,
                                                                    self.useGenreSubFolders, self.conversionType))
            elif cmdline.lower().rstrip(' \n\r') == 'call run' or cmdline.lower().rstrip(' \n\r') == 'call run.bat':
                self.logger.log("    <WARNING> game uses call run.bat", self.logger.WARNING)
                if game in ['bisle2', 'Blood', 'Carmaged', 'comcon', 'comconra', 'CrypticP', 'lemm3', 'LewLeon',
                            'MechW2', 'rarkani1', 'Resurrec', 'stjudgec']:
                    self.handleRunBat(game, localGameOutputDir)
                retroDosboxBat.write(cmdline)
            else:
                retroDosboxBat.write(cmdline)

    # Treat run.bat command inside game directory
    def handleRunBat(self, game, localGameOutputDir):
        runBat = os.path.join(localGameOutputDir, game, 'run.bat')
        if os.path.exists(runBat):
            runFile = open(runBat, 'r')
            runFileClone = open(runBat + '1', 'w')
            # Clone run.bat and only modify imgmount lines
            # Add some hardcoded lines which are impossible to handle
            handled = {
                'imgmount d ".\\games\\comcon\\cd\\Command & Conquer CD-2.iso" ".\\games\\comcon\\cd\\Command & Conquer CD-1.iso" ".\\games\\comcon\\cd\\Covert Operations.cue" -t cdrom \n':
                    'imgmount d ".\\cd\\comma2.iso" ".\\cd\\comma1.iso" ".\\cd\\cover3.cue" -t cdrom',
                'imgmount d ".\\games\\comcon\\cd\\Covert Operations.cue" ".\\games\\comcon\\cd\\Command & Conquer CD-2.iso" ".\\games\\comcon\\cd\\Command & Conquer CD-1.iso" -t cdrom \n':
                    'imgmount d ".\\cd\\cover3.cue" ".\\cd\\comma2.iso" ".\\cd\\comma1.iso" -t cdrom',
                'imgmount d ".\\games\\comconra\\cd\\Red Alert CD2.iso" ".\\games\\comconra\\cd\\Red Alert CD1.iso" ".\\games\\comconra\\cd\\Red Alert Counterstrike CD3.iso" ".\\games\\comconra\\cd\\Red Alert Aftermath CD4.iso" -t cdrom \n':
                    'imgmount d ".\\cd\\redal2.iso" ".\\cd\\redal1.iso" ".\\cd\\redal3.iso" ".\\cd\\redal4.iso" -t cdrom',
                'imgmount d ".\\games\\comconra\\cd\\Red Alert Aftermath CD4.iso" ".\\games\\comconra\\cd\\Red Alert CD1.iso" ".\\games\\comconra\\cd\\Red Alert CD2.iso" ".\\games\\comconra\\cd\\Red Alert Counterstrike CD3.iso" -t cdrom \n':
                    'imgmount d ".\\cd\\redal4.iso" ".\\cd\\redal1.iso" ".\\cd\\redal2.iso" ".\\cd\\redal3.iso" -t cdrom',
                'imgmount d ".\\games\\comconra\\cd\\Red Alert Counterstrike CD3.iso" ".\\games\\comconra\\cd\\Red Alert CD1.iso" ".\\games\\comconra\\cd\\Red Alert CD2.iso" ".\\games\\comconra\\cd\\Red Alert Aftermath CD4.iso" -t cdrom \n':
                    'imgmount d ".\\cd\\redal3.iso" ".\\cd\\redal1.iso" ".\\cd\\redal2.iso" ".\\cd\\redal4.iso" -t cdrom',
                'imgmount -u d\n': '\n'
            }
            for cmdline in runFile.readlines():
                # always remove @
                cmdline = cmdline.lstrip('@ ')
                if cmdline.lower().startswith("imgmount "):
                    if cmdline not in handled:
                        handled[cmdline] = self.commandHandler.handleImgmount(cmdline, game, localGameOutputDir, True)
                    runFileClone.write(handled[cmdline])
                    if self.conversionConf['useDebugMode']:
                        runFileClone.write("\npause\n")
                    else:
                        runFileClone.write("\n")
                else:
                    runFileClone.write(cmdline)
            runFileClone.close()
            runFile.close()
            # Delete runbat and rename runbat clone to runbat
            os.remove(os.path.join(localGameOutputDir, game, 'run.bat'))
            os.rename(os.path.join(localGameOutputDir, game, 'run.bat1'),
                      os.path.join(localGameOutputDir, game, 'run.bat'))
        else:
            self.logger.log('      <ERROR> run.bat not found', self.logger.ERROR)
