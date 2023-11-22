import copy

categoryOrder = ['[sdl]', '[dosbox]', '[render]', '[cpu]', '[mixer]', '[midi]', '[sblaster]', '[gus]', '[speaker]',
                 '[joystick]', '[serial]', '[dos]', '[ipx]']


def loadDosboxConf(dosboxFile, dosboxConf):
    dosboxConfCopy = copy.deepcopy(dosboxConf)
    dosboxConfFile = open(dosboxFile)
    currentCategory = None
    for line in dosboxConfFile.readlines():
        if line.startswith('#'):
            continue
        if line.startswith('[autoexec]'):
            break
        if line.startswith('['):
            currentCategory = line.rstrip(' \n\r')
            if currentCategory not in dosboxConfCopy:
                dosboxConfCopy[currentCategory] = dict()
        else:
            cleanLine = line.rstrip(' \n\r')
            if cleanLine != '':
                keyValue = cleanLine.split('=')
                value = keyValue[1].rstrip(' \n\r').strip(' \n\r')
                if value != '':
                    dosboxConfCopy[currentCategory][keyValue[0].rstrip(' \n\r').strip(' \n\r')] \
                        = keyValue[1].rstrip(' \n\r').strip(' \n\r')

    dosboxConfFile.close()
    return dosboxConfCopy


def writeDosboxConf(path, dosboxConf):
    file = open(path, 'w')
    for category in dosboxConf:
        file.write(category + '\n')
        for key in dosboxConf[category]:
            file.write(key + '=' + dosboxConf[category][key] + '\n')
    file.close()
