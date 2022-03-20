from utils import *


class Editor(object):
    WINDOW_WIDTH, WINDOW_HEIGHT = 800, 500
    def __init__(self):
        
        self._screenName = 'PYTEXT EDIT'# name of application
        self._fileTypes = [("Text Documents", "*.txt"),
                           ("Python Files", ("*.py", ".pyw")),
                           ("C Files", "*.c"),
                           ("C++ Files", "*.cpp"),
                           ("Java Files", "*.java"),
                           ("Go Files", '*.go'),
                           ("All Files", "*.*")]

        #add more file types later

        self._currentOpenFile = None
        
        self._editorWindow = Window(self._screenName, PATH_TO_ICON, (Editor.WINDOW_WIDTH, Editor.WINDOW_HEIGHT))
        

        #most of the indisputable attributes of the Standard text are defined in the class itself
        #to reduce ambiguity
        'explicitely defining some default attributes as well'
        
        self._textArea = StandardText(self._editorWindow, bg='#FFFFFF', fg = '#000000')
        self._applyBindings()
        self._initWindow()
        if len(sys.argv)>1:
            self._currentOpenFile = sys.argv[1]
            self.__openFileWithSelf()

    def __openFileWithSelf(self):
        '''
        there is a windows option that says open with
        this option will provide the filename as a command line arguments
        these arguments then can be used by the program to open the file
        by using this special method specifically for it
        '''
        try:
            with open(self._currentOpenFile, 'r') as file:
                content = file.read()
                self._textArea.delete("1.0", tkinter.END)  ##clear the text area
                self._textArea.insert(tkinter.END, content) ##after deletion END==1.0
                self._textArea.update_status(None)
            self._editorWindow.title(self._screenName+'  -  '+ os.path.basename(self._currentOpenFile))
        except UnicodeError:
            #if there is a problem opening the file
            self._editorWindow.bell()     ##<<<<<<------- check again
            messageBox.showinfo('{}'.format(self._screenName), 'File Format Not Supported!')
            self._currentOpenFile = None
        except (FileExistsError, FileNotFoundError):
            # if there is a problem opening the file
            self._editorWindow.bell()  ##<<<<<<------- check again
            messageBox.showerror('{}'.format(self._screenName), 'File Not Found!')
            self._currentOpenFile = None

                                      
    def _applyBindings(self):
        self._editorWindow.bind('<Control-s>', lambda event:self.__saveFile())
        self._editorWindow.bind('<Control-Shift-s>', lambda event:self.__saveFileAs())
        self._editorWindow.bind('<Control-n>', lambda event:self.__newFile())
        self._editorWindow.bind('<Control-o>', lambda event:self.__openFile())
        self._editorWindow.bind('<Control-p>', lambda event:self.__givePrintCommand())
        self._editorWindow.bind('<Control-w>', lambda event:self.__exit_window())
        self._editorWindow.bind('<F1>', lambda ev : self. __showHelp())
        self._editorWindow.bind('<Button-3>', self.right_click_popup)
        #also bind clicking anywhere in the window to updatting the status bar since it too can be affected
        #by actions in other parts of thw window such as creating a new file

        self._editorWindow.bind('<Button-1>', self._textArea.update_status)

    def _initWindow(self):
        self._createMenu()
        self._editorWindow.title(self._screenName+'  -  Untitled')
        self._textArea.pack(side = tkinter.LEFT, expand = True, fill = tkinter.BOTH)
        self._editorWindow.protocol("WM_DELETE_WINDOW", self._quitApplication)
        create_tool_tip(self.__optionsMenu, f'Configure {self._screenName} to suit you')
        '''
        The ev parameter in most of the methods are used in binding. will be removed if a betterv approach
        comes to mind
        '''
    def right_click_popup(self, ev):
        self.__create_context_menu()
        self._pop_up_menu.tk_popup(ev.x_root+10, ev.y_root+5)
        #or
        #self._pop_up_menu.post(ev.x_root, ev.y_root)

        
    def __create_context_menu(self):
        self._pop_up_menu = tkinter.Menu(self._editorWindow, tearoff = 0, font = ('times', 13))#, hidemargin = False)
    
        self._pop_up_menu.add_command(label="Undo               ", command=self._textArea.undo_event)
        
        self._pop_up_menu.add_command(label="Redo               ", command=self._textArea.redo_event)
   
        self._pop_up_menu.add_separator()
        self._pop_up_menu.add_command(label="Cut                ",command=self._textArea.cut_event) # to give a feature of copy
        self._pop_up_menu.add_command(label="Copy               ",command=self._textArea.copy_event)# to give a feature of copy
        self._pop_up_menu.add_command(label="Paste              ",command=self._textArea.paste_event)# to give a feature of copy
        self._pop_up_menu.add_command(label="Select All         ", command=self._textArea.select_all)
        self._pop_up_menu.add_command(label="Delete             ",command=self._textArea.delete_event)# to
        self._pop_up_menu.add_separator()
        self.ins_sub_menu = tkinter.Menu(master = self._pop_up_menu,font = ('elephant', 11, 'normal'), tearoff = 0)
        self.ins_sub_menu.add_command(label = 'Date/Time', command = self._textArea.insert_date)
        self.ins_sub_menu.add_command(label = 'File Name', command=self._insert_filename)
        self._pop_up_menu.add_cascade(label = 'Insert              ', menu = self.__insertSubMenu)
        


    def __newFile(self):
        if self._currentOpenFile is not None:
            #if user accepts to save before creating a new file
            #ignores the option of cancel, no and closing of window

            #first check if file is saved ie the content of the textarea is the same
            #as that of the file
            try:
                with open(self._currentOpenFile, 'r') as file:
                    if file.read() != self._textArea.get(1.0, tkinter.END+'-1c'):
                     #note that one newline character is always added to the text area and must be excluded in
                        #comparison
                        if messageBox.askyesnocancel(self._screenName, f"Do you want to save changes to '{self._currentOpenFile}'?"):
                            self.__saveFile()
            except (FileExistsError, FileNotFoundError):
                 #delibrately ignore 
                 pass

        self._editorWindow.title(f'{self._screenName}  -  Untitled')
        self._currentOpenFile = None
        self._textArea.delete(1.0, tkinter.END)#empty text area

        #status bar of the text area is forcefully updated since the Insert cursor would probably not be updated yet???
        #or ??????
        self._textArea.update_status()

    def __openFile(self):
        # first check if there is an open file
        if self._currentOpenFile is not None:
                        #first check if file is saved ie the content of the textarea is the same
            #as that of the file
            try:
                with open(self._currentOpenFile, 'r') as file:
                    if file.read() != self._textArea.get(1.0, tkinter.END+'-1c'):
                        #note that one newline character is always added to the text area and must be excluded in
                        #comparison
                        if messageBox.askyesnocancel(self._screenName, f"Do you want to save changes to '{self._currentOpenFile}'?"):
                            self.__saveFile()
            except (FileExistsError, FileNotFoundError):
                 #delibrately ignore 
                 pass
            else:
                return
            #there is an open file

        self._currentOpenFile = fileDialog.askopenfilename(title = 'Open File', initialdir = '..', defaultextension ='*.txt', filetypes = self._fileTypes)
        if self._currentOpenFile == '':
            self._currentOpenFile = None
            return #user cancelled the window
        try:
            with open(self._currentOpenFile, 'r') as file:
                content = file.read()
                self._textArea.delete("1.0", tkinter.END)  ##clear the text area
                self._textArea.insert(tkinter.END, content) ##after deletion END==1.0
                self._textArea.update_status(None)
            self._editorWindow.title(self._screenName+'  -  '+ os.path.basename(self._currentOpenFile))
        except UnicodeError:
            #if there is a problem opening the file
            self._editorWindow.bell()     ##<<<<<<------- check again
            self._currentOpenFile = None
            messageBox.showinfo('{}'.format(self._screenName), 'File Format Not Supported!')
        except (FileExistsError, FileNotFoundError):
            # if there is a problem opening the file
            self._editorWindow.bell()  ##<<<<<<------- check again
            self._currentOpenFile = None
            messageBox.showerror('{}'.format(self._screenName), 'File Not Found!')

            #update the status bar
            self._textArea.update_status

    def __saveFile(self):
        if self._currentOpenFile is None:
            self._currentOpenFile = fileDialog.asksaveasfilename(title = 'Save File', initialdir = '..', defaultextension=".txt", filetypes= self._fileTypes)
            if self._currentOpenFile == '':
                self._currentOpenFile = None
                return   ##user cancelled the file dialog
        try:
            with open(self._currentOpenFile, 'w') as file:
                file.write(self._textArea.get("1.0", tkinter.END))
            self._editorWindow.title(self._screenName+'  -  '+os.path.basename(self._currentOpenFile))
        except (FileExistsError, FileNotFoundError):#file can be deleted while working on it
            # if there is a problem opening the file
            self._editorWindow.bell()  ##<<<<<<------- check again
            messageBox.showerror('{}'.format(self._screenName), 'File No Longer Exists!')



    def __saveFileAs(self):   #save with different extension or a different name
        if self._currentOpenFile is None:#must save file first
            self._editorWindow.bell()  ##<<<<<<------- check again
            messageBox.showerror('{}'.format(self._screenName), 'File must be saved first!')
            return
        newfile = fileDialog.asksaveasfilename(title = 'Save File As', initialdir = '..', defaultextension=".txt", filetypes=self._fileTypes)
        if newfile == self._currentOpenFile:
            self._editorWindow.bell()  ##<<<<<<------- check again
            messageBox.showinfo('{}'.format(self._screenName), 'File already exists!')
            return

        #no need to use try block; error will not occur , at least as far as i know
        with open(newfile, 'w') as file:
            file.write(self._textArea.get("1.0", tkinter.END))


    def __saveFileCopyAs(self):#
        if self._currentOpenFile is None:#must save file first
            self._editorWindow.bell()  ##<<<<<<------- check again
            messageBox.showerror('{}'.format(self._screenName), 'File must be saved first!')
            return
        newdir = fileDialog.askdirectory(title = 'Save File Copy As', initialdir = '..',
                                   defaultextension=".txt", filetypes=self._fileTypes)

        #no need to use try block; error will not occur , at least as far as i know
        with open(os.path.join(newdir, 'copy of '+os.path.basename(self._currentOpenFile)),'w') as file:
            file.write(self._textArea.get("1.0", tkinter.END))


    def __exportToJson(self):
        '''
            will use json a built in module
            note that note all text data are suitable to convert to json
            will dispaly and error message if the conversion cannot take place

            :return None
        '''
        import json
        pass

    def __exportToRtf(self):
        '''
        RTF:Rich text format a general format for files that can be opened by crossplatform word
        processors
        simply creates a file with same name but changes the extension
        :return: None
        '''
        if self._currentOpenFile is not None:
            name, _ = os.path.splitext( self._currentOpenFile)  #extension is ignored
            try:
                with open(name+'.rtf', 'wb') as file:
                    file.write(self._textArea.get(1.0, tkinter.END))
            except Exception as e:
                messageBox.showerror('Fatal Error', 'Code : oxFDEFF289A\nAn error occured while generating file')
        else:
            messageBox.showinfo(f'{self._screenName} ', 'File must Be saved first!!!')
            #or a better message: "Save this file before proceeding!!"

    def __exportToPdf(self):
        if self._currentOpenFile is not None:
            #import pdfkit
            #pdfkit.

            with open(os.path.splitext( self._currentOpenFile)[0]+'.pdf' , "wb") as file:
                pass

    def __exportToDoc(self):

        if self._currentOpenFile is not None:
            import docx
            doc = docx.Document()
            text = self._textArea.get(1.0, tkinter.END)
            doc.add_paragraph(text)
            name, _ = os.path.splitext(self._currentOpenFile)  # extension is ignored
            doc.save(f'{name}.docx')
            #os.startfile(name+'.docx') #opens the file with the default word processor
        else:
            messageBox.showinfo(f'{self._screenName} ', 'File must Be saved first!!!')

    def  __givePrintCommand(self):
        pass

    def _quitApplication(self):#uses root.protocol and calls exit window
        '''
        write the new data to data file before shutting down the application
        :return:
        '''

        with open('config.json', 'w') as f:
            json.dump(config, f)

        if self._currentOpenFile is not None:
            save = messageBox.askyesnocancel(self._screenName,f"File '{self._currentOpenFile}' has been modified...\nDo you want to save changes?")
            if save=='yes':
                self.__saveFile()
            elif save is None:
                return 
        elif self._textArea.get(1.0, "end-1c"):
            save=messageBox.askyesnocancel(self._screenName, "Do you want to save changes to Untitled?")
            if save:
                self.__saveFile()
            elif save is None:
                return  #don't close app if prompt was cancelled or closed
            
        self._editorWindow.quit()
        self._editorWindow.destroy()
        sys.exit()


    def _insert_filename(self):
        if self._currentOpenFile is None:
            self._textArea.insert(tkinter.INSERT, 'Untitled')
        else:
            self._textArea.insert(tkinter.INSERT, self._currentOpenFile)
        self._textArea.update_status(None)
    #add menu Controls
    def _createMenu(self):
        standard_font = ('courier', 10, 'normal')
        self._menuBar = tkinter.Menu(master = self._editorWindow, tearoff = 0,font = standard_font) #menu can't be torn off
        #options activebackground, activeforeground, accelerator, background, bitmap, columnbreak, command,
        #font, foreground, hidemargin, image, indicatoron, label, menu, offvalue, onvalue, selector, selectimage
        #state, underline, value, variable
        self.__fileMenu = tkinter.Menu(self._menuBar,font = standard_font, tearoff = 0)
        #--------------File menu
       
        self.__fileMenu.add_command(label="New          Ctrl+N", command=self.__newFile) # "accelerator = '<Control-n>"
                    #               ,underline = 1,compound = LEFT,
                   #image = ImageTk.PhotoImage(Image.open(r'C:\Users\nfor\Desktop\icon\icons_pro\delete.ico').resize((64,64))))
                 # To open a already existing file
        self.__fileMenu.add_command(label="Open         Ctrl+O", command=self.__openFile)# To save current file
        self.__fileMenu.add_command(label="Save         Ctrl+S", command=self.__saveFile)
        self.__fileMenu.add_command(label="Save as      Ctrl+shift+S", command=self.__saveFileAs)
        self.__fileMenu.add_command(label="Save copy as           ", command=self.__saveFileCopyAs)

        self.__fileMenu.add_separator()

        self.__exportMenu = tkinter.Menu(self.__fileMenu, tearoff = 0,font = ('times', 12, 'normal'))
        self.__exportMenu.add_command(label='To JSON', command=self.__exportToJson)
        self.__exportMenu.add_command(label='To RTF', command=self.__exportToRtf)
        self.__exportMenu.add_command(label='To PDF', command=self.__exportToPdf)
        self.__exportMenu.add_command(label='To MS Word Doc.', command=self.__exportToDoc)
        self.__fileMenu.add_cascade(label = "Export", menu = self.__exportMenu)
        self.__fileMenu.add_separator()

        self.__fileMenu.add_command(label = 'Print        Ctrl+P', command = self.__givePrintCommand)
        self.__fileMenu.add_separator()

        self.__fileMenu.add_command(label="Exit         Ctrl+W", command= self._quitApplication) #for all
        
        self._menuBar.add_cascade(label="File    ",font = standard_font, menu=self.__fileMenu)# To give a feature of cut

        self.__editMenu = tkinter.Menu(self._menuBar,font = standard_font, tearoff = 0)
        #
        #--------------Edit Menu
        #
        self.__editMenu.add_command(label="Undo         Ctrl+Z", command=self._textArea.undo_event)
        self.__editMenu.add_command(label="Redo         Ctrl+Shift+Z", command=self._textArea.redo_event)
        self.__editMenu.add_separator()
        self.__editMenu.add_command(label="Cut          Ctrl+X", command=self._textArea.cut_event)# to give a feature of copy
        self.__editMenu.add_command(label="Copy         Ctrl+C",command=self._textArea.copy_event)# to give a feature of copy
        self.__editMenu.add_command(label="Paste        Ctrl+P",command=self._textArea.paste_event)# to give a feature of copy
        self.__editMenu.add_command(label="Select All   Ctrl+A", command=self._textArea.select_all)
        self.__editMenu.add_command(label="Delete       Del",command=self._textArea.delete_event)# to
        self.__editMenu.add_separator()
        self.__insertSubMenu = tkinter.Menu(master = self.__editMenu,font = ('elephant', 11, 'normal'), tearoff = 0)
        self.__insertSubMenu.add_command(label = 'Date/Time', command = self._textArea.insert_date)
        self.__insertSubMenu.add_command(label = 'File Name', command=self._insert_filename)
        self.__editMenu.add_cascade(label = 'Insert', menu = self.__insertSubMenu)
        self._menuBar.add_cascade(label="Edit    ",font = standard_font, menu=self.__editMenu)

        self.__searchMenu = tkinter.Menu(self._menuBar,font = standard_font, tearoff = 0)
        #
        #------search menu
        #

        self.__searchMenu.add_command(label = 'Find              Ctrl+F', command = self._textArea.find)
        self.__searchMenu.add_command(label = 'Find Next         Ctrl+G', command=self._textArea.findNext)
        self.__searchMenu.add_command(label = 'Find in Selection  ', command=self._textArea.findSel)
        self.__searchMenu.add_separator()
        self.__searchMenu.add_command(label='Replace           Ctrl+R', command=self._textArea.f_replace)
        self.__searchMenu.add_command(label='Goto Line ', command=self._textArea.gotoLine)
        self._menuBar.add_cascade(label="Search   ", menu=self.__searchMenu)

        
        self.__formatMenu = tkinter.Menu(self._menuBar,font = standard_font, tearoff = 0)
        #
        #------format menu
        #
        self.__formatMenu.add_command(label = 'Word Wrap', command = self._textArea.wordwrap)
        self.__formatMenu.add_separator()
        self.__formatMenu.add_command(label = 'Indent region    Ctrl+[', command = self._textArea.indent)
        self.__formatMenu.add_command(label = 'Dedent region    Ctrl+]', command=self._textArea.dedent)
        self.__formatMenu.add_command(label = 'Comment out      Alt+C', command=self._textArea.commentOut)
        self.__formatMenu.add_command(label = 'Uncomment        Alt+Shift+C', command=self._textArea.uncomment)
        self.__formatMenu.add_separator()
        self.__formatMenu.add_command(label='New Indent Width', command=self._setTabSize)
        self.__formatMenu.add_command(label='Strip Trailing White Spaces', command=self._stripWS)

        self._menuBar.add_cascade(label="Format   ", menu=self.__formatMenu)
        
        self.__viewMenu = tkinter.Menu(self._menuBar,font = standard_font, tearoff = 0)
        #
        #------view menu
        #
        self.__showStat = tkinter.StringVar()
        self.__showNum = tkinter.StringVar()
        self.__viewMenu.add_checkbutton(label = 'Status Bar', variable = self.__showStat, state = tkinter.DISABLED, command = self._showStatus)
        self.__viewMenu.add_radiobutton(label = 'Line Numbers', variable = self.__showNum, state =tkinter.ACTIVE, command = self._showLineNums)

        self._menuBar.add_cascade(label="View    ", menu=self.__viewMenu)
        
        self.__optionsMenu = tkinter.Menu(self._menuBar,font = standard_font, tearoff = 0)
        #
        #------options menu
        #
        self.__optionsMenu.add_command(label = 'Font...', command = lambda master = self._editorWindow: self._textArea.setFont( self._editorWindow))
        self.__optionsMenu.add_separator()
        self.__optionsMenu.add_command(label = f'Editor options(Configure {self._screenName})', command = self._configEditor)
        self._menuBar.add_cascade(menu = self.__optionsMenu, label = 'Editor Options   ')
        
        self.__helpMenu = tkinter.Menu(self._menuBar,font = standard_font, tearoff = 0)
        #
        #------help menu
        #
        self.__helpMenu.add_command(label="Help Index     F1".format(self._screenName), command=self.__showHelp)
        self.__helpMenu.add_command(label="About {}".format(self._screenName), command=self.__showAbout)
        self._menuBar.add_cascade(label="Help    ", menu=self.__helpMenu)

        self._editorWindow.configure(menu = self._menuBar)


    def run(self):
        self._editorWindow.mainloop()

    '''
        editor methods to be completed later
        -will be implemented in the tabbed and multiple window paradigm
        -the menus uding them will be diasabled
    '''
    def __showHelp(self):
        help_text = config['help']#text will be read from a file
        #fonts will be altered undeline some, different fonts for Some and different sizes for some
        self._help_window = tix.Toplevel(self._editorWindow)
        self._help_window.title (f'{self._screenName} ~~ Help')
        self._help_window.geometry('%dx%d+%d+%d'%(int(self.__screenSize.width*0.6), int(0.6*self.__screenSize.height),
                                                  40, 20))
        self._help_window.resizable(False, False)
        self._help_window.transient(self._editorWindow)
        self.__sup_frame = tkinter.Frame(self._help_window)
        self.__textBox = tkinter.scrolledtext.ScrolledText(self.__sup_frame,fg = '#000000', font = ('times', 13, 'bold italic'),
                                                background = '#dcdcdc', wrap=tkinter.NONE)
        self.__bar = tkinter.Scrollbar(self.__sup_frame, command  = self.__textBox.xview, orient = tkinter.HORIZONTAL)
        self.__textBox.configure(xscrollcommand = self.__bar.set)
        self.__textBox.insert(tkinter.INSERT, help_text)
        self.__textBox.configure(state = tkinter.DISABLED)
        self.__bar.pack(side = tkinter.BOTTOM, fill = tkinter.X)
        self.__textBox.pack(side = tkinter.LEFT)
        self.__sup_frame.pack()
        self._help_window.focus_set()
        #grab_set set makes dure the window does not lose focus to the parent
        self._help_window.grab_set()
        
        #window.wait_window(window)

    def __showAbout(self):
        messageBox.showinfo('About {}'.format(self._screenName),
                      f'{self._screenName} is a simple text editor similar to MS Notepad\n'
                      'with added complexity\n\n'
                      'Developed by @Glenn-Po as a Programming Learninng Project in the Python Programming Language\n\n'
                      '')

    def _configEditor(self):
        self._config_win = tix.Toplevel(self._editorWindow)
        self._config_win.title(f'Configure {self._screenName}')
        self._config_win.resizable(False, False)
        ###########################################################
        #text area to give user a preview of the changes being made
        #############################################################
        #self._config_win.geometry('%dx%d+%d+%d'%(200, 175,40, 20))
        sup_frame = tkinter.Frame(self._config_win, relief = tkinter.SOLID, borderwidth = 5)
        textBox = tkinter.scrolledtext.ScrolledText(sup_frame,
                                                    relief = tkinter.SUNKEN, borderwidth=2,

                                                    width = 40, height = 6,
                                                    state = 'disabled',
                                                    font=('times', 13, 'bold italic'),
                                                    fg='#000000',
                                                    #tabs = tkfont.Font(font = self['font']).measure('    ')
                                                    foreground='black',
                                                    background='white',
                                                    wrap=tkinter.NONE)
        bar = tkinter.Scrollbar(sup_frame, command=textBox.xview, orient=tkinter.HORIZONTAL)
        textBox.configure(xscrollcommand=bar.set)
        textBox.configure(state=tkinter.DISABLED)
        bar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        textBox.pack(side=tkinter.LEFT)
        sup_frame.grid(row =0, column = 0, padx = 20, pady = 20)
        
        self._config_win.resizable(False, False)
        self._config_win.transient(self._editorWindow)
        self._config_win.focus_set()
        #grab_set set makes dure the window does not lose focus to the parent
        self._config_win.grab_set()

    def _showStatus(self):
        pass

    def _showLineNums(self):
        pass

    def _stripWS(self):
        pass

    def _setTabSize(self):
        pass
