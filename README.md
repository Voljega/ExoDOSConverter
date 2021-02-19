[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate?hosted_button_id=LEAH843NKNG72)

# ExoConverter

A custom converter of the eXoDOS v5 and eXoWin3x collections to several EmulationStation and/or Linux based distributions format : 
 - Recalbox
 - Batocera
 - Retrobat
 - Retropie
 - Emuelec  
 - OpenDingux (both SimpleMenu / Esoteric flavours) with mapping for RG350
 - MiSTer

## ExoDOS & ExoWin3x

https://www.retro-exo.com

eXoDOS and eXoWin3x collections are collections of DOS and Windows 3.1 games and in my opinion the best ones as it includes full, correct configuration for all games.
It is based on Launchbox and Windows only though

eXoDOS supported in its V5 full and lite versions only for eXoDOS, V4 support has been dropped
eXOWin3x is supported in its latest V2 version.

If you use eXoDOS Lite version, games you wish to convert will be downloaded on the fly if needed, using direct download from The Eye

There's also an ExoDOSWin3x collection for Windows 3.1 games, version 2 of which will be supported when it's released

Before using this tool, don't forget to install the collections (eXoDOS full and lite V5 versions, or eXoWin3x) with theuir respective `setup.bat`

## The Tool

The original aim of this tool was to convert any selection of games of the eXoDOS collection to emulationstation / basic dosbox for linux format, so that in can be used on Retropie on any other like minded distribution.
As the project evolved it now covers diffrent distributions and/or formats. 

The conversion should cover the following :
 - conversion of the game to a correct format, including dosbox.cfg and dosbox.bat
 - scrapping of the game metadata, including front boxart, metada and manual

The tool is now fully compatible with Windows and Linux, Mac OS should work although some graphic issues may be present

## Anti-virus false positives

Some antiviruses (like Windows Defender) might detect the released exe version as false postive.  
This is due to the exe python packager `pyInstaller` and it's safe to exclude the tool from virus detection 

## State of development

For now the tool is in beta stage, it seems to work fine, but some games throw errors when beeing converted.
This will be corrected when possible

Fully supported distributions are Batocera, Recalbox, Retropie, Emuelec, Retrobat, MiSTeR and OpenDingux.

MiSTer compatibility is still beeing worked on at the moment and is already at a pretty advanced stage.

### Linux/MacOS installation and execution :
- eXoDOSConverter requires that python3 is installed (it's developed on 3.8)
- first install Tkinter for python3 if needed : `sudo apt-get install python3-tk`
- you might need to install pillow : `pip install pillow`
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
>Unzip `./Content/XODOSMetadata.zip` to the home dir of the collection, this should create `./Images` and `./xml` folder

>Unzip `./Content/!DOSmetadata.zip` to the home dir of the collection, this should create a `./eXo/eXoDOS/!dos folder`

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
  
  
### Licences, shoutouts

eXoConverter uses python code from [MobyGamer's Total DOS Launcher](https://github.com/MobyGamer/total-dos-launcher)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=LEAH843NKNG72)
