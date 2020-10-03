import os.path
import collections
from PIL import Image

GUIString = collections.namedtuple('GUIString', 'id label help order')

confDir = r"conf"
confFilename = r"conf-{setKey}"
guiStringsFilename = r'gui-en-{setKey}.csv'

batocera = 'Batocera'
recalbox = 'Recalbox'
retropie = 'Retropie'
mister = 'MiSTer'
simplemenu = 'OpenDingux/SimpleMenu'
esoteric = 'OpenDingux/Esoteric'
conversionTypes = [batocera, recalbox, retropie, simplemenu, esoteric, mister]

exodosVersions = ['v4', 'v5']

mappers = ['No', 'RG350']


def getKeySetString(string, setKey):
    return string.replace('{setKey}', setKey)


def getConfFilename(setKey):
    return getKeySetString(confFilename, setKey) + '.conf'


def getConfBakFilename(setKey):
    return getKeySetString(confFilename, setKey) + '.bak'


def getGuiStringsFilename(setKey):
    return getKeySetString(guiStringsFilename, setKey)


# Loads UI Strings
def loadUIStrings(scriptDir, guiStringsFilename):
    guiStrings = dict()
    file = open(os.path.join(scriptDir, 'gui', guiStringsFilename), 'r', encoding="utf-8")
    order = 0
    for line in file.readlines()[1:]:
        confLine = line.split(";")
        if len(confLine) == 3:
            guiStrings[confLine[0]] = GUIString(confLine[0], confLine[1], confLine[2].rstrip('\n\r '), order)
            order = order + 1
    file.close()
    return guiStrings


# Resize image for opendingux
def resize(imgPath):
    im = Image.open(imgPath)
    height = 200
    wpercent = (height / float(im.size[1]))
    vsize = int((float(im.size[0]) * float(wpercent)))
    im = im.resize((vsize, height), Image.ANTIALIAS)
    im.save(imgPath, "PNG")


# Return full clean game name
def getCleanGameID(metadata, ext):
    cleanGameName = metadata.name.replace(':', '-').replace('?', '').replace('!', '').replace('/', '-').replace('\\',
                                                                                                                '-')
    return cleanGameName + ' (' + str(metadata.year) + ')' + ext


# Returns distrib roms directory prefix
def getRomsFolderPrefix(conversionType):
    if conversionType == batocera:
        return "/userdata/roms/dos"
    elif conversionType == recalbox:
        return "/recalbox/share/roms/dos"
    elif conversionType == retropie:
        return "/home/pi/RetroPie/roms/pc"
    else:
        return "."


# Checks validity of the collection path and its content
def validCollectionPath(collectionPath):
    return os.path.exists(os.path.join(collectionPath, 'eXoDOS')) and os.path.exists(
        os.path.join(collectionPath, 'eXoDOS', 'Games')) and os.path.exists(
        os.path.join(collectionPath, 'xml')) and os.path.exists(os.path.join(collectionPath, 'Images'))


# Parse the collection static cache file to generate list of games
def fullnameToGameDir(scriptDir):
    gameDict = dict()
    collectFile = open(os.path.join(scriptDir,'data','collec-v4.csv'),'r')
    for line in collectFile.readlines():
        strings = line.split(';')
        gameDict[strings[0]] = strings[1].rstrip('\n\r')
    return gameDict


# Finds pic for a game in the three pics caches
def findPic(gameName, cache, ext):
    frontPicCache, titlePicCache, gameplayPicCache = cache
    imgName = (gameName + '-01' + ext).replace(':', '_').replace("'", '_')
    imgPath = None
    if imgName in frontPicCache:
        imgPath = frontPicCache.get(imgName)
    elif imgName in titlePicCache:
        imgPath = titlePicCache.get(imgName)
    elif imgName in gameplayPicCache:
        imgPath = gameplayPicCache.get(imgName)
    return imgPath


# Constructs a specific pic cache
def buildPicCache(imageFolder, picCache, logger):
    logger.log("Building cache %s" % picCache)
    picCacheFile = open(picCache, 'w')
    cache = dict()
    if os.path.exists(imageFolder):
        rootImages = [file for file in os.listdir(imageFolder) if not os.path.isdir(file)]
        subFolders = [file for file in os.listdir(imageFolder) if os.path.isdir(os.path.join(imageFolder, file))]
        for image in rootImages:
            cache[image] = os.path.join(imageFolder, image)
            picCacheFile.write(image + "=" + os.path.join(imageFolder, image) + '\n')
        for subFolder in subFolders:
            subFolderImages = [file for file in os.listdir(os.path.join(imageFolder, subFolder)) if
                               not os.path.isdir(file)]
            for image in subFolderImages:
                cache[image] = os.path.join(imageFolder, subFolder, image)
                picCacheFile.write(image + "=" + os.path.join(imageFolder, subFolder, image) + '\n')
    picCacheFile.close()
    return cache


# Loads a specific pic cache
def loadPicCache(picCache, logger):
    logger.log("Loading cache %s" % picCache)
    picCacheFile = open(picCache, 'r')
    cache = dict()
    for line in picCacheFile.readlines():
        tokens = line.split("=")
        cache[tokens[0]] = tokens[1].rstrip('\n\r ')
    picCacheFile.close()
    return cache


# Clean all three pic caches
def cleanCache(scriptDir):
    cacheDir = os.path.join(scriptDir, 'cache')
    frontPicCacheFile = os.path.join(cacheDir, '.frontPicCache')
    if os.path.exists(frontPicCacheFile):
        os.remove(frontPicCacheFile)
    titlePicCacheFile = os.path.join(cacheDir, '.titlePicCache')
    if os.path.exists(titlePicCacheFile):
        os.remove(titlePicCacheFile)
    gameplayPicCacheFile = os.path.join(cacheDir, '.gameplayPicCache')
    if os.path.exists(gameplayPicCacheFile):
        os.remove(gameplayPicCacheFile)

    # Builds or loads all three pic caches


def buildCache(scriptDir, collectionDir, logger):
    cacheDir = os.path.join(scriptDir, 'cache')
    if not os.path.exists(cacheDir):
        os.mkdir(cacheDir)

    frontPicCacheFile = os.path.join(cacheDir, '.frontPicCache')
    frontPicCache = loadPicCache(frontPicCacheFile, logger) if os.path.exists(frontPicCacheFile) else buildPicCache(
        os.path.join(collectionDir, 'Images', 'MS-DOS', 'Box - Front'), frontPicCacheFile, logger)
    logger.log("frontPicCache: %i entities" % len(frontPicCache.keys()))

    titlePicCacheFile = os.path.join(cacheDir, '.titlePicCache')
    titlePicCache = loadPicCache(titlePicCacheFile, logger) if os.path.exists(titlePicCacheFile) else buildPicCache(
        os.path.join(collectionDir, 'Images', 'MS-DOS', 'Screenshot - Game Title'), titlePicCacheFile, logger)
    logger.log("titlePicCache: %i entities" % len(titlePicCache.keys()))

    gameplayPicCacheFile = os.path.join(cacheDir, '.gameplayPicCache')
    gameplayPicCache = loadPicCache(gameplayPicCacheFile, logger) if os.path.exists(
        gameplayPicCacheFile) else buildPicCache(
        os.path.join(collectionDir, 'Images', 'MS-DOS', 'Screenshot - Gameplay'), gameplayPicCacheFile, logger)
    logger.log("gameplayPicCache: %i entities" % len(gameplayPicCache.keys()))

    return frontPicCache, titlePicCache, gameplayPicCache
