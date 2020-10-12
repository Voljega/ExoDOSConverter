import os
import util
import shutil
import ntpath
import platform


# Creates launch.bat and handles mount and imgmount paths
def launchAndMounts(game, outputDir, localGameOutputDir, logger):
    dosboxBat = open(os.path.join(localGameOutputDir, "dosbox.bat"), 'r')
    launchBat = open(os.path.join(localGameOutputDir, "1_Start.bat"), 'w')
    lines = dosboxBat.readlines()
    for line in lines:
        line = line.lstrip('@ ').rstrip(' \n\r')
        if line.lower() != 'c:':
            if line.startswith("imgmount"):
                launchBat.write(convertImgMount(line, game, outputDir, localGameOutputDir, logger))
            elif line.startswith("mount"):
                launchBat.write(convertMount(line, game, outputDir, localGameOutputDir, logger))
            elif line.startswith("boot"):
                if line == 'boot -l c':
                    launchBat.write('imgset r\n')
                elif line != 'boot':
                    launchBat.write(convertBoot(line, game, outputDir, localGameOutputDir, logger))
                else:
                    logger.log('      <ERROR> Impossible to convert %s command' % line)
                    launchBat.write(line + '\n')
            elif line.lower() in ['d:','f:','g:','h:','i:','j:','k:']:
                launchBat.write('e:\n')
            else:
                launchBat.write(line+'\n')
    # Change imgmount iso command to imgset ide10 cdgames/gamefolder/game.iso
    # Include imgset in the outputDir ?
    # Convert imgmount or mount of floppy to imgset fdd0 /floppy/filename.img
    launchBat.close()
    dosboxBat.close()
    createSetupBat(localGameOutputDir, game)
    createEditBat(localGameOutputDir, game)
    os.remove(os.path.join(localGameOutputDir, 'dosbox.bat'))


# Convert imgmount command for MiSTeR
def convertImgMount(line, game, outputDir, localGameOutputDir, logger):
    return handlesFileType(line, 2, game, outputDir, localGameOutputDir, logger)


# Convert mount command for MiSTeR
def convertMount(line, game, outputDir, localGameOutputDir, logger):
    return handlesFileType(line, 2, game, outputDir, localGameOutputDir, logger)


# Convert boot command for MiSTeR
def convertBoot(line, game, outputDir, localGameOutputDir, logger):
    return handlesFileType(line, 1, game, outputDir, localGameOutputDir, logger)


# Determine type of files
def handlesFileType(line, pathPos, game, outputDir, localGameOutputDir, logger):
    params = line.split(' ')
    # TODO Boot command without parameter will crash here, needs to be parsed properly
    path = params[pathPos].replace('"', '')
    if params[0] in ['imgmount','mount']:
        if params[-1].rstrip('\n\r ') == 'cdrom':
            localPath = locateMountedFiles(path, params[0], game, outputDir, localGameOutputDir)
            return convertCD(localPath, game, outputDir, localGameOutputDir, logger)
        elif params[-1].rstrip('\n\r ') == 'floppy':
            localPath = locateMountedFiles(path, params[0], game, outputDir, localGameOutputDir)
            return convertFloppy(localPath, game, outputDir, localGameOutputDir, logger)
        else:  # Treat default version as cd
            localPath = locateMountedFiles(path, params[0], game, outputDir, localGameOutputDir)
            if params[1].rstrip('\n\r ') == 'c':
                return convertBootDisk(localPath, game, outputDir, localGameOutputDir, logger)
            else:
                return convertCD(localPath, game, outputDir, localGameOutputDir, logger)
    else:  # Boot command
        localPath = locateMountedFiles(path, params[0], game, outputDir, localGameOutputDir)
        return convertFloppy(localPath, game, outputDir, localGameOutputDir, logger)


# Locate mounted files
def locateMountedFiles(path, command, game, outputDir, localGameOutputDir):
    if platform.system() == 'Windows':
        path = path.replace('/','\\')

    localPath = util.localOutputPath(os.path.join(localGameOutputDir, path))
    if not os.path.exists(localPath):
        localPath = util.localOutputPath(os.path.join(localGameOutputDir, game, path))
    if not os.path.exists(localPath):
        localPath = util.localOutputPath(os.path.join(outputDir, path))
    if not os.path.exists(localPath):
        localPath = util.localOutputPath(os.path.join(outputDir, game, path))
    return localPath


# Convert cds file
def convertCD(localPath, game, outputDir, localGameOutputDir, logger):
    # Move cds file
    if not os.path.exists(os.path.join(outputDir, 'cd')):
        os.mkdir(os.path.join(outputDir, 'cd'))

    if os.path.isdir(localPath):
        return convertMountedFolder('e', localPath, game, outputDir, localGameOutputDir, logger)
    else:
        # Move cds file
        if not os.path.exists(os.path.join(outputDir, 'cd', game)):
            os.mkdir(os.path.join(outputDir, 'cd', game))

        imgmountDir = os.path.dirname(localPath)

        cdFiles = [file for file in os.listdir(imgmountDir) if os.path.splitext(file)[-1].lower() in ['.ccd', '.sub', '.cue', '.iso', '.img', '.bin']]
        for cdFile in cdFiles:
            logger.log("      move %s to %s folder" % (cdFile, 'cd'))
            shutil.move(os.path.join(imgmountDir,cdFile),os.path.join(outputDir,'cd',game))
        # Modify and return command line
        return 'imgset ide10 "/cd/' + game + '/' + ntpath.basename(localPath) + '"\n'


