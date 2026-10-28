from tkinter import ttk
import tkinter as Tk
import wckToolTips
import os
import webbrowser


class SettingsGUI:
    """Parameters of the application itself, and the way to support it"""

    DONATE_URL = 'https://www.paypal.com/donate?hosted_button_id=LEAH843NKNG72'
    DONATE_IMAGE = 'btn_donateCC_LG.gif'

    def __init__(self, frame, gui):
        self.frame = frame
        self.gui = gui

    def draw(self):
        themeFrame = ttk.LabelFrame(self.frame, text='Appearance', padding=(10, 5))
        themeFrame.grid(column=0, row=0, sticky="EW", pady=5)
        label = ttk.Label(themeFrame, text='Theme')
        wckToolTips.register(label, 'Colors of the application, applied immediately')
        label.grid(column=0, row=0, sticky="W", pady=5)
        themes = self.gui.THEMES
        self.themeVar = Tk.StringVar(value=next(name for name, theme in themes.items() if theme == self.gui.theme))
        comboBox = ttk.Combobox(themeFrame, state="readonly", width=15, textvariable=self.themeVar,
                                values=list(themes))
        comboBox.grid(column=1, row=0, sticky="W", padx=10, pady=5)
        comboBox.bind('<<ComboboxSelected>>', self.__changeTheme)
        self.__drawDonate()

    def __drawDonate(self):
        donateFrame = ttk.LabelFrame(self.frame, text='Donate', padding=(10, 5))
        donateFrame.grid(column=0, row=1, sticky="EW", pady=5)
        ttk.Label(donateFrame, text='eXoConverter is free, if it is useful to you, you can support its development.') \
            .grid(column=0, row=0, sticky="W", pady=5)
        imagePath = os.path.join(self.gui.scriptDir, 'data', 'images', self.DONATE_IMAGE)
        if os.path.exists(imagePath):
            # the official PayPal donate button
            self.donateImage = Tk.PhotoImage(file=imagePath)
            button = ttk.Label(donateFrame, image=self.donateImage, cursor='hand2')
            button.bind('<Button-1>', lambda event: webbrowser.open(self.DONATE_URL))
        else:
            button = ttk.Button(donateFrame, text='Donate with PayPal', command=lambda: webbrowser.open(self.DONATE_URL))
        button.grid(column=0, row=1, sticky="W", pady=5)
        wckToolTips.register(button, 'Open the PayPal donation page in your browser')

    def __changeTheme(self, event):
        self.gui.changeTheme(self.gui.THEMES[self.themeVar.get()])
