import os


keyTranslations = {'Button 1': 'b', 'Button 2': 'a', 'Button 3': 'y', 'Button 4': 'x', 'Button 5': 'pageup',
                   'Button 6': 'pagedown', 'Button 7': 'l2', 'Button 8': 'l3', 'Start Button': 'start',
                   'Left Thumb': 'l3', 'Right Thumb': 'r3',
                   'DPad up': 'up', 'DPad left': 'left', 'DPad down': 'down', 'DPad right': 'right', 'Right Stick up': 'joystick2up',
                   'Right Stick left': 'joystick2left', 'Right Stick down': 'joystick2down', 'Right Stick right': 'joystick2right',
                   'Select Right Stick left': 'hotkey+joystick2left', 'Select Right Stick down': 'hotkey+joystick2down',
                   'Select Right Stick right': 'hotkey+joystick2right', 'Select Right Stick up': 'hotkey+joystick2up',
                   'Select Left Thumb': 'hotkey+l3', 'Select Right Thumb': 'hotkey+r3'}

# TODO
# separator for the csv fields, added manually when extracting data from the google sheet
# might be better to change it to something else in the future
# also needs to change 'Select RightThumb' column to 'Select Right Thumb'
separator = '$'


# Parses keyb2joypad csv
class Keyb2Joypad:

    def __init__(self, scriptDir, logger):
        self.scriptDir = scriptDir
        self.logger = logger
        self.gamesConf = dict()

    def load(self):
        sourceFile = os.path.join(self.scriptDir, 'data', 'keyb2Joypad.csv')
        columns = []
        keyb2joypadFile = open(sourceFile, 'r', encoding='utf-8')
        for line in keyb2joypadFile.readlines():
            confLine = line.rstrip(' \n\r').split("$")
            if confLine[0] == 'eXoID':  # first line
                columns = confLine
            else:
                game = self.get(confLine, columns, 'Game')
                conf = dict()
                # Select used as hotkey 'mod3'
                # 'Button 1' to 'Button 8' and 'Start Button', 'Left Thumb' 'Right Thumb' Stick Clicks
                # 1 -> South (B), 2-> East (A), 3 -> West (Y), 4 -> North (X)
                for button in ['Button 1', 'Button 2', 'Button 3', 'Button 4', 'Button 5', 'Button 6', 'Button 7',
                               'Button 8', 'Start Button', 'Left Thumb', 'Right Thumb']:
                    self.extractCtrlButtonConf(self.getValues(confLine, columns, button), conf, button)
                # 'DPad up' etc
                for dpadDir in ['DPad up', 'DPad left', 'DPad down', 'DPad right']:
                    self.extractCtrlButtonConf(self.getValues(confLine, columns, dpadDir), conf, dpadDir)
                # 'Right Stick up' etc
                for rightStickDir in ['Right Stick up', 'Right Stick left', 'Right Stick down', 'Right Stick right']:
                    self.extractCtrlButtonConf(self.getValues(confLine, columns, rightStickDir), conf, rightStickDir)
                # 'Select Right Stick up' etc Right Stick Hotkeys
                for rightStickHotkey in ['Select Right Stick up', 'Select Right Stick left', 'Select Right Stick down',
                                         'Select Right Stick right']:
                    self.extractCtrlButtonConf(self.getValues(confLine, columns, rightStickHotkey), conf, rightStickHotkey)
                # 'Select Left Thumb' 'Select Right Thumb' Stick Click Hotkeys
                for stickClickHotkey in ['Select Left Thumb', 'Select Right Thumb']:
                    self.extractCtrlButtonConf(self.getValues(confLine, columns, stickClickHotkey), conf, stickClickHotkey)

                self.gamesConf[game] = conf

        keyb2joypadFile.close()
        self.logger.log('Loaded %i games keyb2joypad configurations' % len(self.gamesConf.keys()))
        return self.gamesConf

    @staticmethod
    def get(conf, columns, value):
        return conf[columns.index(value)].strip().rstrip(' \n\r')

    @staticmethod
    def getValues(conf, columns, values):
        return list(map(lambda b: b.strip().rstrip(' \n\r'), conf[columns.index(values)].split(':')))

    @staticmethod
    def extractCtrlButtonConf(buttonCellValues, conf, button):
        if not Keyb2Joypad.emptyList(buttonCellValues):
            conf[keyTranslations[button]] = {'description': buttonCellValues[0], 'key': buttonCellValues[-1]}

    @staticmethod
    def emptyList(values):
        return len(values) == 0 or (len(values) == 1 and values[0] == '')