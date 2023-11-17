[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/donate?hosted_button_id=LEAH843NKNG72)

# ExoConverter

A custom converter of the eXoDOS v6, eXoWin3x and C64 Dreams collections to several EmulationStation and/or Linux based distributions format : 
 - Recalbox
 - Batocera
 - Retrobat
 - Retropie
 - Emuelec  
 - OpenDingux (both SimpleMenu / Esoteric flavours) with mapping for RG350
 - MiSTer

## The Tool

The original aim of this tool was to convert any selection of games of the eXoDOS collection to emulationstation / basic dosbox for linux format, so that in can be used on Retropie on any other like minded distribution.
As the project evolved it now covers different collections, distributions and/or formats. 

The conversion should cover the following :
 - conversion of the game to a correct format, including dosbox.cfg and dosbox.bat
 - scrapping of the game metadata, including front boxart, metada and manual
 - when possible, custom or generic controller configuration

The tool is now fully compatible with Windows and Linux, Mac OS should work although some graphic issues may be present
It should be used on a separate computer, not on the system you are targetting.

The conversion now works fine with dosbox-pure, although it doesn't generate zipped games and it might be wise to disable auto mapping.
In the libretro version this can be done by simply changing the focus mode by clicking Scroll Lock on you keyboard


## ExoDOS & ExoWin3x

[Retro-Exo](https://www.retro-exo.com)

eXoDOS and eXoWin3x collections are collections of DOS and Windows 3.1 games and in my opinion the best ones as it includes full, correct configuration for all games.  
It is based on Launchbox and Windows only though

eXoDOS: full support for v6 version (lite version not supported yet), v5 support has been dropped  
eXoWin3x: full support for v2

If you use eXoDOS Lite version, games you wish to convert will be downloaded on the fly if needed, using direct download from The Eye or download through torrent (much slower)

Before using this tool, don't forget to install the collections (eXoDOS full and lite V5 versions, or eXoWin3x) with their respective `setup.bat`

They should be installed separately and not combined/merged, or the tool will not work.

## C64 Dreams

[C64 Dreams](https://forums.launchbox-app.com/topic/49324-c64-dreams-massive-curated-c64-collection/)

C64 Dreams is a carefully crafted collection of C64 Games, based on Launchbox and Windows only too.

C64 Dreams: support for v0.60 (custom mapping files not supported yet)

Support is prelimilary, but it's fully functional

Mostly missing is the conversion of keyboard to joystick mapping files (whi I hope to implement later)

UI is not fully adapted yet, most extra parameters will do nothing foe this collection generation 

## Anti-virus false positives

Some antiviruses (like Windows Defender) might detect the released exe version as false postive.  
This is due to the exe python packager `pyInstaller` and it's safe to exclude the tool from virus detection 

## State of development

For now the tool is in beta stage, it seems to work fine, but some games throw errors when beeing converted.  
This will be corrected when possible

Fully supported (but not always tested) distributions are Batocera, Recalbox, Retropie, Emuelec, Retrobat, MiSTeR and OpenDingux.

MiSTer compatibility is still beeing worked on at the moment but is already at a pretty advanced stage, espeically for DOS games.

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

Before using the tool, install the collection by executing `setup.bat`

## Expert mode

see [wiki page](https://github.com/Voljega/ExoDOSConverter/wiki/Expert-mode)

### MiSTeR

see [wiki page](https://github.com/Voljega/ExoDOSConverter/wiki/MiSTeR-AO486-support)

## RG350

see [wiki page](https://github.com/Voljega/ExoDOSConverter/wiki/RG350-support)

## Known issues

A few games in both collections have some conversion issues with this tool.  
For eXoDOS v5 issues (not updated for v6), see [wiki page](https://github.com/Voljega/ExoDOSConverter/wiki/Known-issues:-eXoDOS-v5)
For eXoWin3x v2 issues, see [wiki page](https://github.com/Voljega/ExoDOSConverter/wiki/Known-issues:-eXoWin3x-v2)
For C64 Dreams v0.60 issues, see [wiki page](https://github.com/Voljega/ExoDOSConverter/wiki/Known-Issues:-C64-Dreams)
  
  
### Licences, shoutouts

eXoConverter uses python code from [MobyGamer's Total DOS Launcher](https://github.com/MobyGamer/total-dos-launcher)

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/donate?hosted_button_id=LEAH843NKNG72)
