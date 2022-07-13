import errno
import shutil
import subprocess
import os.path
import platform
import collections
import shutil
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

def lines_that_contain(string, fp):
    return [line for line in fp if string in line]

def callProcess(subProcessArgs,logger):
    process = subprocess.Popen(subProcessArgs, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, universal_newlines=True)
    logger.logProcess(process)
    return process.wait()
    
def installAria2cWindows(exoCollectionDir, logger):
    eXoUtilDir = os.path.join(exoCollectionDir, 'eXo', 'util')
    subProcessArgs = [os.path.join(eXoUtilDir, "unzip.exe"), "-o", "-d",
                      eXoUtilDir, os.path.join(eXoUtilDir, "util.zip"), "aria.zip"]
    exitCode = callProcess(subProcessArgs, logger)

    #extract next file if succesful
    if not exitCode:
        subProcessArgs = [os.path.join(eXoUtilDir, "unzip.exe"), "-o",
                          "-d", eXoUtilDir, os.path.join(eXoUtilDir, "aria.zip"), "aria/*"]
        exitCode = callProcess(subProcessArgs, logger)

def installAria2cLinux(exoCollectionDir, logger):
    logger.log("  <Error> Installing aria2c for Linux not implemented yet",logger.ERROR)

def installAria2cMac(exoCollectionDir, logger):
    logger.log("  <Error> Installing aria2c for Mac not implemented yet",logger.ERROR)

def installAria2c(exoCollectionDir, logger):
        if platform.system() == 'Windows':
            installAria2cWindows(exoCollectionDir, logger)
        elif platform.system() == 'Linux':
            installAria2cLinux(exoCollectionDir, logger)
        elif platform.system() == 'Darwin':
            installAria2cMac(exoCollectionDir, logger)

def downloadTorrent(gameZip, gameZipPath, exoCollectionDir, logger):
    eXoDir = os.path.join(exoCollectionDir, 'eXo')
    outputDir = os.path.join(eXoDir, "eXoDOS", "DOWNLOAD")
    aria2cDir = os.path.join(exoCollectionDir, 'eXo', 'util', 'aria')
    eXoTorrentIndex = os.path.join(aria2cDir, 'index.txt')
    downloadFolderAlreadyExisted = False
    downloadedSuccess = False

    #try and install Aria2c(torrent downloader) based on platform.
    if not os.path.exists(eXoTorrentIndex):
        logger.log("  <WARNING> Missing index.txt from eXoDOS util.zip, attempting extraction.", logger.WARNING)
        installAria2c(exoCollectionDir, logger)

    #check again as we cannot assume the above succeeded, but if it did work we can then use the tool on a first run.
    if os.path.exists(eXoTorrentIndex):
        with open(eXoTorrentIndex, "r") as fp:
            for line in lines_that_contain(gameZip, fp):
                gameInfo = line.split(':')

        #make our downloads DIR at the torrent will create files we Don't want due to chunk size
        try:
            os.mkdir(outputDir)
        except OSError as e:
            #continue if DOWNLOAD folder already exists.
            if e.errno != errno.EEXIST:
                raise
            downloadFolderAlreadyExisted = True
            logger.log(
                f"  <WARNING> {outputDir} already exists, will not remove when done.", logger.WARNING)

        if platform.system() == 'Windows':
            command = os.path.join(aria2cDir, 'aria2c.exe')
        elif platform.system() == 'Linux':
            command = os.path.join(aria2cDir, 'aria2c')
        elif platform.system() == 'Darwin':
            command = os.path.join(aria2cDir, 'aria2c')

        subProcessArgs = [command, "--select-file=" + gameInfo[0], "--index-out="+gameInfo[0] + "=..\\" + gameZip, "--dir=" +
                          outputDir, "--file-allocation=none", "--allow-overwrite=true", "--seed-time=0", aria2cDir + "\\eXoDOS.torrent"]
        logger.log("  Downloading... " + gameZip)

        # run torrent downloader aria2c
        # retry download a few times as the torrent sometimes ends up at 0 bytes
        # didn't seem to help, but no reason to remove this code we will just retry 0 times
        retryCount = 0
        exitCode = -1
        while ((retryCount >= 0) and (not downloadedSuccess)):
            try:
                if os.path.getsize(gameZipPath):
                    # TODO: Check against size in index.txt
                    downloadedSuccess = True
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise
                
            exitCode = callProcess(subProcessArgs,logger)
            retryCount -= 1

        if exitCode == 0 and os.path.getsize(gameZipPath):
            logger.log("  Download Succeeded!")
        elif exitCode == 9:
            logger.log("  <ERROR> Not enough disk Space!", logger.ERROR)
        else:
            logger.log("  Download Had Issues!", logger.ERROR)

        #remove the outputDir if we created it... download would have been moved already
        if not downloadFolderAlreadyExisted:
            shutil.rmtree(outputDir)
        return True
    else:
        logger.log("  <ERROR> Could not Install Torrent Tools!", logger.ERROR)
    return downloadedSuccess

