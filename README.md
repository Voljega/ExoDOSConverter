# ExoDOSConverter

a custom converter of the ExoDOS collection v4 to several EmulationStation and/or Linux based distributions format : 
 - Recalbox
 - Batocera
 - Retropie
 - OpenDingux (both SimpleMenu / Esoteric flavours) with mapping for RG350
 - MiSTer (in the future)

## ExoDOS

https://www.retro-exo.com

For those of you for which this name doesn't mean anything, ExoDOS Collection is a collection of DOS games and in my opinion the best one as it includes full, correct configuration for all games.
It is based on Launchbox and Windows only though
There's also an ExoDOSWin3x collection for Windows 3.1 games

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

Fully supported distributions are Batocera, Recalbox, Retropie and OpenDingux.

Next step is to add MiSTer compatibility

### LINUX INSTALLATION AND EXECUTION :
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
>Unzip `XODOSMetadata.zip` to the home dir of the collection, this should create a `Images` folder

>Unzip `!DOSmetadata.zip` to the home dir of the collection, this should create a `eXoDOS/Games/!dos folder`

- launch with `./ExoDOSConverter.sh` or `./ExoDOSConverter`

## RG350

For RG350, select the flavor of frontend you are using (either SimpleMenu or Esoteric/GxMenu)
Don't forget to select 'RG350' for the mapper, this will generate the defaut mapping for controls :
 - DPad: directions
 - Select: ESC
 - Start: Enter
 - A: Left Alt
 - B: Space
 - X: Left Control
 - Y: Left Shift
 - L1: n
 - R1: y
 
 Remember that L1 displays the virtual keyboard.
 Power+B activates the mouse on right stick, with L2 and R2 as left and right buttons 

Launch the game by clicking `dosbox.bat` inside the game folder
If the default mappings are practical for the game, modify 'mapper.map' inside the game folder

You can quit dosbox with `Power+Select`

*EDIT Note :* 

The specific nature of dosbox on RG350 doesn't actually allows for custom mapping on a game by game basis, nor does it takes into account the dosbox.cfg for each game.

The only way to do that at the moment seems to modify `dosbox.conf` in `/media/data/local/home/.dosbox/` :

- copy the `mapper.map` of the game into  `/media/data/local/home/.dosbox/`
- edit the line starting with `mapper` and change the mapper name to `mapper.map`
- you can then modify the mapper.map file however you want, but this mapping will be taken into account for all games

I'm still in search of a solution to allow a real custom configuration and mapping for all games on RG350

## Known issues

A few games in eXoDOS v4 have some conversion issues with this tool.

#### The 11th Hour (1995)

The generation autodetects some error but the game actually should run fine.

The `[autoexec]` part of `dosbox.conf` file in the `eXoDOS\Games\!dos\11thHour` of the collection can be fixed like that to pass generation:
```
[autoexec]
mount c .\Games\
@imgmount d ".\Games\11thhour\discs\1.cue" ".\Games\11thhour\discs\2.cue" ".\Games\11thhour\discs\3.cue" ".\Games\11thhour\discs\4.cue" -t iso
cd ..
@c:
@echo off
cls
echo.
echo Press Ctrl-F4 when prompted to switch CD's.
echo.
pause
@call run
exit
```

#### Pim-Pam-Pum (1992)

The archive of the game contains some strange file with a special character at the beginning which seems to be unused by the game.
Unzip the `Pim-Pam-Pum (1992).zip` archive, suppress the file (named eihter `_EC.SAM` or some variation with a special character instead of `_`).
Then recompress folder `PimPam` and rename the zip as `Pim-Pam-Pum (1992).zip`

#### BAT 2 - The Koshan Conspiracy (1992).zip

This floppy version uses the CD of the CD version

The `[autoexec]` part of `dosbox.conf` file in the `eXoDOS\Games\!dos\KCDFlop` of the collection can be fixed like that to pass generation:
```
[autoexec]
cd ..
@cd ..
@mount c .\Games\
@c:
cls
@cd kcdflop
@koshan.com
exit
```

#### Enterprise (1989)

An extra imgmount command is used which shouldn't be here

The `[autoexec]` part of `dosbox.conf` file in the `eXoDOS\Games\!dos\Enterp89` of the collection can be fixed like that to pass generation:
```
[autoexec]
mount c .\Games\Enterp89
c:
@cls
@boot ENTERPRI.IMG -l a
exit
```

#### Zombieville (1997)

The game is fine but the cue file are not properly recognized by the converter
Unzip the `Zombieville (1997).zip` archive, and modify the first lines of the two cue files.
For `Zombieville.Cd1Of2.cue` : `FILE "Zombieville.Cd1Of2.bin" BINARY`  
For `Zombieville.Cd2Of2.cue` : `FILE "Zombieville.Cd2Of2.bin" BINARY`

Then recompress folder `zombvill` and rename the zip as `Zombieville (1997).zip`


#### Das Hexagon-Kartell

Typo in the `dosbox.conf` for the game

The `[autoexec]` part of `dosbox.conf` file in the `eXoDOS\Games\!dos\DasHexag` of the collection can be fixed like that to pass generation:
```
[autoexec]
echo off
mount c .\Games\DasHexag
imgmount d ".\Games\DasHexag\CD\HEXAGON_CD1.iso" ".\Games\DasHexag\CD\HEXAGON_CD2.iso" -t cdrom
c:
@cd HEXAGON
cls
echo.
echo This game spans 2 CDs. Press Ctrl+F4 when prompted to switch to the next disc.
echo.
pause
cls
@call HEXAGON
exit
```


#### Orion Burger (1996) (Linux only)

One of the paths in `dosbox.conf` of the game doesn't use the right case.  
However, the converted game should run fine in DOSBox

The `[autoexec]` part of `dosbox.conf` file in the `eXoDOS\Games\!dos\burger` of the collection can be fixed like that to pass generation:
```
[autoexec]
@mount c .\Games\BURGER
imgmount d .\Games\burger\cd\DBURGER.cue -t cdrom
@c:
cd burger
cls
@call run
exit
```


#### Panoplia: The Full Armor of God (1991) (Linux only)

One of the paths in `dosbox.conf` of the game doesn't use the right case.  
However, the converted game should run fine in DOSBox

The `[autoexec]` part of `dosbox.conf` file in the `eXoDOS\Games\!dos\panoplia` of the collection can be fixed like that to pass generation:
```
[autoexec]
mount c .\Games\Panoplia
imgmount a .\Games\panoplia\floppy\panoplia.ima -t floppy
c:
cd panoplia
@cls
@panoplia
exit
```