# Convert floppy file
def convertFloppy(localPath, game, outputDir, localGameOutputDir, logger):
    # Move bootable file
    if not os.path.exists(os.path.join(outputDir, 'floppy')):
        os.mkdir(os.path.join(outputDir, 'floppy'))

    if os.path.isdir(localPath):
        return convertMountedFolder('a', localPath, game, outputDir, localGameOutputDir, logger)
    else:
        if not os.path.exists(os.path.join(outputDir, 'floppy', game)):
            os.mkdir(os.path.join(outputDir, 'floppy', game))
        logger.log("      move %s to %s folder" % (ntpath.basename(localPath), 'floppy'))
        shutil.move(localPath, os.path.join(outputDir, 'floppy', game))
        # Modify and return command line
        return 'imgset fdd0 "/floppy/' + game + '/' + ntpath.basename(localPath) + '"\n'


# Convert bootdisk file
def convertBootDisk(localPath, game, outputDir, localGameOutputDir, logger):
    # Move bootable file
    if not os.path.exists(os.path.join(outputDir, 'bootdisk')):
        os.mkdir(os.path.join(outputDir, 'bootdisk'))

    if os.path.isdir(localPath):
        return convertMountedFolder('c', localPath, game, outputDir, localGameOutputDir, logger)
    else:
        if not os.path.exists(os.path.join(outputDir, 'bootdisk', game)):
            os.mkdir(os.path.join(outputDir, 'bootdisk', game))
        logger.log("      move %s to %s folder" % (ntpath.basename(localPath), 'bootdisk'))
        shutil.move(localPath, os.path.join(outputDir, 'bootdisk', game, os.path.splitext(ntpath.basename(localPath))[0]+'.vhd'))
        # Modify and return command line
        return 'imgset ide00 "/bootdisk/' + game + '/' + os.path.splitext(ntpath.basename(localPath))[0]+'.vhd' + '"\n'


# Convert mounted or imgmounted folder
def convertMountedFolder(letter, localPath, game, outputDir, localGameOutputDir, logger):
    if localPath.endswith('\\'):
        localPath = localPath[:-1]
    # TODO basename is not good either, path is lost !! needs reduction of the path instead / missing parts
    logger.log("      subst folder %s as %s:" % (ntpath.basename(localPath), letter))
    return 'subst /d ' + letter + ':\nsubst ' + letter + ': ' + ntpath.basename(localPath)


# Create Setup.bat file
def createSetupBat(localGameOutputDir, game):
    setupBat = open(os.path.join(localGameOutputDir, "3_Setup.bat"), 'w')
    setupBat.write('@echo off\n')
    setupBat.write('cd %s\n' % game)
    setupBat.write('\n')
    setupBat.write('IF EXIST setsound.exe goto :sound1\n')
    setupBat.write('IF EXIST sound.exe goto :sound2\n')
    setupBat.write('IF EXIST sound.com goto :sound3\n')
    setupBat.write('IF EXIST install.exe goto :install1\n')
    setupBat.write('IF EXIST install.com goto :install2\n')
    setupBat.write('IF EXIST setup.exe goto :setup1\n')
    setupBat.write('IF EXIST setup.com goto :setup2\n')
    setupBat.write('\n')
    setupBat.write(
        'ECHO No setup files were found for this game.  You will need to manually run the appropriate setup in DOS.\n')
    setupBat.write('pause\n')
    setupBat.write('goto :END\n')
    setupBat.write('\n')
    setupBat.write(':sound1\n')
    setupBat.write('call setsound.exe\n')
    setupBat.write('goto :END\n')
    setupBat.write('\n')
    setupBat.write(':sound2\n')
    setupBat.write('call sound.exe\n')
    setupBat.write('goto :END\n')
    setupBat.write('\n')
    setupBat.write(':sound3\n')
    setupBat.write('call sound.com\n')
    setupBat.write('gotto :END\n')
    setupBat.write('\n')
    setupBat.write(':setup1\n')
    setupBat.write('call setup.exe\n')
    setupBat.write('goto :END\n')
    setupBat.write('\n')
    setupBat.write(':setup2\n')
    setupBat.write('call setup.com\n')
    setupBat.write('goto :END\n')
    setupBat.write('\n')
    setupBat.write(':install1\n')
    setupBat.write('call install.exe\n')
    setupBat.write('goto :END\n')
    setupBat.write('\n')
    setupBat.write(':install2\n')
    setupBat.write('call install.com\n')
    setupBat.write('goto :END\n')
    setupBat.write('\n')
    setupBat.write(':END\n')
    setupBat.write('CLS\n')
    setupBat.close()


# Create Edit.bat file
def createEditBat(localGameOutputDir, game):
    editBat = open(os.path.join(localGameOutputDir, "4_Edit.bat"), 'w')
    editBat.write('@echo off\nedit 1_Start.bat\n')
    editBat.close()
