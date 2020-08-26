import os,shutil,collections,sys
import xml.etree.ElementTree as etree
from xml.dom import minidom
import util

DosGame = collections.namedtuple('DosGame', 'dosname metadataname name genres publisher developer year frontPic manual desc')

class MetadataHandler():
    
    def __init__(self,exoDosDir, cache,logger) :
        self.exoDosDir = exoDosDir
        self.cache = cache
        self.logger = logger
        self.metadatas = dict()
        
    def get(self,i,e):
        ll=i.find(e)        
        return ll.text if ll != None else None
    
    def initXml(self, outputDir) :
        if os.path.exists(os.path.join(outputDir,"gamelist.xml")) :
            parser = etree.XMLParser(encoding="utf-8")
            return etree.parse(os.path.join(outputDir,"gamelist.xml"), parser=parser)
        else :
            tree = etree.ElementTree()
            tree._setroot(etree.Element('gameList'))
            return tree
        
    def writeXml(self, outputDir, gamelist) :
        xmlstr = minidom.parseString(etree.tostring(gamelist.getroot())).toprettyxml(indent="   ", newl="\r")
        xmlstr = '\n'.join([s for s in xmlstr.splitlines() if s.strip()])
        with open(os.path.join(outputDir,"gamelist.xml"), "wb") as f:
            f.write(xmlstr.encode('utf-8'))
        
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
        
    def processGame(self, game, gamelist, genre, outputDir) :
        dosGame = self.handleMetadata(game)
        self.logger.log("  computed genre %s" %genre)
        self.logger.log("  copy pics and manual")
        if dosGame.frontPic is not None and os.path.exists(dosGame.frontPic) :
            shutil.copy2(dosGame.frontPic,os.path.join(outputDir,'downloaded_images'))
        if dosGame.manual is not None and os.path.exists(dosGame.manual) :
            shutil.copy2(dosGame.manual, os.path.join(outputDir, 'manuals'))
        self.logger.log("")
        self.writeGamelistEntry(gamelist,dosGame,game,genre)
        return genre
    
    # replace “ ” ’ …
    def cleanString(self, s) :
        return s.replace('&','&amp;')
        
    def writeGamelistEntry(self,gamelist,dosGame,game,genre):
        root = gamelist.getroot()
        frontPic = './downloaded_images/' + dosGame.frontPic.split('\\')[-1] if dosGame.frontPic is not None else ''
        manual = './manuals/' + dosGame.manual.split('\\')[-1] if dosGame.manual is not None else ''
        gameElt = etree.SubElement(root,'game')
        etree.SubElement(gameElt,'path').text = "./"+genre+"/"+self.cleanString(game)+".pc"
        etree.SubElement(gameElt,'name').text = dosGame.name
        etree.SubElement(gameElt,'desc').text = dosGame.desc
        etree.SubElement(gameElt,'releasedate').text = dosGame.year+"0101T000000"      
        etree.SubElement(gameElt,'developer').text = dosGame.developer
        etree.SubElement(gameElt,'publisher').text = dosGame.publisher
        etree.SubElement(gameElt,'genre').text = genre
        etree.SubElement(gameElt,'manual').text = manual
        etree.SubElement(gameElt,'image').text = frontPic
    
    def handleMetadata(self,game) :
        dosGame = self.metadatas.get(game)
        self.logger.log("  Metadata: %s (%s), genres: %s" %(dosGame.name,dosGame.year," | ".join(dosGame.genres)))     
        return dosGame
    
    def buildGenre(self,dosGame):
        if 'Sports' in dosGame.genres :
            return dosGame.genre
        elif "Racing" in dosGame.genres or "Driving" in dosGame.genres or "Racing / Driving" in dosGame.genres:
            return "Race"
        elif 'Pinball' in dosGame.genres :
            return 'Pinball'
        elif "Puzzle" in dosGame.genres or "Board" in dosGame.genres :
            return "Puzzle"
        elif 'RPG' in dosGame.genres or 'Role-Playing' in dosGame.genres :
            return 'RPG'
        elif 'Shooter' in dosGame.genres :
            return 'ShootEmUp'
        elif 'Platform' in dosGame.genres :
            return 'Platform'
        elif 'FPS' in dosGame.genres :
            return 'Gun-FPS'
        elif 'Fighting' in dosGame.genres :
            return 'BeatEmUp'
        elif 'Strategy' in dosGame.genres and not "Puzzle" in dosGame.genres :
            return 'Strategy-Gestion'        
        elif 'Simulation' in dosGame.genres and 'Managerial' in dosGame.genres :
            return 'Strategy-Gestion'
        elif 'Simulation' in dosGame.genres :
            return 'Simulation'
        elif "Adventure" in dosGame.genres and "Action" in dosGame.genres :
            return "Action-Adventure"
        elif "Adventure" in dosGame.genres :
            return "Adventure"
        elif 'Action' in dosGame.genres :
            return 'Action-Adventure'
        else :
            return 'Unknown'