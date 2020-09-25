import os,shutil,collections,sys
import xml.etree.ElementTree as etree
from xml.dom import minidom
import util

DosGame = collections.namedtuple('DosGame', 'dosname metadataname name genres publisher developer year frontPic manual desc')

# Metadata exporting
class MetadataHandler():
    
    def __init__(self,exoDosDir, cache,logger) :
        self.exoDosDir = exoDosDir
        self.cache = cache
        self.logger = logger
        self.metadatas = dict()
    
    # Reads a given node    
    def get(self,i,e):
        ll=i.find(e)        
        return ll.text if ll != None else None
    
    # Inits in-memory gamelist xml either by opening the file or creating it
    def initXml(self, outputDir) :
        if os.path.exists(os.path.join(outputDir,"gamelist.xml")) :
            parser = etree.XMLParser(encoding="utf-8")
            return etree.parse(os.path.join(outputDir,"gamelist.xml"), parser=parser)
        else :
            tree = etree.ElementTree()
            tree._setroot(etree.Element('gameList'))
            return tree
    
    # Write full in-memory gamelist xml to outputDir    
    def writeXml(self, outputDir, gamelist) :
        xmlstr = minidom.parseString(etree.tostring(gamelist.getroot())).toprettyxml(indent="   ", newl="\r")
        xmlstr = '\n'.join([s for s in xmlstr.splitlines() if s.strip()])
        with open(os.path.join(outputDir,"gamelist.xml"), "wb") as f:
            f.write(xmlstr.encode('utf-8'))
    
    # Parse exoDos metadata file    
    def parseXmlMetadata(self) :
        xmlPath = os.path.join(self.exoDosDir,'Data','Platforms','MS-DOS.xml')
        metadatas = dict();
        if os.path.exists(xmlPath) :
            parser = etree.XMLParser(encoding="utf-8")
            games = etree.parse(xmlPath, parser=parser).findall(".//Game")
            for g in games:
                try :
                    path = self.get(g,'ApplicationPath').split("\\")
                    dosname = path[-2]
                    metadataname = os.path.splitext(path[-1])[0]
                    name = self.get(g,'Title')
#                    print("%s %s %s" %(dosname, name, metadataname))
                    desc = self.get(g,'Notes')
                    releasedate = self.get(g,'ReleaseDate')[:4] if self.get(g,'ReleaseDate') is not None else None
                    developer = self.get(g,'Developer')
                    publisher = self.get(g,'Publisher')
                    genres = self.get(g,'Genre').split(';') if self.get(g,'Genre') is not None else []                    
                    manual = self.get(g,'ManualPath')
                    manualpath = os.path.join(self.exoDosDir,manual) if manual is not None else None                    
                    frontPic = util.findPic(name,self.cache,'.jpg')
                    frontPic = frontPic if frontPic is not None else util.findPic(name,self.cache,'.png')
