# ExoDOSConverter

a custom converter of the ExoDOS collection v4 to several EmulationStation and/or Linux based distributions format : 
 - Recalbox
 - Batocera
 - Retropie
 - OpenDingux
 - MiSTer (in the future)

## ExoDOS

https://www.retro-exo.com

For those of you for which this name doesn't mean anything, ExoDOS Collection is a collection of DOS games and in my opinion the best one as it includes full, correct configuration for all games.
It is based on Launchbox and Windows only though
There's also an ExoDOSWin3x collection for Windows 3.1 games

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
However it is a conversion / rewrite of a same previous command line tool, which I used in the past to convert a few thousands of games from both ExoDOS and ExoWin3x collection without too much trouble, so it should already be in an ok state

Fully supported distributions are Batocera, Recalbox, Retropie and OpenDingux.

Next step is to add MiSTer compatibility

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
If the default mappings are not enough, modify 'mapper.map' inside the game folder 
