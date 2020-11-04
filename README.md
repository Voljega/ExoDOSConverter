# ExoDOSConverter

a custom converter of the ExoDOS collection v5 to several EmulationStation and/or Linux based distributions format : 
 - Recalbox
 - Batocera
 - Retropie
 - OpenDingux (both SimpleMenu / Esoteric flavours) with mapping for RG350
 - MiSTer (in the future)

## ExoDOS

https://www.retro-exo.com

For those of you for which this name doesn't mean anything, ExoDOS Collection is a collection of DOS games and in my opinion the best one as it includes full, correct configuration for all games.
It is based on Launchbox and Windows only though
The collection is supported in its V5 full version only, V4 support has been dropped
Lite version will be likely supported later with Download on demand implemented in the converter, if it's feasible
There's also an ExoDOSWin3x collection for Windows 3.1 games, version 2 of which will be supported when it's released

Before using this tool, don't forget to install the collection with its `setup.bat`

## The Tool

ExoDOSConverter is a rework with GUI of an old project of mine, and the aim is to fully support ExoDOS v5 and ExoWin3x v2 when they are released.
For now the tool works with current versions of the collection

The aim of this tool is to convert any selection of games of the ExoDOS collection to emulationstation / basic dosbox for linux format, so that in can be used on Retropie on any other like minded distribution.

The conversion should cover the following :
 - conversion of the game to a correct format, including dosbox.cfg and dosbox.bat
 - scrapping of the game metadata, including front boxart and manuals

As the ExoDOSCollection itself uses a lot of `.bat` script and other Windows-only features, this tool will also be windows only.
This might evolve is some workaround are found to fully exploit this on Linux on other OSes

## State of development

For now the tool is in beta stage, it seems to work fine, but some games throw errors when beeing converted.
This will be corrected when possible

Fully supported distributions are Batocera, Recalbox, Retropie, Emuelec, Retrobat and OpenDingux.

MiSTer compatibility is beeing worked one at the moment

### Linux/MacOS installation and execution :
- eXoDOSConverter requires that python3 is installed (it's developed on 3.8)
- first install Tkinter for python3 if needed : `sudo apt-get install python3-tk`
- directly download sources or clone the repo with :
 ```
 sudo apt install git # optional, only if git is not installed
 git clone https://github.com/Voljega/ExoDOSConverter
 ```
- give execution rights to `ExoDOSConverter.sh` :
```
cd ExoDOSConverter            # change to ExoDOSConverter directory
chmod u+x ExoDOSConverter.sh  # give execution perms (already done in git-cloned version)
```
- If you didn't install the collection beforehand on Windows or with wine by executing `setup.bat`, you'll need to do that or  alternatively:
>Unzip `.Content/XODOSMetadata.zip` to the home dir of the collection, this should create `Images` and `xml` folder

>Unzip `.Content/!DOSmetadata.zip` to the home dir of the collection, this should create a `eXoDOS/Games/!dos folder`

- launch with `./ExoDOSConverter.sh` or `./ExoDOSConverter`

### Windows installation and execution :

Either use the latest [release](https://github.com/Voljega/ExoDOSConverter/releases) or you can build your own version using one of these two options :
- @flynnsbit [tutorial video](https://www.youtube.com/watch?v=wW2yhrw9Jp0&lc=UgzkMKahMRjhABX4FhN4AaABAg)
- read the `build.txt` to build your own version

## Expert mode

see [wiki page](https://github.com/Voljega/ExoDOSConverter/wiki/Expert-mode)

### MiSTeR

see [wiki page](https://github.com/Voljega/ExoDOSConverter/wiki/MiSTeR-AO486-support)

## RG350

see [wiki page](https://github.com/Voljega/ExoDOSConverter/wiki/RG350-support)

## Know issues

A few games in eXoDOS v5 have some conversion issues with this tool.  
see [wiki page](https://github.com/Voljega/ExoDOSConverter/wiki/Known-issues)