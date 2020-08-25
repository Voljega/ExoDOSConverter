import os,shutil
from metadatahandler import MetadataHandler
from commandhandler import CommandHandler

class ConfConverter():
    
    def __init__(self,games,exoDosDir,outputDir) :
        self.games = games
        self.exoDosDir = exoDosDir
        self.outputDir = outputDir
        self.commandHandler = CommandHandler(self.outputDir)

    def process(self,game,genre) :
        dest = os.path.join(self.outputDir,genre,game+".pc")
        exoDosboxConf = open(os.path.join(dest,game,"dosbox.conf"),'r')#original
        retroDosboxCfg = open(os.path.join(dest,"dosbox.cfg"),'w')#retroarch dosbox.cfg
        retroDosboxBat = open(os.path.join(dest,"dosbox.bat"),'w')#retroarch dosbox.bat
        
        count =0
        lines = exoDosboxConf.readlines()
        for line in lines :
            if line.startswith("fullscreen"):
                retroDosboxCfg.write("fullscreen=true\n")
            elif line.startswith("fullresolution"):
                retroDosboxCfg.write("fullresolution=desktop\n")
            elif line.startswith("output"):
                retroDosboxCfg.write("output=texture\n")
                retroDosboxCfg.write("renderer = auto\n")
                retroDosboxCfg.write("vsync=false\n")            
            elif line.startswith("buttonwrap") :            
                retroDosboxCfg.write("buttonwrap=false\n")
            elif line.startswith("mapperfile"):
                retroDosboxCfg.write("mapperfile=mapper.map\n")
            elif line.startswith("ultradir"):
                retroDosboxCfg.write(r"ultradir=C:\ULTRASND")
                retroDosboxCfg.write("\n")
            elif line.startswith("[autoexec]"):
                retroDosboxCfg.write(line)          
                self.createDosboxBat(lines[count+1:],retroDosboxBat,retroDosboxCfg,game,dest)
                break
            else :
                retroDosboxCfg.write(line)
        
            count = count +1
        
        exoDosboxConf.close()
        os.remove(os.path.join(dest,game,"dosbox.conf"))
        retroDosboxCfg.close()
        retroDosboxBat.close()        
        
    def createDosboxBat(self,lines,retroDosboxBat,retroDosboxCfg,game,dest) :
        gameDir = os.path.join(self.exoDosDir,"Games",game)
        #nécessaire de voir où est monté mount c ?
        cutLines = ["cd ..","cd ..","cls","mount c","mount c","#","exit"]
        # TODO First move into game dir but better add that after included c:
        retroDosboxBat.write("cd %s\n" %game)
        for line in lines :
            # keep conf in dosbox.cfg but comment it
            retroDosboxCfg.write("# "+line)
            # always remove @
            line = line.lstrip('@ ')
            
            if self.commandHandler.isGoodLine(line,cutLines) :
                #remove cd to gamedir            
                if line.lower().startswith("cd "):                
                    path = self.commandHandler.reducePath(line.rstrip('\n\r ').split(" ")[-1].rstrip('\n\r '),game)
                    # TODO should be adapted coz games are in subfolder now
                    if path.lower() == game.lower() and not os.path.exists(os.path.join(gameDir,path)):
                        print("analyzing cd path %s -> path is game name and no existing subpath, removed" %line.rstrip('\n\r '))
                    else :
                        print("analyzing cd path %s -> kept" %line.rstrip('\n\r '))
                        retroDosboxBat.write(line)
                elif line.lower().startswith("imgmount d"):
                    retroDosboxBat.write(self.commandHandler.handleCDMount(line,game,dest))
                    retroDosboxBat.write("pause\n")
                elif line.lower().startswith("mount "):
                    retroDosboxBat.write(self.commandHandler.handleCDMount(line,game,dest))
                    retroDosboxBat.write("pause\n")
                else :
                    retroDosboxBat.write(line)       
        #insérer pause
