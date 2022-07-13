import queue
import re


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
            #no reason we can't have two \r incase its missing
            print(msg.rstrip('\n'), end='\r')

    #log a subprocess call
    def logProcess(self, process):
        # some Process use ANSI color control characters,
        # they are not that neccesary and would need a re-work of logger to show
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        with process:
            if process.stdout:
                for line in process.stdout:
                    # TODO used for torrent but too verbose, try to better it, see what was done with regular downloads to overwrite same line
                    line = line.strip()
                    if line != "":
                        line = ansi_escape.sub('', line)
                        if line.startswith("[") and line.endswith("]"):
                            self.log("    " + line, replaceLine=True)
                        else:
                            self.log("    " + line)
            if process.stderr:
                for line in process.stderr:
                    self.log("  " + line,self.ERROR)