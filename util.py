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

EXODOS = 'eXoDOS v5'
EXOWIN3X = 'eXoWin3x v2'
exoVersions = [EXODOS, EXOWIN3X]

exoCollectionsDirs = {EXODOS: {'gamesDir': 'eXoDOS', 'gamesConfDir': '!dos', 'metadataId': 'MS-DOS'},
                      EXOWIN3X: {'gamesDir': 'eXoWin3x', 'gamesConfDir': '!win3x', 'metadataId': 'Windows 3x'}}

mappers = ['Yes', 'No']

theEyeUrl = 'http://the-eye.eu/public/Games/eXo/eXoDOS_v5/eXo/eXoDOS/'

misterCleanNameToGameDir = dict()


def isWin3x(collectionVersion):
    return collectionVersion == EXOWIN3X


def getCollectionGamesDirToken(collection):
    return exoCollectionsDirs[collection]['gamesDir']


def getCollectionGamesDir(collectionDir, collection):
    return os.path.join(collectionDir, 'eXo', getCollectionGamesDirToken(collection))


def getCollectionGamesConfDir(collectionDir, collection):
    return os.path.join(getCollectionGamesDir(collectionDir, collection),
                        exoCollectionsDirs[collection]['gamesConfDir'])


def getCollectionUpdateDir(collectionDir, collection):
    return os.path.join(collectionDir, 'eXo', 'Update', exoCollectionsDirs[collection]['gamesConfDir'])


def getCollectionMetadataID(collection):
    return exoCollectionsDirs[collection]['metadataId']


def getKeySetString(string, setKey):
    return string.replace('{setKey}', setKey)


def getConfFilename(setKey):
    return getKeySetString(confFilename, setKey) + '.conf'


def getConfBakFilename(setKey):
    return getKeySetString(confFilename, setKey) + '.bak'


def getGuiStringsFilename(setKey):
    return getKeySetString(guiStringsFilename, setKey)


def downloadZip(gameZip, gameZipPath, logger):
    response = requests.get(theEyeUrl + '/' + urllib.parse.quote(gameZip), stream=True,
                            headers={'User-agent': 'Mozilla/5.0'})
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
def localOSPath(path):
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
    cleanGameName = metadata.name.replace(':', ' -').replace('?', '').replace('!', '').replace('/', '-').replace('\\',
                                                                                                                 '-').replace(
        '*', '_').replace('í', 'i')
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
def isCollectionPath(collectionPath, collection):
    return os.path.isdir(collectionPath) and os.path.exists(getCollectionGamesDir(collectionPath, collection)) \
           and os.path.exists(getCollectionGamesConfDir(collectionPath, collection)) \
           and os.path.exists(os.path.join(collectionPath, 'xml')) \
           and os.path.exists(os.path.join(collectionPath, 'Images'))


def validCollectionPath(collectionPath):
    if isCollectionPath(collectionPath, EXODOS):
        return EXODOS
    elif isCollectionPath(collectionPath, EXOWIN3X):
        return EXOWIN3X
    else:
        return None


# Parse the collection static cache file to generate list of games
def fullnameToGameDir(scriptDir, collectionVersion):
    gameDict = dict()
    collectFile = open(os.path.join(scriptDir, 'data', collectionVersion.replace(' ','')+'.csv'), 'r', encoding='utf-8')
    for line in collectFile.readlines():
        strings = line.split(';')
        gameDict[strings[0]] = strings[1].rstrip('\n\r')
    return gameDict


# Build games csv for a new/updated collection
def buildCollectionCSV(scriptDir, gamesConfDir, logger):
    collectFile = open(os.path.join(scriptDir, 'data', 'collec-new.csv'), 'w', encoding='utf-8')
    logger.log('Listing games in %s' % gamesConfDir, logger.WARNING)
    games = [file for file in os.listdir(gamesConfDir) if os.path.isdir(os.path.join(gamesConfDir, file))]

    for game in games:  # games = list of folder in !dos dir
        if os.path.isdir(os.path.join(gamesConfDir, game)):
            bats = [os.path.splitext(filename)[0] for filename in os.listdir(os.path.join(gamesConfDir, game)) if
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
        rootImages = [file for file in os.listdir(imageFolder) if not os.path.isdir(os.path.join(imageFolder, file))]
        subFolders = [file for file in os.listdir(imageFolder) if os.path.isdir(os.path.join(imageFolder, file))]
        for image in rootImages:
            cache[image] = os.path.join(imageFolder, image)
            picCacheFile.write(image + "=" + image + '\n')
        for subFolder in subFolders:
            subFolderImages = [file for file in os.listdir(os.path.join(imageFolder, subFolder)) if
                               not os.path.isdir(file)]
            for image in subFolderImages:
                cache[image] = os.path.join(imageFolder, subFolder, image)
                picCacheFile.write(image + "=" + os.path.join(subFolder, image) + '\n')
    picCacheFile.close()
    return cache


# Loads a specific pic cache
def loadPicCache(picCache, imageFolder, logger):
    logger.log("Loading cache %s" % picCache)
    picCacheFile = open(picCache, 'r')
    cache = dict()
    for line in picCacheFile.readlines():
        tokens = line.split("=")
        cache[tokens[0]] = os.path.join(imageFolder, localOSPath(tokens[1].rstrip('\n\r ')))
    picCacheFile.close()
    return cache


def buildCache(scriptDir, collectionDir, collection, logger):
    cacheDir = os.path.join(scriptDir, 'cache')
    if not os.path.exists(cacheDir):
        os.mkdir(cacheDir)

    frontPicCacheFile = os.path.join(cacheDir, '.%s-frontPicCache' % getCollectionGamesDirToken(collection))
    frontPicImgFolder = os.path.join(collectionDir, 'Images', getCollectionMetadataID(collection), 'Box - Front')
    frontPicCache = loadPicCache(frontPicCacheFile, frontPicImgFolder, logger) if os.path.exists(frontPicCacheFile) \
        else buildPicCache(frontPicImgFolder, frontPicCacheFile, logger)
    logger.log("frontPicCache: %i entities" % len(frontPicCache.keys()))

    titlePicCacheFile = os.path.join(cacheDir, '.%s-titlePicCache' % getCollectionGamesDirToken(collection))
    titlePicImgFolder = os.path.join(collectionDir, 'Images', getCollectionMetadataID(collection), 'Screenshot - Game Title')
    titlePicCache = loadPicCache(titlePicCacheFile, titlePicImgFolder, logger) if os.path.exists(titlePicCacheFile) \
        else buildPicCache(titlePicImgFolder, titlePicCacheFile, logger)
    logger.log("titlePicCache: %i entities" % len(titlePicCache.keys()))

    gameplayPicCacheFile = os.path.join(cacheDir, '.%s-gameplayPicCache' % getCollectionGamesDirToken(collection))
    gameplayPicImgFolder = os.path.join(collectionDir, 'Images', getCollectionMetadataID(collection),
                                        'Screenshot - Gameplay')
    gameplayPicCache = loadPicCache(gameplayPicCacheFile, gameplayPicImgFolder, logger) if os.path.exists(gameplayPicCacheFile) \
        else buildPicCache(gameplayPicImgFolder, gameplayPicCacheFile, logger)
    logger.log("gameplayPicCache: %i entities" % len(gameplayPicCache.keys()))

    return frontPicCache, titlePicCache, gameplayPicCache
