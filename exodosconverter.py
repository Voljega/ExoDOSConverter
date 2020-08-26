import os,shutil, subprocess, sys
from confconverter import ConfConverter

class ExoDOSConverter():
    
    def __init__(self,games,exoDosDir,gamesDosDir,outputDir, metadataHandler,logger) :
        self.games = games
        self.exoDosDir = exoDosDir
        self.logger = logger
        self.gamesDosDir = gamesDosDir
        self.outputDir = outputDir
        self.metadataHandler = metadataHandler
        self.confConverter = ConfConverter(self.games, self.exoDosDir, self.outputDir, self.logger)
    
    def convertGames(self) :
        self.logger.log("Loading metadatas...")
        self.metadataHandler.parseXmlMetadata()
        self.logger.log("")
        if not os.path.exists(os.path.join(self.outputDir,'downloaded_images')) :
            os.mkdir(os.path.join(self.outputDir,'downloaded_images'))
        if not os.path.exists(os.path.join(self.outputDir,'manuals')) :
            os.mkdir(os.path.join(self.outputDir,'manuals'))
        
        gamelist = self.metadataHandler.initXml(self.outputDir)
        
        count = 1;
        total = len(self.games)
        for game in self.games :
            try:
                self.convertGame(game, gamelist, total, count)                
            except:
                self.logger.log('Error %s while converting game %s' %(sys.exc_info()[0],game))
                
            count = count + 1
        
        self.metadataHandler.writeXml(self.outputDir, gamelist)
        self.logger.log('\n<--------- Finished Process --------->')
        
    def convertGame(self, game, gamelist, total, count) :
        genre = self.metadataHandler.buildGenre(self.metadataHandler.metadatas.get(game))        
        
        if not os.path.exists(os.path.join(self.outputDir,genre,game+".pc")):
            self.logger.log(">>> %i/%i >>> %s: starting conversion" %(count,total,game))
            
            self.metadataHandler.processGame(game,gamelist,genre, self.outputDir)
            
            if not os.path.exists(os.path.join(self.exoDosDir,"Games",game)):
                self.logger.log("  needs installation...")
                #automatic F and N
                subprocess.call("cmd /C (echo Y&echo F&echo N) | Install.bat", cwd=os.path.join(self.gamesDosDir,game), shell=False)
                self.logger.log("  installed")
            else :
                self.logger.log("  already installed")
            
            self.copyGameFiles(game,genre)    
            self.confConverter.process(game,genre)
        else :
            self.logger.log(">>> %i/%i >>> %s: already converted in output folder" %(count,total,game))
        
        self.logger.log("")      
        
        
    def copyGameFiles(self,game,genre):
        dest = os.path.join(self.outputDir,genre,game+".pc",game)
        self.logger.log("  copy game data")        
        # Copy game files in game.pc/game
        shutil.copytree(os.path.join(self.exoDosDir,"Games",game),dest)
        self.logger.log("  copy dosbox conf")
         # Copy dosbox.conf in game.pc
        shutil.copy2(os.path.join(self.exoDosDir,"Games","!dos",game,"dosbox.conf"),os.path.join(dest,"dosbox.conf"))
        