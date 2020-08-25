import os.path
from exodosconverter import ExoDOSConverter

exoDosDir = r"G:\Romsets\eXoDOS4\eXoDOS"
outputDir = r'G:\ExoDOSConverted'

if __name__ == "__main__":
    nbGames = int(input("How many games do you want to convert ? : ").lower())
#    startGame = input("At which game do you want to start ")
    print("Convert %i games" %(nbGames))
    
    if not os.path.isdir(exoDosDir) :
        print("%s is not a directory or doesn't exist" %exoDosDir)
        exit
    
    if not os.path.isdir(outputDir) :
        print("%s is not a directory or doesn't exist" %outputDir)
        exit
        
    gamesDir = os.path.join(exoDosDir,"Games")
    gamesDosDir = os.path.join(gamesDir,"!dos")
    
    if not os.path.isdir(gamesDir) or not os.path.isdir(gamesDosDir) :
        print("%s doesn't seem to be a valid ExoDOSCollection folder" %exoDosDir)
        exit
        
    games = [filename for filename in os.listdir(gamesDosDir)][:nbGames]
    
    exoDOSConverter = ExoDOSConverter(games, exoDosDir, gamesDosDir, outputDir)
    exoDOSConverter.convertGames()