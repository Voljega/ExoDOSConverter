import os.path, collections

GUIString = collections.namedtuple('GUIString', 'id label help order')

confDir = r"conf"
confFilename = r"conf-{setKey}"
guiStringsFilename = r'gui-en-{setKey}.csv'

def getKeySetString(string,setKey) :
        return string.replace('{setKey}',setKey)

def getConfFilename(setKey) :
    return getKeySetString(confFilename,setKey)+'.conf'

def getConfBakFilename(setKey) :
    return getKeySetString(confFilename,setKey)+'.bak'

def getGuiStringsFilename(setKey) :
    return getKeySetString(guiStringsFilename,setKey)

# UI Strings
def loadUIStrings(scriptDir,guiStringsFilename) :
    guiStrings = dict()
    file = open(os.path.join(scriptDir,'GUI',guiStringsFilename),'r',encoding="utf-8")
    order = 0
    for line in file.readlines()[1:] :
        confLine = line.split(";")
        if len(confLine) == 3 :
            guiStrings[confLine[0]] = GUIString(confLine[0],confLine[1],confLine[2].rstrip('\n\r '), order)
            order = order + 1
    file.close()
    return guiStrings

def findPic(gameName, cache, ext) :
    frontPicCache, titlePicCache, gameplayPicCache = cache
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

def fullnameToGameDir(exoDosDir) :
    gamesDosDir = os.path.join(exoDosDir,"eXoDOS","Games","!dos")
    games = [filename for filename in os.listdir(gamesDosDir)]
    return gameDirMap(gamesDosDir,games);

def buildCache(scriptDir, exoDosDir, logger):
    cacheDir = os.path.join(scriptDir,'cache')
    if not os.path.exists(cacheDir) :
        os.mkdir(cacheDir)
        
    frontPicCacheFile = os.path.join(cacheDir,'.frontPicCache')
    frontPicCache = loadPicCache(frontPicCacheFile) if os.path.exists(frontPicCacheFile) else buildPicCache(os.path.join(exoDosDir,'Images','MS-DOS','Box - Front'),frontPicCacheFile)
    logger.log("frontPicCache: %i entities" %len(frontPicCache.keys()))
    
    titlePicCacheFile = os.path.join(cacheDir,'.titlePicCache')
    titlePicCache = loadPicCache(titlePicCacheFile) if os.path.exists(titlePicCacheFile) else buildPicCache(os.path.join(exoDosDir,'Images','MS-DOS','Screenshot - Game Title'),titlePicCacheFile)
    logger.log("titlePicCache: %i entities" %len(titlePicCache.keys()))
    
    gameplayPicCacheFile = os.path.join(cacheDir,'.gameplayPicCache')
    gameplayPicCache = loadPicCache(gameplayPicCacheFile) if os.path.exists(gameplayPicCacheFile) else buildPicCache(os.path.join(exoDosDir,'Images','MS-DOS','Screenshot - Gameplay'),gameplayPicCacheFile)
    logger.log("gameplayPicCache: %i entities" %len(gameplayPicCache.keys()))
            
    return frontPicCache, titlePicCache, gameplayPicCache