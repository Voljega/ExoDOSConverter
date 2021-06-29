import os
import util
import shutil
import ntpath
import platform
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw


# Removed unused CDs
def removeUnusedCds(game, localGameDataOutputDir, logger):
    unusedCds = {
        'heromm2d': '.\\CD\\Heroes of Might and Magic 2.cue',
        'VirtSqua': '.\\cd\\V_SQUAD.CUE',
        'SSN21Se': '.\\cd\\SEAWOLF___.cue',
        'FIFAInte': '.\\CD\\FIFA.International.Soccer.cue',
        'vengexca': '..\\spirexc\\CD\\SPIRIT.cue',
        'whalvoy2': '..\\whalvoy1\\cd\\whalvoy1.cue',
        'WC2DLX': '..\\WC\\cd\\WC.cue'
    }
    if game in unusedCds:
        cue = os.path.join(localGameDataOutputDir, util.localOSPath(unusedCds[game]))
        cueDir = os.path.dirname(cue)
        cdFiles = [file for file in os.listdir(cueDir) if
                   os.path.splitext(ntpath.basename(cue))[0] == os.path.splitext(file)[0]
                   and os.path.splitext(file)[-1].lower() in ['.ccd', '.sub', '.cue', '.iso', '.img', '.bin']]
        for cdFile in cdFiles:
            logger.log("      remove unused cd file %s" % cdFile)
            os.remove(os.path.join(cueDir, cdFile))


# Creates launch.bat and handles mount and imgmount paths
def batsAndMounts(gGator):
    dosboxBat = open(os.path.join(gGator.getLocalGameOutputDir(), "dosbox.bat"), 'r')
    launchBat = open(os.path.join(gGator.getLocalGameOutputDir(), "1_Start.bat"), 'w', newline='\r\n')
    lines = dosboxBat.readlines()
    for line in lines:
        line = line.lstrip('@ ').rstrip(' \n\r')
        if line.lower() != 'c:' and not line.lower().startswith('path=') and not line.lower().startswith('path ='):
            if line.startswith("imgmount"):
                launchBat.write(convertImgMount(line, gGator))
            elif line.startswith("mount") and not line.lower().startswith('mountain'):
                launchBat.write(convertMount(line, gGator))
            elif line.startswith("boot") and line != 'boots':
                if line == 'boot -l c':
                    launchBat.write('imgset r\n')
                elif line != 'boot' and line != 'boot -l a':
                    launchBat.write(convertBoot(line, gGator))
                else:
                    gGator.logger.log('      <ERROR> Impossible to convert "%s" command' % line, gGator.logger.ERROR)
                    launchBat.write(line + '\n')
            elif line.lower() in ['d:', 'f:', 'g:', 'h:', 'i:', 'j:', 'k:']:
                launchBat.write('f:\n')
            elif line.lower() == 'call run' or line.lower() == 'call run.bat':
                if gGator.game in ['bisle2', 'Blood', 'Carmaged', 'comcon', 'comconra', 'CrypticP', 'lemm3', 'LewLeon',
                                   'MechW2', 'rarkani1', 'Resurrec', 'stjudgec']:
                    handleRunBat(gGator)
                launchBat.write(line)
            else:
                launchBat.write(line + '\n')
    # Change imgmount iso command to imgset ide10 cdgames/gamefolder/game.iso
    # Include imgset in the outputDir ?
    # Convert imgmount or mount of floppy to imgset fdd0 /floppy/filename.img
    launchBat.close()
    dosboxBat.close()
    createSetupBat(gGator)
    createEditBat(gGator)
    os.remove(os.path.join(gGator.getLocalGameOutputDir(), 'dosbox.bat'))


