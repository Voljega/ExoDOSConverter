import os.path, sys
from exogui import ExoGUI
from logger import Logger

exoDosDir = r"G:\Romsets\eXoDOS4"
outputDir = r'G:\ExoDOSConverted'

if __name__ == "__main__":
    scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
    title = 'eXoDOSConverter 0.4-beta'
    logger = Logger()
    logger.log(title)
    logger.log('Script path : '+scriptDir)
    
    gui = ExoGUI(scriptDir,logger, title) 
    gui.draw()
