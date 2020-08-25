import os,shutil, subprocess, sys
from metadatahandler import MetadataHandler
from confconverter import ConfConverter

class ExoDOSConverter():
    
    def __init__(self,games,exoDosDir,gamesDosDir,outputDir) :
        self.games = games
        self.exoDosDir = exoDosDir
        self.gamesDosDir = gamesDosDir
        self.outputDir = outputDir
        self.metadataHandler = MetadataHandler(self.gamesDosDir, self.outputDir)
        self.confConverter = ConfConverter(self.games, self.exoDosDir, self.outputDir)
    
    def convertGames(self) :
        gamelist = open(os.path.join(self.outputDir,"gamelist.xml"),'w')
        gamelist.write('<?xml version="1.0"?>\n')
        gamelist.write("<gameList>\n")
#        TODO catch exceptions on game by game basis
        for game in self.games :
            try:
                self.convertGame(game, gamelist)
            except:
                print('Error %s while converting game %s' %(sys.exc_info()[0],game))
    
        gamelist.write("</gameList>\n")
        gamelist.close()
        
    def convertGame(self, game, gamelist) :
        print("----------- Starting conversion for %s -----------" %game)        
        genre = self.metadataHandler.process(game,gamelist)
        
        if not os.path.exists(os.path.join(self.outputDir,genre,game+".pc")):
            if not os.path.exists(os.path.join(self.exoDosDir,"Games",game)):
                print("%s needs installation" %game)
                #automatic F and N
                subprocess.call("cmd /C (echo Y&echo F&echo N) | Install.bat", cwd=os.path.join(self.gamesDosDir,game), shell=False)
                print("installed %s" %game)
            else :
                print("%s is already installed" %game)
     
            self.copyGameFiles(game,genre)    
            self.confConverter.process(game,genre)       
        
        else :
            print("%s already in output folder" %game)
        
        print("----------- Finished conversion for %s -----------" %game)
        print("")      
        
        
    def copyGameFiles(self,game,genre):
        dest = os.path.join(self.outputDir,genre,game+".pc",game)
        print("copy %s game dir" %game)        
        # Copy game files in game.pc/game
        shutil.copytree(os.path.join(self.exoDosDir,"Games",game),dest)
        print("copy dosbox conf")
         # Copy game files in game.pc
        shutil.copy2(os.path.join(self.exoDosDir,"Games","!dos",game,"dosbox.conf"),os.path.join(dest,"dosbox.conf"))
        