# Treat run.bat command inside game directory
def handleRunBat(gGator):
    runBat = os.path.join(gGator.getLocalGameDataOutputDir(), 'run.bat')
    if os.path.exists(runBat):
        runFile = open(runBat, 'r')
        runFileClone = open(runBat + '1', 'w', newline='\r\n')
        # Clone run.bat and only modify imgmount lines
        # Add some hardcoded lines which are impossible to handle
        handled = {
            'imgmount d ".\\cd\\comma2.iso" ".\\cd\\comma1.iso" ".\\cd\\cover3.cue" -t cdrom': 'imgset ide10 "/cd/comcon/comma2.iso"',
            'imgmount d ".\\cd\\cover3.cue" ".\\cd\\comma2.iso" ".\\cd\\comma1.iso" -t cdrom': 'imgset ide10 "/cd/comcon/cover3.cue"',
            'imgmount d ".\\cd\\redal2.iso" ".\\cd\\redal1.iso" ".\\cd\\redal3.cue" ".\\cd\\redal4.cue" -t cdrom':
                'imgset ide10 "/cd/comconra/redal2.iso"',
            'imgmount d ".\\cd\\redal4.cue" ".\\cd\\redal1.iso" ".\\cd\\redal2.iso" ".\\cd\\redal3.cue" -t cdrom':
                'imgset ide10 "/cd/comconra/redal4.cue"',
            'imgmount d ".\\cd\\redal3.cue" ".\\cd\\redal1.iso" ".\\cd\\redal2.iso" ".\\cd\\redal4.cue" -t cdrom':
                'imgset ide10 "/cd/comconra/redal3.cue"',
            'imgmount d .\\cd\\redal4.cue -t cdrom': 'imgset ide10 "/cd/comconra/redal4.cue"'
        }
        for cmdline in runFile.readlines():
            cmdline = cmdline.lstrip('@ ').rstrip(' \n\r')
            if cmdline.lower().startswith("imgmount "):
                if cmdline not in handled:
                    handled[cmdline] = convertImgMount(cmdline, gGator)
                runFileClone.write(handled[cmdline] + '\n')
            elif cmdline.lower().startswith("config "):
                converted_sound_command = convertSoundConfig(cmdline)
                runFileClone.write(converted_sound_command + '\n')
            else:
                runFileClone.write(cmdline + '\n')
        runFileClone.close()
        runFile.close()
        # Delete runbat and rename runbat clone to runbat
        os.remove(os.path.join(gGator.getLocalGameDataOutputDir(), 'run.bat'))
        os.rename(os.path.join(gGator.getLocalGameDataOutputDir(), 'run.bat1'), os.path.join(gGator.getLocalGameDataOutputDir(), 'run.bat'))
    else:
        gGator.logger.log('    <ERROR> run.bat not found', gGator.logger.ERROR)


# Convert sound command for MiSTeR
def convertSoundConfig(line):
    if 'mididevice' in line:
        if 'mt32' in line:
            return 'mt32-pi -m -v'
        elif 'fluidsynth' in line:
            return 'mt32-pi -g -v'
        elif 'default' in line:
            return 'mt32-pi -g -v'
    return 'REM ' + line


# Convert imgmount command for MiSTeR
def convertImgMount(line, gGator):
    return handlesFileType(line, 2, gGator)


# Convert mount command for MiSTeR
def convertMount(line, gGator):
    return handlesFileType(line, 2, gGator)


# Convert boot command for MiSTeR
def convertBoot(line, gGator):
    return handlesFileType(line, 1, gGator)


# Determine type of files
def handlesFileType(line, pathPos, gGator):
    params = line.split(' ')
    # TODO Boot command without parameter will crash here, needs to be parsed properly
    path = params[pathPos].replace('"', '')
    if params[0] in ['imgmount', 'mount']:
        if params[-1].rstrip('\n\r ') == 'cdrom' or params[-1].rstrip('\n\r ') == 'iso':
            localPath = locateMountedFiles(path, gGator)
            misterCommand = convertCD(localPath, gGator, params[1])
            # params size > 5 and not extras param like -fs ?
            if len(params) > 5 and params[3] != '-t':
                i = 3
                while i < (len(params) - 2):
                    print(params[i])
                    localPath = locateMountedFiles(params[i].replace('"', ''), gGator)
                    # Only move the other CDs
                    convertCD(localPath, gGator, params[1])
                    i = i + 1
            return misterCommand
        elif params[-1].rstrip('\n\r ') == 'floppy':
            localPath = locateMountedFiles(path, gGator)
            return convertFloppy(localPath, gGator, params[1])
        else:  # Treat default version as cd
            localPath = locateMountedFiles(path, gGator)
            if params[1].rstrip('\n\r ') == 'c':
                return convertBootDisk(localPath, gGator)
            else:
                return convertCD(localPath, gGator)
    else:  # Boot command
        localPath = locateMountedFiles(path, gGator)
        return convertFloppy(localPath, gGator, 'a')


