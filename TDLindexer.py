"""
The TDL indexer discovers all of the files in/under the provided source
directory and builds a list of all of the filenames.  It then uses this
list to perform the following:
- Derive DOS-friendly filenames from the discovered files
- Copy the discovered files to the destination directory provided, using the DOS-friendly filenames as the destination filenames
- Build indexes that allow the DOS TDL to work faster.

For more information on the index file formats this tool generates, consult
index_formats.txt.

This is my very first Python project.  All mockery and jeers can be
directed to trixter@oldskool.org, although it would be more helpful
to the project if you could fix my novice coding and make this program better.

"""
import sys
import os
import shutil
import struct
import hashlib
import re
from zipfile import ZipFile


def scantree_files(path):
    # Recursively yield DirEntry objects for given directory
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree_files(entry.path)
        else:
            yield entry


# Cleans filenames for safer matching
def clean_name(name):
    # Replace any number of spaces with _
    name = re.sub(r'\s+', '_', name)
    # Allow letters, numbers, and meaningful punctuation
    return re.sub(r'[^a-zA-Z0-9_!$]', '', name)


def index(outputDir, scriptDir, fullnameToGameDir, isDebug, preExtractGames, logger):
    sourceDir = os.path.join(outputDir, 'games')
    destDir = os.path.join(outputDir, 'tdlprocessed')
    gamesDataTempDir = os.path.join(outputDir, 'games-data')
    distroDir = os.path.join(scriptDir, 'data', 'mister', 'distro')
    filesIDX = distroDir + '/FILES.IDX'
    titlesIDX = distroDir + '/TITLES.IDX'
    filesDir = destDir + '/files/'

    if not os.path.exists(distroDir):
        with ZipFile(os.path.join(scriptDir, 'data', 'mister', 'distro.zip'), 'r') as zipFile:
            # Extract distro (compressed to preserve file handlings)
            logger.log("  unzipping distro.zip")
            zipFile.extractall(path=os.path.join(scriptDir, 'data', 'mister'))

    sourceFiles = []  # Source filenames with full paths and extensions (sorted)
    baseFiles = []  # Source filenames with extensions (no paths)
    titles = []  # Source filenames without paths or extensions
    DOSnames = []  # titles() converted to 8.3-friendly DOS names

    foundfiles = list(scantree_files(sourceDir))

    if isDebug:
        logger.log("  Indexing %i files" % len(foundfiles))

    if len(foundfiles) > 32767:
        logger.log("  Fatal: Current design of DOS TDL does not support more than 32767 files.", logger.ERROR)
        return

    if len(foundfiles) > 16383:
        logger.log('  Warning: This many files may cause the DOS TDL to operate slower than normal\n'
                   '  due to the titles index not being able to be cached in memory.  TDL will still\n'
                   '  run, but might require a very fast I/O device for acceptable speed.', logger.WARNING)

    # Sort discovered files by their filename, case insensitive.  Additional
    # sort criteria may be added in the future, but I lack the skills to do so,
    # someone please help me!  Ideally I would like add an option to sort
    # on something that can be regex'd, like (1983) or [Adventure].

    sfoundfiles = sorted(foundfiles, key=lambda dirent: dirent.name.lower())

    for entry in sfoundfiles:
        sourceFiles.append(entry.path)
        fname = entry.name
        baseFiles.append(fname)
        tmptitle = fname.rsplit(sep='.', maxsplit=1)[0]
        tmptitle = tmptitle.encode('ascii', 'backslashreplace').decode()
        titles.append(tmptitle)

    # if isDebug:
    #     logger.log("  First 5 files found were:")
    #     logger.log(baseFiles[0:5] + "\n")
    #     logger.log("  First 5 titles found were:")
    #     logger.log(titles[0:5] + "\n")
    #     # logger.log ("Last 5 files found were:")
    #     # logger.log(baseFiles[-5:],"\n")
    #     # logger.log ("Last 5 titles found were:")
    #     # logger.log(titles[-5:],"\n")

    logger.log("  Converting to DOS-friendly 8.3 filenames")
    dosNameToLongname = dict()
    for idx, longname in enumerate(baseFiles):
        base_name = longname.replace('.zip', '')
        if base_name.startswith('('):
            # For 'custom' files starting with -, we just remove all the bits of the filename that aren't
            # valid DOS chars. We assume there won't be any conflicts here.
            cleaned_name = '(' + re.sub(r'[^a-zA-Z0-9]', '', base_name).upper()
            if len(cleaned_name) > 8:
                cleaned_name = cleaned_name[0:8]
            DOSnames.append(f"{cleaned_name}.ZIP")
            dosNameToLongname[f"{cleaned_name}.ZIP"] = longname
        else:
            if base_name not in fullnameToGameDir:
                logger.log("    Unknown game %s no corresponding shortname found" % longname, logger.ERROR)
            else:
                dname = fullnameToGameDir[base_name].upper()
                DOSnames.append(f"{dname}.ZIP")
                dosNameToLongname[f"{dname}.ZIP"] = longname

        # DOSnames.append(dname)
        # dosNameToLongname[dname] = longname

    # if isDebug:
    #     logger.log("  first 5 DOS-friendly filenames are:")
    #     logger.log("  " + DOSnames[0:5] + "\n")
    #     logger.log("  Last 5 DOS-friendly filenames are:")
    #     logger.log(" " + DOSnames[-5:] + "\n")

    # refer to index_formats.txt for info on what is being generated for all the index files, and why
    logger.log("  Generating files index...")
    f = open(filesIDX, 'wb')
    f.write(struct.pack('<H', len(DOSnames)))
    for idx, fname in enumerate(DOSnames):
        f.write(struct.pack('<H', idx))
        f.write(str.encode(fname[0:12].ljust(12, "\x00")))
    f.close()

    # Need to generate this index:
    """
    Title Index format (from index_formats.txt):
    
            numEntries:     16-bit word of how many titles we have available
    REPEAT  (This structure repeats numEntries times)
            titleOfs:       32-bit word of offset where each variable-length
                            record starts
    END
    REPEAT  (This structure repeats numEntries times)
            titleID:        16-bit word
            titleHash:      16 bytes of the MD5 hash of the title string
        titleLen:	1 byte of length of title string
        titleStr:	titleLen characters of title string
    END
    """
    # This index generation method is fugly -- avert thine eyes
    # There is likely a very elegant way to do this using tuples or something
    # but this is my first python program so I'll figure it out later

    logger.log("  Generating titles index...")
    f = open(titlesIDX, 'wb')
    f.write(struct.pack('<H', len(titles)))
    # build list of offsets
    toffsets = []
    curofs = 2 + (len(titles) * 4)  # real starting offset is past the offset structure itself
    for tlen in titles:
        toffsets.append(curofs)
        curofs = curofs + (2 + 16 + 1 + len(tlen))
    # dump offsets to index file
    for tmpofs in toffsets:
        f.write(struct.pack('<L', tmpofs))
    for idx, name in enumerate(titles):
        # write titleID
        f.write(struct.pack('<H', idx))
        # write titleHash
        thash = hashlib.md5(name.encode()).digest()
        f.write(thash)
        # write titleLen
        f.write(struct.pack('B', len(name)))
        # write title itself
        f.write(name.encode())
    f.close()

    # Create mapping table so the user can weed things out and try again.
    # For example, it would be a good idea to not put any "porn" or "adult"
    # games on a system at a show/convention or out on the museum floor.

    f = open("name_mapping.txt", 'w', newline='\r\n')
    for idx, shortn in enumerate(DOSnames):
        f.write(shortn + ' ;' + titles[idx] + '\n')
    f.close()

    """
    Copy everything over to the destination.
    Also copy the TDL itself, the index files, tools needed, etc.
    """
    if os.path.exists(filesDir):
        logger.log(
            '  Output directory %s already exists.\nPlease specify a non-existent directory for the destination.' % destDir)
        sys.exit(1)
    logger.log("  Copying games zip from " + sourceDir + " to " + destDir + ", this might take a while...")
    shutil.copytree(distroDir, destDir)
    if not os.path.exists(filesDir):
        os.makedirs(filesDir)

    # Copy source:longfilenames to destination:shortfilenames
    for i in range(len(DOSnames)):
        if isDebug:
            logger.log("    " + DOSnames[i])
        shutil.copy(sourceFiles[i], filesDir + DOSnames[i])

    logger.log("  All games indexed")

    # Create sub games dir
    os.mkdir(os.path.join(destDir, 'games'))

    # Handle pre extract case
    if preExtractGames:
        # Move content of games/game.pc dir to destDir/games
        for dosZipName in dosNameToLongname:
            if dosZipName not in ['(MANUALL.ZIP', '(UTILITI.ZIP']:
                longCleanName = dosNameToLongname[dosZipName]
                gameDataDir = os.path.join(gamesDataTempDir, os.path.splitext(longCleanName)[0])
                if os.path.exists(gameDataDir):
                    # preExtractFolder = os.path.join(destDir, 'games', os.path.splitext(dosZipName)[0])
                    shutil.move(gameDataDir, os.path.join(destDir, 'games', os.path.splitext(dosZipName)[0]))
                else:
                    logger.log('  Pre-extracted game data no found for %s / %s'
                               % (dosZipName, dosNameToLongname[dosZipName]), logger.ERROR)
            else:
                os.mkdir(os.path.join(destDir, 'games', os.path.splitext(dosZipName)[0]))
                with ZipFile(os.path.join(destDir, 'files', dosZipName), 'r') as zipFile:
                    zipFile.extractall(path=os.path.join(destDir, 'games', os.path.splitext(dosZipName)[0]))

        # delete game-data
        shutil.rmtree(gamesDataTempDir)
