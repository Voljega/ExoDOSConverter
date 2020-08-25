import os,shutil,collections

DosGame = collections.namedtuple('DosGame', 'name genre subgenre publisher developer year frontPic about')

class MetadataHandler():
    
    def __init__(self,gamesDosDir,outputDir) :
        self.gamesDosDir = gamesDosDir
        self.outputDir = outputDir
        
    def process(self, game, gamelist) :
        dosGame = self.handleMetadata(game)
        genre = self.buildGenre(dosGame)
        print("computed genre %s" %genre)
        print("")
        self.writeGamelistEntry(gamelist,dosGame,game,genre)
        return genre
        
    def writeGamelistEntry(self,gamelist,dosGame,game,genre):
        gamelist.write("    <game>\n")
        gamelist.write("        <path>./"+genre+"/"+game+".pc</path>\n")
        gamelist.write("        <name>"+dosGame.name+"</name>\n")
        gamelist.write("        <desc>"+dosGame.about+"</desc>\n")    
        gamelist.write("        <releasedate>"+dosGame.year+"0101T000000</releasedate>\n")
        gamelist.write("        <image>"+dosGame.frontPic+"</image>\n")
        gamelist.write("        <developer>"+dosGame.developer+"</developer>\n")
        gamelist.write("        <publisher>"+dosGame.publisher+"</publisher>\n")
        gamelist.write("        <genre>"+genre+"</genre>\n")
        gamelist.write("    </game>\n")
    
    # TODO do not use meagre shit anymore
    def handleMetadata(self,game) :
        # TODO Needs full rewrite for exoDOS v5
        # Metadat in G:\Romsets\eXoDOS4\Metadata/Metadata.xml
        # Front pics in G:\Romsets\eXoDOS4\Images\MS-DOS\Box - Front and subfolders
        # Game title in G:\Romsets\eXoDOS4\Images\MS-DOS\Screenshot - Game Title and subfolders
        # Game screenshot in G:\Romsets\eXoDOS4\Images\MS-DOS\Screenshot - Gameplay and subfolders
        # Manuals in G:\Romsets\eXoDOS4\Manuals\MS-DOS
        
        meagreDir = os.path.join(self.gamesDosDir,game,"Meagre")
        manualDir = os.path.join(meagreDir,"Manual")
        picDir = os.path.join(meagreDir,"Front")
        screenPicDir = os.path.join(meagreDir,"Screen")
        aboutFile = os.path.join(meagreDir,"About","about.txt")
        iniFileDir = os.path.join(meagreDir,"IniFile")
        
        iniFilename = os.path.join(iniFileDir,os.listdir(iniFileDir)[0])
        iniFile = open(iniFilename,'r')
        
        # Parse iniFile in iniFile dir    
        for line in iniFile.readlines() :
            confLine = line.split("=")
            key = confLine[0]        
            if key == "Name" :
                name = confLine[1].rstrip('\n\r ')
                safeEscapedName = name.replace(":","")
                safeEscapedName = safeEscapedName.replace("/","-")
                safeEscapedName = safeEscapedName.replace("?","")
                safeEscapedName = safeEscapedName.replace("*","-")
            elif key == "Genre" :
                genre = confLine[1].rstrip('\n\r ')
            elif key == "SubGenre" :
                subgenre = confLine[1].rstrip('\n\r ')
            elif key == "SubGenre2" :
                subgenre = subgenre + " " + confLine[1].rstrip('\n\r ')
            elif key == "Publisher" :
                publisher = confLine[1].rstrip('\n\r ')
            elif key == "Developer" :
                developer = confLine[1].rstrip('\n\r ')
            elif key == "Year" :
                year = confLine[1].rstrip('\n\r ')
            elif key == "Front01" :
                frontPic = confLine[1].rstrip('\n\r ')
            elif key == "Screen01" :
                screenPic = confLine[1].rstrip('\n\r ')
        #RECUPERER SCREEN SI FRONT N'EXISTE PAS
        
        front = os.path.join(picDir,frontPic)
        screen = os.path.join(screenPicDir,screenPic)
        #copy front pic if exists else screenPic
        if not os.path.exists(os.path.join(self.outputDir,"downloaded_images")) :
            os.mkdir(os.path.join(self.outputDir,"downloaded_images"))
        if os.path.exists(front) and not os.path.isdir(front):
            #TODO pic must be same name as game
            #print("copy pic file %s to %s" %(frontPic,os.path.join(self.outputDir,"downloaded_images",safeEscapedName +" - front.jpg")))
            shutil.copy2(front,os.path.join(self.outputDir,"downloaded_images",safeEscapedName +" - front.jpg"))
            frontPic = "./downloaded_images/"+safeEscapedName +" - front.jpg"
        elif os.path.exists(screen) and not os.path.isdir(screen):
            #TODO pic must be same name as game
            #print("copy pic file %s to %s" %(screenPic,os.path.join(self.outputDir,"downloaded_images",safeEscapedName +" - front.jpg")))
            shutil.copy2(screen,os.path.join(self.outputDir,"downloaded_images",safeEscapedName +" - front.jpg"))
            frontPic = "./downloaded_images/"+safeEscapedName +" - front.jpg"
        #copy manual files
        if not os.path.exists(os.path.join(self.outputDir,"manuals")) :
            os.mkdir(os.path.join(self.outputDir,"manuals"))
        manualFiles = os.listdir(manualDir)
        if len(manualFiles) > 0 and not os.path.exists(os.path.join(self.outputDir,"manuals",safeEscapedName)):
            os.mkdir(os.path.join(self.outputDir,"manuals",safeEscapedName))
        for manual in manualFiles:
            #print("copy manual file %s to %s" %(manual,os.path.join(self.outputDir,"manuals",safeEscapedName,manual)))
            shutil.copy2(os.path.join(manualDir,manual),os.path.join(self.outputDir,"manuals",safeEscapedName,manual))
        # get content of about in About dir    
        # about = open(aboutFile,'r',encoding='utf-8').read()    
        
        #aboutFile.close() // mandatory ?
        iniFile.close()
                    
        dosGame = DosGame(name,genre,subgenre,publisher,developer,year,"./downloaded_images/"+safeEscapedName +" - front.jpg",'')
        #print("")
        print("Metadata: %s (%s), genre: %s / %s" %(dosGame.name,dosGame.year,dosGame.genre,dosGame.subgenre))    
    #    print("publisher: %s , developer: %s" %(dosGame.publisher,dosGame.developer))
    #    print("pic : %s" %dosGame.frontPic)        
        return dosGame
    
    def buildGenre(self,dosGame):
        if dosGame.genre in ['Sports']:
            return dosGame.genre
        elif "Adventure" in dosGame.genre and "Action" in dosGame.subgenre :
            return "Action-Adventure"
        elif "Adventure" in dosGame.genre :
            return "Adventure"
        elif "Racing" in dosGame.genre :
            return "Race"
        elif dosGame.genre == 'Strategy' and "Board" in dosGame.subgenre:
            return 'Puzzle'
        elif dosGame.genre == 'Strategy' and not "Puzzle" in dosGame.subgenre:
            return 'Strategy-Gestion'
        elif dosGame.genre == 'Strategy' and "Puzzle" in dosGame.subgenre:
            return "Puzzle"
        elif dosGame.genre == 'Simulation' and 'Managerial' in dosGame.subgenre :
            return 'Strategy-Gestion'
        elif dosGame.genre == 'Simulation' and 'Sports' in dosGame.subgenre :
            return 'Sports'
        elif dosGame.genre == 'Simulation' and 'Pinball' in dosGame.subgenre :
            return 'Pinball'
        elif dosGame.genre == 'Simulation' :
            return 'Simulation'
        elif dosGame.genre == 'RPG':
            return 'RPG'
        elif dosGame.genre == 'Action' and 'Pinball' in dosGame.subgenre :
            return 'Pinball'
        elif dosGame.genre == 'Action' and "Puzzle" in dosGame.subgenre:
            return "Puzzle"
        elif dosGame.genre == 'Action' and 'Shooter' in dosGame.subgenre :
            return 'ShootEmUp'
        elif dosGame.genre == 'Action' and 'Platform' in dosGame.subgenre :
            return 'Platform'
        elif dosGame.genre == 'Action' and 'FPS' in dosGame.subgenre :
            return 'Gun-FPS'
        elif dosGame.genre == 'Action' and 'Fighting' in dosGame.subgenre :
            return 'BeatEmUp'
        elif dosGame.genre == 'Action' :
            return 'Action-Adventure'
        else :
            return 'Unknown'