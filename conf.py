# -*- coding: utf-8 -*-

def cleanString(string) :
    return string.rstrip('\n\r ').lstrip()

def loadConf(confFile) :
    conf = dict()
    
    file = open(confFile,'r',encoding="utf-8")
    for line in file.readlines() :
        if not line.startswith('#') :
            confLine = line.split("=")
            if len(confLine) == 2 :
                conf[cleanString(confLine[0])] = cleanString(confLine[1])
    
    file.close()        
    return conf

