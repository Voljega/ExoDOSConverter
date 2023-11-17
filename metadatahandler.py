import collections
import os
import platform
import util
import shutil
import sys
import xml.etree.ElementTree as etree
from xml.dom import minidom

from genre_mapping import mapGenres, Genre

DosGame = collections.namedtuple('DosGame',
                                 'dosname metadataname name genres publisher developer year frontPic manual desc')


# Metadata exporting
# noinspection PyBroadException
class MetadataHandler:

    def __init__(self, scriptDir, exoCollectionDir, collectionVersion, cache, logger):
        self.exoCollectionDir = exoCollectionDir
        self.collectionVersion = collectionVersion
        self.scriptDir = scriptDir
        self.cache = cache
        self.logger = logger
        self.metadatas = dict()
        self.fixGenres = self.loadFixGenre(scriptDir, collectionVersion)


    # Reads a given node
    @staticmethod
    def __getNode__(i, e):
        ll = i.find(e)
        return ll.text if ll is not None else None

    # Inits in-memory gamelist xml either by opening the file or creating it
    @staticmethod
    def initXml(outputDir):
        if os.path.exists(os.path.join(outputDir, "gamelist.xml")):
            parser = etree.XMLParser(encoding="utf-8")
            return etree.parse(os.path.join(outputDir, "gamelist.xml"), parser=parser)
        else:
            tree = etree.ElementTree()
            tree._setroot(etree.Element('gameList'))
            return tree

    # Write full in-memory gamelist xml to outputDir
    @staticmethod
    def writeXml(outputDir, gamelist):
        xmlstr = minidom.parseString(etree.tostring(gamelist.getroot())).toprettyxml(indent="   ", newl="\r")
        xmlstr = '\n'.join([s for s in xmlstr.splitlines() if s.strip()])
        with open(os.path.join(outputDir, "gamelist.xml"), "wb") as f:
            f.write(xmlstr.encode('utf-8'))

    # Parse exo collection metadata file
    def parseXmlMetadata(self):
        xmlPath = os.path.join(util.getCollectionMetadataDir(self.exoCollectionDir), util.getCollectionMetadataID(self.collectionVersion) + '.xml')
        # xmlPath = os.path.join(self.exoCollectionDir, 'xml', 'all', util.getCollectionMetadataID(self.collectionVersion) + '.xml')
        # if not os.path.exists(xmlPath):  # v6 # C64 Dreams
        #     xmlPath = os.path.join(self.exoCollectionDir, 'Data', 'Platforms', util.getCollectionMetadataID(self.collectionVersion) + '.xml')

        metadatas = dict()
        if os.path.exists(xmlPath):
            parser = etree.XMLParser(encoding="utf-8")
            games = etree.parse(xmlPath, parser=parser).findall(".//Game")
            for g in games:
                name = self.__getNode__(g, 'Title')
                if name not in list(map(lambda x: util.exoCollectionsDirs[x]['gamesDir'], list(util.exoCollectionsDirs.keys()))):
                    try:
                        path = self.__getNode__(g, 'ApplicationPath').split("\\")
                        dosname = path[-2]
                        metadataname = os.path.splitext(path[-1])[0]
                        #                    print("%s %s %s" %(dosname, name, metadataname))
                        desc = self.__getNode__(g, 'Notes') if self.__getNode__(g, 'Notes') is not None else ''
                        releasedate = self.__getNode__(g, 'ReleaseDate')[:4] if self.__getNode__(g, 'ReleaseDate') is not None else None
                        developer = self.__getNode__(g, 'Developer')
                        publisher = self.__getNode__(g, 'Publisher')
                        genres = self.__getNode__(g, 'Genre').split(';') if self.__getNode__(g, 'Genre') is not None else []
                        manual = self.__getNode__(g, 'ManualPath')
                        manualpath = util.localOSPath(os.path.join(self.exoCollectionDir, manual)) if manual is not None else None
                        cachePic = util.findPics(name, self.cache)
                        frontPic = cachePic if cachePic is not None else util.findPics(dosname, self.cache)
                        metadata = DosGame(dosname, metadataname, name, genres, publisher, developer, releasedate, frontPic,
                                           manualpath, desc)
                        metadatas[metadata.dosname.lower()] = metadata

                    except:
                        self.logger.log('  Error %s while getting metadata for %s\n' % (sys.exc_info()[0], self.__getNode__(g, 'Title')), self.logger.ERROR)
        self.logger.log('Loaded %i metadatas' % len(metadatas.keys()))
        self.metadatas = metadatas
        return metadatas

    # Retrieve exo collection metadata for a given game
    def __handleMetadata__(self, game):
        if game == 'H.E.R.O':  # dirty fix but no way to do it differently
            game = 'H.E.R.O.'
        if game.lower() in self.metadatas:
            gameMetadata = self.metadatas.get(game.lower())
            self.logger.log("  Metadata: %s (%s), genres: %s" % (gameMetadata.name, gameMetadata.year, " | ".join(gameMetadata.genres)))
            return gameMetadata
        else:
            self.logger.log('  <ERROR> No metadata found for %s' % game, self.logger.ERROR)
            return None

    # Process and export metadata to in-memory gamelist xml for a given game    
    def processGame(self, game, gamelist, genre, outputDir, useLongFolderNames, useGenreSubFolders, conversionType, nameOverride, manualOverride):
        gameMetadata = self.__handleMetadata__(game)
        self.logger.log("  computed genre %s" % genre)
        self.logger.log("  copy pics and manual")
        if gameMetadata.frontPic is not None and os.path.exists(gameMetadata.frontPic):
            shutil.copy2(gameMetadata.frontPic, os.path.join(outputDir, 'downloaded_images'))
        else:
            self.logger.log('  <WARNING> No pic found for %s, please file a report on Github with the game name' % game, self.logger.WARNING)
        if gameMetadata.manual is not None and os.path.exists(gameMetadata.manual):
            shutil.copy2(gameMetadata.manual, os.path.join(outputDir, 'manuals'))
        self.__writeGamelistEntry__(gamelist, gameMetadata, game, genre, useLongFolderNames, useGenreSubFolders, conversionType, nameOverride, manualOverride)
        return gameMetadata

    # Replaces “ ” ’ …
    @staticmethod
    def __cleanXmlString__(s):
        return s.replace('&', '&amp;')

    # Write metadata for a hidden given game to in-memory gamelist.xml
    def writeHiddenGamelistEntry(self, gamelist, game, genre, useGenreSubFolders):
        root = gamelist.getroot()
        path = "./" + genre + "/" + game if useGenreSubFolders else "./" + game
        existsInGamelist = [child for child in root.iter('game') if
                            self.__getNode__(child, "name") == game]
        if len(existsInGamelist) == 0:
            gameElt = etree.SubElement(root, 'game')
            etree.SubElement(gameElt, 'path').text = path
            etree.SubElement(gameElt, 'hidden').text = 'true'

    # Write metada for a given game to in-memory gamelist xml
    def __writeGamelistEntry__(self, gamelist, metadata, game, genre, useLongFolderNames, useGenreSubFolders, conversionType, nameOverride, manualOverride):
        root = gamelist.getroot()

        if platform.system() == 'Windows':
            frontPic = './downloaded_images/' + metadata.frontPic.split('\\')[-1] if metadata.frontPic is not None else ''
            manual = './manuals/' + metadata.manual.split('\\')[-1] if metadata.manual is not None else ''
        else:
            frontPic = './downloaded_images/' + metadata.frontPic.split('/')[-1] if metadata.frontPic is not None else ''
            manual = './manuals/' + metadata.manual.split('/')[-1] if metadata.manual is not None else ''

        if manualOverride is not None:
            manual = './manuals/' + manualOverride

        year = metadata.year + "0101T000000" if metadata.year is not None else ''

        if conversionType == util.retropie:
            gameFilePath = nameOverride if nameOverride is not None else util.getCleanGameID(metadata, '.conf')
            path = "./" + genre + "/" + gameFilePath if useGenreSubFolders else "./" + gameFilePath
        elif (conversionType == util.batocera or conversionType == util.retrobat) and useLongFolderNames:
            gameFilePath = nameOverride if nameOverride is not None else util.getCleanGameID(metadata, '.pc')
            path = "./" + genre + "/" + gameFilePath if useGenreSubFolders else "./" + gameFilePath
        else:
            gameFilePath = nameOverride if nameOverride is not None else self.__cleanXmlString__(game) + ".pc"
            path = "./" + genre + "/" + gameFilePath if useGenreSubFolders else "./" + gameFilePath

        existsInGamelist = [child for child in root.iter('game') if
                            self.__getNode__(child, "name") == metadata.name and self.__getNode__(child, "releasedate") == year]
        if len(existsInGamelist) == 0:
            gameElt = etree.SubElement(root, 'game')
            etree.SubElement(gameElt, 'path').text = path
            etree.SubElement(gameElt, 'name').text = metadata.name
            etree.SubElement(gameElt, 'desc').text = metadata.desc if metadata.desc is not None else ''
            etree.SubElement(gameElt, 'releasedate').text = year
            etree.SubElement(gameElt, 'developer').text = metadata.developer if metadata.developer is not None else ''
            etree.SubElement(gameElt, 'publisher').text = metadata.publisher if metadata.publisher is not None else ''
            etree.SubElement(gameElt, 'genre').text = genre
            etree.SubElement(gameElt, 'manual').text = manual
            etree.SubElement(gameElt, 'image').text = frontPic
        else:
            # TODO not clear
            # game exists lets make sure path is correct to whats been done with subFolders/longNames
            for child in existsInGamelist:
                child.find("path").text = path

    @staticmethod
    def loadFixGenre(scriptDir, collectionVersion):
        fixGenresPath = os.path.join(scriptDir, 'data', 'fixGenres-' + collectionVersion.replace(' ', '') + '.csv')
        if os.path.exists(fixGenresPath):
            fixGenres = open(fixGenresPath, 'r', encoding="utf-8")
            fg = dict()
            for line in fixGenres.readlines():
                [genre, game] = line.split(';')
                fg[game.rstrip('\n\r ').lstrip()] = genre.rstrip('\n\r ').lstrip()
            fixGenres.close()
            return fg
        return None

    # Convert multi genres exo collection format to a single one
    @staticmethod
    def buildGenre(dosGame, fixGenres):
        if dosGame is None or dosGame.genres is None:
            return Genre.UNKNOWN.value
        if fixGenres is not None and dosGame.dosname in fixGenres:
            return fixGenres[dosGame.dosname]
        else:
            return mapGenres(dosGame.genres)
