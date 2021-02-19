import os
from commandhandler import CommandHandler
import util


# Converts dosbox.conf to dosbox.cfg and dosbox.bat, at the moment Batocera/ Recalbox linux flavor
class ConfConverter:

    def __init__(self, gGator):
        self.logger = gGator.logger
        self.conversionConf = gGator.conversionConf
        self.commandHandler = CommandHandler(gGator)
        # self.outputDir = gGator.outputDir
        # self.useGenreSubFolders = gGator.useGenreSubFolders
        # self.conversionType = gGator.conversionType
        # self.conversionConf = gGator.conversionConf
        # self.collectionVersion = gGator.collectionVersion
        # self.commandHandler = CommandHandler(gGator)

    # Handle Parameter in ExpertMod
    def getExpertParam(self, parameter, defaultValue):
        if self.conversionConf['useExpertMode']:
            return self.conversionConf[parameter]
        else:
            return defaultValue

    # Converts exo collection dosbox.conf to dosbox.cfg and dosbox.bat
    def process(self, gGator):
        self.logger.log("  create dosbox.bat")
        exoDosboxConf = open(os.path.join(gGator.getLocalGameDataOutputDir(), "dosbox.conf"), 'r') # original
        retroDosboxCfg = open(os.path.join(gGator.getLocalGameOutputDir(), "dosbox.cfg"), 'w')  # retroarch dosbox.cfg
        retroDosboxBat = open(os.path.join(gGator.getLocalGameOutputDir(), "dosbox.bat"), 'w')  # retroarch dosbox.bat

        count = 0
        lines = exoDosboxConf.readlines()
        for cmdline in lines:
            if cmdline.startswith("fullscreen"):
                retroDosboxCfg.write("fullscreen=true\n")
            elif cmdline.startswith("fullresolution"):
                if gGator.conversionType == util.retrobat:
                    retroDosboxCfg.write(cmdline)
                else:
                    retroDosboxCfg.write("fullresolution=" + self.getExpertParam("fullresolutionCfg", "desktop") + "\n")
            elif cmdline.startswith("output"):
                if gGator.conversionType == util.retrobat:
                    retroDosboxCfg.write(cmdline)
                else:
                    retroDosboxCfg.write("output=" + self.getExpertParam("outputCfg", "texture") + "\n")
                retroDosboxCfg.write("renderer=" + self.getExpertParam("rendererCfg", "auto") + "\n")
                if gGator.conversionConf['vsyncCfg']:
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
                self.createDosboxBat(lines[count + 1:], retroDosboxBat, retroDosboxCfg, gGator)
                break
            else:
                retroDosboxCfg.write(cmdline)

            count = count + 1

        exoDosboxConf.close()
        os.remove(os.path.join(gGator.getLocalGameDataOutputDir(), "dosbox.conf"))
        retroDosboxCfg.close()
        retroDosboxBat.close()

    # Creates dosbox.bat from dosbox.conf [autoexec] part
    def createDosboxBat(self, cmdlines, retroDosboxBat, retroDosboxCfg, gGator):
        for cmdline in cmdlines:
            # keep conf in dosbox.cfg but comment it
            if self.conversionConf['useDebugMode']:
                retroDosboxCfg.write("# " + cmdline)
            self.convertLine(cmdline, retroDosboxBat, gGator)

    # Convert command line to dosbox.bat
    def convertLine(self, cmdline, retroDosboxBat, gGator):
        cutLines = ["cd ..", "cls", "mount c", "#", "exit", "echo off", "echo on"]
        # always remove @
        cmdline = cmdline.lstrip('@ ')
        # TODO whereWeAt identifies where we are in the game tree based on instructions, use in the future ?
        whereWeAt = ['c:','.']
        if self.commandHandler.useLine(cmdline, cutLines):
            if cmdline.lower().startswith("c:"):
                retroDosboxBat.write(cmdline)
                if not gGator.isWin3x():
                    # First add move into game subdir
                    retroDosboxBat.write("cd %s\n" % gGator.game)
                    whereWeAt.append('game')
            # remove cd to gamedir as it is already done, but keep others cd
            elif cmdline.lower().startswith("cd "):
                path = self.commandHandler.reducePath(cmdline.rstrip('\n\r ').split(" ")[-1].rstrip('\n\r '))
                if path.lower() == gGator.game.lower() and not os.path.exists(
                        os.path.join(gGator.getLocalGameDataOutputDir(), path)):
                    self.logger.log("    cd command: '%s' -> path is game name and no existing subpath, removed"
                                    % cmdline.rstrip('\n\r '))
                else:
                    self.logger.log("    cd command: '%s' -> kept" % cmdline.rstrip('\n\r '))
                    retroDosboxBat.write(cmdline)
                    whereWeAt.append(path)
            elif cmdline.lower().startswith("imgmount "):
                retroDosboxBat.write(self.commandHandler.handleImgmount(cmdline.rstrip('\n\r ')))
                if self.conversionConf['useDebugMode']:
                    retroDosboxBat.write("\npause\n")
                else:
                    retroDosboxBat.write("\n")
            elif cmdline.lower().startswith("mount "):
                retroDosboxBat.write(self.commandHandler.handleMount(cmdline.rstrip('\n\r ')))
                if self.conversionConf['useDebugMode']:
                    retroDosboxBat.write("\npause\n")
                else:
                    retroDosboxBat.write("\n")
            elif cmdline.lower().startswith("boot "):
                retroDosboxBat.write(self.commandHandler.handleBoot(cmdline.rstrip('\n\r ')))
            elif cmdline.lower().rstrip(' \n\r') == 'call run' or cmdline.lower().rstrip(' \n\r') == 'call run.bat':
                self.logger.log("    <WARNING> game uses call run.bat", self.logger.WARNING)
                if gGator.game in ['bisle2', 'Blood', 'Carmaged', 'comcon', 'comconra', 'CrypticP', 'lemm3', 'LewLeon',
                            'MechW2', 'rarkani1', 'Resurrec', 'stjudgec', 'heromm2d']:
                    self.handleRunBat(gGator)
                self.handlePotentialSubFile(cmdline, gGator)
                retroDosboxBat.write(cmdline)
            else:
                self.handlePotentialSubFile(cmdline, gGator)
                retroDosboxBat.write(cmdline)

    # Handle potential sub files and problems in it
    def handlePotentialSubFile(self, subPath, gGator, handledSubFiles=[]):
        subPath = subPath.lstrip('@ ').lower().replace('call ','') if subPath.lstrip('@ ').lower().startswith("call ") else subPath
        subBat = os.path.join(gGator.getLocalGameDataOutputDir(), subPath.rstrip(' \n\r') + '.bat')
        if os.path.exists(subBat) and not os.path.isdir(subBat) and subBat.lower() not in handledSubFiles:
            self.logger.log('    Handle Bat File %s' % subBat, self.logger.WARNING)
            handledSubFiles.append(subBat.lower())
            subBatFile = open(subBat, 'r')
            subBatFileClone = open(subBat + '1', 'w', newline='\r\n')
            for cmdline in subBatFile.readlines():
                # always remove @
                cmdline = cmdline.lstrip('@ ')
                if cmdline.lower().rstrip(' \n\r') == 'c:' and gGator.conversionType == util.mister:
                    self.logger.log('      Remove c: for MiSTeR', self.logger.WARNING)
                else:
                    if 'c:\\' in cmdline.lower():
                        if gGator.conversionType == util.mister:
                            # TODO might need win3x fix
                            cmdline = cmdline.replace('c:', 'E:\\GAMES\\' + gGator.game).replace('C:', 'E:\\GAMES\\' + gGator.game)
                        else:
                            if not gGator.isWin3x():
                                cmdline = cmdline.replace('c:','c:\\'+gGator.game).replace('C:','C:\\'+gGator.game)
                    else:
                        self.handlePotentialSubFile(cmdline, gGator, handledSubFiles)
                    subBatFileClone.write(cmdline)
            subBatFileClone.close()
            subBatFile.close()
            # Delete runbat and rename runbat clone to runbat
            os.remove(subBat)
            os.rename(subBat + '1', subBat)

    # Treat run.bat command inside game directory
    def handleRunBat(self, gGator):
        runBat = os.path.join(gGator.getLocalGameDataOutputDir(), 'run.bat')
        if os.path.exists(runBat):
            runFile = open(runBat, 'r')
            runFileClone = open(runBat + '1', 'w', newline='\r\n')
            # Clone run.bat and only modify imgmount lines
            # Add some hardcoded lines which are impossible to handle
            handled = {
                'imgmount d ".\\eXoDOS\\comcon\\cd\\Command & Conquer CD-2.iso" ".\\eXoDOS\\comcon\\cd\\Command & Conquer CD-1.iso" ".\\eXoDOS\\comcon\\cd\\Covert Operations.cue" -t cdrom \n':
                    'imgmount d ".\\cd\\comma2.iso" ".\\cd\\comma1.iso" ".\\cd\\cover3.cue" -t cdrom',
                'imgmount d ".\\eXoDOS\\comcon\\cd\\Covert Operations.cue" ".\\eXoDOS\\comcon\\cd\\Command & Conquer CD-2.iso" ".\\eXoDOS\\comcon\\cd\\Command & Conquer CD-1.iso" -t cdrom \n':
                    'imgmount d ".\\cd\\cover3.cue" ".\\cd\\comma2.iso" ".\\cd\\comma1.iso" -t cdrom',
                'imgmount d ".\\eXoDOS\\comconra\\cd\\Red Alert CD2.iso" ".\\eXoDOS\\comconra\\cd\\Red Alert CD1.iso" ".\\eXoDOS\\comconra\\cd\\Red Alert Counterstrike CD3.cue" ".\\eXoDOS\\comconra\\cd\\Red Alert Aftermath CD4.cue" -t cdrom \n':
                    'imgmount d ".\\cd\\redal2.iso" ".\\cd\\redal1.iso" ".\\cd\\redal3.cue" ".\\cd\\redal4.cue" -t cdrom',
                'imgmount d ".\\eXoDOS\\comconra\\cd\\Red Alert Aftermath CD4.cue" ".\\eXoDOS\\comconra\\cd\\Red Alert CD1.iso" ".\\eXoDOS\\comconra\\cd\\Red Alert CD2.iso" ".\\eXoDOS\\comconra\\cd\\Red Alert Counterstrike CD3.cue" -t cdrom \n':
                    'imgmount d ".\\cd\\redal4.cue" ".\\cd\\redal1.iso" ".\\cd\\redal2.iso" ".\\cd\\redal3.cue" -t cdrom',
                'imgmount d ".\\eXoDOS\\comconra\\cd\\Red Alert Counterstrike CD3.cue" ".\\eXoDOS\\comconra\\cd\\Red Alert CD1.iso" ".\\eXoDOS\\comconra\\cd\\Red Alert CD2.iso" ".\\eXoDOS\\comconra\\cd\\Red Alert Aftermath CD4.cue" -t cdrom \n':
                    'imgmount d ".\\cd\\redal3.cue" ".\\cd\\redal1.iso" ".\\cd\\redal2.iso" ".\\cd\\redal4.cue" -t cdrom',
                'imgmount d ".\\eXoDOS\\comconra\\cd\\Red Alert Aftermath CD4.cue" -t cdrom \n': 'imgmount d .\\cd\\redal4.cue -t cdrom',
                'imgmount -u d\n': '\n'
            }
            for cmdline in runFile.readlines():
                # always remove @
                cmdline = cmdline.lstrip('@ ')
                if cmdline.lower().startswith("imgmount "):
                    if cmdline not in handled:
                        handled[cmdline] = self.commandHandler.handleImgmount(cmdline, True)
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
            os.remove(os.path.join(gGator.getLocalGameDataOutputDir(), 'run.bat'))
            os.rename(os.path.join(gGator.getLocalGameDataOutputDir(), 'run.bat1'), os.path.join(gGator.getLocalGameDataOutputDir(), 'run.bat'))
        else:
            self.logger.log('      <ERROR> run.bat not found', self.logger.ERROR)
