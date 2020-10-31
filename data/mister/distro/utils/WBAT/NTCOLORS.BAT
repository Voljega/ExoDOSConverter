@echo off
goto START

:NT
#                  Colors for Windows NT / 2000                         ^

The WBAT Demo uses light background colors that cannot be activated
by the WBAT program under NT (this only works under Windows 95/98).

If you would like to have soft background colors, go to the CMD box
properties (right click on top frame), and adjust the RGB values for
~bright~ colors and ~normal white~ as follows:

                                red/green/blue

   light green                  192 / 232 / 192


   light brown (yellow)         240 / 216 / 176


   light blue                   184 / 184 / 252


   normal white (grey)          216 / 216 / 216
:

:START
set wtexthi=red on white
wbat cls (black on white) ! text 2,4 @+NTCOLORS.BAT:NT
wbat fill 11,4 (3,70) (black on light green)
wbat fill 14,4 (3,70) (black on light brown)
wbat fill 17,4 (3,70) (black on light blue)
wbat box 21,64 refresh,exit
if not errorlevel 2 goto START
set wtexthi=
wbat cls
