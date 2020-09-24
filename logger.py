# -*- coding: utf-8 -*-

import queue

class Logger() :
    
    def __init__(self) :
        self.log_queue = queue.Queue()
    
    # Print dictionary to logger
    def printDict(self, dictList) :    
        for key in dictList :
            self.log(key+ ' : '+ dictList[key])
    
    # Print list to logger
    def logList(self,desc,list) :
        msg = desc + ": " + ' '.join(list)        
        self.log(msg)
    
    # Print one line msg to logger
    def log(self,msg) :
        self.log_queue.put(msg.rstrip('\n'))
        print(msg.rstrip('\n'))