# Locate mounted files
def locateMountedFiles(path, gGator):
    if platform.system() == 'Windows':
        path = path.replace('/', '\\')

    localPath = util.localOSPath(os.path.join(gGator.getLocalGameOutputDir(), path))
    if not os.path.exists(localPath):
        localPath = util.localOSPath(os.path.join(gGator.getLocalGameDataOutputDir(), path))
    if not os.path.exists(localPath):
        localPath = util.localOSPath(os.path.join(gGator.outputDir, path))
    # TODO Same as the first two ifs but without genre ? used ?
    # if not os.path.exists(localPath):
    #     localPath = util.localOutputPath(os.path.join(gGator.outputDir, gGator.game + '.pc', path))
    # if not os.path.exists(localPath):
    #     localPath = util.localOutputPath(os.path.join(gGator.outputDir, gGator.game + '.pc', gGator.game, path))
    return localPath


# Convert cds file
def convertCD(localPath, gGator, letter='d'):
    # Move cds file
    # TODO see if we can do makedirs below instead
    if not os.path.exists(os.path.join(gGator.outputDir, 'cd')):
        os.mkdir(os.path.join(gGator.outputDir, 'cd'))

    if os.path.isdir(localPath):
        return convertMountedFolder('d', localPath, gGator)
    else:
        gameCDDir = os.path.join(gGator.outputDir, 'cd', gGator.game)
        # Move cds file
        if not os.path.exists(gameCDDir):
            os.mkdir(gameCDDir)

        imgmountDir = os.path.dirname(localPath)

        cdFiles = [file for file in os.listdir(imgmountDir) if
                   os.path.splitext(ntpath.basename(localPath))[0] == os.path.splitext(file)[0]
                   and os.path.splitext(file)[-1].lower() in ['.ccd', '.sub', '.cue', '.iso', '.img', '.bin']]
        for cdFile in cdFiles:
            gGator.logger.log("      move %s to %s folder" % (cdFile, 'cd'))
            shutil.move(os.path.join(imgmountDir, cdFile), gameCDDir)
        # Move all music files except FLAC an FLA
        musicFiles = [file for file in os.listdir(imgmountDir)
                      if os.path.splitext(file)[-1].lower() in ['.ogg', '.mp3', '.wav']]
        for musicFile in musicFiles:
            gGator.logger.log("      move %s to %s folder" % (musicFile, 'cd'))
            shutil.move(os.path.join(imgmountDir, musicFile), gameCDDir)
        # Delete all FLAC and FLA files
        flacFiles = [file for file in os.listdir(imgmountDir)
                     if os.path.splitext(file)[-1].lower() in ['.flac', '.fla']]
        for flacFile in flacFiles:
            os.remove(os.path.join(imgmountDir, flacFile))
        # Modify and return command line
        if letter == 'd':
            return 'imgset ide10 "/cd/' + gGator.game + '/' + ntpath.basename(localPath) + '"\n'
        else:
            return 'imgset ide11 "/cd/' + gGator.game + '/' + ntpath.basename(localPath) + '"\n'


# Convert floppy file
def convertFloppy(localPath, gGator, letter):
    # Move bootable file
    # TODO see if we can do makedirs below instead
    if not os.path.exists(os.path.join(gGator.outputDir, 'floppy')):
        os.mkdir(os.path.join(gGator.outputDir, 'floppy'))

    if os.path.isdir(localPath):
        return convertMountedFolder(letter, localPath, gGator)
    else:
        gameFloppyDir = os.path.join(gGator.outputDir, 'floppy', gGator.game)
        if not os.path.exists(gameFloppyDir):
            os.mkdir(gameFloppyDir)
        gGator.logger.log("      move %s to %s folder" % (ntpath.basename(localPath), 'floppy'))
        shutil.move(localPath, gameFloppyDir)
        # Modify and return command line
        return 'imgset fdd0 "/floppy/' + gGator.game + '/' + ntpath.basename(localPath) + '"\n'


# Convert bootdisk file
def convertBootDisk(localPath, gGator):
    # Move bootable file
    # TODO see if we can do makedirs below instead
    if not os.path.exists(os.path.join(gGator.outputDir, 'bootdisk')):
        os.mkdir(os.path.join(gGator.outputDir, 'bootdisk'))

    if os.path.isdir(localPath):
        return convertMountedFolder('c', localPath, gGator)
    else:
        gameBootDiskDir = os.path.join(gGator.outputDir, 'bootdisk', gGator.game)
        if not os.path.exists(gameBootDiskDir):
            os.mkdir(gameBootDiskDir)
        gGator.logger.log("      move %s to %s folder" % (ntpath.basename(localPath), 'bootdisk'))
        shutil.move(localPath,
                    os.path.join(gameBootDiskDir, os.path.splitext(ntpath.basename(localPath))[0] + '.vhd'))
        # Modify and return command line
        return 'imgset ide00 "/bootdisk/' + gGator.game + '/' + os.path.splitext(ntpath.basename(localPath))[
            0] + '.vhd' + '"\n'


