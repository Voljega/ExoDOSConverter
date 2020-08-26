import os.path

def findPic(gameName, cache, ext) :
    fullnameToGameDir, frontPicCache, titlePicCache, gameplayPicCache = cache
    imgName = (gameName+'-01'+ext).replace(':','_').replace("'",'_')
    imgPath = None
    if imgName in frontPicCache :
        imgPath = frontPicCache.get(imgName)
    elif imgName in titlePicCache :
        imgPath = titlePicCache.get(imgName)
    elif imgName in gameplayPicCache :
        imgPath = gameplayPicCache.get(imgName)
    return imgPath

def buildPicCache(imageFolder,picCache) :
    print("Building cache %s" %picCache)
    picCacheFile = open(picCache,'w')
    cache = dict()
    if os.path.exists(imageFolder) :
        rootImages = [file for file in os.listdir(imageFolder) if not os.path.isdir(file)]
        subFolders = [file for file in os.listdir(imageFolder) if os.path.isdir(os.path.join(imageFolder,file))]
        for image in rootImages :
            cache[image] = os.path.join(imageFolder,image)
            picCacheFile.write(image+"="+os.path.join(imageFolder,image)+'\n')
        for subFolder in subFolders :
            subFolderImages = [file for file in os.listdir(os.path.join(imageFolder,subFolder)) if not os.path.isdir(file)]
            for image in subFolderImages :
                cache[image] = os.path.join(imageFolder,subFolder,image)
                picCacheFile.write(image+"="+os.path.join(imageFolder,subFolder,image)+'\n')
    picCacheFile.close()
    return cache

def loadPicCache(picCache) :
    print("Loading cache %s" %picCache)
    picCacheFile = open(picCache,'r')
    cache = dict()
    for line in picCacheFile.readlines() :
        tokens = line.split("=")
        cache[tokens[0]] = tokens[1].rstrip('\n\r ')
    picCacheFile.close()
    return cache

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
        
    frontPicCacheFile = os.path.join(cacheDir,'.frontPicCache')
    frontPicCache = loadPicCache(frontPicCacheFile) if os.path.exists(frontPicCacheFile) else buildPicCache(os.path.join(exoDosDir,'Images','MS-DOS','Box - Front'),frontPicCacheFile)
    print("frontPicCache: %i entities" %len(frontPicCache.keys()))
    
    titlePicCacheFile = os.path.join(cacheDir,'.titlePicCache')
    titlePicCache = loadPicCache(titlePicCacheFile) if os.path.exists(titlePicCacheFile) else buildPicCache(os.path.join(exoDosDir,'Images','MS-DOS','Screenshot - Game Title'),titlePicCacheFile)
    print("titlePicCache: %i entities" %len(titlePicCache.keys()))
    
    gameplayPicCacheFile = os.path.join(cacheDir,'.gameplayPicCache')
    gameplayPicCache = loadPicCache(gameplayPicCacheFile) if os.path.exists(gameplayPicCacheFile) else buildPicCache(os.path.join(exoDosDir,'Images','MS-DOS','Screenshot - Gameplay'),gameplayPicCacheFile)
    print("gameplayPicCache: %i entities" %len(gameplayPicCache.keys()))
        
    cache = os.path.join(cacheDir,'cache.csv')
    fullnameToGameDir = dict()
    if not os.path.exists(cache) :
        print("Building cache... this will take a while")
        cacheFile = open(cache,'w')
        
        #TODO needs to build a full cache for this and metadatas
        gamesDosDir = os.path.join(exoDosDir,"eXoDOS","Games","!dos")
        games = [filename for filename in os.listdir(gamesDosDir)]
        fullnameToGameDir = gameDirMap(gamesDosDir,games);
        print(fullnameToGameDir)
        
        cacheFile.close()
    else :
        print("Reading cache")
        
    return fullnameToGameDir, frontPicCache, titlePicCache, gameplayPicCache