@echo off
set /p "version=Version number: "
echo .
echo Clean build directory content
rd /s /q .\build
if exist .\build rd /s /q .\build
if not exist .\build mkdir .\build
cd build
echo Copy build files
copy ..\*.py .
copy ..\*.ico .
echo .
echo .
echo Build with pyinstaller
echo .
pyinstaller --icon=exodosicon.ico --clean -F main.py
echo .
echo Pyinstaller has ended its work
echo .
echo Clean build directory
del *.py
move *.ico .\dist
del *.spec
rd /s /q .\build
if exist .\build rd /s /q .\build
echo Moving conf files
if not exist .\dist\data mkdir .\dist\data
copy ..\data\*.* .\dist\data
if not exist .\dist\data\mister mkdir .\dist\data\mister
copy ..\data\mister\*.* .\dist\data\mister
if not exist .\dist\conf mkdir .\dist\conf
copy ..\conf\*.conf .\dist\conf
if not exist .\dist\GUI mkdir .\dist\GUI
copy ..\GUI\*.* .\dist\GUI
copy ..\*.md .\dist
copy ..\*.sh .\dist
copy ..\changelog.txt \dist
echo .
echo Rename exec and dir
ren .\dist\main.exe eXoConverter-%version%.exe
ren .\dist eXoConverter-%version%
cd ..
echo Finished building version %version%