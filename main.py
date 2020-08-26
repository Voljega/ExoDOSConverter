import os.path, sys
from exodosconverter import ExoDOSConverter
from metadatahandler import MetadataHandler
import util

exoDosDir = r"G:\Romsets\eXoDOS4"
outputDir = r'G:\ExoDOSConverted'

if __name__ == "__main__":
    scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
    
    nbGames = int(input("How many games do you want to convert ? : ").lower())
    print("Convert %i games" %(nbGames))
    
    if not os.path.isdir(exoDosDir) :
        print("%s is not a directory or doesn't exist" %exoDosDir)
        exit
    
    if not os.path.isdir(outputDir) :
        print("%s is not a directory or doesn't exist" %outputDir)
        exit
    
    cache = util.buildCache(scriptDir,exoDosDir)
    
    gamesDir = os.path.join(exoDosDir,"eXoDOS","Games")
    gamesDosDir = os.path.join(gamesDir,"!dos")
    games = [filename for filename in os.listdir(gamesDosDir)][:nbGames]
    
    if not os.path.isdir(gamesDir) or not os.path.isdir(gamesDosDir) :
        print("%s doesn't seem to be a valid ExoDOSCollection folder" %exoDosDir)
        exit
        
    metadataHandler = MetadataHandler(exoDosDir, cache)
    metadataHandler.parseXmlMetadata()   
    
    exoDOSConverter = ExoDOSConverter(games, os.path.join(exoDosDir,'eXoDOS'), gamesDosDir, outputDir, metadataHandler)
    exoDOSConverter.convertGames()
    

            
        