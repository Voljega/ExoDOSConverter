import os,stat
import util

# Converts dosbox commands to desired format and paths, at the moment Batocera/ Recalbox linux flavor
class CommandHandler():
    
    def __init__(self,outputDir, logger) :
        self.outputDir = outputDir
        self.logger = logger
    
    # Checks if a command line should be kept or not    
    def useLine(self,l,cLines):
        for cL in cLines :
            if l.strip().lower().startswith(cL) :
                return False
        return True
    
    # Removes games parts from exoDos paths
    def reducePath(self,path,game):
#        self.logger.log("    PATH CONVERT: %s" %path)
        if path.lower().startswith(".\games") or path.lower().startswith("\games") or path.lower().startswith("games") :
            pathList = path.split('\\')
            if pathList[0]=='.' :
                pathList = pathList[1:]
            if len(pathList) > 1 and pathList[0].lower()=='games' : #and pathList[1].lower()==game.lower() :
                path = ".\\"+ "\\".join(pathList[1:])
#        self.logger.log("    TO: %s" %path)
        return path
    
    # Parses command lines path parts
    def pathListInCommandLine(self,line,startTokens,endTokens) :
        command = line.split(" ")    
        startIndex = -1
        endIndex = -1
        count =0
        for param in command :
            if param.lower() in startTokens :
                startIndex = count
            elif param.lower() in endTokens :
                endIndex = count
            count = count + 1
            
        if endIndex == -1 :
            endIndex = len(command)
        
        return command[startIndex+1:endIndex], command, startIndex,endIndex
    
    # Converts imgmount command line    
    def handleImgmount(self,line,game,dest) :        
        paths, command, startIndex,endIndex = self.pathListInCommandLine(line,startTokens=['a','b','c','d','e','y'],endTokens=['-t'])
        
        prString = ""
        if len(paths)==1 :
                path = self.reducePath(paths[0].replace('"',""),game)
                self.logger.log("    clean single imgmount")
                path = self.cleanCDname(path,dest)
                prString = prString + " "+path
        else :
            # See if path contains ""
            redoPath = " ".join(paths)
            countChar = redoPath.count('"')
            if countChar == 2 :
                # Single path with space
                # casetest: Take Back / CSS
                path = self.reducePath(redoPath.replace('"',""),game)
                self.logger.log("    clean single imgmount")
                path = self.cleanCDname(path,dest)
                prString = prString + " "+path
            else :
                # several paths (multi cds)
                self.logger.logList("    multi imgmount",paths)
                # analyze paths to see if there are spaces in it  
                # casetest: Star Trek Borg / STBorg
                spaceInPaths = False
                for path in paths :
                    if path.startswith('"') and not path.endswith('"') :
                        spaceInPaths = True
                        break
                if spaceInPaths :
                    reshapedPaths = []
                    fixedPath = ''
                    for path in paths :
                        if path.startswith('"') and not path.endswith('"') :
                            fixedPath = path
                        elif not path.startswith('"') and path.endswith('"') :
                            fixedPath = fixedPath +" "+ path
                            reshapedPaths.append(fixedPath)
                            fixedPath = ""
                        else :
                            fixedPath = fixedPath +" "+path
                    paths = reshapedPaths
                        
                cdCount = 1
                for path in paths :
                    path = self.reducePath(path.replace('"',""),game)
                    path = self.cleanCDname(path,dest,cdCount)
                    prString = prString + " "+'"'+path+'"'
                    cdCount = cdCount + 1
        
        fullString = " ".join(command[0:startIndex+1]) + prString + " " + " ".join(command[endIndex:])
        self.logger.log("    imgmount path: "+line.rstrip('\n\r ') + " --> " +fullString.rstrip('\n\r ')) 
        return fullString
    
    # Converts mount command line
    def handleMount(self,line,game,dest,genre,useGenreSubFolders,conversionType) :
        paths, command, startIndex,endIndex = self.pathListInCommandLine(line,startTokens=['a','b','d','e'],endTokens=['-t'])
        
        prString = ""
        if len(paths)==1 :
            path = self.reducePath(paths[0].replace('"',""),game)
            prString = prString +" "+path
        else :
             # See if path contains ""
            redoPath = " ".join(paths)
            countChar = redoPath.count('"')
            if countChar == 2 :
                path = self.reducePath(paths[0].replace('"',""),game)
                prString = prString +" "+path
            else :
                self.logger.log("    <ERROR> MULTIPATH/MULTISPACE")
                self.logger.logList("    paths",paths)
                for path in paths :
                    path = self.reducePath(path.replace('"',""),game) 
                    prString = prString +" "+path
        
        # Mount command needs to be absolute linux path
        if prString.strip().startswith('.') :            
            prString = prString.strip()[1:]
        gameString =  "/"+genre+"/"+game+".pc" if useGenreSubFolders else "/"+game+".pc"
        prString = util.getRomsFolderPrefix(conversionType)+gameString+prString.strip()
        prString = ' "' + prString.replace("\\","/") +'"'
       
        fullString = " ".join(command[0:startIndex+1]) + prString + " " + " ".join(command[endIndex:])
        self.logger.log("    mount path: "+line.rstrip('\n\r ') + " --> " +fullString.rstrip('\n\r '))
        return fullString
    
    # Rename a filename to a dos compatible 8 char name    
    def dosRename(self, path, originalFile, fileName, fileExt,cdCount) :
        fileName = fileName.replace(" ","")
        if len(fileName) > 8 :
            if cdCount is None :
                fileName = fileName[0:7]
            else:
                fileName = fileName[0:5]+str(cdCount)
        # Double rename file to avoid trouble with case on Windows
        source = os.path.join(path,originalFile)
        targetTemp = os.path.join(path,fileName+"1"+fileExt)
        target = os.path.join(path,fileName+fileExt)        
        os.rename(source, targetTemp)        
        os.rename(targetTemp, target)
        return fileName
    
    # Cleans cd names to a dos compatible 8 char name
    def cleanCDname(self,path,dest,cdCount=None):
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
                cdFilename = self.dosRename(cdsPath,cdFile,cdFilename,cdFileExt,cdCount)
                self.logger.log("      renamed %s to %s" %(cdFile,cdFilename+cdFileExt))
                
                if cdFileExt == ".cue" :
                    self.cleanCue(cdsPath,cdFilename,cdCount)               
                        
                cleanedPath = "\\".join(pathList[:-1])+"\\"+cdFilename+cdFileExt