def downloadZip(gameZip, gameZipPath, logger):
    response = requests.get(theEyeUrl + '/' + urllib.parse.quote(gameZip), stream=True,
                            headers={'User-agent': 'Mozilla/5.0'})
    if response.status_code == 200:
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
                    logger.log('\r    [{}{}]'.format(
                        '█' * done, '.' * (50 - done)), logger.INFO, True)
        return True
    else:
        logger.log(
            '  <ERROR> error %s while downloading from web %s: %s' % (
                response.status_code, gameZipPath, response.reason),
            logger.ERROR)
        return False
    

# Loads UI Strings
def loadUIStrings(scriptDir, guiStringsFile):
    guiStrings = dict()
    file = open(os.path.join(scriptDir, 'gui', guiStringsFile), 'r', encoding="utf-8")
    order = 0
    for line in file.readlines()[1:]:
        confLine = line.split(";")
        if len(confLine) == 3:
            guiStrings[confLine[0]] = GUIString(confLine[0], confLine[1], confLine[2].rstrip('\n\r ').replace("#n","\n"), order)
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
    # Some special chars name in metadata have a clean name for the picture
    specialCharsGame = {'Pył': 'Pyl'}
    gameName = name if name not in specialCharsGame.keys() else specialCharsGame[name]
    frontPic = findPic(gameName, cache, '.jpg')
    frontPic = frontPic if frontPic is not None else findPic(gameName, cache, '.png')
    frontPic = frontPic if frontPic is not None else findPic(gameName, cache, '.gif')
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

def checkMultipleofSameGame(useGenreSubFolders, metadata, genre, game, gameDir, outputDir, logger):
    wantedPath = os.path.join(outputDir, genre, gameDir) if useGenreSubFolders else os.path.join(outputDir,gameDir)
    paths = {
    'shortPath':        os.path.join(outputDir,game + ".pc"),
    'longPath':         os.path.join(outputDir,getCleanGameID(metadata,".pc")),
    'shortPathGenre':   os.path.join(outputDir,genre,game + ".pc"),
    'longPathGenre':    os.path.join(outputDir,genre,getCleanGameID(metadata,".pc"))
    }

    totalExistingPaths = 0
    for name,path in paths.items():
        if os.path.exists(path):
            totalExistingPaths += 1
            logger.log("  Existing Path: " + path)

    if totalExistingPaths > 1:
        logger.log("  \tDue to not Clearing output folder you have...\n\t\t\t\t MULTIPLE COPIES.\n\t\tIf changing conversion type this may lead to bigger issues.")

def moveFolderifExist(useGenreSubFolders, metadata, genre, game, gameDir, outputDir, logger):
    wantedPath = os.path.join(outputDir, genre, gameDir) if useGenreSubFolders else os.path.join(outputDir,gameDir)
    paths = {
    'shortPath':        os.path.join(outputDir,game + ".pc"),
    'longPath':         os.path.join(outputDir,getCleanGameID(metadata,".pc")),
    'shortPathGenre':   os.path.join(outputDir,genre,game + ".pc"),
    'longPathGenre':    os.path.join(outputDir,genre,getCleanGameID(metadata,".pc"))
    }

    totalExistingPaths = 0
    existingPath = []
    for name,path in paths.items():
        if os.path.exists(path):
            existingPath.append(path)
            totalExistingPaths += 1
            logger.log("  Existing Path: " + path)

    if totalExistingPaths > 1:
        logger.log("    There can only be one, aborting auto rename.")
        logger.log("    If no Errors, gamelist.xml will be accurate.")
        for path in existingPath:
            if path == wantedPath:
                return True
        #more than 1 path already, don't know what they want so create requested folder(will result in duplicates/triplicates/quad)
        return False
    elif totalExistingPaths == 0:
        #game folder is non existent in any path, so create it.
        return False
    
    #only one existing path found rename it to wanted path
    if wantedPath != existingPath[0]:
        logger.log("  Moving Existing -> " + wantedPath)
        shutil.move(existingPath[0],wantedPath)
        #moved it so now its exists
        return True
    return True