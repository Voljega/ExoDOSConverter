import os.path
import platform
import collections
from PIL import Image
import requests
import urllib.request
import urllib.parse

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
retrobat = 'Retrobat'
emuelec = 'Emuelec'
conversionTypes = [batocera, recalbox, retropie, retrobat, emuelec, simplemenu, esoteric, mister]

exodosVersions = ['eXoDOS v5']

mappers = ['No', 'RG350']

theEyeUrl = 'http://the-eye.eu/public/Games/eXo/eXoDOS_v5/eXo/eXoDOS/'


def getKeySetString(string, setKey):
    return string.replace('{setKey}', setKey)


def getConfFilename(setKey):
    return getKeySetString(confFilename, setKey) + '.conf'


def getConfBakFilename(setKey):
    return getKeySetString(confFilename, setKey) + '.bak'


def getGuiStringsFilename(setKey):
    return getKeySetString(guiStringsFilename, setKey)


def downloadZip(gameZip, gameZipPath, logger):
    response = requests.get(theEyeUrl + '/' + urllib.parse.quote(gameZip), stream=True, headers={'User-agent': 'Mozilla/5.0'})
    totalSize = int(response.headers.get('content-length'))
    rightSize = totalSize
    typeSize = ['b', 'kb', 'mb', 'gb']
    typeIndex = 0
    printableSize = ''
    while rightSize > 0 and typeIndex < len(typeSize):
        printableSize = str(rightSize) + ' ' + typeSize[typeIndex]
        rightSize = int(rightSize / 1024)
        typeIndex = typeIndex + 1
    logger.log('  Downloading %s of size %s' % (gameZip, printableSize))
    if response.status_code == 200:
        with open(gameZipPath, 'wb') as f:
            if totalSize is None:
                f.write(response.content)
            else:
                downloaded = 0
                totalSize = int(totalSize)
                for data in response.iter_content(chunk_size=max(int(totalSize / 1000), 1024 * 1024)):
                    downloaded += len(data)
                    f.write(data)
                    done = int(50 * downloaded / totalSize)
                    logger.log('\r    [{}{}]'.format('█' * done, '.' * (50 - done)), logger.INFO, True)
    else:
        logger.log(
            '  <ERROR> error %s while downloading %s: %s' % (response.status_code, gameZipPath, response.reason),
            logger.ERROR)


# Loads UI Strings
def loadUIStrings(scriptDir, guiStringsFile):
    guiStrings = dict()
    file = open(os.path.join(scriptDir, 'gui', guiStringsFile), 'r', encoding="utf-8")
    order = 0
    for line in file.readlines()[1:]:
        confLine = line.split(";")
        if len(confLine) == 3:
            guiStrings[confLine[0]] = GUIString(confLine[0], confLine[1], confLine[2].rstrip('\n\r '), order)
            order = order + 1
    file.close()
    return guiStrings


# Handle os escaping of path in local output dir
def localOutputPath(path):
    if platform.system() == 'Windows':
        return path
    else:
        return path.replace('\\', '/')


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
    cleanGameName = metadata.name.replace(':', ' -').replace('?', '').replace('!', '').replace('/', '-').replace('\\','-').replace('*','_').replace('í','i')
    return cleanGameName + ' (' + str(metadata.year) + ')' + ext


# Returns distrib roms directory prefix for mount command
def getRomsFolderPrefix(conversionType, conversionConf):
    if conversionConf['useExpertMode']:
        return conversionConf['mountPrefix']
    elif conversionType == batocera:
        return "/userdata/roms/dos"
    elif conversionType == recalbox:
        return "/recalbox/share/roms/dos"
    elif conversionType == retropie:
        return "/home/pi/RetroPie/roms/pc"
    elif conversionType == retrobat:
        return r"..\\..\\roms\\dos"
    elif conversionType == emuelec:
        return "/storage/roms/pcdata"
    else:
        return "."


# Checks validity of the collection path and its content
def validCollectionPath(collectionPath):
    return os.path.isdir(collectionPath) and os.path.exists(os.path.join(collectionPath, 'eXo')) and os.path.exists(
        os.path.join(collectionPath, 'eXo', 'eXoDOS')) and os.path.exists(
        os.path.join(collectionPath, 'xml')) and os.path.exists(os.path.join(collectionPath, 'Images'))


# Parse the collection static cache file to generate list of games
def fullnameToGameDir(scriptDir):
    gameDict = dict()
    collectFile = open(os.path.join(scriptDir,'data','eXoDOSv5.csv'),'r', encoding='utf-8')
    for line in collectFile.readlines():
        strings = line.split(';')
        gameDict[strings[0]] = strings[1].rstrip('\n\r')
    return gameDict


# Build games csv for a new/updated collection
def buildCollectionCSV(scriptDir, gamesDosDir, logger):
    collectFile = open(os.path.join(scriptDir, 'data', 'collec-new.csv'), 'w', encoding='utf-8')
    logger.log('Listing games in %s' % gamesDosDir, logger.WARNING)
    games = [file for file in os.listdir(gamesDosDir) if os.path.isdir(os.path.join(gamesDosDir, file))]

    for game in games:  # games = list of folder in !dos dir
        if os.path.isdir(os.path.join(gamesDosDir, game)):
            bats = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join(gamesDosDir, game)) if
                    os.path.splitext(filename)[-1].lower() == '.bat' and not os.path.splitext(filename)[
                                                                                 0].lower() == 'install']
            # logger.log('  ' + bats[0] + '->' + game, logger.WARNING)
            collectFile.write(bats[0] + ';' + game + '\n')


# Finds pic for a game in the three pics caches
def findPics(name, cache):
    frontPic = findPic(name, cache, '.jpg')
    frontPic = frontPic if frontPic is not None else findPic(name, cache, '.png')
    frontPic = frontPic if frontPic is not None else findPic(name, cache, '.gif')
    return frontPic


# Finds pic with ext for a game in the three pics caches
def findPic(gameName, cache, ext):
    frontPicCache, titlePicCache, gameplayPicCache = cache
    imgName = (gameName + '-01' + ext).replace(':', '_').replace("'", '_')
    imgNameAlt = (gameName + '-02' + ext).replace(':', '_').replace("'", '_')
    imgPath = None
    if imgName in frontPicCache:
        imgPath = frontPicCache.get(imgName)
    elif imgNameAlt in frontPicCache:
        imgPath = frontPicCache.get(imgNameAlt)
    elif imgName in titlePicCache:
        imgPath = titlePicCache.get(imgName)
    elif imgNameAlt in titlePicCache:
        imgPath = titlePicCache.get(imgNameAlt)
    elif imgName in gameplayPicCache:
        imgPath = gameplayPicCache.get(imgName)
    elif imgNameAlt in gameplayPicCache:
        imgPath = gameplayPicCache.get(imgNameAlt)
    return imgPath


# Constructs a specific pic cache
def buildPicCache(imageFolder, picCache, logger):
    logger.log("Building cache %s" % picCache)
    picCacheFile = open(picCache, 'w')
    cache = dict()
    if os.path.exists(imageFolder):
        rootImages = [file for file in os.listdir(imageFolder) if not os.path.isdir(os.path.join(imageFolder,file))]
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
