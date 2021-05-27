import os

defaultKeys = {'l2': {'type': 'kp', 'description': '1', "key": "1"},
               'r2': {'type': 'kp', 'description': '2', "key": "2"},
               'up': {'type': 'key', 'description': 'Up', 'key': 'up'},
               'down': {'type': 'key', 'description': 'Down', 'key': 'down'},
               'left': {'type': 'key', 'description': 'Left', 'key': 'left'},
               'right': {'type': 'key', 'description': 'Right', 'key': 'right'},
               'select': {'type': 'key', 'description': 'Esc', 'key': 'esc'},
               'start': {'type': 'key', 'description': 'Enter', 'key': 'enter'},
               'a': {'type': 'key', 'description': 'Left Alt', 'key': 'leftalt'},
               'b': {'type': 'key', 'description': 'Left Control', 'key': 'leftctrl'},
               'x': {'type': 'key', 'description': 'Left Shift', 'key': 'leftshift'},
               'y': {'type': 'key', 'description': 'Space', 'key': 'space'},
               'pageup': {"type": "btn", "description": "Left Mouse Click", "key": "left"},
               'pagedown': {"type": "btn", "description": "Right Mouse Click", "key": "right"},
               'l3': {'type': 'key', 'description': 'Y', 'key': 'y'},
               'r3': {'type': 'key', 'description': 'N', 'key': 'n'},
               'hotkey+start': {'type': 'key', 'description': 'Quit emulator', 'key': 'F9+leftctrl'},
               'hotkey+pageup': {'type': 'key', 'description': 'Change CD', 'key': 'F4+leftctrl'}
               }

defaultStickKeys = {'joystick2': {"type": "mouse", "description": "mouse"},
                    'joystick1up': {"type": "key", "description": "Up", "key": "up"},
                    'joystick1down': {"type": "key", "description": "Down", "key": "down"},
                    'joystick1left': {"type": "key", "description": "Left", "key": "left"},
                    'joystick1right': {"type": "key", "description": "Right", "key": "right"}
                    }


# Generates controller mapping
class Mapping:

    def __init__(self, gamesConf, game, localGameOutputDir, conversionConf, logger):
        self.gamesConf = gamesConf
        self.game = game
        self.localGameOutputDir = localGameOutputDir
        self.conversionConf = conversionConf
        self.logger = logger

    def __initGameMapping__(self):
        mappings = dict(defaultKeys)
        if 'mapSticks' in self.conversionConf and self.conversionConf['mapSticks']:
            mappings.update(defaultStickKeys)
        if 'useKeyb2Joypad' in self.conversionConf and self.conversionConf['useKeyb2Joypad'] and self.game in self.gamesConf:
            gameMappings = dict(self.gamesConf[self.game])
            if 'mapSticks' not in self.conversionConf or not self.conversionConf['mapSticks']:
                stickKeys = list(filter(lambda k: 'stick' in k.lower(), gameMappings.keys()))
                for key in stickKeys:
                    del gameMappings[key]
            for key in gameMappings.keys():
                mappings[key] = self.__convertK2JToGeneric__(gameMappings[key])

        return mappings

    def __convertK2JToGeneric__(self, keymapping):
        k2jkey2generickey = { 'lctrl': 'leftctrl', 'lalt': 'leftalt', 'rctrl': 'rightctrl', 'ralt': 'rightalt'}
        genericMapping = dict()
        genericMapping['description'] = keymapping['description']
        genericMapping['key'] = k2jkey2generickey[keymapping['key']] if keymapping['key'] in k2jkey2generickey \
            else keymapping['key']
        genericMapping['type'] = 'key' if keymapping['key'] not in ['0','1','2','3','4','5','6','7','8','9'] else 'kp'

        return genericMapping

    def mapForBatocera(self):
        self.logger.log("    Generate pad2key controller mapping")
        gameMapping = self.__initGameMapping__()
        p2kFile = open(os.path.join(self.localGameOutputDir, 'padto.keys'), 'w', encoding='utf-8')
        p2kFile.write('{\n')
        p2kFile.write('    "actions_player1": [\n')
        nbMappings = len(gameMapping)
        c = 0
        # convert genericMapping to batocera format
        for key in gameMapping.keys():
            keyMapping = gameMapping[key]
            p2kFile.write('        {\n')
            if '+' in key:
                p2kFile.write('            "trigger": [\n')
                p2kFile.write('                "%s",\n' % key.split('+')[0])
                p2kFile.write('                "%s"\n' % key.split('+')[1])
                p2kFile.write('            ],\n')
            else:
                p2kFile.write('            "trigger": "%s",\n' % key)
            # TODO following if/elif/else might be simplified. might.
            if keyMapping['type'] == 'kp':
                p2kFile.write('            "type": "key",\n')
                target = 'key_' + keyMapping['type'] + keyMapping['key']
                p2kFile.write('            "target": "%s",\n' % target.upper())
            elif keyMapping['type'] == 'mouse':
                p2kFile.write('            "type": "mouse",\n')
            elif keyMapping['type'] == 'btn':
                p2kFile.write('            "type": "key",\n')
                target = keyMapping['type'] + '_' + keyMapping['key']
                p2kFile.write('            "target": "%s",\n' % target.upper())
            else:
                p2kFile.write('            "type": "%s",\n' % keyMapping['type'])
                if '+' in keyMapping['key']:
                    p2kFile.write('            "target": [\n')
                    target = 'key_' + keyMapping['key'].split('+')[0]
                    p2kFile.write('                "%s",\n' % target.upper())
                    target = 'key_' + keyMapping['key'].split('+')[1]
                    p2kFile.write('                "%s"\n' % target.upper())
                    p2kFile.write('            ],\n')
                else:
                    target = 'key_' + keyMapping['key']
                    p2kFile.write('            "target": "%s",\n' % target.upper())
            p2kFile.write('            "description": "%s"\n' % keyMapping['description'])
            if c == nbMappings - 1:
                p2kFile.write('        }\n')
            else:
                p2kFile.write('        },\n')
            c = c + 1

        p2kFile.write('    ]\n')
        p2kFile.write('}\n\n')
        p2kFile.close()

