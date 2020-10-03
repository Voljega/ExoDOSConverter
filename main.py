import os.path
import sys
from exogui import ExoGUI
from logger import Logger

exoDosDir = r"G:\Romsets\eXoDOS4"
outputDir = r'G:\ExoDOSConverted'

if __name__ == "__main__":
    scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
    title = 'eXoDOSConverter 0.5-beta'
    logger = Logger()
    logger.log(title)
    logger.log('Script path : '+scriptDir)
    
    gui = ExoGUI(scriptDir,logger, title) 
    gui.draw()

# TODO V5 :
# In the launchbox folder v4 had a folder called "eXoDOS". this is now just "eXo"
# So all exo projects can reside there
# Then, under "eXoDOS" there used to be a "Games" folder
# This has been renamed to "eXoDOS".
# As each projects games will get their own folder here
# VoljegaHier à 15:28
# no more !dos/shortgamename thing either ?
# eXoHier à 15:28
# That is there
# Just doesn't appear until you run setup
# It will appear in the eXoDOS folder
