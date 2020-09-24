# ExoDOSConverter

a custom converter of the ExoDOS collection v4 to several emulation station based distribution format : Recalbox, Batocera, Retropie and soon OpenDingux and MiSTer

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

    conversion of the game to a correct format, including dosbox.cfg and dosbox.bat
    scrapping of the game metadata, including front boxart and manuals

As the ExoDOSCollection itself uses a lot of `.bat` script and other Windows-only features, this tool will also be windows only.
This might evolve is some workaround are found to fully exploit this on Linux on other OSes

## State of development

For now the tool is in beta stage, it seems to work fine, but some games throw errors when beeing converted.
However it is a conversion / rewrite of a same previous command line tool, which I used in the past to convert a few thousands of games from both ExoDOS and ExoWin3x collection without too much trouble, so it should already be in an ok state

Fully supported distributions are Batocera and Recalbox.
It should work with OpenDingux too, minus the boxart.

Retropie needs a little work still, and in the future, I will try to add MiSTer compatibility


