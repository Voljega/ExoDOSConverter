# -*- coding: utf-8 -*-

import queue


class Logger:
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFO = 'INFO'

    def __init__(self):
        self.log_queue = queue.Queue()

    # Print dictionary to logger
    def printDict(self, dictList, level=INFO):
        for key in dictList:
            self.log(key + ' : ' + dictList[key], level)

    # Print list to logger
    def logList(self, desc, msgList, level=INFO):
        msg = desc + ": " + ' '.join(msgList)
        self.log(msg, level)

    # Print one line msg to logger
    def log(self, msg, level=INFO, replaceLine=False):
        self.log_queue.put([level, replaceLine, msg.rstrip('\n').strip('\r')])
        if not replaceLine:
            print(msg.rstrip('\n'))
        else:
            print(msg.rstrip('\n'), end='')
