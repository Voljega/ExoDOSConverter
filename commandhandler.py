import os
import stat
import util


# Converts dosbox commands to desired format and paths, at the moment Batocera/ Recalbox linux flavor
class CommandHandler:

    def __init__(self, outputDir, logger):
        self.outputDir = outputDir
        self.logger = logger

    # Checks if a command line should be kept or not    
    def useLine(self, l, cLines):
        for cL in cLines:
            if l.strip().lower().startswith(cL):
                return False
        return True

    # Removes games parts from exoDos paths
    def reducePath(self, path, game):
        #        self.logger.log("    PATH CONVERT: %s" %path)
        if path.lower().startswith(".\games") or path.lower().startswith("\games") or path.lower().startswith("games"):
            pathList = path.split('\\')
            if pathList[0] == '.':
                pathList = pathList[1:]
            if len(pathList) > 1 and pathList[0].lower() == 'games':  # and pathList[1].lower()==game.lower() :
                path = ".\\" + "\\".join(pathList[1:])
        #        self.logger.log("    TO: %s" %path)
        return path

    # Parses command lines path parts
    def pathListInCommandLine(self, line, startTokens, endTokens):
        command = line.split(" ")
        startIndex = -1
        endIndex = -1
        count = 0
        for param in command:
            if param.lower() in startTokens and startIndex == -1:
                startIndex = count
            elif param.lower() in endTokens and endIndex == -1:
                endIndex = count
            count = count + 1

        if endIndex == -1:
            endIndex = len(command)

        return command[startIndex + 1:endIndex], command, startIndex, endIndex

    # Converts imgmount command line    
    def handleImgmount(self, line, game, localGameOutputDir):
        paths, command, startIndex, endIndex = self.pathListInCommandLine(line,
                                                                          startTokens=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'y', '0', '2'],
                                                                          endTokens=['-t', '-size'])

        prString = ""
        if len(paths) == 1:
            path = self.reducePath(paths[0].replace('"', ""), game)
            self.logger.log("    clean single imgmount")
            path = self.cleanCDname(path.rstrip('\n'), localGameOutputDir, game)
            prString = prString + " " + path
        else:
            # See if path contains ""
            redoPath = " ".join(paths)
            countChar = redoPath.count('"')
            if countChar == 2:
                # Single path with space
                # TESTCASE: Take Back / CSS
                path = self.reducePath(redoPath.replace('"', ""), game)
                self.logger.log("    clean single imgmount")
                path = self.cleanCDname(path, localGameOutputDir, game)
                prString = prString + " " + path
            else:
                # several paths (multi cds)
                self.logger.logList("    multi imgmount", paths)
                # analyze paths to see if there are spaces in it  
                # TESTCASE: Star Trek Borg / STBorg
                spaceInPaths = False
                for path in paths:
                    if path.startswith('"') and not path.endswith('"'):
                        spaceInPaths = True
                        break
                if spaceInPaths:
                    reshapedPaths = []
                    fixedPath = ''
                    for path in paths:
                        if path.startswith('"') and not path.endswith('"'):
                            fixedPath = path
                        elif not path.startswith('"') and path.endswith('"'):
                            fixedPath = fixedPath + " " + path
                            reshapedPaths.append(fixedPath)
                            fixedPath = ""
                        else:
                            fixedPath = fixedPath + " " + path
                    paths = reshapedPaths

                cdCount = 1
                for path in paths:
                    path = self.reducePath(path.replace('"', ""), game)
                    path = self.cleanCDname(path, localGameOutputDir, game, cdCount)
                    prString = prString + " " + '"' + path + '"'
                    cdCount = cdCount + 1

        fullString = " ".join(command[0:startIndex + 1]) + prString + " " + " ".join(command[endIndex:])
        self.logger.log("    imgmount path: " + line.rstrip('\n\r ') + " --> " + fullString.rstrip('\n\r '))
        return fullString.rstrip(' ')

    # Converts mount command line
    def handleBoot(self, line, game, localGameOutputDir, genre, useGenreSubFolders, conversionType):
        bootPath = line.replace('boot ','').replace('BOOT ','').rstrip(' \n\r')
        if bootPath != '-l c' and bootPath != '-l c>null':
            # reduce except for boot -l c
            paths = bootPath.split(' ')
            cleanedPath = []
            for path in paths:
                if path not in ['-l', 'a']:
                    path = self.reducePath(path.replace('"', ""), game)
                    # Verify path
                    postfix = path.find('-l')
                    chkPath = path[:postfix].rstrip(' ') if postfix != -1 else path
                    if not os.path.exists(os.path.join(localGameOutputDir, util.localOutputPath(chkPath))):
                        if not os.path.exists(os.path.join(localGameOutputDir, game, util.localOutputPath(chkPath))):
                            self.logger.log("      <ERROR> path %s doesn't exist" % os.path.join(localGameOutputDir, util.localOutputPath(chkPath)))
                cleanedPath.append(path)

            bootPath = " ".join(cleanedPath)

        fullString = "boot " + bootPath + "\n"
        self.logger.log("    boot path: " + line.rstrip('\n\r ') + " --> " + fullString.rstrip('\n\r '))
        return fullString

    # Converts mount command line
    def handleMount(self, line, game, localGameOutputDir, genre, useGenreSubFolders, conversionType):
        paths, command, startIndex, endIndex = self.pathListInCommandLine(line, startTokens=['a', 'b', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k'],
                                                                          endTokens=['-t'])

        prString = ""
        if len(paths) == 1:
            # TESTCASE: Sidewalk (1987) / Sidewalk
            path = self.reducePath(paths[0].replace('"', ""), game)
            prString = prString + " " + path
        else:
            # See if path contains ""
            redoPath = " ".join(paths)
            countChar = redoPath.count('"')
            if countChar == 2:
                path = self.reducePath(paths[0].replace('"', ""), game)
                prString = prString + " " + path
            else:
                self.logger.log("    <ERROR> MULTIPATH/MULTISPACE")
                self.logger.logList("    paths", paths)
                for path in paths:
                    path = self.reducePath(path.replace('"', ""), game)
                    prString = prString + " " + path

        # Mount command needs to be absolute linux path
        if prString.strip().startswith('.'):
            prString = prString.strip()[1:]
        gameString = "/" + genre + "/" + game + ".pc" if useGenreSubFolders else "/" + game + ".pc"
        prString = util.getRomsFolderPrefix(conversionType) + gameString + prString.strip()
        prString = ' "' + prString.replace("\\", "/") + '"'

        fullString = " ".join(command[0:startIndex + 1]) + prString + " " + " ".join(command[endIndex:])
        self.logger.log("    mount path: " + line.rstrip('\n\r ') + " --> " + fullString.rstrip('\n\r '))
        return fullString

    # Rename a filename to a dos compatible 8 char name    
    def dosRename(self, path, originalFile, fileName, fileExt, cdCount):
        fileName = fileName.replace(" ", "")
        if len(fileName) > 8:
            if cdCount is None:
                fileName = fileName[0:7]
            else:
                fileName = fileName[0:5] + str(cdCount)
        if os.path.exists(os.path.join(path, fileName + fileExt)):
            fileName = fileName = fileName[0:6] + "1"
        # Double rename file to avoid trouble with case on Windows
        source = os.path.join(path, originalFile)
        targetTemp = os.path.join(path, fileName + "1" + fileExt)
        target = os.path.join(path, fileName + fileExt)
        os.rename(util.localOutputPath(source), util.localOutputPath(targetTemp))
        os.rename(util.localOutputPath(targetTemp), util.localOutputPath(target))
        return fileName

    # Cleans cd names to a dos compatible 8 char name
    def cleanCDname(self, path, localGameOutputDir, game, cdCount=None):
        cdFileFullPath = os.path.join(localGameOutputDir, path)
        if os.path.exists(util.localOutputPath(cdFileFullPath)):
            if os.path.isdir(util.localOutputPath(cdFileFullPath)):
                return path
            else:
                pathList = path.split('\\')
                cdFile = pathList[-1]
                oldCdFilename = os.path.splitext(cdFile)[0].lower()
                cdFileExt = os.path.splitext(cdFile)[-1].lower()

                # Root path of CDs
                cdsPath = "\\".join(cdFileFullPath.split('\\')[:-1])

                # Rename file to dos compatible name                
                cdFilename = self.dosRename(cdsPath, cdFile, oldCdFilename, cdFileExt, cdCount)
                self.logger.log("      renamed %s to %s" % (cdFile, cdFilename + cdFileExt))

                if cdFileExt == ".cue":
                    self.cleanCue(cdsPath, cdFilename, cdCount)

                # Clean remaining ccd and sub file which might have the same name as the cue file
                otherCdFiles = [file for file in os.listdir(util.localOutputPath(cdsPath)) if
                                os.path.splitext(file)[0].lower() == oldCdFilename and os.path.splitext(file)[
                                    -1].lower() in ['.ccd', '.sub']]
                for otherCdFile in otherCdFiles:
                    otherCdFileExt = os.path.splitext(otherCdFile)[-1].lower()
                    otherCdFilename = self.dosRename(cdsPath, otherCdFile, cdFilename, otherCdFileExt, cdCount)
                    self.logger.log("      renamed %s to %s" % (otherCdFile, otherCdFilename + otherCdFileExt))

                cleanedPath = "\\".join(pathList[:-1]) + "\\" + cdFilename + cdFileExt
                #                self.logger.log("    modify dosbox.bat : %s -> %s" %(path,cleanedPath))
                return cleanedPath
        else:
            if not os.path.exists(os.path.join(localGameOutputDir, game, path)):
                self.logger.log("      <ERROR> path %s doesn't exist" % cdFileFullPath)
            return path

    # Cleans cue files content to dos compatible 8 char name
    def cleanCue(self, path, fileName, cdCount):
        oldFile = open(os.path.join(util.localOutputPath(path), fileName + ".cue"), 'r')
        newFile = open(os.path.join(util.localOutputPath(path), fileName + "-fix.cue"), 'w')
        modifiedFirstLine = False
        for line in oldFile.readlines():
            if line.startswith("FILE") and not modifiedFirstLine:
                params = line.split('"')
                isobin = os.path.splitext(params[1].lower())
                fixedIsoBinName = self.dosRename(path, params[1], isobin[0], isobin[1], cdCount)
                self.logger.log("      renamed %s to %s" % (params[1], fixedIsoBinName + isobin[1]))
                # TESTCASE: Pinball Arcade (1994) / PBArc94:
                params[1] = fixedIsoBinName + isobin[-1]
                line = '"'.join(params)
                self.logger.log("      convert cue content -> " + line.rstrip('\n\r '))
                # Only do it for the first Line
                modifiedFirstLine = True

            newFile.write(line)
        oldFile.close()
        newFile.close()
        # Remove readonly attribute if present before deleting
        os.chmod(os.path.join(util.localOutputPath(path), fileName + ".cue"), stat.S_IWRITE)
        os.remove(os.path.join(util.localOutputPath(path), fileName + ".cue"))
        os.rename(os.path.join(util.localOutputPath(path), fileName + "-fix.cue"), os.path.join(util.localOutputPath(path), fileName + ".cue"))

