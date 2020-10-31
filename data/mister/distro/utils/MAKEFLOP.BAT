echo off

:LOOPSTART
cls
echo You've selected this bootable floppy disk image:
echo .
echo %1
echo .
echo These can only be executed reliably from an actual bootable floppy disk.
echo So let's make one!  This procedure requires a floppy disk for your A: drive
echo that you don't care about erasing.
echo .
ask -l Do you have a blank floppy disk handy?  Hit Y to continue, or N to abort.

if ERRORLEVEL 121 goto WRITEIMAGE
if ERRORLEVEL 110 goto ABORT
REM invalid number? Go back to main menu
goto LOOPSTART

:WRITEIMAGE
echo .
echo Insert your blank floppy disk into drive A: and
pause
formatf a1
img2dsk %1 a:
cls
echo Your floppy disk has now been written with the image file you selected.
echo When you exit the TDL, use CTRL-ALT-DELETE to boot the new floppy disk.
goto FINISHED

:ABORT
echo You chose to abort preparing a floppy disk with the selected image.

:FINISHED
pause
