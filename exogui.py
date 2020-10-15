import tkinter as Tk
from tkinter import ttk, messagebox
from operator import attrgetter
import tkinter.font as Font
import wckToolTips
import conf, util
import os, shutil, platform
from exodosconverter import ExoDOSConverter
import _thread


# Main GUI
class ExoGUI:
    DEFAULT_FONT_SIZE = 9

    def __init__(self, scriptDir, logger, title):
        self.scriptDir = scriptDir
        self.setKey = 'exo'
        self.cache = None
        self.needsCacheRefresh = False
        self.loading = True
        # TODO create conf file from guiStrings if it doesn't exist and do not ship it with tool anymore 
        self.configuration = conf.loadConf(
            os.path.join(self.scriptDir, util.confDir, util.getConfFilename(self.setKey)))
        self.guiVars = dict()
        self.guiStrings = util.loadUIStrings(self.scriptDir, util.getGuiStringsFilename(self.setKey))
        # TODO will need to reload that when changing version
        self.fullnameToGameDir = util.fullnameToGameDir(scriptDir)

        self.window = Tk.Tk()
        self.window.resizable(False, False)
        self.startFontSize = self.DEFAULT_FONT_SIZE

        if platform.system() == 'Windows':
            self.window.iconbitmap('exodosicon.ico')

        self.setFontSize(self.startFontSize)
        self.window.title(title)
        self.logger = logger

    def draw(self):
        self.root = Tk.Frame(self.window, padx=10, pady=5)
        self.root.grid(column=0, row=0)
        self.drawMainframe()
        self.window.mainloop()

    def setFontSize(self, value):
        default_font = Font.nametofont("TkDefaultFont")
        default_font.configure(size=value)
        text_font = Font.nametofont("TkTextFont")
        text_font.configure(size=value)
        fixed_font = Font.nametofont("TkFixedFont")
        fixed_font.configure(size=value)

    # Main mama Frame    
    def drawMainframe(self):
        self.mainFrame = Tk.Frame(self.root, padx=10, pady=0)
        self.mainFrame.grid(column=0, row=1, sticky="EW", pady=5)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        self.drawPathsFrame()
        self.drawConfigurationFrame()
        self.drawSelectionFrame()
        self.drawButtonsFrame()
        self.drawConsole()

    # Paths frame    
    def drawPathsFrame(self):
        self.pathsFrame = Tk.LabelFrame(self.mainFrame, text="Your Paths", padx=10, pady=5)
        self.pathsFrame.grid(column=0, row=0, sticky="EW", pady=5)
        self.pathsFrame.grid_columnconfigure(1, weight=1)
        setRow = 0

        label = Tk.Label(self.pathsFrame, text=self.guiStrings['collectionDir'].label)
        wckToolTips.register(label, self.guiStrings['collectionDir'].help)
        label.grid(column=0, row=setRow, padx=5, sticky="W")
        self.guiVars['collectionDir'] = Tk.StringVar()
        self.guiVars['collectionDir'].set(self.configuration['collectionDir'])
        self.guiVars['collectionDir'].trace_add("write", self.handleCollectionFolder)
        self.collectionEntry = Tk.Entry(self.pathsFrame, textvariable=self.guiVars['collectionDir'])
        self.collectionEntry.grid(column=1, row=setRow, padx=5, sticky=("WE"))
        setRow = setRow + 1

        outputDirLabel = Tk.Label(self.pathsFrame, text=self.guiStrings['outputDir'].label)
        wckToolTips.register(outputDirLabel, self.guiStrings['outputDir'].help)
        outputDirLabel.grid(column=0, row=setRow, padx=5, sticky=(Tk.W))
        self.guiVars['outputDir'] = Tk.StringVar()
        self.guiVars['outputDir'].set(self.configuration['outputDir'])
        self.outputEntry = Tk.Entry(self.pathsFrame, textvariable=self.guiVars['outputDir'])
        self.outputEntry.grid(column=1, row=setRow, columnspan=5, padx=5, sticky="WE")

    # Configuration Frame    
    def drawConfigurationFrame(self):
        self.configurationFrame = Tk.LabelFrame(self.mainFrame, text="Configuration", padx=10, pady=5)
        self.configurationFrame.grid(column=0, row=1, sticky="EW", pady=5)
        self.configurationFrame.columnconfigure(0, weight=1)

        # Collection parameters
        self.collectionFrame = Tk.Frame(self.configurationFrame)
        self.collectionFrame.grid(column=0, row=0, padx=5, sticky="EW")
        self.conversionTypeLabel = Tk.Label(self.collectionFrame, text=self.guiStrings['conversionType'].label)
        wckToolTips.register(self.conversionTypeLabel, self.guiStrings['conversionType'].help)
        self.conversionTypeLabel.grid(column=0, row=0, sticky="W", pady=5)
        self.guiVars['conversionType'] = Tk.StringVar()
        self.guiVars['conversionType'].set(self.configuration['conversionType'])
        self.conversionTypeComboBox = ttk.Combobox(self.collectionFrame, state="readonly",
                                                   textvariable=self.guiVars['conversionType'])
        self.conversionTypeComboBox.grid(column=1, row=0, sticky="W", pady=5, padx=5)
        self.conversionTypeValues = util.conversionTypes.copy()
        self.conversionTypeComboBox['values'] = self.conversionTypeValues

        self.exodosVersionLabel = Tk.Label(self.collectionFrame, text=self.guiStrings['exodosVersion'].label)
        wckToolTips.register(self.exodosVersionLabel, self.guiStrings['exodosVersion'].help)
        self.exodosVersionLabel.grid(column=2, row=0, sticky="W", pady=5)
        self.guiVars['exodosVersion'] = Tk.StringVar()
        self.guiVars['exodosVersion'].set(self.configuration['exodosVersion'])
        self.exodosVersionComboBox = ttk.Combobox(self.collectionFrame, state="readonly",
                                                  textvariable=self.guiVars['exodosVersion'])
        self.exodosVersionComboBox.grid(column=3, row=0, sticky="W", pady=5, padx=5)
        self.exodosVersionValues = util.exodosVersions.copy()
        self.exodosVersionComboBox['values'] = self.exodosVersionValues

        self.mapperLabel = Tk.Label(self.collectionFrame, text=self.guiStrings['mapper'].label)
        wckToolTips.register(self.mapperLabel, self.guiStrings['mapper'].help)
        self.mapperLabel.grid(column=4, row=0, sticky="E", pady=5)
        self.guiVars['mapper'] = Tk.StringVar()
        self.guiVars['mapper'].set(self.configuration['mapper'])
        self.mapperComboBox = ttk.Combobox(self.collectionFrame, state="readonly",
                                                  textvariable=self.guiVars['mapper'])
        self.mapperComboBox.grid(column=5, row=0, sticky="E", pady=5, padx=5)
        self.mapperValues = util.mappers.copy()
        self.mapperComboBox['values'] = self.mapperValues

        ttk.Separator(self.configurationFrame, orient=Tk.HORIZONTAL).grid(column=0, row=1, padx=5, pady=0,
                                                                   sticky="EW")

        # Conversion parameters
        self.conversionFrame = Tk.Frame(self.configurationFrame)
        self.conversionFrame.grid(column=0, row=2, padx=5, sticky="EW")
        self.conversionFrame.columnconfigure(0,weight=1)

        self.conversionFirstLineFrame = Tk.Frame(self.conversionFrame)
        self.conversionFirstLineFrame.grid(column=0, row=0, sticky="EW")

        self.guiVars['debugMode'] = Tk.IntVar()
        self.guiVars['debugMode'].set(self.configuration['debugMode'])
        self.debugModeCheckButton = Tk.Checkbutton(self.conversionFirstLineFrame,
                                                   text=self.guiStrings['debugMode'].label,
                                                   variable=self.guiVars['debugMode'], onvalue=1,
                                                   offvalue=0)
        wckToolTips.register(self.debugModeCheckButton, self.guiStrings['debugMode'].help)
        self.debugModeCheckButton.grid(column=0, row=0, sticky="W", pady=5)

        self.guiVars['genreSubFolders'] = Tk.IntVar()
        self.guiVars['genreSubFolders'].set(self.configuration['genreSubFolders'])
        self.useGenreSubFolderCheckButton = Tk.Checkbutton(self.conversionFirstLineFrame,
                                                           text=self.guiStrings['genreSubFolders'].label,
                                                           variable=self.guiVars['genreSubFolders'], onvalue=1,
                                                           offvalue=0)
        wckToolTips.register(self.useGenreSubFolderCheckButton, self.guiStrings['genreSubFolders'].help)
        self.useGenreSubFolderCheckButton.grid(column=1, row=0, sticky="W", pady=5, padx=5)

        self.guiVars['expertMode'] = Tk.IntVar()
        self.guiVars['expertMode'].set(self.configuration['expertMode'])
        self.expertModeCheckButton = Tk.Checkbutton(self.conversionFirstLineFrame,
                                                           text=self.guiStrings['expertMode'].label,
                                                           variable=self.guiVars['expertMode'], onvalue=1,
                                                           offvalue=0, command=self.checkExpertMode)
        wckToolTips.register(self.expertModeCheckButton, self.guiStrings['expertMode'].help)
        self.expertModeCheckButton.grid(column=2, row=0, sticky="W", pady=5, padx=5)

        # Expert parameters
        label = Tk.Label(self.conversionFirstLineFrame, text=self.guiStrings['mountPrefix'].label)
        wckToolTips.register(label, self.guiStrings['mountPrefix'].help)
        label.grid(column=3, row=0, padx=5, sticky="W")
        self.guiVars['mountPrefix'] = Tk.StringVar()
        self.guiVars['mountPrefix'].set(self.configuration['mountPrefix'])
        self.mountPrefixEntry = Tk.Entry(self.conversionFirstLineFrame, textvariable=self.guiVars['mountPrefix'])
        self.mountPrefixEntry.grid(column=4, row=0, padx=5, sticky=("WE"))
        self.conversionFirstLineFrame.columnconfigure(4, weight=1)

        self.conversionSecondLineFrame = Tk.Frame(self.conversionFrame)
        self.conversionSecondLineFrame.grid(column=0, row=1, sticky="EW")

        self.guiVars['vsyncCfg'] = Tk.IntVar()
        self.guiVars['vsyncCfg'].set(self.configuration['vsyncCfg'])
        self.vsyncCfgCheckButton = Tk.Checkbutton(self.conversionSecondLineFrame,
                                                    text=self.guiStrings['vsyncCfg'].label,
                                                    variable=self.guiVars['vsyncCfg'], onvalue=1,
                                                    offvalue=0)
        wckToolTips.register(self.vsyncCfgCheckButton, self.guiStrings['vsyncCfg'].help)
        self.vsyncCfgCheckButton.grid(column=0, row=1, sticky="W")

        frame = Tk.Frame(self.conversionSecondLineFrame, width=20)
        frame.grid(column=1, row=1, sticky="EW")

        label = Tk.Label(self.conversionSecondLineFrame, text=self.guiStrings['fullresolutionCfg'].label)
        wckToolTips.register(label, self.guiStrings['fullresolutionCfg'].help)
        label.grid(column=2, row=1, sticky="W")
        self.guiVars['fullresolutionCfg'] = Tk.StringVar()
        self.guiVars['fullresolutionCfg'].set(self.configuration['fullresolutionCfg'])
        self.fullResolutionCfgEntry = Tk.Entry(self.conversionSecondLineFrame, textvariable=self.guiVars['fullresolutionCfg'])
        self.fullResolutionCfgEntry.grid(column=3, row=1, padx=5, sticky=("WE"))

        frame = Tk.Frame(self.conversionSecondLineFrame, width=20)
        frame.grid(column=4, row=1, sticky="EW")

        label = Tk.Label(self.conversionSecondLineFrame, text=self.guiStrings['rendererCfg'].label)
        wckToolTips.register(label, self.guiStrings['rendererCfg'].help)
        label.grid(column=5, row=1, sticky="W")
        self.guiVars['rendererCfg'] = Tk.StringVar()
        self.guiVars['rendererCfg'].set(self.configuration['rendererCfg'])
        self.rendererCfgEntry = Tk.Entry(self.conversionSecondLineFrame, textvariable=self.guiVars['rendererCfg'])
        self.rendererCfgEntry.grid(column=6, row=1, padx=5, sticky=("WE"))

        frame = Tk.Frame(self.conversionSecondLineFrame, width=20)
        frame.grid(column=7, row=1, sticky="EW")

        label = Tk.Label(self.conversionSecondLineFrame, text=self.guiStrings['outputCfg'].label)
        wckToolTips.register(label, self.guiStrings['outputCfg'].help)
        label.grid(column=8, row=1, padx=5, sticky="W")
        self.guiVars['outputCfg'] = Tk.StringVar()
        self.guiVars['outputCfg'].set(self.configuration['outputCfg'])
        self.outputCfgEntry = Tk.Entry(self.conversionSecondLineFrame, textvariable=self.guiVars['outputCfg'])
        self.outputCfgEntry.grid(column=9, row=1, sticky=("WE"))

        self.checkExpertMode()
        self.loading = False

    # Listener for Expert Mode Check
    def checkExpertMode(self):
        if self.guiVars['expertMode'].get() != 1:
            self.mountPrefixEntry['state'] = 'disabled'
            self.vsyncCfgCheckButton['state'] = 'disabled'
            self.fullResolutionCfgEntry['state'] = 'disabled'
            self.rendererCfgEntry['state'] = 'disabled'
            self.outputCfgEntry['state'] = 'disabled'
        else:
            self.logger.log('Only use Expert Mode if you know what you are doing!\nCheck the github wiki for more information', self.logger.WARNING)
            if not self.loading :
                messagebox.showwarning('Are you sure ?', 'Only use Expert Mode if you know what you are doing!\nCheck the github wiki for more information')
            self.mountPrefixEntry['state'] = 'normal'
            self.vsyncCfgCheckButton['state'] = 'normal'
            self.fullResolutionCfgEntry['state'] = 'normal'
            self.rendererCfgEntry['state'] = 'normal'
            self.outputCfgEntry['state'] = 'normal'

    # Listener for collection path modifications
    def handleCollectionFolder(self, *args):
        collectionDir = self.guiVars['collectionDir'].get()

        # TODO better test here with all subfolders and differenciation between v4 and v5 ?
        # and maybe an error message somewhere
        if not os.path.isdir(collectionDir) or not util.validCollectionPath(collectionDir):
            self.logger.log(
                "%s is not a directory, doesn't exist, or is not a valid ExoDOS Collection directory" % collectionDir)
            self.logger.log("Did you install the collection with setup.bat beforehand ?")
            self.exodosGamesListbox['state'] = 'disabled'
            self.selectedGamesListbox['state'] = 'disabled'
            self.selectGameButton['state'] = 'disabled'
            self.deselectGameButton['state'] = 'disabled'
            self.selectAllGamesButton['state'] = 'disabled'
            self.unselectAllGamesButton['state'] = 'disabled'
            self.filterEntry['state'] = 'disabled'
        else:
            # Do not rebuild cache on first refresh of the value
            if self.needsCacheRefresh is True:
                self.logger.log("Rebuild image caches")
                util.cleanCache(self.scriptDir)
            else:
                self.needsCacheRefresh = True
            self.cache = util.buildCache(self.scriptDir, collectionDir, self.logger)
            self.guiVars['filter'].set('')
            self.exodosGamesListbox['state'] = 'normal'
            self.selectedGamesListbox['state'] = 'normal'
            self.selectGameButton['state'] = 'normal'
            self.deselectGameButton['state'] = 'normal'
            self.selectAllGamesButton['state'] = 'normal'
            self.unselectAllGamesButton['state'] = 'normal'
            self.filterEntry['state'] = 'normal'

            # Listener for filter entry modification

    def filterGamesList(self, *args):
        filterValue = self.guiVars['filter'].get()
        filteredGameslist = [g for g in self.fullnameToGameDir.keys() if filterValue.lower() in g.lower()]
        self.exodosGamesListbox.selection_clear(0, Tk.END)
        self.exodosGamesValues.set(sorted(filteredGameslist))
        self.leftListLabel.set(self.guiStrings['leftList'].label + ' (' + str(len(self.exodosGamesValues.get())) + ')')

    # Selection Frame
    def drawSelectionFrame(self):
        self.selectionFrame = Tk.LabelFrame(self.mainFrame, padx=10, pady=5)
        self.selectionFrame.grid(column=0, row=2, sticky="EW", pady=5)
        self.selectionFrame.grid_columnconfigure(0, weight=1)

        self.guiVars['filter'] = Tk.StringVar()
        self.guiVars['filter'].set('')
        self.guiVars['filter'].trace_add("write", self.filterGamesList)
        self.filterEntry = Tk.Entry(self.selectionFrame, textvariable=self.guiVars['filter'])
        self.filterEntry.grid(column=0, row=0, sticky='W')
        wckToolTips.register(self.filterEntry, self.guiStrings['filter'].help)

        self.leftFrame = Tk.Frame(self.selectionFrame)
        self.leftFrame.grid(column=0, row=1, sticky="W", pady=5)
        self.leftFrame.grid_columnconfigure(0, weight=3)
        self.leftListLabel = Tk.StringVar(value=self.guiStrings['leftList'].label)

        hatLeftFrame = Tk.Frame(self.leftFrame)
        hatLeftFrame.grid(column=0,row=0, sticky='WE')
        hatLeftFrame.grid_columnconfigure(0, weight=3)

        label = Tk.Label(hatLeftFrame, textvariable=self.leftListLabel, anchor='w')
        wckToolTips.register(label, self.guiStrings['leftList'].help)
        label.grid(column=0, row=0, sticky="W")

        emptyFrame = Tk.Frame(hatLeftFrame, width=10)
        emptyFrame.grid(column=1,row=0, sticky='W')

        self.selectAllGamesButton = Tk.Button(hatLeftFrame, text=self.guiStrings['selectall'].label,
                                              command=self.selectAll)
        wckToolTips.register(self.selectAllGamesButton, self.guiStrings['selectall'].help)
        self.selectAllGamesButton.grid(column=2, row=0, sticky='E')

        self.exodosGamesValues = Tk.Variable(value=[])
        self.exodosGamesListbox = Tk.Listbox(self.leftFrame, listvariable=self.exodosGamesValues,
                                             selectmode=Tk.EXTENDED, width=70)
        self.exodosGamesListbox.grid(column=0, row=1, sticky="W", pady=5)
        self.exodosGamesListbox.grid_rowconfigure(0, weight=3)

        # TODO will need to refresh that when changing exodos version
        self.exodosGamesValues.set(sorted(list(self.fullnameToGameDir.keys())))
        self.leftListLabel.set(
            self.guiStrings['leftList'].label + ' (' + str(len(self.fullnameToGameDir.keys())) + ')')

        scrollbarLeft = Tk.Scrollbar(self.leftFrame, orient=Tk.VERTICAL, command=self.exodosGamesListbox.yview)
        scrollbarLeft.grid(column=1, row=1, sticky=(Tk.N, Tk.S),)
        self.exodosGamesListbox['yscrollcommand'] = scrollbarLeft.set

        self.buttonsColumnFrame = Tk.Frame(self.selectionFrame, padx=10)
        self.buttonsColumnFrame.grid(column=1, row=1, pady=5)
        self.buttonsColumnFrame.grid_columnconfigure(1, weight=1)
        emptyFrame = Tk.Frame(self.buttonsColumnFrame, padx=10)
        emptyFrame.grid(column=0, row=0, pady=5)
        self.selectGameButton = Tk.Button(self.buttonsColumnFrame, text='->', command=self.clickRight)
        wckToolTips.register(self.selectGameButton, self.guiStrings['right'].help)
        self.selectGameButton.grid(column=0, row=3, padx=3)
        emptyFrame = Tk.Frame(self.buttonsColumnFrame, padx=10)
        emptyFrame.grid(column=0, row=4, pady=5)
        self.deselectGameButton = Tk.Button(self.buttonsColumnFrame, text='<-', command=self.clickLeft)
        wckToolTips.register(self.deselectGameButton, self.guiStrings['left'].help)
        self.deselectGameButton.grid(column=0, row=7, padx=3)
        emptyFrame = Tk.Frame(self.buttonsColumnFrame, padx=10)
        emptyFrame.grid(column=0, row=8, pady=5)

        self.rightFrame = Tk.Frame(self.selectionFrame)
        self.rightFrame.grid(column=2, row=1, sticky="E", pady=5)
        self.rightFrame.grid_columnconfigure(2, weight=3)
        self.rightListLabel = Tk.StringVar(value=self.guiStrings['rightList'].label + ' (0)')

        hatRightFrame = Tk.Frame(self.rightFrame)
        hatRightFrame.grid(column=0, row=0, sticky='WE')
        hatRightFrame.grid_columnconfigure(0, weight=3)

        label = Tk.Label(hatRightFrame, textvariable=self.rightListLabel, anchor='w')
        wckToolTips.register(label, self.guiStrings['rightList'].help)
        label.grid(column=0, row=0, sticky="W")

        emptyFrame = Tk.Frame(hatRightFrame, width=10)
        emptyFrame.grid(column=1, row=0, sticky='W')

        self.unselectAllGamesButton = Tk.Button(hatRightFrame, text=self.guiStrings['unselectall'].label,
                                              command=self.unselectAll)
        wckToolTips.register(self.unselectAllGamesButton, self.guiStrings['unselectall'].help)
        self.unselectAllGamesButton.grid(column=2, row=0, sticky='E')


        self.selectedGamesValues = Tk.Variable(value=[])
        self.selectedGamesListbox = Tk.Listbox(self.rightFrame, listvariable=self.selectedGamesValues,
                                               selectmode=Tk.EXTENDED, width=70)
        self.selectedGamesListbox.grid(column=0, row=1, sticky="E", pady=5)
        self.selectedGamesListbox.grid_columnconfigure(0, weight=3)

        scrollbarRight = Tk.Scrollbar(self.rightFrame, orient=Tk.VERTICAL, command=self.selectedGamesListbox.yview)
        scrollbarRight.grid(column=1, row=1, sticky=(Tk.N, Tk.S))
        self.selectedGamesListbox['yscrollcommand'] = scrollbarRight.set

        self.handleCollectionFolder()

    # Listener to remove game from selection    
    def clickLeft(self):
        selectedOnRight = self.selectedGamesListbox.curselection()
        for sel in reversed(selectedOnRight):
            self.selectedGamesListbox.delete(sel)

        self.selectedGamesListbox.selection_clear(0, Tk.END)
        self.rightListLabel.set(
            self.guiStrings['rightList'].label + ' (' + str(len(self.selectedGamesValues.get())) + ')')

    # Listener to add all games to the selection
    def selectAll(self):
        selectedAll = self.exodosGamesValues.get()
        alreadyOnRight = self.selectedGamesValues.get()
        for sel in selectedAll:
            if sel not in alreadyOnRight:
                self.selectedGamesListbox.insert(Tk.END, sel)
        self.selectedGamesValues.set(sorted(self.selectedGamesValues.get()))

        self.exodosGamesListbox.selection_clear(0, Tk.END)
        self.rightListLabel.set(
            self.guiStrings['rightList'].label + ' (' + str(len(self.selectedGamesValues.get())) + ')')

    # Listener to remove all games from the selection
    def unselectAll(self):
        self.selectedGamesValues.set([])
        self.rightListLabel.set(
            self.guiStrings['rightList'].label + ' (' + str(len(self.selectedGamesValues.get())) + ')')

    # Listener to add selected game to selection
    def clickRight(self):
        selectedOnLeft = [self.exodosGamesListbox.get(int(item)) for item in self.exodosGamesListbox.curselection()]
        alreadyOnRight = self.selectedGamesValues.get()
        for sel in selectedOnLeft:
            if sel not in alreadyOnRight:
                self.selectedGamesListbox.insert(Tk.END, sel)
        self.selectedGamesValues.set(sorted(self.selectedGamesValues.get()))

        self.exodosGamesListbox.selection_clear(0, Tk.END)
        self.rightListLabel.set(
            self.guiStrings['rightList'].label + ' (' + str(len(self.selectedGamesValues.get())) + ')')

    # Action buttons frame    
    def drawButtonsFrame(self):
        self.buttonsFrame = Tk.Frame(self.mainFrame, padx=10)
        self.buttonsFrame.grid(column=0, row=3, sticky="EW", pady=5)
        emptyFrame = Tk.Frame(self.buttonsFrame, padx=10, width=400)
        emptyFrame.grid(column=0, row=0, sticky="NEWS", pady=5)
        emptyFrame.grid_columnconfigure(0, weight=3)
        self.verifyButton = Tk.Button(self.buttonsFrame, text=self.guiStrings['verify'].label, command=self.clickVerify)
        wckToolTips.register(self.verifyButton, self.guiStrings['verify'].help)
        self.verifyButton.grid(column=1, row=0, sticky="EW", padx=3)
        self.saveButton = Tk.Button(self.buttonsFrame, text=self.guiStrings['save'].label, command=self.clickSave)
        wckToolTips.register(self.saveButton, self.guiStrings['save'].help)
        self.saveButton.grid(column=2, row=0, sticky="EW", padx=3)
        self.proceedButton = Tk.Button(self.buttonsFrame, text=self.guiStrings['proceed'].label,
                                       command=self.clickProceed)
        wckToolTips.register(self.proceedButton, self.guiStrings['proceed'].help)
        self.proceedButton.grid(column=3, row=0, sticky="EW", padx=3)
        emptyFrame = Tk.Frame(self.buttonsFrame, padx=10, width=350)
        emptyFrame.grid(column=4, row=0, sticky="NEWS", pady=5)
        emptyFrame.grid_columnconfigure(4, weight=3)

    # Listener for Save button    
    def clickSave(self):
        self.logger.log('\n<--------- Saving configuration --------->')
        self.saveConfFile()
        self.saveConfInMem()

        # Saves to conf file

    def saveConfFile(self):
        confBackupFilePath = os.path.join(self.scriptDir, util.confDir, util.getConfBakFilename(self.setKey))
        if os.path.exists(confBackupFilePath):
            os.remove(confBackupFilePath)
        shutil.copy2(os.path.join(self.scriptDir, util.confDir, util.getConfFilename(self.setKey)),
                     os.path.join(self.scriptDir, util.confDir, util.getConfBakFilename(self.setKey)))
        confFile = open(os.path.join(self.scriptDir, util.confDir, util.getConfFilename(self.setKey)), "w",
                        encoding="utf-8")
        listKeys = sorted(self.guiStrings.values(), key=attrgetter('order'))
        for key in listKeys:
            if key.id not in ['verify', 'save', 'proceed', 'confirm', 'left', 'right', 'leftList', 'rightList',
                              'filter', 'selectall', 'unselectall']:
                if key.help:
                    confFile.write('# ' + key.help.replace('#n', '\n# ') + '\n')
                if key.id == 'images':
                    imagesValue = self.guiVars[self.guiStrings['images'].label + ' #1'].get()
                    if self.guiStrings['images'].label + ' #2' in self.guiVars:
                        imagesValue = imagesValue + '|' + self.guiVars[self.guiStrings['images'].label + ' #2'].get()
                    confFile.write(key.id + ' = ' + imagesValue + '\n')
                else:
                    if key.id in self.guiVars:
                        confFile.write(key.id + ' = ' + str(self.guiVars[key.id].get()) + '\n')
        confFile.close()
        self.logger.log('    Configuration saved in ' + util.getConfFilename(self.setKey) + ' file')

        # Saves in memory

    def saveConfInMem(self):
        listKeys = sorted(self.guiStrings.values(), key=attrgetter('order'))
        for key in listKeys:
            if key.id not in ['verify', 'save', 'proceed', 'confirm', 'left', 'right', 'leftList', 'rightList', 'selectall', 'unselectall']:
                if key.id == 'images':
                    imagesValue = self.guiVars[self.guiStrings['images'].label + ' #1'].get()
                    if self.guiStrings['images'].label + ' #2' in self.guiVars:
                        imagesValue = imagesValue + '|' + self.guiVars[self.guiStrings['images'].label + ' #2'].get()
                    self.configuration['images'] = imagesValue
                else:
                    if key.id in self.guiVars:
                        self.configuration[key.id] = str(self.guiVars[key.id].get())
        self.logger.log('    Configuration saved in memory')

        # Listener for Verify button

    def clickVerify(self):
        self.logger.log('\n<--------- Verify ' + self.setKey + ' Parameters --------->')
        error = False
        for key in ['outputDir', 'collectionDir']:
            if not os.path.exists(self.guiVars[key].get()):
                error = True
                self.logger.log(key + ' folder does not exist')

        if not error:
            self.logger.log('All Good!')

    # Listener for Proceed Button
    def clickProceed(self):
        self.logger.log('\n<--------- Saving ' + self.setKey + ' configuration --------->')
        self.verifyButton['state'] = 'disabled'
        self.saveButton['state'] = 'disabled'
        self.proceedButton['state'] = 'disabled'
        self.exodosGamesListbox['state'] = 'disabled'
        self.selectedGamesListbox['state'] = 'disabled'
        self.selectGameButton['state'] = 'disabled'
        self.deselectGameButton['state'] = 'disabled'
        self.selectAllGamesButton['state'] = 'disabled'
        self.unselectAllGamesButton['state'] = 'disabled'
        self.filterEntry['state'] = 'disabled'
        self.conversionTypeComboBox['state'] = 'disabled'
        self.exodosVersionComboBox['state'] = 'disabled'
        self.useGenreSubFolderCheckButton['state'] = 'disabled'
        self.mapperComboBox['state'] = 'disabled'
        self.collectionEntry['state'] = 'disabled'
        self.outputEntry['state'] = 'disabled'
        self.mountPrefixEntry['state'] = 'disabled'
        self.vsyncCfgCheckButton['state'] = 'disabled'
        self.fullResolutionCfgEntry['state'] = 'disabled'
        self.rendererCfgEntry['state'] = 'disabled'
        self.outputCfgEntry['state'] = 'disabled'
        self.debugModeCheckButton['state'] = 'disabled'
        self.expertModeCheckButton['state'] = 'disabled'

        self.logger.log('\n<--------- Starting ' + self.setKey + ' Process --------->')
        # TODO see if there's a way to have more simpler parameters passed to converter and logging here, better simplify code in converter
        collectionDir = self.guiVars['collectionDir'].get()
        conversionType = self.guiVars['conversionType'].get()
        useGenreSubFolders = True if self.guiVars['genreSubFolders'].get() == 1 else False
        outputDir = self.guiVars['outputDir'].get()
        # Configuration parameters
        conversionConf = dict()
        conversionConf['useDebugMode'] = True if self.guiVars['debugMode'].get() == 1 else False
        conversionConf['useExpertMode'] = True if self.guiVars['expertMode'].get() == 1 else False
        conversionConf['mountPrefix'] = self.guiVars['mountPrefix'].get()
        conversionConf['fullresolutionCfg'] = self.guiVars['fullresolutionCfg'].get()
        conversionConf['rendererCfg'] = self.guiVars['rendererCfg'].get()
        conversionConf['outputCfg'] = self.guiVars['outputCfg'].get()
        conversionConf['vsyncCfg'] = True if self.guiVars['vsyncCfg'].get() == 1 else False
        # TODO better move this to converter when v5 is released and properly handle it, or move it to verify ? Also use messagebox
        gamesDir = os.path.join(collectionDir, "eXoDOS", "Games")
        gamesDosDir = os.path.join(gamesDir, "!dos")
        games = [self.fullnameToGameDir.get(name) for name in self.selectedGamesValues.get()]
        self.logger.log(str(len(games)) + ' game(s) selected for conversion')
        # TODO we could go from list of full game names now, as 'games' short names from !dos folder should correspond to dir in the zip of each game

        if not os.path.isdir(gamesDir) or not os.path.isdir(gamesDosDir):
            self.logger.log("%s doesn't seem to be a valid ExoDOSCollection folder" % collectionDir)
        else:
            exoDOSConverter = ExoDOSConverter(games, self.cache, self.scriptDir, collectionDir, gamesDosDir, outputDir, conversionType,
                                              useGenreSubFolders, self.logger)
            _thread.start_new(exoDOSConverter.convertGames, ())

    # Console Frame    
    def drawConsole(self):
        self.consoleFrame = Tk.Frame(self.root, padx=10)
        self.consoleFrame.grid(column=0, row=5, sticky="EW", pady=5)
        self.consoleFrame.grid_columnconfigure(0, weight=1)
        self.logTest = Tk.Text(self.consoleFrame, height=25, state='disabled', wrap='word', background='black',
                               foreground='yellow')
        self.logTest.grid(column=0, row=0, sticky="EW")
        self.logTest.tag_config('WARNING', background='black', foreground='red')
        self.logTest.tag_config('INFO', background='black', foreground='yellow')
        self.scrollbar = Tk.Scrollbar(self.consoleFrame, orient=Tk.VERTICAL, command=self.logTest.yview)
        self.scrollbar.grid(column=1, row=0, sticky=(Tk.N, Tk.S))
        self.logTest['yscrollcommand'] = self.scrollbar.set
        self.logTest.after(10, self.updateConsoleFromQueue)

    # Grabs messages from logger queue
    def updateConsoleFromQueue(self):
        while not self.logger.log_queue.empty():
            line = self.logger.log_queue.get()
            self.writeToConsole(line)
            self.root.update_idletasks()
        self.logTest.after(10, self.updateConsoleFromQueue)

    # Write message to console    
    def writeToConsole(self, msg):
        numlines = self.logTest.index('end - 1 line').split('.')[0]
        self.logTest['state'] = 'normal'
        if numlines == 24:
            self.logTest.delete(1.0, 2.0)
        if self.logTest.index('end-1c') != '1.0':
            self.logTest.insert('end', '\n')
        self.logTest.insert('end', msg[1], msg[0])
        self.logTest.see(Tk.END)
        self.logTest['state'] = 'disabled'
