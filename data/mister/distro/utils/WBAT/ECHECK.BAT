@echo off
rem     Check environmental space by assigning 10 strings with length of %1
rem     Supply %1 = any string with length = (required space)/10 - 5
rem     Example: required: 200 bytes, length of %1: 200/10 -5 = 15
rem     If no output, there is enough space; else: batch aborts with msg.

for %%a in (0 1 2 3 4 5 6 7 8 9) do set $E%%a=%1
for %%a in (0 1 2 3 4 5 6 7 8) do set $E%%a=
if (%$E9%)==(%1) goto END
echo  Not enough environmental space!
echo.
echo  Assign more space in Properties of DOS box / Memory
echo  or start new Command shell with /E parameter.
echo.
echo.
wbat box 20,60 help,abort
if not errorlevel 2 wbat list @espace.txt
@echo on
goto nuke batch

:END
set $E9=
