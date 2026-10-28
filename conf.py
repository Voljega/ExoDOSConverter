import os


def cleanString(string):
    return string.rstrip('\n\r ').lstrip()


# GUI string ids that are not configuration values
NON_CONF_KEYS = ['verify', 'save', 'proceed', 'confirm', 'left', 'right', 'leftList', 'rightList', 'filter',
                 'selectall', 'unselectall', 'loadCustom', 'saveCustom', 'selectOutputDir', 'selectCollectionDir',
                 'selectSelectionPath', 'converterSettings', 'dosboxBasicSettings', 'dosboxExpertSettings']
# Defaults other than an empty value
DEFAULT_VALUES = {'collectionVersion': 'eXoDOS v6', 'conversionType': 'Batocera', 'genreSubFolders': '1',
                  'mapper': 'None', 'useKeyb2Joypad': '0', 'mapSticks': '0', 'longGameFolder': '0',
                  'downloadOnDemand': '0', 'preExtractGames': '0', 'dosboxPureZip': '0', 'debugMode': '0',
                  'expertMode': '0', 'mountPrefix': './', 'fullresolutionCfg': 'desktop', 'rendererCfg': 'auto',
                  'outputCfg': 'texture', 'vsyncCfg': '0'}


def defaultConf(guiStrings):
    return {key: DEFAULT_VALUES.get(key, '') for key in guiStrings if key not in NON_CONF_KEYS}


def loadConf(confFile, guiStrings):
    """Load confFile over the defaults of the given GUI strings, a missing file gives the defaults only"""
    conf = defaultConf(guiStrings)
    if not os.path.exists(confFile):
        return conf

    file = open(confFile,'r',encoding="utf-8")
    for line in file.readlines():
        if not line.startswith('#'):
            confLine = line.split("=")
            if len(confLine) == 2:
                conf[cleanString(confLine[0])] = cleanString(confLine[1])

    file.close()
    return conf


def loadSettings(confFile):
    """Load the settings of the application itself, a missing file gives no settings"""
    return loadConf(confFile, dict())


def saveSettings(confFile, settings):
    """Write the key = value settings of the application itself, not of a set"""
    os.makedirs(os.path.dirname(confFile), exist_ok=True)
    file = open(confFile, 'w', encoding="utf-8")
    for key, value in settings.items():
        file.write(key + ' = ' + value + '\n')
    file.close()
