import tkinter as Tk
from tkinter import ttk,messagebox
from operator import attrgetter
import tkinter.font as Font
import wckToolTips
import conf,util
import os,shutil, platform
from exodosconverter import ExoDOSConverter
import _thread

# Main GUI
class ExoGUI() :
    
    DEFAULT_FONT_SIZE = 9 
    
    def __init__(self,scriptDir,logger,title) :        
        self.scriptDir = scriptDir
        self.setKey='exo'
        self.cache = None
        self.needsCacheRefresh = False
        # TODO create conf file from guiStrings if it doesn't exist and do not ship it with tool anymore 
        self.configuration = conf.loadConf(os.path.join(self.scriptDir,util.confDir,util.getConfFilename(self.setKey)))
        self.guiVars = dict()
        self.guiStrings = util.loadUIStrings(self.scriptDir, util.getGuiStringsFilename(self.setKey))        
        
        self.window = Tk.Tk()
        self.window.resizable(False,False)        
        self.startFontSize = self.DEFAULT_FONT_SIZE        
        
        if platform.system() == 'Windows' :
            self.window.iconbitmap('exodosicon.ico')
            
        self.setFontSize(self.startFontSize)
        self.window.title(title)        
        self.logger = logger
        self.fullnameToGameDir = dict()

    def draw(self) :
        self.root = Tk.Frame(self.window,padx=10,pady=5)
        self.root.grid(column=0,row=0)
        self.drawMainframe()
        self.window.mainloop()
        
    def setFontSize(self, value) :        
        default_font = Font.nametofont("TkDefaultFont")
        default_font.configure(size=value)
        text_font = Font.nametofont("TkTextFont")
        text_font.configure(size=value)
        fixed_font = Font.nametofont("TkFixedFont")
        fixed_font.configure(size=value)
    
    # Main mama Frame    
    def drawMainframe(self) :
        self.mainFrame = Tk.Frame(self.root,padx=10,pady=0)
        self.mainFrame.grid(column=0,row=1,sticky="EW",pady=5)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        self.drawPathsFrame()
        self.drawConfigurationFrame()
        self.drawSelectionFrame()        
        self.drawButtonsFrame()
        self.drawConsole()
    
    # Paths frame    
    def drawPathsFrame(self) :
        self.pathsFrame = Tk.LabelFrame(self.mainFrame,text="Your Paths",padx=10,pady=5)
        self.pathsFrame.grid(column=0,row=0,sticky="EW",pady=5)
        self.pathsFrame.grid_columnconfigure(1, weight=1)
        setRow = 0
        
        label = Tk.Label(self.pathsFrame, text=self.guiStrings['collectionDir'].label)
        wckToolTips.register(label, self.guiStrings['collectionDir'].help)
        label.grid(column=0, row=setRow, padx=5,sticky="W")
        self.guiVars['collectionDir'] = Tk.StringVar()
        self.guiVars['collectionDir'].set(self.configuration['collectionDir'])
        self.guiVars['collectionDir'].trace_add("write", self.handleCollectionFolder)
        self.collectionEntry = Tk.Entry(self.pathsFrame, textvariable=self.guiVars['collectionDir'])
        self.collectionEntry.grid(column=1, row=setRow, padx=5,sticky=("WE"))
        setRow = setRow + 1
        
        outputDirLabel = Tk.Label(self.pathsFrame, text=self.guiStrings['outputDir'].label)
        wckToolTips.register(outputDirLabel, self.guiStrings['outputDir'].help)
        outputDirLabel.grid(column=0, row=setRow, padx=5,sticky=(Tk.W))
        self.guiVars['outputDir'] = Tk.StringVar()
        self.guiVars['outputDir'].set(self.configuration['outputDir'])
        self.outputEntry = Tk.Entry(self.pathsFrame, textvariable=self.guiVars['outputDir'])
        self.outputEntry.grid(column=1, row=setRow, columnspan=5,padx=5,sticky="WE")
    
    # Configuration Frame    
    def drawConfigurationFrame(self) :
        self.configurationFrame = Tk.LabelFrame(self.mainFrame,text="Configuration",padx=10,pady=5)
        self.configurationFrame.grid(column=0,row=1,sticky="EW",pady=5)
        
        self.conversionTypeLabel = Tk.Label(self.configurationFrame, text=self.guiStrings['conversionType'].label)
        wckToolTips.register(self.conversionTypeLabel, self.guiStrings['conversionType'].help)
        self.conversionTypeLabel.grid(column=0, row=0,sticky="W",pady=5)        
        self.guiVars['conversionType'] = Tk.StringVar()
        self.guiVars['conversionType'].set(self.configuration['conversionType'])
        self.conversionTypeComboBox = ttk.Combobox(self.configurationFrame, state="readonly", textvariable=self.guiVars['conversionType'])
        self.conversionTypeComboBox.grid(column=1,row=0, sticky="W",pady=5,padx=5)
        self.conversionTypeValues = util.conversionTypes.copy()
        self.conversionTypeComboBox['values'] = self.conversionTypeValues
        
        self.exodosVersionLabel = Tk.Label(self.configurationFrame, text=self.guiStrings['exodosVersion'].label)
        wckToolTips.register(self.exodosVersionLabel, self.guiStrings['exodosVersion'].help)
        self.exodosVersionLabel.grid(column=2, row=0,sticky="W",pady=5)        
        self.guiVars['exodosVersion'] = Tk.StringVar()
        self.guiVars['exodosVersion'].set(self.configuration['exodosVersion'])
        self.exodosVersionComboBox = ttk.Combobox(self.configurationFrame, state="readonly", textvariable=self.guiVars['exodosVersion'])
        self.exodosVersionComboBox.grid(column=3,row=0, sticky="W",pady=5,padx=5)
        self.exodosVersionValues = util.exodosVersions.copy()
        self.exodosVersionComboBox['values'] = self.exodosVersionValues
        
        self.guiVars['genreSubFolders'] = Tk.IntVar()
        self.guiVars['genreSubFolders'].set(self.configuration['genreSubFolders'])        
        self.useGenreSubFolderCheckButton = Tk.Checkbutton(self.configurationFrame,text=self.guiStrings['genreSubFolders'].label, variable=self.guiVars['genreSubFolders'], onvalue=1, offvalue = 0)
        wckToolTips.register(self.useGenreSubFolderCheckButton, self.guiStrings['genreSubFolders'].help)
        self.useGenreSubFolderCheckButton.grid(column=5,row=0,sticky="W",pady=5,padx=5)
    
    # Listener for collection path modifications
    def handleCollectionFolder(self,*args) :
        collectionDir = self.guiVars['collectionDir'].get()
        
        #TODO better test here with all subfolders and differenciation between v4 and v5 ?
        # and maybe an error message somewhere
        if not os.path.isdir(collectionDir) or not util.validCollectionPath(collectionDir) :
            self.logger.log("%s is not a directory, doesn't exist, or is not a valid ExoDOS Collection directory" %collectionDir)
            self.exodosGamesValues.set([])
            self.leftListLabel.set(self.guiStrings['leftList'].label+' (0)')
            self.exodosGamesListbox['state']='disabled'
            self.selectedGamesListbox['state']='disabled'
            self.selectGameButton['state']='disabled'
            self.deselectGameButton['state']='disabled'
            self.filterEntry['state']='disabled'
        else :
            # Do not rebuild cache on first refresh of the value
            if self.needsCacheRefresh is True :            
                util.cleanCache(self.scriptDir)
            else :
               self.needsCacheRefresh = True 
            self.cache = util.buildCache(self.scriptDir,collectionDir,self.logger)
            self.logger.log("Loading exoDOS games list, this might take a while ...")
            self.guiVars['filter'].set('')
            #TODO thread issue on first launch, nothing is displayed for full collection
            self.fullnameToGameDir = util.fullnameToGameDir(collectionDir)
            self.exodosGamesValues.set(sorted(list(self.fullnameToGameDir.keys())))
            self.leftListLabel.set(self.guiStrings['leftList'].label+' ('+str(len(self.fullnameToGameDir.keys()))+')')
            self.exodosGamesListbox['state']='normal'
            self.selectedGamesListbox['state']='normal'
            self.selectGameButton['state']='normal'
            self.deselectGameButton['state']='normal'
            self.filterEntry['state']='normal'            
    
    # Listener for filter entry modification
    def filterGamesList  (self,*args) :
        filterValue = self.guiVars['filter'].get()
        filteredGameslist = [g for g in self.fullnameToGameDir.keys() if filterValue.lower() in g.lower()]        
        self.exodosGamesListbox.selection_clear(0, Tk.END)        
        self.exodosGamesValues.set(sorted(filteredGameslist))
        self.leftListLabel.set(self.guiStrings['leftList'].label+' ('+str(len(self.exodosGamesValues.get()))+')')
    
    # Selection Frame
    def drawSelectionFrame(self) :        
        self.selectionFrame = Tk.LabelFrame(self.mainFrame,padx=10,pady=5)
        self.selectionFrame.grid(column=0,row=2,sticky="EW",pady=5)
        self.selectionFrame.grid_columnconfigure(0, weight=1)
        
        self.guiVars['filter'] = Tk.StringVar()
        self.guiVars['filter'].set('')
        self.guiVars['filter'].trace_add("write", self.filterGamesList)
        self.filterEntry = Tk.Entry(self.selectionFrame,textvariable=self.guiVars['filter'])
        self.filterEntry.grid(column=0,row=0,sticky='W')
        wckToolTips.register(self.filterEntry, self.guiStrings['filter'].help)
        
        self.leftFrame = Tk.Frame(self.selectionFrame)
        self.leftFrame.grid(column=0,row=1,sticky="W",pady=5)
        self.leftFrame.grid_columnconfigure(0, weight=3)
        self.leftListLabel = Tk.StringVar(value=self.guiStrings['leftList'].label)
        label = Tk.Label(self.leftFrame, textvariable=self.leftListLabel)
        wckToolTips.register(label, self.guiStrings['leftList'].help)
        label.grid(column=0, row=0, sticky="W")
        self.exodosGamesValues = Tk.Variable(value=[])
        self.exodosGamesListbox = Tk.Listbox(self.leftFrame, listvariable=self.exodosGamesValues , selectmode=Tk.EXTENDED, width=70)
        self.exodosGamesListbox.grid(column=0,row=1,sticky="W",pady=5)
        self.exodosGamesListbox.grid_rowconfigure(0, weight=3)
        
        scrollbarLeft = Tk.Scrollbar(self.leftFrame, orient=Tk.VERTICAL,command=self.exodosGamesListbox.yview)
        scrollbarLeft.grid(column=1,row=1,sticky=(Tk.N,Tk.S))
        self.exodosGamesListbox['yscrollcommand'] = scrollbarLeft.set
        
        self.buttonsColumnFrame = Tk.Frame(self.selectionFrame,padx=10)
        self.buttonsColumnFrame.grid(column=1,row=1,pady=5)
        self.buttonsColumnFrame.grid_columnconfigure(1, weight = 1)
        emptyFrame = Tk.Frame(self.buttonsColumnFrame,padx=10)        
        emptyFrame.grid(column=0,row=0,pady=5)    
        self.selectGameButton = Tk.Button(self.buttonsColumnFrame,text='->', command=self.clickRight)
        wckToolTips.register(self.selectGameButton, self.guiStrings['right'].help)
        self.selectGameButton.grid(column=0,row=3,padx=3)
        emptyFrame = Tk.Frame(self.buttonsColumnFrame,padx=10)
        emptyFrame.grid(column=0,row=4,pady=5)
        self.deselectGameButton = Tk.Button(self.buttonsColumnFrame,text='<-', command=self.clickLeft)
        wckToolTips.register(self.deselectGameButton, self.guiStrings['left'].help)
        self.deselectGameButton.grid(column=0,row=7,padx=3)
        emptyFrame = Tk.Frame(self.buttonsColumnFrame,padx=10)
        emptyFrame.grid(column=0,row=8,pady=5)
        
        self.rightFrame = Tk.Frame(self.selectionFrame)
        self.rightFrame.grid(column=2,row=1,sticky="E",pady=5)
        self.rightFrame.grid_columnconfigure(2, weight=3)
        self.rightListLabel = Tk.StringVar(value=self.guiStrings['rightList'].label)
        label = Tk.Label(self.rightFrame, textvariable=self.rightListLabel)
        wckToolTips.register(label, self.guiStrings['rightList'].help)
        label.grid(column=0, row=0, sticky="W")
        self.selectedGamesValues = Tk.Variable(value=[])        
        self.selectedGamesListbox = Tk.Listbox(self.rightFrame, listvariable=self.selectedGamesValues ,selectmode=Tk.EXTENDED, width=70)
        self.selectedGamesListbox.grid(column=0,row=1,sticky="E",pady=5)
        self.selectedGamesListbox.grid_columnconfigure(0, weight=3)
        
        scrollbarRight = Tk.Scrollbar(self.rightFrame, orient=Tk.VERTICAL,command=self.selectedGamesListbox.yview)
        scrollbarRight.grid(column=1,row=1,sticky=(Tk.N,Tk.S))
        self.selectedGamesListbox['yscrollcommand'] = scrollbarRight.set
        
        self.handleCollectionFolder()
    
    # Listener to remove game from selection    
    def clickLeft(self) :
        selectedOnRight = self.selectedGamesListbox.curselection()
        for sel in reversed(selectedOnRight) :
            self.selectedGamesListbox.delete(sel)
            
        self.selectedGamesListbox.selection_clear(0, Tk.END)
        self.rightListLabel.set(self.guiStrings['rightList'].label+' ('+str(len(self.selectedGamesValues.get()))+')')
    
    # Listener to ad game to selection 
    def clickRight(self) :        
        selectedOnLeft = [self.exodosGamesListbox.get(int(item)) for item in self.exodosGamesListbox.curselection()]
        alreadyOnRight = self.selectedGamesValues.get()
        for sel in selectedOnLeft :
            if sel not in alreadyOnRight :
                self.selectedGamesListbox.insert(Tk.END, sel)
        self.selectedGamesValues.set(sorted(self.selectedGamesValues.get()))
        
        self.exodosGamesListbox.selection_clear(0, Tk.END)
        self.rightListLabel.set(self.guiStrings['rightList'].label+' ('+str(len(self.selectedGamesValues.get()))+')')
    
    # Action buttons frame    
    def drawButtonsFrame(self) :
        self.buttonsFrame = Tk.Frame(self.mainFrame,padx=10)
        self.buttonsFrame.grid(column=0,row=3,sticky="EW",pady=5)
        emptyFrame = Tk.Frame(self.buttonsFrame,padx=10,width=400)
        emptyFrame.grid(column=0,row=0,sticky="NEWS",pady=5)
        emptyFrame.grid_columnconfigure(0, weight=3)
        self.verifyButton = Tk.Button(self.buttonsFrame,text=self.guiStrings['verify'].label, command=self.clickVerify)
        wckToolTips.register(self.verifyButton, self.guiStrings['verify'].help)
        self.verifyButton.grid(column=1,row=0,sticky="EW",padx=3)
        self.saveButton = Tk.Button(self.buttonsFrame,text=self.guiStrings['save'].label, command=self.clickSave)
        wckToolTips.register(self.saveButton, self.guiStrings['save'].help)
        self.saveButton.grid(column=2,row=0,sticky="EW",padx=3)
        self.proceedButton = Tk.Button(self.buttonsFrame,text=self.guiStrings['proceed'].label, command=self.clickProceed)
        wckToolTips.register(self.proceedButton, self.guiStrings['proceed'].help)
        self.proceedButton.grid(column=3,row=0,sticky="EW",padx=3)
        emptyFrame = Tk.Frame(self.buttonsFrame,padx=10, width=350)
        emptyFrame.grid(column=4,row=0,sticky="NEWS",pady=5)
        emptyFrame.grid_columnconfigure(4, weight=3)
    
    # Listener for Save button    
    def clickSave(self) :
        self.logger.log ('\n<--------- Saving configuration --------->')
        self.saveConfFile()
        self.saveConfInMem()    
    
    # Saves to conf file
    def saveConfFile(self) :        
        confBackupFilePath = os.path.join(self.scriptDir,util.confDir,util.getConfBakFilename(self.setKey))
        if os.path.exists(confBackupFilePath) :
            os.remove(confBackupFilePath)
        shutil.copy2(os.path.join(self.scriptDir,util.confDir,util.getConfFilename(self.setKey)),os.path.join(self.scriptDir,util.confDir,util.getConfBakFilename(self.setKey)))
        confFile = open(os.path.join(self.scriptDir,util.confDir,util.getConfFilename(self.setKey)),"w",encoding="utf-8")
        listKeys = sorted(self.guiStrings.values(), key=attrgetter('order'))
        for key in listKeys :
            if key.id not in ['verify','save','proceed','confirm','left','right','leftList','rightList','filter'] :
                if key.help :
                        confFile.write('# ' + key.help.replace('#n','\n# ')+ '\n')
                if key.id == 'images' :
                    imagesValue = self.guiVars[self.guiStrings['images'].label+' #1'].get()
                    if self.guiStrings['images'].label+' #2' in self.guiVars :
                        imagesValue = imagesValue + '|' + self.guiVars[self.guiStrings['images'].label+' #2'].get()
                    confFile.write(key.id + ' = ' + imagesValue +'\n')         
                else :                
                    if key.id in self.guiVars :
                        confFile.write(key.id + ' = ' + str(self.guiVars[key.id].get())+'\n')            
        confFile.close()
        self.logger.log ('    Configuration saved in '+util.getConfFilename(self.setKey)+' file')    
    
    # Saves in memory
    def saveConfInMem(self) :
        listKeys = sorted(self.guiStrings.values(), key=attrgetter('order'))        
        for key in listKeys :
            if key.id not in ['verify','save','proceed','confirm','left','right','leftList','rightList'] :                
                if key.id == 'images' :
                    imagesValue = self.guiVars[self.guiStrings['images'].label+' #1'].get()
                    if self.guiStrings['images'].label+' #2' in self.guiVars :
                        imagesValue = imagesValue + '|' + self.guiVars[self.guiStrings['images'].label+' #2'].get()
                    self.configuration['images']=  imagesValue
                else :                
                    if key.id in self.guiVars :
                        self.configuration[key.id] = str(self.guiVars[key.id].get())
        self.logger.log('    Configuration saved in memory')       
    
    # Listener for Verify button
    def clickVerify(self) :
        self.logger.log('\n<--------- Verify '+self.setKey+' Parameters --------->')
        error = False
        for key in ['outputDir','collectionDir'] :
            if not os.path.exists(self.guiVars[key].get()) :
                error = True
                self.logger.log(key +' folder does not exist')
            
        if not error :
            self.logger.log('All Good!')
    
    # Listener for Proceed Button
    def clickProceed(self) :
        self.logger.log ('\n<--------- Saving '+self.setKey+' configuration --------->')        
        self.verifyButton['state'] = 'disabled'
        self.saveButton['state'] = 'disabled'
        self.proceedButton['state'] = 'disabled'
        self.exodosGamesListbox['state']='disabled'
        self.selectedGamesListbox['state']='disabled'
        self.selectGameButton['state']='disabled'
        self.deselectGameButton['state']='disabled'
        self.filterEntry['state']='disabled'
        self.conversionTypeComboBox['state']='disabled'
        self.exodosVersionComboBox['state']='disabled'
        self.useGenreSubFolderCheckButton['state']='disabled'
        self.collectionEntry['state']='disabled'
        self.outputEntry['state']='disabled'
        
        self.logger.log('\n<--------- Starting '+self.setKey+' Process --------->')
        #TODO see if there's a way to have more simpler parameters passed to converter and logging here, better simplify code in converter 
        collectionDir = self.guiVars['collectionDir'].get()
        conversionType = self.guiVars['conversionType'].get()
        useGenreSubFolders = True if self.guiVars['genreSubFolders'].get() == 1 else False
        outputDir = self.guiVars['outputDir'].get()
        #TODO better move this to converter when v5 is released and properly handle it, or move it to verify ? Also use messagebox
        gamesDir = os.path.join(collectionDir,"eXoDOS","Games")
        gamesDosDir = os.path.join(gamesDir,"!dos")
        games = [self.fullnameToGameDir.get(name) for name in self.selectedGamesValues.get()]
        
        if not os.path.isdir(gamesDir) or not os.path.isdir(gamesDosDir) :
            self.logger.log("%s doesn't seem to be a valid ExoDOSCollection folder" %collectionDir)
        else :
            exoDOSConverter = ExoDOSConverter(games, self.cache, collectionDir, gamesDosDir, outputDir, conversionType, useGenreSubFolders,self.logger)
            _thread.start_new(exoDOSConverter.convertGames,())
    
    # Console Frame    
    def drawConsole(self) :
        self.consoleFrame = Tk.Frame(self.root, padx=10)
        self.consoleFrame.grid(column=0,row=5,sticky="EW",pady=5)
        self.consoleFrame.grid_columnconfigure(0, weight=1)
        self.logTest = Tk.Text(self.consoleFrame, height=25, state='disabled', wrap='word',background='black',foreground='yellow')
        self.logTest.grid(column=0,row=0,sticky="EW")
        self.scrollbar = Tk.Scrollbar(self.consoleFrame, orient=Tk.VERTICAL,command=self.logTest.yview)
        self.scrollbar.grid(column=1,row=0,sticky=(Tk.N,Tk.S))
        self.logTest['yscrollcommand'] = self.scrollbar.set
        self.logTest.after(10,self.updateConsoleFromQueue)
    
    # Grabs messages from logger queue
    def updateConsoleFromQueue(self):        
        while not self.logger.log_queue.empty():
            line = self.logger.log_queue.get()            
            self.writeToConsole(line)
            self.root.update_idletasks()
        self.logTest.after(10,self.updateConsoleFromQueue)
    
    # Write message to console    
    def writeToConsole(self, msg):                
        numlines = self.logTest.index('end - 1 line').split('.')[0]
        self.logTest['state'] = 'normal'
        if numlines==24:
            self.logTest.delete(1.0, 2.0)
        if self.logTest.index('end-1c')!='1.0':
            self.logTest.insert('end', '\n')
        self.logTest.insert('end', msg)
        self.logTest.see(Tk.END)
        self.logTest['state'] = 'disabled'