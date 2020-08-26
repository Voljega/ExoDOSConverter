import os

class CommandHandler():
    
    def __init__(self,outputDir, logger) :
        self.outputDir = outputDir
        self.logger = logger
        
    def useLine(self,l,cLines):
        for cL in cLines :
            if l.strip().lower().startswith(cL) :
                return False
        return True

    def reducePath(self,path,game):
        #self.logger.log("PATH CONVERT: %s" %path)
        if path.lower().startswith(".\games") or path.lower().startswith("\games") or path.lower().startswith("games") :
            pathList = path.split('\\')        
            if pathList[0]=='.' :
                pathList = pathList[1:]
            if len(pathList) > 1 and pathList[0].lower()=='games' and pathList[1].lower()==game.lower() :
                path = ".\\"+ "\\".join(pathList[1:])
        #self.logger.log("TO: %s" %path)
        return path
        
    # TODO separate CD Mount and basic mount    
    def handleCDMount(self,line,game,dest) :          
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
        #TODO paths in several part should be joined if same cd and we should work on that
        # else it's several cds and it should be handled in else parts ...
        for path in paths :
            path = self.reducePath(path.replace('"',""),game)        
            if len(paths)==1 :
                self.logger.log("    clean single CD")
                path = self.cleanCDname(path,dest)
            else :
                self.logger.log("    <ERROR> MULTIPATH/MULTISPACE")
                self.logger.log(paths)
            prString = prString + " "+path
        
        # treat mount a and d here
        # TODO shitty code to rework
        if line.startswith("mount a") or line.startswith("mount d") :        
            prString = dest.replace(self.outputDir+"\\","/recalbox/share/roms/dos/") + "/" + prString.strip()        
            prString = ' "' + prString.replace("\\","/") +'"'        
        
        fullString = " ".join(command[0:startIndex+1]) + prString + " " + " ".join(command[endIndex:])        
        return fullString
    
    def cleanCDname(self,path,dest):
        cdFileFullPath = os.path.join(dest,path)        
        if os.path.exists(cdFileFullPath) :
            if os.path.isdir(cdFileFullPath) :            
                return path
            else :                                   
                pathList = path.split('\\')
                cdFile = pathList[-1]                       
                cdFilename = os.path.splitext(cdFile)[0].lower()
                cdFileExt = os.path.splitext(cdFile)[-1].lower()                
                
                # Root path of CDs
                cdsPath = "\\".join(cdFileFullPath.split('\\')[:-1])
                    
                # Rename file to dos compatible name                
                cdFilename = self.dosRename(cdsPath,cdFile,cdFilename,cdFileExt)
                self.logger.log("    renamed %s to %s" %(cdFile,cdFilename+cdFileExt))
                
                if cdFileExt == ".cue" :
                    self.cleanCue(cdsPath,cdFilename)                   
                        
                cleanedPath = "\\".join(pathList[:-1])+"\\"+cdFilename+cdFileExt
                self.logger.log("    modify dosbox.bat : %s -> %s" %(path,cleanedPath))
                return cleanedPath
        else :
            self.logger.log("    <ERROR> path %s doesn't exist" %cdFileFullPath)
            return path
        
    def dosRename(self, path, originalFile, fileName, fileExt) :
        if len(fileName) > 8 :
            fileName = fileName[0:7]                    
        # Double rename file to avoid trouble with case on Windows
        source = os.path.join(path,originalFile)
        targetTemp = os.path.join(path,fileName+"1"+fileExt)
        target = os.path.join(path,fileName+fileExt)        
        os.rename(source, targetTemp)        
        os.rename(targetTemp, target)
        return fileName
    
    def cleanCue(self,path,fileName):
        oldFile = open(os.path.join(path,fileName+".cue"),'r')
        newFile = open(os.path.join(path,fileName+"-fix.cue"),'w')   
        for line in oldFile.readlines() :        
            if line.startswith("FILE") :
                params = line.split('"')
                isobin = os.path.splitext(params[1].lower())
                fixedIsoBinName = self.dosRename(path,params[1],isobin[0],isobin[1])
                params[1] = fixedIsoBinName + isobin[-1]
                line = '"'.join(params)
                self.logger.log("    cue FILE line -> " +line.rstrip('\n\r'))
                
            newFile.write(line)
        oldFile.close()
        newFile.close()
        os.remove(os.path.join(path,fileName+".cue"))
        os.rename(os.path.join(path,fileName+"-fix.cue"),os.path.join(path,fileName+".cue"))
        
        
        