# -*- coding: utf-8 -*-

import queue

class Logger() :
    
    def __init__(self) :
        self.log_queue = queue.Queue()
    
    def printDict(self, dictList) :    
        for key in dictList :
            self.log(key+ ' : '+ dictList[key])
            
    def logList(self,desc,list) :
        msg = desc + ": " + ' '.join(list)        
        self.log(msg)
            
    def log(self,msg) :
        self.log_queue.put(msg.rstrip('\n'))
        print(msg.rstrip('\n'))
