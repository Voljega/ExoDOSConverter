import os
from commandhandler import CommandHandler

# Converts dosbox.conf to dosbox.cfg and dosbox.bat, at the moment Batocera/ Recalbox linux flavor
class ConfConverter():
    
    def __init__(self,games,exoDosDir,outputDir,useGenreSubFolders,conversionType,logger) :
        self.games = games
        self.logger = logger
        self.exoDosDir = exoDosDir
        self.outputDir = outputDir
        self.useGenreSubFolders = useGenreSubFolders
        self.conversionType = conversionType
        self.commandHandler = CommandHandler(self.outputDir, self.logger)
    
    # Converts exoDos dosbox.conf to dosbox.cfg and dosbox.bat
    def process(self,game,dest,genre) :
        self.logger.log("  create dosbox.bat")
        exoDosboxConf = open(os.path.join(dest,game,"dosbox.conf"),'r')#original
        retroDosboxCfg = open(os.path.join(dest,"dosbox.cfg"),'w')#retroarch dosbox.cfg
        retroDosboxBat = open(os.path.join(dest,"dosbox.bat"),'w')#retroarch dosbox.bat
        
        count = 0
        lines = exoDosboxConf.readlines()
        # TODO modify exoDos dosbox.conf to custom dosbox.cfg (including commenting [autoexec] part), might need to be put in a function and reworked
        for cmdline in lines :
            if cmdline.startswith("fullscreen"):
                retroDosboxCfg.write("fullscreen=true\n")
            elif cmdline.startswith("fullresolution"):
                retroDosboxCfg.write("fullresolution=desktop\n")
            elif cmdline.startswith("output"):
                retroDosboxCfg.write("output=texture\n")
                retroDosboxCfg.write("renderer = auto\n")
                retroDosboxCfg.write("vsync=false\n")            
            elif cmdline.startswith("buttonwrap") :            
                retroDosboxCfg.write("buttonwrap=false\n")
            elif cmdline.startswith("mapperfile"):
                retroDosboxCfg.write("mapperfile=mapper.map\n")
            elif cmdline.startswith("ultradir"):
                retroDosboxCfg.write(r"ultradir=C:\ULTRASND")
                retroDosboxCfg.write("\n")
            elif cmdline.startswith("[autoexec]"):
                retroDosboxCfg.write(cmdline)          
                self.createDosboxBat(lines[count+1:],retroDosboxBat,retroDosboxCfg,game,dest,genre)
                break
            else :
                retroDosboxCfg.write(cmdline)
        
            count = count +1
        
        exoDosboxConf.close()
        os.remove(os.path.join(dest,game,"dosbox.conf"))
        retroDosboxCfg.close()
        retroDosboxBat.close()        
    
    # Creates dosbox.bat from dosbox.conf [autoexec] part
    def createDosboxBat(self,cmdlines,retroDosboxBat,retroDosboxCfg,game,dest,genre) :
        gameDir = os.path.join(self.exoDosDir,"Games",game)
        cutLines = ["cd ..","cls","mount c","#","exit","echo off","echo on"]
        
        for cmdline in cmdlines :
            # keep conf in dosbox.cfg but comment it
            retroDosboxCfg.write("# "+cmdline)
            # always remove @
            cmdline = cmdline.lstrip('@ ')
            
            if self.commandHandler.useLine(cmdline,cutLines) :
                if cmdline.lower().startswith("c:") :
                    retroDosboxBat.write(cmdline)
                    # First add move into game subdir
                    retroDosboxBat.write("cd %s\n" %game)        
                #remove cd to gamedir as it is already done, but keep others cd     
                elif cmdline.lower().startswith("cd "):                
                    path = self.commandHandler.reducePath(cmdline.rstrip('\n\r ').split(" ")[-1].rstrip('\n\r '),game)
                    if path.lower() == game.lower() and not os.path.exists(os.path.join(gameDir,path)):
                        self.logger.log("    cd command: '%s' -> path is game name and no existing subpath, removed" %cmdline.rstrip('\n\r '))
                    else :
                        self.logger.log("    cd command: '%s' -> kept" %cmdline.rstrip('\n\r '))
                        retroDosboxBat.write(cmdline)
                elif cmdline.lower().startswith("imgmount "):
                    retroDosboxBat.write(self.commandHandler.handleImgmount(cmdline,game,dest))
                    retroDosboxBat.write("pause\n")
                elif cmdline.lower().startswith("mount "):
                    retroDosboxBat.write(self.commandHandler.handleMount(cmdline,game,dest,genre,self.useGenreSubFolders,self.conversionType))
                    retroDosboxBat.write("\npause\n")
                else :
                    retroDosboxBat.write(cmdline)
