import os

class CommandHandler():
    
    def __init__(self,outputDir) :
        self.outputDir = outputDir
        
    def isGoodLine(self,l,cLines):
        for cL in cLines :
            if l.strip().lower().startswith(cL) :
                return False    
        return True

    def reducePath(self,path,game):    
        if path.startswith(".\games") or path.startswith("\games") or path.startswith("games") :
            pathList = path.split('\\')        
            if pathList[0]=='.' :
                pathList = pathList[1:]
            # TODO shouldn't remove game anymore    
            if len(pathList) > 1 and pathList[0].lower()=='games' and pathList[1].lower()==game.lower() :
                cleanedPath = "."
                for pathElt in pathList[2:] :
                    cleanedPath = cleanedPath + "\\" + pathElt            
                return cleanedPath
            else :
                return path
        else :
            return path
        
    # TODO separate CD Mount and basic mount    
    def handleCDMount(self,line,game,dest) :    
        line = line.replace("@","")#always show imgmount command    
        command = line.split(" ")    
        startIndex = -1
        endIndex = -1
        count =0
        for param in command :
            if param == 'd' or param == 'a' or param == 'b':
                startIndex = count
            elif param == '-t' :
                endIndex = count
            count = count + 1
        
        paths = command[startIndex+1:endIndex]    
        prString = ""
        for path in paths :
            path = self.reducePath(path.replace('"',""),game)        
            if len(paths)==1 :
                #HANDLE FILENAME FOR LEN(PATHS ) == 1
                path = self.cleanCDname(path,game,dest)        
            prString = prString + " "+path
        
        # treat mount a and d here        
        if line.startswith("mount a") or line.startswith("mount d") :        
            prString = dest.replace(self.outputDir+"\\","/recalbox/share/roms/dos/") + "/" + prString.strip()        
            prString = ' "' + prString.replace("\\","/") +'"'        
        
        fullString = " ".join(command[0:startIndex+1]) + prString + " " + " ".join(command[endIndex:])
        print(fullString)
        return fullString
    
    def cleanCDname(self,path,game,dest):
        pathFile = os.path.join(dest,path)    
        if os.path.exists(pathFile) :
            if os.path.isdir(pathFile) :            
                return path
            else :                     
                pathList = path.split('\\')
                filename = pathList[-1]                       
                cleanName = filename.split(".")[0].lower()
                ext = filename.split(".")[-1]
                if len(cleanName)>8 :
                    cleanName = cleanName[0:7]            
                dirPath = "\\".join(pathFile.split('\\')[:-1])
                for file in os.listdir(dirPath) :
                    if file.split(".")[0].lower() == filename.split(".")[0].lower() :        
                        if len(file.split("."))>1 and file.split(".")[-1].lower() == "cue" :
                            print("create new clean cue file "+cleanName+"."+file.split(".")[-1])
                            print(file)
                            sourceFile = file;
                            targetFile = cleanName+"."+file.split(".")[-1].lower();
                            source = os.path.join(dirPath,sourceFile)
                            target = os.path.join(dirPath,targetFile)
        #                    print("%s != %s %r" %(sourceFile.lower(),targetFile,not sourceFile.lower() == targetFile))
        #                    print("%s == %s %r" %(sourceFile.lower(),targetFile, sourceFile.lower() == targetFile))
                            if not sourceFile.lower() == targetFile :
                                self.cleanCue(source,target,cleanName)
                                os.remove(os.path.join(dirPath,file))
                            else :
                                print ("cue already well named")
                                self.cleanCue(source,target+"1",cleanName)
                                os.remove(os.path.join(dirPath,file))
                                os.rename(target+"1",target)
                        else :
                            print("renamed %s to %s" %(file,cleanName+"."+file.split(".")[-1].lower()))
                            #double rename to avoid problems of same name with different case
                            os.rename(os.path.join(dirPath,file),os.path.join(dirPath,cleanName+"."+file.split(".")[-1].lower()+"1"))
                            os.rename(os.path.join(dirPath,cleanName+"."+file.split(".")[-1].lower()+"1"),os.path.join(dirPath,cleanName+"."+file.split(".")[-1].lower()))
                        
                cleanedPath = "\\".join(pathList[:-1])+"\\"+cleanName+"."+ext.lower()
                print("modify dosbox.bat : %s -> %s" %(path,cleanedPath))
                return cleanedPath
        else :
            print("<ERROR> %s doesn't exist" %pathFile)
            return path
        
        
    def cleanCue(self,old,new,cleanName):
        oldFile = open(old,'r')
        newFile = open(new,'w')   
        for line in oldFile.readlines() :        
            if line.startswith("FILE") :
                params = line.split('"')            
                params[1] = cleanName + "." + params[1].split(".")[-1].lower()
                line = '"'.join(params)
                print("cue FILE line -> " +line.rstrip('\n\r'))
                
            newFile.write(line)
        oldFile.close()
        newFile.close()