import os.path
import sys
from exogui import ExoGUI
from logger import Logger


if __name__ == "__main__":
    scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
    title = 'eXoConverter 0.9.2-beta'
    logger = Logger()
    logger.log(title)
    logger.log('Script path : '+scriptDir)
    
    gui = ExoGUI(scriptDir,logger, title) 
    gui.draw()
