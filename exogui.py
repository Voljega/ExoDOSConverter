import tkinter as Tk
from tkinter import ttk, messagebox, filedialog
from operator import attrgetter
import tkinter.font as Font
import wckToolTips
import conf
import util
import os
import shutil
import platform
from datetime import datetime
from exoconverter import ExoConverter
from functools import partial
import _thread


# Main GUI
class ExoGUI:
    DEFAULT_FONT_SIZE = 9

    def __init__(self, scriptDir, logger, title):
        self.scriptDir = scriptDir
        self.setKey = 'exo'
        self.cache = None
        self.loading = True
        # TODO create conf file from guiStrings if it doesn't exist and do not ship it with tool anymore 
        self.configuration = conf.loadConf(
            os.path.join(self.scriptDir, util.confDir, util.getConfFilename(self.setKey)))
        self.guiVars = dict()
        self.guiStrings = util.loadUIStrings(self.scriptDir, util.getGuiStringsFilename(self.setKey))
        # util.buildCollectionCSV(self.scriptDir, 'H:\eXo\eXoDOS\eXo\eXoDOS\!dos', logger)
        self.fullnameToGameDir = util.fullnameToGameDir(scriptDir, self.configuration['collectionVersion'])

        self.window = Tk.Tk()
        self.window.resizable(False, False)
        self.window.geometry('+50+50')
        self.startFontSize = self.DEFAULT_FONT_SIZE

        if platform.system() == 'Windows':
            self.window.iconbitmap('exodosicon.ico')

        self.__setFontSize__(self.startFontSize)
        self.window.title(title)
        self.logger = logger

        # Init all components
        self.root = None
        self.mainFrame = None
        self.pathsFrame = None
        self.collectionEntry = None
        self.selectCollectionDirButton = None
        self.outputEntry = None
        self.selectOutputDirButton = None
        self.configurationFrame = None
        self.collectionFrame = None
        self.versionFrame = None
        self.collectionVersionLabel = None
        self.conversionTypeComboBox = None
        self.conversionTypeValues = None
        self.downloadOnDemandCheckButton = None
        self.longGameFolderCheckButton = None
        self.mapperLabel = None
        self.mapperComboBox = None
        self.mapperValues = None
        self.preExtractGamesCheckButton = None
        self.conversionFrame = None
        self.genericConversionFrame = None
        self.expertConversionFrame = None
        self.mapperConversionFrame = None
        self.conversionTypeLabel = None
        self.debugModeCheckButton = None
        self.useGenreSubFolderCheckButton = None
        self.expertModeCheckButton = None
        self.mountPrefixEntry = None
        self.vsyncCfgCheckButton = None
        self.fullResolutionCfgEntry = None
        self.rendererCfgEntry = None
        self.outputCfgEntry = None
        self.mapSticksCheckButton = None
        self.useKeyb2JoypadCheckButton = None
        self.selectionFrame = None
        self.filterEntry = None
        self.customSelectionFrame = None
        self.selectionPathEntry = None
        self.selectSelectionPathButton = None
        self.leftFrame = None
        self.leftListLabel = None
        self.selectAllGamesButton = None
        self.exoGamesValues = None
        self.exoGamesListbox = None
        self.buttonsColumnFrame = None
        self.selectGameButton = None
        self.deselectGameButton = None
        self.rightFrame = None
        self.rightListLabel = None
        self.unselectAllGamesButton = None
        self.loadCustomButton = None
        self.saveCustomButton = None
        self.selectedGamesValues = None
        self.selectedGamesListbox = None
        self.buttonsFrame = None
        self.verifyButton = None
        self.saveButton = None
        self.proceedButton = None
        self.consoleFrame = None
        self.logTest = None
        self.scrollbar = None

    def draw(self):
        self.root = Tk.Frame(self.window, padx=10, pady=5)
        self.root.grid(column=0, row=0)
        self.__drawMainframe__()
        self.window.mainloop()

    def __setFontSize__(self, value):
        fontSize = value if value is not None else self.startFontSize
        default_font = Font.nametofont("TkDefaultFont")
        default_font.configure(size=fontSize)
        text_font = Font.nametofont("TkTextFont")
        text_font.configure(size=fontSize)
        fixed_font = Font.nametofont("TkFixedFont")
        fixed_font.configure(size=fontSize)

    # Main mama Frame    
    def __drawMainframe__(self):
        self.mainFrame = Tk.Frame(self.root, padx=10, pady=0)
        self.mainFrame.grid(column=0, row=1, sticky="EW", pady=5)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        self.__drawPathsFrame__()
        self.__drawConfigurationFrame__()
        self.__drawSelectionFrame__()
        self.__drawButtonsFrame__()
        self.__drawConsole__()

    # File Explorer for various vars
    def __openFileExplorer__(self, openDir, var, fileType):
        if openDir:
            result = filedialog.askdirectory(initialdir=self.guiVars[var].get(),
                                             title="Select your " + self.guiStrings[var].label)
        else:
            basedir = os.path.dirname(self.guiVars[var].get())
            initialDir = basedir if os.path.exists(basedir) else self.scriptDir
            result = filedialog.askopenfilename(initialdir=initialDir,
                                                title="Select your " + self.guiStrings[var].label,
                                                filetypes=[('Selection Files', '*.%s' % fileType)])
        if result != '':
            if platform.system() == 'Windows':
                result = result.replace('/', '\\')
            self.__updateConsoleFromQueue__()
            self.guiVars[var].set(result)
            if not openDir and var == 'selectionPath':
                self.__loadCustom__()

    # Paths frame    
    def __drawPathsFrame__(self):
        self.pathsFrame = Tk.LabelFrame(self.mainFrame, text="Your Paths", padx=10, pady=5)
        self.pathsFrame.grid(column=0, row=0, sticky="EW", pady=5)
        self.pathsFrame.grid_columnconfigure(1, weight=1)
        setRow = 0

        label = Tk.Label(self.pathsFrame, text=self.guiStrings['collectionDir'].label)
        wckToolTips.register(label, self.guiStrings['collectionDir'].help)
        label.grid(column=0, row=setRow, padx=5, sticky="W")
        self.guiVars['collectionDir'] = Tk.StringVar()
        self.guiVars['collectionDir'].set(self.configuration['collectionDir'])
        self.guiVars['collectionDir'].trace_add("write", self.__handleCollectionFolder__)
        self.collectionEntry = Tk.Entry(self.pathsFrame, textvariable=self.guiVars['collectionDir'])
        self.collectionEntry.grid(column=1, row=setRow, padx=5, sticky="WE")
        self.selectCollectionDirButton = Tk.Button(self.pathsFrame, text=self.guiStrings['selectCollectionDir'].label,
                                                   command=lambda: self.__openFileExplorer__(True, 'collectionDir', None))
        self.selectCollectionDirButton.grid(column=2, row=setRow, padx=5, sticky="WE")
        wckToolTips.register(self.selectCollectionDirButton, self.guiStrings['selectCollectionDir'].help)
        setRow = setRow + 1

        outputDirLabel = Tk.Label(self.pathsFrame, text=self.guiStrings['outputDir'].label)
        wckToolTips.register(outputDirLabel, self.guiStrings['outputDir'].help)
        outputDirLabel.grid(column=0, row=setRow, padx=5, sticky=Tk.W)
        self.guiVars['outputDir'] = Tk.StringVar()
        self.guiVars['outputDir'].set(self.configuration['outputDir'])
        self.outputEntry = Tk.Entry(self.pathsFrame, textvariable=self.guiVars['outputDir'])
        self.outputEntry.grid(column=1, row=setRow, padx=5, sticky="WE")
        self.selectOutputDirButton = Tk.Button(self.pathsFrame, text=self.guiStrings['selectOutputDir'].label,
                                               command=lambda: self.__openFileExplorer__(True, 'outputDir', None))
        self.selectOutputDirButton.grid(column=2, row=setRow, padx=5, sticky="WE")
        wckToolTips.register(self.selectOutputDirButton, self.guiStrings['selectOutputDir'].help)

    # Handle conversion type change
    def __changeConversionType__(self, event):
        self.__handleComponentsState__(False)

    # Configuration Frame
    def __drawConfigurationFrame__(self):
        self.__drawGenericConfigurationFrame__()
        self.__drawExpertConfigurationFrame__()
        self.__drawMapperConfigurationFrame__()
        self.__checkExpertMode__()
        self.loading = False

    def __drawGenericConfigurationFrame__(self):
        self.configurationFrame = Tk.LabelFrame(self.mainFrame, text="Configuration", padx=10, pady=5)
        self.configurationFrame.grid(column=0, row=1, sticky="EW", pady=5)
        self.configurationFrame.columnconfigure(0, weight=1)

        self.versionFrame = Tk.Frame(self.configurationFrame)
        self.versionFrame.grid(column=0, row=0, padx=5, sticky="EW")
        self.guiVars['collectionVersion'] = Tk.StringVar()
        self.guiVars['collectionVersion'].set(self.configuration['collectionVersion'])
        self.guiVars['collectionVersionLabel'] = Tk.StringVar()
        self.guiVars['collectionVersionLabel'].set(
            self.guiStrings['collectionVersion'].label + ' : ' + self.guiVars['collectionVersion'].get())
        self.collectionVersionLabel = Tk.Label(self.versionFrame,
                                               textvariable=self.guiVars['collectionVersionLabel'])
        wckToolTips.register(self.collectionVersionLabel, self.guiStrings['collectionVersion'].help)
        self.collectionVersionLabel.grid(column=0, row=0, sticky="W")

        # Collection parameters
        self.collectionFrame = Tk.Frame(self.configurationFrame)
        self.collectionFrame.grid(column=0, row=1, padx=5, sticky="EW")

        self.conversionTypeLabel = Tk.Label(self.collectionFrame, text=self.guiStrings['conversionType'].label)
        wckToolTips.register(self.conversionTypeLabel, self.guiStrings['conversionType'].help)
        self.conversionTypeLabel.grid(column=0, row=0, sticky="W", pady=5)
        self.guiVars['conversionType'] = Tk.StringVar()
        self.guiVars['conversionType'].set(self.configuration['conversionType'])
        self.conversionTypeComboBox = ttk.Combobox(self.collectionFrame, state="readonly",
                                                   textvariable=self.guiVars['conversionType'])
        self.conversionTypeComboBox.bind('<<ComboboxSelected>>', self.__changeConversionType__)
        self.conversionTypeComboBox.grid(column=1, row=0, sticky="W", pady=5, padx=5)
        self.conversionTypeValues = util.conversionTypes.copy()
        self.conversionTypeComboBox['values'] = self.conversionTypeValues

        self.guiVars['downloadOnDemand'] = Tk.IntVar()
        self.guiVars['downloadOnDemand'].set(self.configuration['downloadOnDemand'])
        self.downloadOnDemandCheckButton = Tk.Checkbutton(self.collectionFrame,
                                                          text=self.guiStrings['downloadOnDemand'].label,
                                                          variable=self.guiVars['downloadOnDemand'], onvalue=1,
                                                          offvalue=0)
        wckToolTips.register(self.downloadOnDemandCheckButton, self.guiStrings['downloadOnDemand'].help)
        self.downloadOnDemandCheckButton.grid(column=3, row=0, sticky="E", pady=5)

        self.guiVars['longGameFolder'] = Tk.IntVar()
        self.guiVars['longGameFolder'].set(self.configuration['longGameFolder'])
        self.longGameFolderCheckButton = Tk.Checkbutton(self.collectionFrame,
                                                          text=self.guiStrings['longGameFolder'].label,
                                                          variable=self.guiVars['longGameFolder'], onvalue=1,
                                                          offvalue=0)
        wckToolTips.register(self.longGameFolderCheckButton, self.guiStrings['longGameFolder'].help)
        self.longGameFolderCheckButton.grid(column=4, row=0, sticky="", pady=5)

        self.guiVars['preExtractGames'] = Tk.IntVar()
        self.guiVars['preExtractGames'].set(self.configuration['preExtractGames'])
        self.preExtractGamesCheckButton = Tk.Checkbutton(self.collectionFrame,
                                                         text=self.guiStrings['preExtractGames'].label,
                                                         variable=self.guiVars['preExtractGames'], onvalue=1,
                                                         offvalue=0)
        wckToolTips.register(self.preExtractGamesCheckButton, self.guiStrings['preExtractGames'].help)
        self.preExtractGamesCheckButton.grid(column=5, row=0, sticky="W", pady=5)

        ttk.Separator(self.configurationFrame, orient=Tk.HORIZONTAL).grid(column=0, row=2, padx=5, pady=0,
                                                                          sticky="EW")

        # Conversion parameters
        self.conversionFrame = Tk.Frame(self.configurationFrame)
        self.conversionFrame.grid(column=0, row=3, padx=5, sticky="EW")
        self.conversionFrame.columnconfigure(0, weight=1)

        self.genericConversionFrame = Tk.Frame(self.conversionFrame)
        self.genericConversionFrame.grid(column=0, row=0, sticky="EW")

        self.guiVars['debugMode'] = Tk.IntVar()
        self.guiVars['debugMode'].set(self.configuration['debugMode'])
        self.debugModeCheckButton = Tk.Checkbutton(self.genericConversionFrame,
                                                   text=self.guiStrings['debugMode'].label,
                                                   variable=self.guiVars['debugMode'], onvalue=1,
                                                   offvalue=0)
        wckToolTips.register(self.debugModeCheckButton, self.guiStrings['debugMode'].help)
        self.debugModeCheckButton.grid(column=0, row=0, sticky="W", pady=5)

        self.guiVars['genreSubFolders'] = Tk.IntVar()
        self.guiVars['genreSubFolders'].set(self.configuration['genreSubFolders'])
        self.useGenreSubFolderCheckButton = Tk.Checkbutton(self.genericConversionFrame,
                                                           text=self.guiStrings['genreSubFolders'].label,
                                                           variable=self.guiVars['genreSubFolders'], onvalue=1,
                                                           offvalue=0)
        wckToolTips.register(self.useGenreSubFolderCheckButton, self.guiStrings['genreSubFolders'].help)
        self.useGenreSubFolderCheckButton.grid(column=1, row=0, sticky="W", pady=5, padx=5)

        self.guiVars['vsyncCfg'] = Tk.IntVar()
        self.guiVars['vsyncCfg'].set(self.configuration['vsyncCfg'])
        self.vsyncCfgCheckButton = Tk.Checkbutton(self.genericConversionFrame,
                                                  text=self.guiStrings['vsyncCfg'].label,
                                                  variable=self.guiVars['vsyncCfg'], onvalue=1,
                                                  offvalue=0)
        wckToolTips.register(self.vsyncCfgCheckButton, self.guiStrings['vsyncCfg'].help)
        self.vsyncCfgCheckButton.grid(column=4, row=0, sticky="W")

    def __drawExpertConfigurationFrame__(self):
        self.expertConversionFrame = Tk.Frame(self.conversionFrame)
        self.expertConversionFrame.grid(column=0, row=1, sticky="EW")

        self.guiVars['expertMode'] = Tk.IntVar()
        self.guiVars['expertMode'].set(self.configuration['expertMode'])
        self.expertModeCheckButton = Tk.Checkbutton(self.expertConversionFrame,
                                                    text=self.guiStrings['expertMode'].label,
                                                    variable=self.guiVars['expertMode'], onvalue=1,
                                                    offvalue=0, command=self.__checkExpertMode__)
        wckToolTips.register(self.expertModeCheckButton, self.guiStrings['expertMode'].help)
        self.expertModeCheckButton.grid(column=0, row=0, sticky="W")

        label = Tk.Label(self.expertConversionFrame, text=self.guiStrings['mountPrefix'].label)
        wckToolTips.register(label, self.guiStrings['mountPrefix'].help)
        label.grid(column=1, row=0, padx=5, sticky="W")
        self.guiVars['mountPrefix'] = Tk.StringVar()
        self.guiVars['mountPrefix'].set(self.configuration['mountPrefix'])
        self.mountPrefixEntry = Tk.Entry(self.expertConversionFrame, textvariable=self.guiVars['mountPrefix'], width=51)
        self.mountPrefixEntry.grid(column=2, row=0, padx=5, sticky="W")
        self.genericConversionFrame.columnconfigure(4, weight=1)

        label = Tk.Label(self.expertConversionFrame, text=self.guiStrings['fullresolutionCfg'].label)
        wckToolTips.register(label, self.guiStrings['fullresolutionCfg'].help)
        label.grid(column=3, row=0, sticky="W")
        self.guiVars['fullresolutionCfg'] = Tk.StringVar()
        self.guiVars['fullresolutionCfg'].set(self.configuration['fullresolutionCfg'])
        self.fullResolutionCfgEntry = Tk.Entry(self.expertConversionFrame,
                                               textvariable=self.guiVars['fullresolutionCfg'], width=11)
        self.fullResolutionCfgEntry.grid(column=4, row=0, padx=5, sticky="W")

        label = Tk.Label(self.expertConversionFrame, text=self.guiStrings['rendererCfg'].label)
        wckToolTips.register(label, self.guiStrings['rendererCfg'].help)
        label.grid(column=5, row=0, sticky="W")
        self.guiVars['rendererCfg'] = Tk.StringVar()
        self.guiVars['rendererCfg'].set(self.configuration['rendererCfg'])
        self.rendererCfgEntry = Tk.Entry(self.expertConversionFrame, textvariable=self.guiVars['rendererCfg'], width=11)
        self.rendererCfgEntry.grid(column=6, row=0, padx=5, sticky="WE")

        # frame = Tk.Frame(self.conversionSecondLineFrame, width=20)
        # frame.grid(column=9, row=0, sticky="EW")

        label = Tk.Label(self.expertConversionFrame, text=self.guiStrings['outputCfg'].label)
        wckToolTips.register(label, self.guiStrings['outputCfg'].help)
        label.grid(column=7, row=0, padx=5, sticky="W")
        self.guiVars['outputCfg'] = Tk.StringVar()
        self.guiVars['outputCfg'].set(self.configuration['outputCfg'])
        self.outputCfgEntry = Tk.Entry(self.expertConversionFrame, textvariable=self.guiVars['outputCfg'], width=11)
        self.outputCfgEntry.grid(column=8, row=0, sticky="W")

    def __drawMapperConfigurationFrame__(self):
        ttk.Separator(self.conversionFrame, orient=Tk.HORIZONTAL).grid(column=0, row=2, pady=5,
                                                                          sticky="EW")
        self.mapperConversionFrame = Tk.Frame(self.conversionFrame)
        self.mapperConversionFrame.grid(column=0, row=3, sticky="EW")
        # TODO add better mapper handling, based on chosen conversion, with warning messages and all
        self.mapperLabel = Tk.Label(self.mapperConversionFrame, text=self.guiStrings['mapper'].label)
        wckToolTips.register(self.mapperLabel, self.guiStrings['mapper'].help)
        self.mapperLabel.grid(column=1, row=1, sticky="E", pady=5)
        self.guiVars['mapper'] = Tk.StringVar()
        self.guiVars['mapper'].set(self.configuration['mapper'])
        self.mapperComboBox = ttk.Combobox(self.mapperConversionFrame, state="readonly",
                                           textvariable=self.guiVars['mapper'])
        self.mapperComboBox.grid(column=2, row=1, sticky="E", pady=5, padx=5)
        self.mapperValues = util.mappers.copy()
        self.mapperComboBox['values'] = self.mapperValues

        self.guiVars['mapSticks'] = Tk.IntVar()
        self.guiVars['mapSticks'].set(self.configuration['mapSticks'])
        self.mapSticksCheckButton = Tk.Checkbutton(self.mapperConversionFrame, text=self.guiStrings['mapSticks'].label,
                                                   variable=self.guiVars['mapSticks'], onvalue=1, offvalue=0)
        wckToolTips.register(self.mapSticksCheckButton, self.guiStrings['mapSticks'].help)
        self.mapSticksCheckButton.grid(column=3, row=1, sticky="W")

        self.guiVars['useKeyb2Joypad'] = Tk.IntVar()
        self.guiVars['useKeyb2Joypad'].set(self.configuration['useKeyb2Joypad'])
        self.useKeyb2JoypadCheckButton = Tk.Checkbutton(self.mapperConversionFrame,
                                                        text=self.guiStrings['useKeyb2Joypad'].label,
                                                        variable=self.guiVars['useKeyb2Joypad'], onvalue=1, offvalue=0)
        wckToolTips.register(self.useKeyb2JoypadCheckButton, self.guiStrings['useKeyb2Joypad'].help)
        self.useKeyb2JoypadCheckButton.grid(column=4, row=1, sticky="W")

    # Listener for Expert Mode Check
    def __checkExpertMode__(self):
        self.__handleComponentsState__(False)
        if self.guiVars['expertMode'].get() == 1:
            self.logger.log(
                '\nOnly use Expert Mode if you know what you are doing!\nCheck the github wiki for more information',
                self.logger.ERROR)
            if not self.loading:
                messagebox.showwarning('Are you sure ?',
                                       'Only use Expert Mode if you know what you are doing!\nCheck the github wiki for more information')

    # Listener for collection path modifications
    def __handleCollectionFolder__(self, *args):
        collectionDir = self.guiVars['collectionDir'].get()
        collectionVersion = util.validCollectionPath(collectionDir)
        self.guiVars['collectionVersion'].set(collectionVersion)
        self.guiVars['collectionVersionLabel'].set(self.guiStrings['collectionVersion'].label + ': ' + self.guiVars['collectionVersion'].get())

        if collectionVersion is None:
            self.logger.log(
                "\n%s is not a directory, doesn't exist, or is not a valid eXo collection directory" % collectionDir, self.logger.ERROR)
            self.logger.log("Did you install the collection with setup.bat beforehand ?", self.logger.ERROR)
        else:
            self.fullnameToGameDir = util.fullnameToGameDir(self.scriptDir, self.guiVars['collectionVersion'].get())
            # Empty filter
            self.guiVars['filter'].set('')
            # Empty right textarea
            self.selectedGamesListbox.selection_clear(0, Tk.END)
            self.selectedGamesValues.set([])
            self.rightListLabel.set(
                self.guiStrings['rightList'].label + ' (' + str(len(self.selectedGamesValues.get())) + ')')
            # Fill left textarea with new values
            self.exoGamesListbox.selection_clear(0, Tk.END)
            self.exoGamesValues.set(sorted(list(self.fullnameToGameDir.keys())))
            self.leftListLabel.set(self.guiStrings['leftList'].label + ' (' + str(len(self.exoGamesValues.get())) + ')')

            self.logger.log("\nBuild/Load image caches, this might take a while ...")
            self.cache = util.buildCache(self.scriptDir, collectionDir, collectionVersion, self.logger)

        self.__handleComponentsState__(False)

    # Listener for filter entry modification
    def __filterGamesList__(self, *args):
        filterValue = self.guiVars['filter'].get()
        filteredGameslist = [g for g in self.fullnameToGameDir.keys() if filterValue.lower() in g.lower()]
        self.exoGamesListbox.selection_clear(0, Tk.END)
        self.exoGamesValues.set(sorted(filteredGameslist))
        self.leftListLabel.set(self.guiStrings['leftList'].label + ' (' + str(len(self.exoGamesValues.get())) + ')')

    # Selection Frame
    def __drawSelectionFrame__(self):
        self.selectionFrame = Tk.LabelFrame(self.mainFrame, padx=10, pady=5)
        self.selectionFrame.grid(column=0, row=2, sticky="EW", pady=5)
        self.selectionFrame.grid_columnconfigure(0, weight=1)

        self.guiVars['filter'] = Tk.StringVar()
        self.guiVars['filter'].set('')
        self.guiVars['filter'].trace_add("write", self.__filterGamesList__)
        self.filterEntry = Tk.Entry(self.selectionFrame, textvariable=self.guiVars['filter'])
        self.filterEntry.grid(column=0, row=0, sticky='W')
        wckToolTips.register(self.filterEntry, self.guiStrings['filter'].help)

        # Custom Selection
        self.customSelectionFrame = Tk.Frame(self.selectionFrame, borderwidth=1)
        self.customSelectionFrame.grid(column=2, row=0, sticky='W')

        label = Tk.Label(self.customSelectionFrame, text=self.guiStrings['selectionPath'].label)
        wckToolTips.register(label, self.guiStrings['selectionPath'].help)
        label.grid(column=0, row=0, sticky="W")

        self.guiVars['selectionPath'] = Tk.StringVar()
        self.guiVars['selectionPath'].set(self.configuration['selectionPath'])
        # self.guiVars['selectionPath'].trace_add("write", self.filterGamesList)
        self.selectionPathEntry = Tk.Entry(self.customSelectionFrame, textvariable=self.guiVars['selectionPath'],
                                           width=44)
        self.selectionPathEntry.grid(column=1, row=0, padx=5, sticky='W')
        wckToolTips.register(self.selectionPathEntry, self.guiStrings['selectionPath'].help)
        self.selectSelectionPathButton = Tk.Button(self.customSelectionFrame,
                                                   text=self.guiStrings['selectSelectionPath'].label,
                                                   command=lambda: self.__openFileExplorer__(False, 'selectionPath', '*'))
        self.selectSelectionPathButton.grid(column=2, row=0, padx=5, sticky="WE")
        wckToolTips.register(self.selectSelectionPathButton, self.guiStrings['selectSelectionPath'].help)

        # Left List
        self.leftFrame = Tk.Frame(self.selectionFrame)
        self.leftFrame.grid(column=0, row=1, sticky="W", pady=5)
        self.leftFrame.grid_columnconfigure(0, weight=3)
        self.leftListLabel = Tk.StringVar(value=self.guiStrings['leftList'].label)

        hatLeftFrame = Tk.Frame(self.leftFrame)
        hatLeftFrame.grid(column=0, row=0, sticky='WE')
        hatLeftFrame.grid_columnconfigure(0, weight=3)

        label = Tk.Label(hatLeftFrame, textvariable=self.leftListLabel, anchor='w')
        wckToolTips.register(label, self.guiStrings['leftList'].help)
        label.grid(column=0, row=0, sticky="W")

        emptyFrame = Tk.Frame(hatLeftFrame, width=10)
        emptyFrame.grid(column=1, row=0, sticky='W')

        self.selectAllGamesButton = Tk.Button(hatLeftFrame, text=self.guiStrings['selectall'].label,
                                              command=self.__selectAll__)
        wckToolTips.register(self.selectAllGamesButton, self.guiStrings['selectall'].help)
        self.selectAllGamesButton.grid(column=2, row=0, sticky='E')

        self.exoGamesValues = Tk.Variable(value=[])
        self.exoGamesListbox = Tk.Listbox(self.leftFrame, listvariable=self.exoGamesValues,
                                          selectmode=Tk.EXTENDED, width=70)
        self.exoGamesListbox.grid(column=0, row=1, sticky="W", pady=5)
        self.exoGamesListbox.grid_rowconfigure(0, weight=3)

        self.exoGamesValues.set(sorted(list(self.fullnameToGameDir.keys())))
        self.leftListLabel.set(
            self.guiStrings['leftList'].label + ' (' + str(len(self.fullnameToGameDir.keys())) + ')')

        scrollbarLeft = Tk.Scrollbar(self.leftFrame, orient=Tk.VERTICAL, command=self.exoGamesListbox.yview)
        scrollbarLeft.grid(column=1, row=1, sticky=(Tk.N, Tk.S), )
        self.exoGamesListbox['yscrollcommand'] = scrollbarLeft.set

        # Selection Buttons Frame
        self.buttonsColumnFrame = Tk.Frame(self.selectionFrame, padx=10)
        self.buttonsColumnFrame.grid(column=1, row=1, pady=5)
        self.buttonsColumnFrame.grid_columnconfigure(1, weight=1)
        emptyFrame = Tk.Frame(self.buttonsColumnFrame, padx=10)
        emptyFrame.grid(column=0, row=0, pady=5)
        self.selectGameButton = Tk.Button(self.buttonsColumnFrame, text='->', command=self.__clickRight__)
        wckToolTips.register(self.selectGameButton, self.guiStrings['right'].help)
        self.selectGameButton.grid(column=0, row=3, padx=3)
        emptyFrame = Tk.Frame(self.buttonsColumnFrame, padx=10)
        emptyFrame.grid(column=0, row=4, pady=5)
        self.deselectGameButton = Tk.Button(self.buttonsColumnFrame, text='<-', command=self.__clickLeft__)
        wckToolTips.register(self.deselectGameButton, self.guiStrings['left'].help)
        self.deselectGameButton.grid(column=0, row=7, padx=3)
        emptyFrame = Tk.Frame(self.buttonsColumnFrame, padx=10)
        emptyFrame.grid(column=0, row=8, pady=5)

        # Right List
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

        emptyFrame = Tk.Frame(hatRightFrame, width=20)
        emptyFrame.grid(column=1, row=0, sticky='W')

        self.unselectAllGamesButton = Tk.Button(hatRightFrame, text=self.guiStrings['unselectall'].label,
                                                command=self.__unselectAll__)
        wckToolTips.register(self.unselectAllGamesButton, self.guiStrings['unselectall'].help)
        self.unselectAllGamesButton.grid(column=2, row=0, sticky='E')

        loadSaveFrame = Tk.Frame(hatRightFrame)
        loadSaveFrame.grid(column=0, row=0, sticky='E')
        self.loadCustomButton = Tk.Button(loadSaveFrame, text=self.guiStrings['loadCustom'].label,
                                          command=self.__loadCustom__)
        wckToolTips.register(self.loadCustomButton, self.guiStrings['loadCustom'].help)
        self.loadCustomButton.grid(column=0, row=0, padx=5, sticky='E')
        self.saveCustomButton = Tk.Button(loadSaveFrame, text=self.guiStrings['saveCustom'].label,
                                          command=self.__saveCustom__)
        wckToolTips.register(self.saveCustomButton, self.guiStrings['saveCustom'].help)
        self.saveCustomButton.grid(column=1, row=0, padx=5, sticky='E')

        self.selectedGamesValues = Tk.Variable(value=[])
        self.selectedGamesListbox = Tk.Listbox(self.rightFrame, listvariable=self.selectedGamesValues,
                                               selectmode=Tk.EXTENDED, width=70)
        self.selectedGamesListbox.grid(column=0, row=1, sticky="E", pady=5)
        self.selectedGamesListbox.grid_columnconfigure(0, weight=3)

        scrollbarRight = Tk.Scrollbar(self.rightFrame, orient=Tk.VERTICAL, command=self.selectedGamesListbox.yview)
        scrollbarRight.grid(column=1, row=1, sticky=(Tk.N, Tk.S))
        self.selectedGamesListbox['yscrollcommand'] = scrollbarRight.set

        self.__handleCollectionFolder__()

    # Listener to save custom selection
    def __saveCustom__(self):
        customSelectionFile = self.selectionPathEntry.get()
        if not os.path.exists(os.path.dirname(customSelectionFile)):
            self.logger.log('Parent dir "%s" for Selection File "%s" does not exist' % (
                os.path.dirname(customSelectionFile), customSelectionFile), self.logger.ERROR)
        else:
            if os.path.exists(customSelectionFile):
                shutil.move(customSelectionFile,
                            customSelectionFile + '-' + datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))
            file = open(customSelectionFile, 'w', encoding='utf-8')
            for selectedGame in self.selectedGamesValues.get():
                file.write(selectedGame + '\n')
            self.logger.log(
                'Saved selection File "%s" with %i games' % (customSelectionFile, len(self.selectedGamesValues.get())))
            file.close()

    # Listener to load custom collection
    def __loadCustom__(self):
        customSelectionFile = self.selectionPathEntry.get()
        if not os.path.exists(customSelectionFile):
            self.logger.log('Selection File "%s" does not exist' % customSelectionFile, self.logger.ERROR)
        else:
            # Empty filter
            self.guiVars['filter'].set('')
            file = open(customSelectionFile, 'r', encoding='utf-8')
            selectedGames = []
            for line in file.readlines():
                game = line.rstrip(' \n\r')
                if game in self.exoGamesValues.get():
                    selectedGames.append(game)
            file.close()
            self.logger.log('Loaded selection File "%s" with %i games' % (customSelectionFile, len(selectedGames)))
            self.selectedGamesValues.set(sorted(selectedGames))
            self.rightListLabel.set(
                self.guiStrings['rightList'].label + ' (' + str(len(self.selectedGamesValues.get())) + ')')

    # Listener to remove game from selection    
    def __clickLeft__(self):
        selectedOnRight = self.selectedGamesListbox.curselection()
        for sel in reversed(selectedOnRight):
            self.selectedGamesListbox.delete(sel)

        self.selectedGamesListbox.selection_clear(0, Tk.END)
        self.rightListLabel.set(
            self.guiStrings['rightList'].label + ' (' + str(len(self.selectedGamesValues.get())) + ')')

    # Listener to add all games to the selection
    def __selectAll__(self):
        selectedAll = self.exoGamesValues.get()
        alreadyOnRight = self.selectedGamesValues.get()
        for sel in selectedAll:
            if sel not in alreadyOnRight:
                self.selectedGamesListbox.insert(Tk.END, sel)
        self.selectedGamesValues.set(sorted(self.selectedGamesValues.get()))

        self.exoGamesListbox.selection_clear(0, Tk.END)
        self.rightListLabel.set(
            self.guiStrings['rightList'].label + ' (' + str(len(self.selectedGamesValues.get())) + ')')

    # Listener to remove all games from the selection
    def __unselectAll__(self):
        self.selectedGamesValues.set([])
        self.rightListLabel.set(
            self.guiStrings['rightList'].label + ' (' + str(len(self.selectedGamesValues.get())) + ')')

    # Listener to add selected game to selection
    def __clickRight__(self):
        selectedOnLeft = [self.exoGamesListbox.get(int(item)) for item in self.exoGamesListbox.curselection()]
        alreadyOnRight = self.selectedGamesValues.get()
        for sel in selectedOnLeft:
            if sel not in alreadyOnRight:
                self.selectedGamesListbox.insert(Tk.END, sel)
        self.selectedGamesValues.set(sorted(self.selectedGamesValues.get()))

        self.exoGamesListbox.selection_clear(0, Tk.END)
        self.rightListLabel.set(
            self.guiStrings['rightList'].label + ' (' + str(len(self.selectedGamesValues.get())) + ')')

    # Action buttons frame    
    def __drawButtonsFrame__(self):
        self.buttonsFrame = Tk.Frame(self.mainFrame, padx=10)
        self.buttonsFrame.grid(column=0, row=3, sticky="EW", pady=5)
        emptyFrame = Tk.Frame(self.buttonsFrame, padx=10, width=400)
        emptyFrame.grid(column=0, row=0, sticky="NEWS", pady=5)
        emptyFrame.grid_columnconfigure(0, weight=3)
        self.verifyButton = Tk.Button(self.buttonsFrame, text=self.guiStrings['verify'].label, command=self.__clickVerify__)
        wckToolTips.register(self.verifyButton, self.guiStrings['verify'].help)
        self.verifyButton.grid(column=1, row=0, sticky="EW", padx=3)
        self.saveButton = Tk.Button(self.buttonsFrame, text=self.guiStrings['save'].label, command=self.__clickSave__)
        wckToolTips.register(self.saveButton, self.guiStrings['save'].help)
        self.saveButton.grid(column=2, row=0, sticky="EW", padx=3)
        self.proceedButton = Tk.Button(self.buttonsFrame, text=self.guiStrings['proceed'].label,
                                       command=self.__clickProceed__)
        wckToolTips.register(self.proceedButton, self.guiStrings['proceed'].help)
        self.proceedButton.grid(column=3, row=0, sticky="EW", padx=3)
        emptyFrame = Tk.Frame(self.buttonsFrame, padx=10, width=350)
        emptyFrame.grid(column=4, row=0, sticky="NEWS", pady=5)
        emptyFrame.grid_columnconfigure(4, weight=3)

    # Listener for Save button    
    def __clickSave__(self):
        self.logger.log('\n<--------- Saving configuration --------->')
        self.__saveConfFile__()
        self.__saveConfInMem__()

        # Saves to conf file

    def __saveConfFile__(self):
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
                              'filter', 'selectall', 'unselectall', 'loadCustom', 'saveCustom', 'selectOutputDir',
                              'selectCollectionDir', 'selectSelectionPath']:
                if key.help:
                    confFile.write('# ' + key.help.replace('\n', '\n# ') + '\n')
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

    def __saveConfInMem__(self):
        listKeys = sorted(self.guiStrings.values(), key=attrgetter('order'))
        for key in listKeys:
            if key.id not in ['verify', 'save', 'proceed', 'confirm', 'left', 'right', 'leftList', 'rightList',
                              'selectall', 'unselectall', 'loadCustom', 'saveCustom', 'selectOutputDir',
                              'selectCollectionDir', 'selectSelectionPath']:
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

    def __clickVerify__(self):
        self.logger.log('\n<--------- Verify ' + self.setKey + ' Parameters --------->')
        error = False
        for key in ['outputDir', 'collectionDir']:
            if not os.path.exists(self.guiVars[key].get()):
                error = True
                self.logger.log(key + ' folder does not exist')

        if not error:
            self.logger.log('All Good!')

    # Listener for Proceed Button
    def __clickProceed__(self):
        self.logger.log('\n<--------- Saving ' + self.setKey + ' configuration --------->')
        self.__handleComponentsState__(True)

        self.logger.log('\n<--------- Starting ' + self.setKey + ' Process --------->')
        collectionDir = self.guiVars['collectionDir'].get()
        conversionType = self.guiVars['conversionType'].get()
        useLongFolderNames = True if self.guiVars['longGameFolder'].get() == 1 else False
        useGenreSubFolders = True if self.guiVars['genreSubFolders'].get() == 1 else False
        outputDir = self.guiVars['outputDir'].get()
        # Configuration parameters
        conversionConf = dict()
        conversionConf['useDebugMode'] = True if self.guiVars['debugMode'].get() == 1 else False
        conversionConf['useExpertMode'] = True if self.guiVars['expertMode'].get() == 1 else False
        conversionConf['useKeyb2Joypad'] = True if self.guiVars['useKeyb2Joypad'].get() == 1 else False
        conversionConf['mapSticks'] = True if self.guiVars['mapSticks'].get() == 1 else False
        conversionConf['mountPrefix'] = self.guiVars['mountPrefix'].get()
        conversionConf['fullresolutionCfg'] = self.guiVars['fullresolutionCfg'].get()
        conversionConf['rendererCfg'] = self.guiVars['rendererCfg'].get()
        conversionConf['outputCfg'] = self.guiVars['outputCfg'].get()
        conversionConf['vsyncCfg'] = True if self.guiVars['vsyncCfg'].get() == 1 else False
        conversionConf['preExtractGames'] = True if self.guiVars['preExtractGames'].get() == 1 else False
        conversionConf['downloadOnDemand'] = True if self.guiVars['downloadOnDemand'].get() == 1 else False
        conversionConf['mapper'] = self.guiVars['mapper'].get()

        games = [self.fullnameToGameDir.get(name) for name in self.selectedGamesValues.get()]

        for g in self.selectedGamesValues.get():
            if self.fullnameToGameDir.get(g) is None:
                self.logger.log(
                    "Game data not found for %s\nIf you used a v4 selection, some games names may have changed in v5" % g,
                    self.logger.ERROR)

        self.logger.log(str(len(games)) + ' game(s) selected for conversion')

        collectionVersion = util.validCollectionPath(collectionDir)
        if collectionVersion is None:
            self.logger.log("%s doesn't seem to be a valid collection folder" % collectionDir)
        else:
            exoConverter = ExoConverter(games, self.cache, self.scriptDir, collectionVersion, collectionDir, outputDir,
                                        conversionType, useLongFolderNames, useGenreSubFolders, conversionConf, self.fullnameToGameDir,
                                        partial(self.postProcess), self.logger)
            _thread.start_new(exoConverter.convertGames, ())

    # Set enabled/disabled state for a component
    @staticmethod
    def __setComponentState__(component, state):
        if component is not None:
            component['state'] = state

    # Handles state of all the components based on UI status
    def __handleComponentsState__(self, clickedProcess):
        collectionVersion = self.guiVars['collectionVersion'].get()
        mainButtons = [self.verifyButton, self.saveButton, self.proceedButton]
        entryComponents = [self.collectionEntry, self.outputEntry, self.selectCollectionDirButton,
                           self.selectOutputDirButton]
        expertComponents = [self.mountPrefixEntry, self.fullResolutionCfgEntry, self.rendererCfgEntry,
                            self.outputCfgEntry]
        otherComponents = [self.exoGamesListbox, self.selectedGamesListbox, self.selectGameButton,
                           self.deselectGameButton, self.selectAllGamesButton, self.unselectAllGamesButton,
                           self.filterEntry,
                           self.conversionTypeComboBox,
                           self.useGenreSubFolderCheckButton,
                           self.mapperComboBox, self.vsyncCfgCheckButton, self.debugModeCheckButton,
                           self.expertModeCheckButton,
                           self.loadCustomButton, self.saveCustomButton, self.selectionPathEntry,
                           self.selectSelectionPathButton,
                           self.preExtractGamesCheckButton, self.downloadOnDemandCheckButton, self.longGameFolderCheckButton]

        if clickedProcess or collectionVersion == 'None':
            [self.__setComponentState__(c, 'disabled' if clickedProcess else 'normal') for c in entryComponents]
            [self.__setComponentState__(c, 'disabled') for c in mainButtons + otherComponents + expertComponents]
        else:
            [self.__setComponentState__(c, 'disabled' if self.guiVars['expertMode'].get() != 1 else 'normal') for c in
             expertComponents]
            [self.__setComponentState__(c, 'normal') for c in mainButtons + otherComponents + entryComponents]
            self.__setComponentState__(self.preExtractGamesCheckButton,
                                       'normal' if self.guiVars['conversionType'].get() == util.mister else 'disabled')
            self.__setComponentState__(self.longGameFolderCheckButton,
                                       'normal' if self.guiVars['conversionType'].get() == util.batocera or self.guiVars['conversionType'].get() == util.retrobat else 'disabled')

    def postProcess(self):
        self.__unselectAll__()
        self.__handleComponentsState__(False)

    # Console Frame    
    def __drawConsole__(self):
        self.consoleFrame = Tk.Frame(self.root, padx=10)
        self.consoleFrame.grid(column=0, row=5, sticky="EW", pady=5)
        self.consoleFrame.grid_columnconfigure(0, weight=1)
        self.logTest = Tk.Text(self.consoleFrame, height=22, state='disabled', wrap='word', background='black',
                               foreground='yellow')
        self.logTest.grid(column=0, row=0, sticky="EW")
        self.logTest.tag_config('ERROR', background='black', foreground='red')
        self.logTest.tag_config('WARNING', background='black', foreground='orange')
        self.logTest.tag_config('INFO', background='black', foreground='yellow')
        self.scrollbar = Tk.Scrollbar(self.consoleFrame, orient=Tk.VERTICAL, command=self.logTest.yview)
        self.scrollbar.grid(column=1, row=0, sticky=(Tk.N, Tk.S))
        self.logTest['yscrollcommand'] = self.scrollbar.set
        self.logTest.after(10, self.__updateConsoleFromQueue__)

    # Grabs messages from logger queue
    def __updateConsoleFromQueue__(self):
        while not self.logger.log_queue.empty():
            line = self.logger.log_queue.get()
            self.__writeToConsole__(line)
            self.root.update_idletasks()
        self.logTest.after(10, self.__updateConsoleFromQueue__)

    # Write message to console    
    def __writeToConsole__(self, msg):
        numlines = self.logTest.index('end - 1 line').split('.')[0]
        self.logTest['state'] = 'normal'
        if numlines == 24:
            self.logTest.delete(1.0, 2.0)
        previousLine = self.logTest.get('end-1c linestart', 'end-1c')
        # handle progress bar
        if msg[1] and previousLine.startswith('    [') and previousLine.endswith(']'):
            self.logTest.delete('end-1c linestart', 'end')

        if self.logTest.index('end-1c') != '1.0':
            self.logTest.insert('end', '\n')
        self.logTest.insert('end', msg[2], msg[0])
        self.logTest.see(Tk.END)
        self.logTest['state'] = 'disabled'
