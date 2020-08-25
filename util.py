import os.path

def gameDirMap(gamesDosDir, games) :
    gameDict = dict()
    for game in games :
        bats = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join(gamesDosDir,game)) if os.path.splitext(filename)[-1].lower() == '.bat' and not os.path.splitext(filename)[0].lower() == 'install']
        gameDict[bats[0]] = game if len(bats) == 1 else game
            
    return gameDict

def buildCache(scriptDir, exoDosDir):
    cacheDir = os.path.join(scriptDir,'cache')
    if not os.path.exists(cacheDir) :
        os.mkdir(cacheDir)
        
    cache = os.path.join(cacheDir,'cache.csv')
    if not os.path.exists(cache) :
        print("Building cache... this will take a while")
        cacheFile = open(cache,'w')
        
        #TODO needs to build a full cache for this and metadatas
        gamesDosDir = os.path.join(exoDosDir,"Games","!dos")
        games = [filename for filename in os.listdir(gamesDosDir)]
        fullnameToGameDir = gameDirMap(gamesDosDir,games);
        print(fullnameToGameDir)
        
        cacheFile.close()
    else :
        print("Reading cache")