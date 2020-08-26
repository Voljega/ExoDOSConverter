import os.path, sys
from exogui import ExoGUI
from logger import Logger
import util

exoDosDir = r"G:\Romsets\eXoDOS4"
outputDir = r'G:\ExoDOSConverted'

if __name__ == "__main__":
    scriptDir = os.path.abspath(os.path.dirname(sys.argv[0]))
    title = 'ExoDOSConverter 0.1beta'
    logger = Logger()
    logger.log(title)
    logger.log('Script path : '+scriptDir)
        
    cache = util.buildCache(scriptDir,exoDosDir,logger)
    
    gui = ExoGUI(scriptDir,logger, title, cache) 
    gui.draw()    

            
        