@echo off
pyinstaller --icon=exodosicon.ico --clean -F main.py
copy ".\dist\main.exe" ExoDOSConverter.exe /y