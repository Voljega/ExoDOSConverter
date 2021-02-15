import os
import shutil
import stat
import util
import ntpath


# Converts dosbox commands to desired format and paths, at the moment Batocera/ Recalbox linux flavor
class CommandHandler:

    def __init__(self, gGator):
        self.outputDir = gGator.outputDir
        self.logger = gGator.logger
        self.gGator = gGator

    # Rename a filename to a dos compatible 8 char name
    def dosRename(self, path, originalFile, fileName, fileExt, cdCount):
        fileName = fileName.replace(" ", "").replace("[", "").replace("]", "")
        if len(fileName) > 8:
            if cdCount is None:
                fileName = fileName[0:7]
            else:
                fileName = fileName[0:5] + str(cdCount)
        # TESTCASE : Ripper (1996) / ripper shouldn't enter here
        if os.path.exists(os.path.join(path, fileName + fileExt)) and (
                fileName + fileExt) != originalFile.lower() and cdCount is None:
            fileName = fileName[0:6] + "1"
        # Double rename file to avoid trouble with case on Windows
        source = os.path.join(path, originalFile)
        targetTemp = os.path.join(path, fileName + "1" + fileExt)
        target = os.path.join(path, fileName + fileExt)
        os.rename(util.localOutputPath(source), util.localOutputPath(targetTemp))
        os.rename(util.localOutputPath(targetTemp), util.localOutputPath(target))
        return fileName

    # Checks if a command line should be kept or not
    def useLine(self, line, cLines):
        for cL in cLines:
            if line.strip().lower().startswith(cL):
                return False
        return True

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

    # Removes eXo collection games folder parts from exo collection paths
    def reducePath(self, path, gameInternalBatFile=False):
        #        self.logger.log("    PATH CONVERT: %s" %path)
        exoToken = util.getCollectionGamesDirToken(self.gGator.collectionVersion).lower()
        if path.lower().startswith(".\\" + exoToken) or path.lower().startswith("\\" + exoToken) \
                or path.lower().startswith(exoToken):
            pathList = path.split('\\')
            if pathList[0] == '.':
                pathList = pathList[1:]
            if len(pathList) > 1 and pathList[0].lower() == exoToken:
                if not gameInternalBatFile:
                    path = ".\\" + "\\".join(pathList[1:])
                else:
                    path = ".\\" + "\\".join(pathList[2:])
        #        self.logger.log("    TO: %s" %path)
        return path

    # Converts imgmount command line
    def handleImgmount(self, line, gameInternalBatFile=False):
        startTokens = ['a', 'b', 'c', 'd', 'e', 'f','g', 'h', 'i', 'j', 'k', 'y', '0','2']
        endTokens = ['-t', '-size']
        paths, command, startIndex, endIndex = self.pathListInCommandLine(line, startTokens, endTokens)

        prString = ""
        if len(paths) == 1:
            path = self.reducePath(paths[0].replace('"', ""), gameInternalBatFile)
            self.logger.log("    clean single imgmount")
            path = self.cleanCDname(path.rstrip('\n'), None, gameInternalBatFile)
            prString = prString + " " + path
        else:
            # See if path contains ""
            redoPath = " ".join(paths)
            countChar = redoPath.count('"')
            if countChar == 2:
                # Single path with space
                # TESTCASE: Take Back / CSS
                path = self.reducePath(redoPath.replace('"', ""), gameInternalBatFile)
                self.logger.log("    clean single imgmount")
                path = self.cleanCDname(path, None, gameInternalBatFile)
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
                    path = self.reducePath(path.replace('"', ""), gameInternalBatFile)
                    path = self.cleanCDname(path, cdCount, gameInternalBatFile)
                    prString = prString + " " + '"' + path + '"'
                    cdCount = cdCount + 1

        fullString = " ".join(command[0:startIndex + 1]) + prString + " " + " ".join(command[endIndex:])
        self.logger.log("    imgmount path: " + line.rstrip('\n\r ') + " --> " + fullString.rstrip('\n\r '))
        return fullString.rstrip(' ')

    # Converts mount command line
    def handleBoot(self, line):
        bootPath = line.replace('boot ', '').replace('BOOT ', '').rstrip(' \n\r')
        if bootPath != '-l c' and bootPath != '-l c>null':
            # reduce except for boot -l c
            paths = bootPath.split(' ')
            cleanedPath = []
            if paths[0].startswith('"') and (
                    paths[-1].lower().endswith('.ima"') or paths[-1].lower().endswith('.img"')):
                paths = [" ".join(paths)]
                path = paths[0].replace('"', '')
                path = self.reducePath(path)
                imgPath = os.path.dirname(path)
                imgFullLocalPath = os.path.join(self.gGator.getLocalGameOutputDir(), util.localOutputPath(imgPath))
                imgFile = ntpath.basename(path)
                oldImgFilename = os.path.splitext(imgFile)[0]
                imgFileExt = os.path.splitext(imgFile)[-1]
                newImgFilename = self.dosRename(imgFullLocalPath, imgFile, oldImgFilename, imgFileExt, None)
                self.logger.log("      renamed %s to %s" % (imgFile, newImgFilename + imgFileExt))
                path = '"' + imgPath + '\\' + newImgFilename + imgFileExt + '"'
                cleanedPath.append(path)
            else:
                for path in paths:
                    if path not in ['-l', 'a', 'a:']:
                        path = self.reducePath(path.replace('"', ""))
                        # Verify path
                        postfix = path.find('-l')
                        chkPath = path[:postfix].rstrip(' ') if postfix != -1 else path
                        if not os.path.exists(
                                os.path.join(self.gGator.getLocalGameOutputDir(), util.localOutputPath(chkPath))):
                            if not os.path.exists(
                                    os.path.join(self.gGator.getLocalGameDataOutputDir(),
                                                 util.localOutputPath(chkPath))):
                                self.logger.log("      <ERROR> path %s doesn't exist"
                                                % os.path.join(self.gGator.getLocalGameOutputDir(),
                                                               util.localOutputPath(chkPath)),
                                                self.logger.ERROR)
                    cleanedPath.append(path)

            bootPath = " ".join(cleanedPath)

        fullString = "boot " + bootPath + "\n"
        self.logger.log("    boot path: " + line.rstrip('\n\r ') + " --> " + fullString.rstrip('\n\r '))
        return fullString

    # Converts mount command line
    def handleMount(self, line):
        startTokens = ['a', 'b', 'd', 'e', 'f', 'g','h', 'i', 'j', 'k']
        endTokens = ['-t']
        paths, command, startIndex, endIndex = self.pathListInCommandLine(line, startTokens, endTokens)

        prString = ""
        if len(paths) == 1:
            # TESTCASE: Sidewalk (1987) / Sidewalk
            path = self.reducePath(paths[0].replace('"', ""))
            if self.gGator.isWin3x():
                path = path.replace('\\' + self.gGator.game, '')

            if not os.path.exists(os.path.join(self.gGator.getLocalGameOutputDir(), path)):
                self.logger.log("    <ERROR> path %s doesn't exist"
                                % os.path.join(os.path.join(self.gGator.getLocalGameOutputDir(), path)),
                                self.logger.ERROR)
            prString = prString + " " + path
        else:
            # See if path contains ""
            redoPath = " ".join(paths)
            countChar = redoPath.count('"')
            if countChar == 2:
                path = self.reducePath(paths[0].replace('"', ""))
                if self.gGator.isWin3x():
                    path = path.replace('\\' + self.gGator.game, '')

                if not os.path.exists(os.path.join(self.gGator.getLocalGameOutputDir(), path)):
                    self.logger.log("    <ERROR> path %s doesn't exist"
                                    % os.path.join(os.path.join(self.gGator.getLocalGameOutputDir(), path)),
                                    self.logger.ERROR)
                prString = prString + " " + path
            else:
                self.logger.log("    <ERROR> MULTIPATH/MULTISPACE", self.logger.ERROR)
                self.logger.logList("    paths", paths)
                for path in paths:
                    path = self.reducePath(path.replace('"', ""))
                    if self.gGator.isWin3x():
                        path = path.replace('\\' + self.gGator.game, '')

                    if not os.path.exists(os.path.join(self.gGator.getLocalGameOutputDir(), path)):
                        self.logger.log("    <ERROR> path %s doesn't exist"
                                        % os.path.join(os.path.join(self.gGator.getLocalGameOutputDir(), path)),
                                        self.logger.ERROR)
                    prString = prString + " " + path

        # Mount command needs to be absolute linux path
        if prString.strip().startswith('.'):
            prString = prString.strip()[1:]
        gameString = "/" + self.gGator.genre + "/" + self.gGator.game + ".pc" if self.gGator.useGenreSubFolders else "/" + self.gGator.game + ".pc"
        prString = util.getRomsFolderPrefix(self.gGator.conversionType,
                                            self.gGator.conversionConf) + gameString + prString.strip()
        prString = ' "' + prString.replace("\\", "/") + '"'
        # Needs windows absolute path for retrobat
        if self.gGator.conversionType == util.retrobat:
            prString = prString.replace("/", "\\")

        fullString = " ".join(command[0:startIndex + 1]) + prString + " " + " ".join(command[endIndex:])
        self.logger.log("    mount path: " + line.rstrip('\n\r ') + " --> " + fullString.rstrip('\n\r '))
        return fullString

    # Cleans cd names to a dos compatible 8 char name
    def cleanCDname(self, path, cdCount=None, gameInternalBatFile=False):
        if self.gGator.isWin3x():
            path = path.replace('\\'+self.gGator.game,'')

        cdFileFullPath = os.path.join(self.gGator.getLocalGameOutputDir(), path) \
            if not gameInternalBatFile else os.path.join(self.gGator.getLocalGameDataOutputDir(), path)
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
            if not os.path.exists(os.path.join(self.gGator.getLocalGameDataOutputDir(), util.localOutputPath(path))):
                self.logger.log("      <ERROR> path %s doesn't exist" % util.localOutputPath(cdFileFullPath),
                                self.logger.ERROR)
            return path

    # Cleans cue files content to dos compatible 8 char name
    def cleanCue(self, path, fileName, cdCount):
        oldFile = open(os.path.join(util.localOutputPath(path), fileName + ".cue"), 'r')
        newFile = open(os.path.join(util.localOutputPath(path), fileName + "-fix.cue"), 'w')
        modifiedFirstLine = False
        for line in oldFile.readlines():
            if line.startswith("FILE"):
                if not modifiedFirstLine:  # Handle first line: img, iso, bin, etc
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
                else:  # Move music files in subfolders to cd folder
                    params = line.split('"')
                    if '\\' in params[1]:
                        musicParams = params[1].split('\\')  # Assume there are only two music file path components
                        shutil.move(os.path.join(util.localOutputPath(path), musicParams[0], musicParams[1]),
                                    os.path.join(util.localOutputPath(path), musicParams[1]))
                        self.logger.log("      move music %s from %s to . -> " % (musicParams[1], musicParams[0]))
                        params[1] = musicParams[1]
                        line = '"'.join(params)
                        self.logger.log("      convert cue content -> " + line.rstrip('\n\r '))

            newFile.write(line)
        oldFile.close()
        newFile.close()
        # Remove readonly attribute if present before deleting
        os.chmod(os.path.join(util.localOutputPath(path), fileName + ".cue"), stat.S_IWRITE)
        os.remove(os.path.join(util.localOutputPath(path), fileName + ".cue"))
        os.rename(os.path.join(util.localOutputPath(path), fileName + "-fix.cue"),
                  os.path.join(util.localOutputPath(path), fileName + ".cue"))