#                self.logger.log("    modify dosbox.bat : %s -> %s" %(path,cleanedPath))
                return cleanedPath
        else :
            self.logger.log("      <ERROR> path %s doesn't exist" %cdFileFullPath)
            return path
    
    # Cleans cue files content to dos compatible 8 char name
    def cleanCue(self,path,fileName,cdCount):
        oldFile = open(os.path.join(path,fileName+".cue"),'r')
        newFile = open(os.path.join(path,fileName+"-fix.cue"),'w')   
        for line in oldFile.readlines() :        
            if line.startswith("FILE") :
                params = line.split('"')
                isobin = os.path.splitext(params[1].lower())
                fixedIsoBinName = self.dosRename(path,params[1],isobin[0],isobin[1],cdCount)
                self.logger.log("      renamed %s to %s" %(params[1],fixedIsoBinName+isobin[1]))
                # TODO might need to search for potential additional files (sub, ccd) with sameisobin[0] name and rename them too
                # casetest: Pinball Arcade (1994) / PBArc94:
                params[1] = fixedIsoBinName + isobin[-1]
                line = '"'.join(params)
                self.logger.log("      convert cue content -> " +line.rstrip('\n\r '))
                
            newFile.write(line)
        oldFile.close()
        newFile.close()
        #Remove readonly attribute if present before deleting
        os.chmod( os.path.join(path,fileName+".cue"), stat.S_IWRITE )
        os.remove(os.path.join(path,fileName+".cue"))
        os.rename(os.path.join(path,fileName+"-fix.cue"),os.path.join(path,fileName+".cue"))
        
        
        