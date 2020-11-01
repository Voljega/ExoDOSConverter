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

TODO:
- import argparse and accept multiple source arguments properly
- search-as-you-type index generation
- "fill to xxMB or xxGB" option, either via alpha, random, or best-fit
- remove duplicate filenames (ie. same file exists in multiple input paths)
"""
import sys
import os
import shutil
import struct
import hashlib
import string


def scantree_files(path):
    # Recursively yield DirEntry objects for given directory
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree_files(entry.path)
        else:
            yield entry


def index(sourceDir, destDir, scriptDir, isDebug, logger):
    distroDir = os.path.join(scriptDir, 'data', 'mister', 'distro')
    filesIDX = distroDir + '/FILES.IDX'
    titlesIDX = distroDir + '/TITLES.IDX'
    filesDir = destDir + '/files/'

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
    """
    Currently, this uses titleid as the short name for simplicity and testing.
    Later versions will use a funging function to generate human-readable
    filenames (ie. "Wizard's Crown (1985)" will become "WIZARDSC", etc.
    (Or maybe just discard vowels, like "WZRDSCRW"?)
    (One unsolved challenge is how to elegantly detect and resolve collisions.)
    """
    translation_table = dict.fromkeys(map(ord, ' [](),.~!@#$%^&*{}:'), None)

    """
    Handle long-to-short collisions by changing the last letter of the filename.
    This allows us up to 35 collisions before we give up.  Back-of-the-napkin
    analysis shows we should never get to that point under normal circumstances,
    but if we do, die and inform the user to complain to the programmer.
    
    BTW: We are forcing letters and numbers in ASCII order instead of incrementing
    the last character because that is less likely to confuse the inquisitive
    end-user who wants to use the 8.3 files manually.  If we incremented the last
    character, we'd have stuff like filename, filenamf, filenamg, (or filenam0,
    filenam1, filenam2) which may imply a relationship between the files that does
    not exist.
    
    BTW2: Filenames can't have any unicode in them to be universally compatible
    with FAT12 filesystems, so we mangle the unicode out of them.
    """

    for idx, longname in enumerate(baseFiles):
        # FAT12 doesn't support unicode - avert thine eyes
        dname = longname.encode('ascii', 'ignore').decode()
        # Truncate basename while keeping extension
        if len(longname) > 12:
            dname = dname.translate(translation_table)[0:8] + longname[-4:]
        dname = str.upper(dname)
        collided = dname
        if isDebug:
            logger.log("  Starting check for " + dname)
        # Do we have a collision?
        if dname in DOSnames:
            for i in string.ascii_uppercase + string.digits:
                dname = longname.translate(translation_table)[0:7] + i + longname[-4:]
                dname = str.upper(dname)
                if dname not in DOSnames:
                    break
            else:
                # If we still have a collision, we need to mangle the name some more
                for i in string.ascii_uppercase + string.digits:
                    for j in string.ascii_uppercase + string.digits:
                        oldname = dname
                        dname = longname.translate(translation_table)[0:6] + i + j + longname[-4:]
                        dname = str.upper(dname)
                        if isDebug:
                            logger.log("    Extra mangling:" + oldname + " to " + dname)
                        if dname not in DOSnames:
                            if isDebug:
                                logger.log("    Success:" + collided + " " + dname)
                            break
                    if dname not in DOSnames:
                        break

        # If we got here, too many collisions (need more code!)
        if dname in DOSnames:
            logger.log("    Namespace collision converting" + longname + " to " + dname)
            logger.log("    Ask the programmer to enhance the collision algorithm.")
            return

        DOSnames.append(dname)

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

    f = open("name_mapping.txt", 'w')
    for idx, shortn in enumerate(DOSnames):
        f.write(shortn + ' ;' + titles[idx] + '\n')
    f.close()

    """
    Copy everything over to the destination.
    Also copy the TDL itself, the index files, tools needed, etc.
    """
    if os.path.exists(filesDir):
        logger.log('  Output directory %s already exists.\nPlease specify a non-existent directory for the destination.' % destDir)
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