#                    print(frontPic if frontPic is not None else 'IMG NOT FOUND')
                    metadata = DosGame(dosname, metadataname, name,genres,publisher,developer,releasedate,frontPic,manualpath,desc)
                    metadatas[metadata.dosname] = metadata
                        
                except :
                    self.logger.log(sys.exc_info())
        self.logger.log('Loaded %i metadatas' %len(metadatas.keys()))
        self.metadatas = metadatas
        return metadatas
    
    # Retrieve exoDos metadata for a given game
    def handleMetadata(self,game) :
        dosGame = self.metadatas.get(game)
        self.logger.log("  Metadata: %s (%s), genres: %s" %(dosGame.name,dosGame.year," | ".join(dosGame.genres)))     
        return dosGame
    
    # Process and export metadata to in-memory gamelist xml for a given game    
    def processGame(self, game, gamelist, genre, outputDir, useGenreSubFolders, conversionType) :
        dosGame = self.handleMetadata(game)
        self.logger.log("  computed genre %s" %genre)
        self.logger.log("  copy pics and manual")
        if dosGame.frontPic is not None and os.path.exists(dosGame.frontPic) :
            shutil.copy2(dosGame.frontPic,os.path.join(outputDir,'downloaded_images'))
        if dosGame.manual is not None and os.path.exists(dosGame.manual) :
            shutil.copy2(dosGame.manual, os.path.join(outputDir, 'manuals'))
        self.writeGamelistEntry(gamelist,dosGame,game,genre, useGenreSubFolders,conversionType)
        return dosGame
    
    # Replaces “ ” ’ …
    def cleanXmlString(self, s) :
        return s.replace('&','&amp;')
    
    # Write metada for a given game to in-memory gamelist xml
    def writeGamelistEntry(self,gamelist,dosGame,game,genre,useGenreSubFolders,conversionType):
        root = gamelist.getroot()

        frontPic = './downloaded_images/' + dosGame.frontPic.split('\\')[-1] if dosGame.frontPic is not None else ''
        manual = './manuals/' + dosGame.manual.split('\\')[-1] if dosGame.manual is not None else ''
        year = dosGame.year+"0101T000000" if dosGame.year is not None else ''
        
        if conversionType == util.retropie :
            path = "./"+genre+"/"+util.getCleanGameID(dosGame,'.conf') if useGenreSubFolders else "./"+util.getCleanGameID(dosGame,'.conf')
        else :
            path = "./"+genre+"/"+self.cleanXmlString(game)+".pc" if useGenreSubFolders else "./"+self.cleanXmlString(game)+".pc"
        
        existsInGamelist = [child for child in root.iter('game') if self.get(child,"name") == dosGame.name and self.get(child,"releasedate") == year]
        if len(existsInGamelist) == 0 :
            gameElt = etree.SubElement(root,'game')
            etree.SubElement(gameElt,'path').text = path
            etree.SubElement(gameElt,'name').text = dosGame.name
            etree.SubElement(gameElt,'desc').text = dosGame.desc if dosGame.desc is not None else ''
            etree.SubElement(gameElt,'releasedate').text = year    
            etree.SubElement(gameElt,'developer').text = dosGame.developer if dosGame.developer is not None else ''
            etree.SubElement(gameElt,'publisher').text = dosGame.publisher if dosGame.publisher is not None else ''
            etree.SubElement(gameElt,'genre').text = genre
            etree.SubElement(gameElt,'manual').text = manual
            etree.SubElement(gameElt,'image').text = frontPic
        
    # Convert multi genres exodos format to a single one
    def buildGenre(self,dosGame):
        if dosGame is not None and dosGame.genres is not None :
            if "Racing" in dosGame.genres or "Driving" in dosGame.genres or "Racing / Driving" in dosGame.genres:
                return "Race"
            elif 'Sports' in dosGame.genres :
                return 'Sports'
            elif 'Pinball' in dosGame.genres :
                return 'Pinball'
            elif "Puzzle" in dosGame.genres or "Board" in dosGame.genres or "Board / Party Game" in dosGame.genres :
                return "Puzzle"
            elif 'RPG' in dosGame.genres or 'Role-Playing' in dosGame.genres :
                return 'RPG'
            elif 'Flight Simulator' in dosGame.genres :
                return 'Simulation'
            elif 'Shooter' in dosGame.genres :
                return 'ShootEmUp'
            elif 'Platform' in dosGame.genres :
                return 'Platform'
            elif 'FPS' in dosGame.genres or 'First Person Shooter' in dosGame.genres :
                return 'Gun-FPS'
            elif 'Fighting' in dosGame.genres :
                return 'BeatEmUp'
            elif 'Strategy' in dosGame.genres and not "Puzzle" in dosGame.genres :
                return 'Strategy-Gestion'        
            elif "Adventure" in dosGame.genres and "Action" in dosGame.genres :
                return "Action-Adventure"
            elif "Adventure" in dosGame.genres :
                return "Adventure-Visual"
            elif 'Simulation' in dosGame.genres and 'Managerial' in dosGame.genres :
                return 'Strategy-Gestion'
            elif 'Simulation' in dosGame.genres :
                return 'Simulation'
            elif 'Action' in dosGame.genres :
                return 'Action-Adventure'
            else :
                return 'Unknown'
        else :
            return 'Unknown'