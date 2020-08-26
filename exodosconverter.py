import os,shutil, subprocess, sys
from confconverter import ConfConverter

class ExoDOSConverter():
    
    def __init__(self,games,exoDosDir,gamesDosDir,outputDir, metadataHandler) :
        self.games = games
        self.exoDosDir = exoDosDir
        self.gamesDosDir = gamesDosDir
        self.outputDir = outputDir
        self.metadataHandler = metadataHandler
        self.confConverter = ConfConverter(self.games, self.exoDosDir, self.outputDir)
    
    def convertGames(self) :
        if not os.path.exists(os.path.join(self.outputDir,'downloaded_images')) :
            os.mkdir(os.path.join(self.outputDir,'downloaded_images'))
        if not os.path.exists(os.path.join(self.outputDir,'manuals')) :
            os.mkdir(os.path.join(self.outputDir,'manuals'))
        # TODO handle gamelist in append mode if it already exists
        gamelist = self.metadataHandler.initXml(self.outputDir)
        print(gamelist.getroot().tag)
            
        # TODO catch exceptions on game by game basis
        for game in self.games :
            try:
                self.convertGame(game, gamelist)
            except:
                print('Error %s while converting game %s' %(sys.exc_info()[0],game))
        
        self.metadataHandler.writeXml(self.outputDir, gamelist)
        
    def convertGame(self, game, gamelist) :
        genre = self.metadataHandler.buildGenre(self.metadataHandler.metadatas.get(game))
        
        if not os.path.exists(os.path.join(self.outputDir,genre,game+".pc")):
            print(">>> %s: starting conversion" %game)
            
            self.metadataHandler.processGame(game,gamelist,genre, self.outputDir)
            
            if not os.path.exists(os.path.join(self.exoDosDir,"Games",game)):
                print("  needs installation...")
                #automatic F and N
                subprocess.call("cmd /C (echo Y&echo F&echo N) | Install.bat", cwd=os.path.join(self.gamesDosDir,game), shell=False)
                print("  installed")
            else :
                print("  already installed")
            
            self.copyGameFiles(game,genre)    
            self.confConverter.process(game,genre)
        else :
            print(">>> %s: already converted in output folder" %game)
        
        print("")      
        
        
    def copyGameFiles(self,game,genre):
        dest = os.path.join(self.outputDir,genre,game+".pc",game)
        print("  copy game data")        
        # Copy game files in game.pc/game
        shutil.copytree(os.path.join(self.exoDosDir,"Games",game),dest)
        print("  copy dosbox conf")
         # Copy dosbox.conf in game.pc
        shutil.copy2(os.path.join(self.exoDosDir,"Games","!dos",game,"dosbox.conf"),os.path.join(dest,"dosbox.conf"))
        