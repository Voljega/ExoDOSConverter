import tkinter as Tk
from operator import attrgetter
import tkinter.font as Font
import wckToolTips
import conf,util
import os,shutil, platform
from exodosconverter import ExoDOSConverter
from metadatahandler import MetadataHandler
import _thread

class ExoGUI() :
    
    DEFAULT_FONT_SIZE = 9 
    
    def __init__(self,scriptDir,logger,title) :        
        self.scriptDir = scriptDir
        self.setKey='exo'
        self.cache = None
        self.needsCacheRefresh = False;
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
        
    def drawMainframe(self) :
        self.mainFrame = Tk.Frame(self.root,padx=10,pady=0)
        self.mainFrame.grid(column=0,row=1,sticky="EW",pady=5)
        self.mainFrame.grid_columnconfigure(0, weight=1)
        self.drawPathsFrame()
        self.drawSelectionFrame()        
        self.drawButtonsFrame()
        self.drawConsole()
        
    def drawPathsFrame(self) :
        # Romsets frame
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
        entry = Tk.Entry(self.pathsFrame, textvariable=self.guiVars['collectionDir'])
        entry.grid(column=1, row=setRow, padx=5,sticky=("WE"))
        setRow = setRow + 1
        
        outputDirLabel = Tk.Label(self.pathsFrame, text=self.guiStrings['outputDir'].label)
        wckToolTips.register(outputDirLabel, self.guiStrings['outputDir'].help)
        outputDirLabel.grid(column=0, row=setRow, padx=5,sticky=(Tk.W))
        self.guiVars['outputDir'] = Tk.StringVar()
        self.guiVars['outputDir'].set(self.configuration['outputDir'])
        outputEntry = Tk.Entry(self.pathsFrame, textvariable=self.guiVars['outputDir'])
        outputEntry.grid(column=1, row=setRow, columnspan=5,padx=5,sticky="WE")    
    
    def handleCollectionFolder(self,*args) :
        collectionDir = self.guiVars['collectionDir'].get()
        
        #TODO better test here with all subfolders and differenciation between v4 and v5 ?
        # and maybe an error message somewhere
        if not os.path.isdir(collectionDir) :
            self.logger.log("%s is not a directory or doesn't exist" %collectionDir)
            self.exodosGamesValues.set([])
            self.leftListLabel.set(self.guiStrings['leftList'].label+' (0)')
            self.exodosGamesListbox['state']='disabled'
            self.selectedGamesListbox['state']='disabled'
            self.selectGameButton['state']='disabled'
            self.deselectGameButton['state']='disabled'
        else :
            # Do not rebuild cache on first refresh of the value
            if self.needsCacheRefresh is True :            
                util.cleanCache(self.scriptDir)
            else :
               self.needsCacheRefresh = True 
            self.cache = util.buildCache(self.scriptDir,collectionDir,self.logger)
            self.logger.log("Loading exoDOS games list, this might take a while ...")
            #TODO thread issue on first launch, nothing is displayed for full collection
            self.fullnameToGameDir = util.fullnameToGameDir(collectionDir)
            self.exodosGamesValues.set(sorted(list(self.fullnameToGameDir.keys())))
            self.leftListLabel.set(self.guiStrings['leftList'].label+' ('+str(len(self.fullnameToGameDir.keys()))+')')
            self.exodosGamesListbox['state']='normal'
            self.selectedGamesListbox['state']='normal'
            self.selectGameButton['state']='normal'
            self.deselectGameButton['state']='normal'
        
    
    def drawSelectionFrame(self) :
        
        self.selectionFrame = Tk.LabelFrame(self.mainFrame,padx=10,pady=5)
        self.selectionFrame.grid(column=0,row=1,sticky="EW",pady=5)
        self.selectionFrame.grid_columnconfigure(0, weight=1)
        
        self.leftFrame = Tk.Frame(self.selectionFrame)
        self.leftFrame.grid(column=0,row=0,sticky="W",pady=5)
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
        self.buttonsColumnFrame.grid(column=1,row=0,pady=5)
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
        self.rightFrame.grid(column=2,row=0,sticky="E",pady=5)
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
        
    def clickLeft(self) :
        selectedOnRight = self.selectedGamesListbox.curselection()
        for sel in reversed(selectedOnRight) :
            self.selectedGamesListbox.delete(sel)
            
        self.selectedGamesListbox.selection_clear(0, Tk.END)
        self.rightListLabel.set(self.guiStrings['rightList'].label+' ('+str(len(self.selectedGamesValues.get()))+')')
        
    def clickRight(self) :        
        selectedOnLeft = [self.exodosGamesListbox.get(int(item)) for item in self.exodosGamesListbox.curselection()]
        alreadyOnRight = self.selectedGamesValues.get()
        for sel in selectedOnLeft :
            if sel not in alreadyOnRight :
                self.selectedGamesListbox.insert(Tk.END, sel)
        self.selectedGamesValues.set(sorted(self.selectedGamesValues.get()))
        
        self.exodosGamesListbox.selection_clear(0, Tk.END)
        self.rightListLabel.set(self.guiStrings['rightList'].label+' ('+str(len(self.selectedGamesValues.get()))+')')
        
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
        
    def clickSave(self) :
        self.logger.log ('\n<--------- Saving configuration --------->')
        self.saveConfFile()
        self.saveConfInMem()    
    
    def saveConfFile(self) :        
        confBackupFilePath = os.path.join(self.scriptDir,util.confDir,util.getConfBakFilename(self.setKey))
        if os.path.exists(confBackupFilePath) :
            os.remove(confBackupFilePath)
        shutil.copy2(os.path.join(self.scriptDir,util.confDir,util.getConfFilename(self.setKey)),os.path.join(self.scriptDir,util.confDir,util.getConfBakFilename(self.setKey)))
        confFile = open(os.path.join(self.scriptDir,util.confDir,util.getConfFilename(self.setKey)),"w",encoding="utf-8")
        listKeys = sorted(self.guiStrings.values(), key=attrgetter('order'))
        for key in listKeys :
            if key.id not in ['verify','save','proceed','confirm','left','right','leftList','rightList'] :
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

    def clickVerify(self) :
        self.logger.log('\n<--------- Verify '+self.setKey+' Parameters --------->')
        error = False
        for key in ['outputDir','collectionDir'] :
            if not os.path.exists(self.guiVars[key].get()) :
                error = True
                self.logger.log(key +' folder does not exist')
            
        if not error :
            self.logger.log('All Good!')

    def clickProceed(self) :
        self.logger.log ('\n<--------- Saving '+self.setKey+' configuration --------->')        
        self.verifyButton['state'] = 'disabled'
        self.saveButton['state'] = 'disabled'
        self.proceedButton['state'] = 'disabled'
        self.exodosGamesListbox['state']='disabled'
        self.selectedGamesListbox['state']='disabled'
        self.selectGameButton['state']='disabled'
        self.deselectGameButton['state']='disabled'
        self.logger.log('\n<--------- Starting '+self.setKey+' Process --------->')
        collectionDir = self.guiVars['collectionDir'].get()
        outputDir = self.guiVars['outputDir'].get()
        gamesDir = os.path.join(collectionDir,"eXoDOS","Games")
        gamesDosDir = os.path.join(gamesDir,"!dos")
        games = [self.fullnameToGameDir.get(name) for name in self.selectedGamesValues.get()]
        
        if not os.path.isdir(gamesDir) or not os.path.isdir(gamesDosDir) :
            self.logger.log("%s doesn't seem to be a valid ExoDOSCollection folder" %collectionDir)
        else :
            # TODO Move metadataHandler in exoDOSConverter ?            
            metadataHandler = MetadataHandler(collectionDir, self.cache,self.logger)
            exoDOSConverter = ExoDOSConverter(games, os.path.join(collectionDir,'eXoDOS'), gamesDosDir, outputDir, metadataHandler,self.logger)
            _thread.start_new(exoDOSConverter.convertGames,())
        
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
    
    def updateConsoleFromQueue(self):        
        while not self.logger.log_queue.empty():
            line = self.logger.log_queue.get()            
            self.writeToConsole(line)
            self.root.update_idletasks()
        self.logTest.after(10,self.updateConsoleFromQueue)
        
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