# Convert mounted or imgmounted folder
def convertMountedFolder(letter, localPath, gGator):
    if localPath.endswith('\\'):
        localPath = localPath[:-1]
    # TODO game\basename is not good either, path is lost !! needs reduction of the path instead / missing parts
    gGator.logger.log("      subst folder %s as %s:" % (ntpath.basename(localPath), letter))
    return 'subst ' + letter + ': /d\nsubst ' + letter + ': ' + gGator.game + '\\' + ntpath.basename(localPath)


# Create Setup.bat file
def createSetupBat(gGator):
    setupBat = open(os.path.join(gGator.getLocalGameOutputDir(), "3_Setup.bat"), 'w', newline='\r\n')
    setupBat.write('@echo off\n')
    if not gGator.isWin3x:
        setupBat.write('cd %s\n' % gGator.game)
    setupFiles = [file.lower() for file in os.listdir(gGator.getLocalGameDataOutputDir()) if file.lower() in
                  [gGator.game.lower(), 'setsound.exe', 'sound.exe', 'sound.com', 'install.exe', 'install.com',
                   'setup.exe', 'setup.com']]
    if len(setupFiles) <= 1 and os.path.exists(os.path.join(gGator.getLocalGameDataOutputDir(), gGator.game)):
        setupBat.write('cd %s\n' % gGator.game)
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
def createEditBat(gGator):
    editBat = open(os.path.join(gGator.getLocalGameOutputDir(), "4_Edit.bat"), 'w', newline='\r\n')
    editBat.write('@echo off\nedit 1_Start.bat\n')
    editBat.close()


# Create about.png
def text2png(scriptDir, text, cover, generatedImgpath):
    padding = 10
    imageWidth = 200
    textWidth = 640 - imageWidth
    color = "#FFF"
    bgcolor = "#000"
    REPLACEMENT_CHARACTER = u'\uFFFD'
    NEWLINE_REPLACEMENT_STRING = ' ' + REPLACEMENT_CHARACTER + ' '
    # font = ImageFont.truetype('DejaVuSans.ttf', 12)
    font = ImageFont.truetype(os.path.join(scriptDir, 'data', 'mister','DejaVuSans.ttf'), 12)
    text = text.replace('\n', NEWLINE_REPLACEMENT_STRING)

    img = Image.new("RGB", (640, 480), bgcolor)
    draw = ImageDraw.Draw(img)
    # Paste cover in the top right corner
    coverImg = Image.open(os.path.join(cover))
    coverWidth, coverHeight = coverImg.size
    ratio = float(coverHeight) / float(coverWidth)
    newHeight = int(ratio * float(imageWidth))
    img.paste(coverImg.resize((imageWidth, newHeight), Image.ANTIALIAS), (textWidth - padding, padding))

    lines = []
    line = u""
    line_height = font.getsize(text)[1]
    text_height = 0
    for word in text.split():
        if word == REPLACEMENT_CHARACTER:  # give a blank line
            lines.append(line[1:])  # slice the white space in the begining of the line
            line = u""
            lines.append(u"")  # the blank line
            text_height = text_height + line_height
            # Change the text width when we are below coevr height + padding
            if text_height >= (newHeight + padding):
                textWidth = 640
        elif font.getsize(line + ' ' + word)[0] <= (textWidth - padding - padding):
            line += ' ' + word
        else:  # start a new line
            lines.append(line[1:])  # slice the white space in the begining of the line
            line = u""
            # Not done: handle too long words at this point
            line += ' ' + word  # for now, assume no word alone can exceed the line width
            text_height = text_height + line_height
            # Change the text width when we are below coevr height + padding
            if text_height >= (newHeight + padding):
                textWidth = 640

    if len(line) != 0:
        lines.append(line[1:])  # add the last line

    y = padding
    for line in lines:
        draw.text((padding, y), line, color, font=font)
        y += line_height

    img.save(generatedImgpath)
