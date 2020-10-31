ECHO OFF
IF "%2" == "/N" GOTO ACTION
IF "%2" == "/n" GOTO ACTION
CLS
ECHO .
ECHO      Batch file instructions:
ECHO  ษออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
ECHO  บ  To avoid this message, use this syntax:  XRAY.BTM filename.ext /N   บ
ECHO  บ (To configure 4FILES to use this program, type Alt-F10 from 4FILES.) บ
ECHO  วฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤฤถ
ECHO  บ This batch file sends the given file name to the appropriate archive บ
ECHO  บ managing utility (AR, LR, ZR, or ZOR) depending on the extension of  บ
ECHO  บ the archive (ARJ, LZH, ZIP and ZOO respectively).  These utilities   บ
ECHO  บ may be found in XRAYxxx.ZIP on BBSs; they can list, browse and unar- บ
ECHO  บ chived files.  Other archive types (ARC, PAK, DWC, LBR and self-     บ
ECHO  บ extracting archives) are sent to FV.COM, which can list, but not     บ
ECHO  บ browse or unarchive the files in an archive.                         บ
ECHO  บ                                                                      บ
ECHO  บ FOR FASTER EXECUTION, you will want to modify the program entries    บ
ECHO  บ below to include the complete drive:pathspec, to locate each program บ
ECHO  บ precisely without relying on a PATH search by DOS.                   บ
ECHO  บ                                                                      บ
ECHO  บ ALSO, if you are NOT using Buerg's LIST or the 4DOS LIST, erase the  บ
ECHO  บ "REM" preceding "pause" on the second to last line (to prevent the   บ
ECHO  บ archive data from scrolling off screen).                             บ
ECHO  บ                                                                      บ
ECHO  ศออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
ECHO .
PAUSE

:ACTION
IF "%@EXT[%1]"=="ZIP" GOTO DO-ZRAY
IF "%@EXT[%1]"=="LZH" GOTO DO-LRAY
IF "%@EXT[%1]"=="ARJ" GOTO DO-ARAY
IF "%@EXT[%1]"=="ZOO" GOTO DO-Z00RAY
IF "%@EXT[%1]"=="ARC" GOTO DO-FV
IF "%@EXT[%1]"=="PAK" GOTO DO-FV
IF "%@EXT[%1]"=="DWC" GOTO DO-FV
IF "%@EXT[%1]"=="LBR" GOTO DO-FV
IF "%@EXT[%1]"=="EXE" GOTO DO-FV
GOTO ERROR

:DO-ZRAY
ZR.COM %1

GOTO END

:DO-LRAY
LR.COM %1

GOTO END

:DO-ARAY
AR.COM %1

GOTO END

:DO-ZOORAY
ZOR.COM %1

GOTO END

:DO-FV
FV.COM %1 /p /c
ECHO .
PAUSE

GOTO END

:ERROR

REM PAUSE

:END