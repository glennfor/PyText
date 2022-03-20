###--------------###
###   Imports    ###
###--------------###

#[GUI]
import tkinter
import tkinter.tix as tix
import tkinter.ttk as ttk

import tkinter.filedialog as fileDialog
import tkinter.messagebox as messageBox
import tkinter.scrolledtext


import tkinter.colorchooser as colorChooser
import tkfontchooser as fontChooser
import tkinter.font as tkfont


#[UTILS]
import os
import sys 
import  time, datetime

import json


#[configuration preferences]
PATH_TO_ICON = "./resources/text_edit_icon.ico"
PATH_TO_CONFIG_FILE = './resources/config.json'
config = {}

with open(PATH_TO_CONFIG_FILE, 'r+') as f:
    config = json.load(f)
    print("Config File Load Success.....")


"""A StandardText widget feels like a text widget but also has a
vertical scroll bar on its right.  (Later, options may be added to
add a horizontal bar as well, to make the bars disappear
automatically when not needed, to move them to the other side of the
window, etc.)

Configuration options are passed to the Text widget.
A Frame widget is insertsed between the master and the text, to hold
the Scrollbar widget.
Most methods calls are inherited from the Text widget; Pack, Grid and
Place methods are redirected to the Frame widget however.
"""

class StandardText(tkinter.Text):
    def __init__(self, master=None, **kw):
        self._frame = tkinter.Frame(master)
        self._vbar = tkinter.Scrollbar(self._frame)
        self._hbar = tkinter.Scrollbar(self._frame, orient = tkinter.HORIZONTAL)
        self._statusbar = tkinter.Label(self._frame, bg = '#202020', fg = 'green', font = ('Times', 15, 'bold'),
                               text = 'Line : 0,  Column : 0',cursor = 'plus', anchor = tkinter.E)
        self._tabsize = 4
        self.is_modified = True # the is_modified variable states if the content has been changed since the last save
        #packing::::-after, -anchor, -before, -expand, -fill, -in, -ipadx, -ipady, -padx, -pady, or -side
        #griding::::-column, -columnspan, -in, -ipadx, -ipady, -padx, -pady, -row, -rowspan, or -sticky
        self._statusbar.pack(side = tkinter.BOTTOM, fill = tkinter.X)
        self._vbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._hbar.pack(side = tkinter.BOTTOM, fill = tkinter.X)
        #nb... packing trick for hbar and status bar skeptical

        kw.update({'yscrollcommand': self._vbar.set, 'xscrollcommand':self._hbar.set})
        tkinter.Text.__init__(self, self._frame, **kw)
        self.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self._vbar['command'] = self.yview
        self._hbar['command'] = self.xview
        self['undo'] = True 
        self['wrap'] = tkinter.NONE
        self['background']= '#FDFAFA'
        self['foreground']= '#2020AA'
        self['font'] = ('courier new', 14, 'bold') # 'normal')#default font

        #set tab size roughly # will make sure to add it to config window
        self['tabs'] = tkfont.Font(font = self['font']).measure('    ')

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(tkinter.Text).keys()
        methods = vars(tkinter.Pack).keys() | vars(tkinter.Grid).keys() | vars(tkinter.Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self._frame, m))
        self._apply_bindings()

    def __str__(self):
        return str(self._frame)

    def _apply_bindings(self):
        #The status bar is updated if the user clicks or presses a key
        self.bind_all('<Key>', self.update_status)
        self.bind_all('<Button-1>', self.update_status)
        
        self.bind('<Control-]>', lambda ev: self.indent())
        self.bind('<Control-[>', lambda e: self.dedent())
        self.bind('<Alt-c>', lambda ev: self.commentOut())
        self.bind('<Alt-Shift-c>', lambda ev: self.uncomment())
        self.bind('<Control-f>',lambda ev:  self.find() )
        self.bind('<Control-g>', lambda ev: self.findNext())
        self.bind('<Control-r>',lambda ev:  self.replace())

    def update_status(self, event):
        'This method will also be called in other methods involving pasting or inserting as it changes the positio of the insertion cursor'
        
        #self.statusbar['text'] = 'Line : {},  Column : {}'.format(*(self.index(INSERT).split('.')))
        #CURRENT is for the cursor(mouse pointer) and INSERT is for the caret(insertion cursor)
        self._statusbar.configure(text = 'Line : {} | Column : {}'.format(*(self.index(tkinter.INSERT).split('.'))))
              
        '''
                Standard bindings in the text widget
                -cut
                -copy
                -paste
                -redo/undo
                -delete
                -select all        
        '''

    def undo_event(self):
        try:
            self.edit_undo()
        except tkinter.TclError:# nothing to undo
            pass
        self.update_status(None)
        #self.event_generate('<<undo>>')

    def redo_event(self):
        try:
            self.edit_redo()
        except tkinter.TclError:
            pass
        self.update_status(None)
        # self.event_generate('<<redo>>')

    def delete_event(self):
        try:
            self.delete(tkinter.SEL_FIRST,tkinter.SEL_LAST)
        except tkinter.TclError:
            pass
        finally:
            self.update_status(None)
        # self.event_generate('<<delete>>')
            
    def copy_event(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.get(tkinter.SEL_FIRST,tkinter.SEL_LAST))
        except tkinter.TclError:
            pass
        # self.event_generate('<<copy>>')

    def cut_event(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.get(tkinter.SEL_FIRST,tkinter.SEL_LAST))
            self.delete(tkinter.SEL_FIRST,tkinter.SEL_LAST)
        except tkinter.TclError:
            pass
        finally:
            self.update_status(None)
         # self.event_generate('<<cut>>')

    def paste_event(self):
        try:
            content = self.clipboard_get()
            self.insert(tkinter.INSERT, content)
            self.update_status(None)
        except tkinter.TclError: #ie nothing to paste
            pass
        # self.event_generate('<<paste>>')

    def select_all(self):
        try:
            self.tag_add(tkinter.SEL, 1.0, tkinter.END+'-1c')#end adds a newline, so subtract 1 char
            self.insert(tkinter.END,'')
        except tkinter.TclError:
            pass
        #or
        #self.tag_add(SEL, 1.0, END+'-1c')#end adds a newline so subtract 1 char
        #self.mark_set(INSERT, "1.0")
        #self.see(INSERT)
        #or
        #self.event_generate('<<Control-a>>')
        self.update_status(None)
        
        #return 'break' #overides the standard binding
        
    def insert_date(self):
            date = str(datetime.datetime.now())[:-7] #or datetime.datetime.today()
            self.insert(tkinter.INSERT, date)
            self.update_status(None)
  
    def f_replace(self, master):
        self.update_status(None)
        top = tkinter.Toplevel()
        top.transient(master)#self._editorWindow)
        top.resizable(0,0)
        info = {'text_to_find':tkinter.StringVar(), 'findall':tkinter.BooleanVar(),
                'replace':tkinter.BooleanVar(), 'replace_all':tkinter.BooleanVar()}
        top.title('PYTEXT EDIT ~~ Find & Replace')
        tkinter.Label(top,text="Find:").grid(row=0, column=0, sticky='e')
        tkinter.Entry(top).grid(row=0,column=1,padx=2,pady=2,sticky='we',columnspan=9)
        tkinter.Label(top, text="Replace:").grid(row=1, column=0, sticky='e')
        tkinter.Entry(top).grid(row=1,column=1,padx=2,pady=2,sticky='we',columnspan=9)
        tkinter.Button(top, text="Find").grid(row=0, column=10, sticky='ew', padx=2,
        pady=2)
        tkinter.Button(top, text="Find All").grid(row=1, column=10, sticky='ew', padx=2)
        tkinter.Button(top, text="Replace").grid(row=2, column=10, sticky='ew', padx=2)
        tkinter.Button(top, text="Replace All").grid(row=3, column=10, sticky='ew',
        padx=2)
        tkinter.Checkbutton(top, text='Match whole word only').grid(row =2, column=1,
        columnspan=4, sticky='w')
        tkinter.Checkbutton(top, text='Match Case').grid(row =3, column=1, columnspan=4,
        sticky='w')
        tkinter.Checkbutton(top, text='Wrap around').grid(row =4, column=1, columnspan=4,
        sticky='w')
        tkinter.Label(top, text="Direction:").grid(row=2, column=6, sticky='w')
        tkinter.Radiobutton(top, text='Up', value=1).grid(row=3, column=6, columnspan=6,
        sticky='w')
        tkinter.Radiobutton(top, text='Down', value=2).grid(row=3, column=7,
        columnspan=2, sticky='e')
        top.mainloop()
        def search():
            pos=(None, None)
            length = len(info['text_to_find'].get())#initial values
            #initial the index of the firstmatch is unknown
            pos[0] = self.search(info['text_to_find'].get())
            pos[1]=pos[0]+length

            while pos[0]+pos[1] <= int(self.index(tkinter.END).split('.')[-1]):
                pass
            

    def find(self):
        pass

    def findNext(self):#or replace with find all if i can tag all finds
        self.update_status(None)
        pass

    def findSel(self):
        self.update_status(None)
        pass

    def replace(self):
        self.update_status(None)
        pass

    def gotoLine(self):
        self.update_status(None)
        pass

    def indent(self):
        '''
        indents a piece of selected text
        :return: None
        '''
        pass

    def dedent(self):
        '''
        -unindents(dedents) a piece of selected text
        :return: None
        '''
        self.update_status(None)
        pass

    def commentOut(self):
        '''
        depending on the language specified
        it comments out a piece fo slected text
        support: py, c, cpp, java, go, kotlin, r, matlab, lua, html, javascript,
        :return:None
        '''
        #comment character
        com_str = '##'#for text files the defaukt the default commenting is an empty string since text files don't have standard
        #comments
        beg = int(self.index(tkinter.SEL_FIRST).split('.')[0])
        last = int(self.index(tkinter.SEL_LAST).split('.')[0])
        while beg <= last:
            self.insert(str(beg+0.0), com_str)
            beg += 1
        self.update_status(None)


    def uncomment(self):
        '''
        same as above
        :return:
        '''
        self.update_status(None)
        pass

    def wordwrap(self):
        pass

    def setFont(self, master):
        font = fontChooser.askfont(master, text = 'AaBbXxYy-123')

        fontString=font['family'].replace(' ', '\ ')+' '+str(font['size'])
        if font['weight']=='bold':
            fontString+=' bold'
        if font['underline']:
            fontString+=' underline'
        if font['overstrike']:
            fontString+=' overtsrike'
        fontString+=' '+font['slant']
        config['font'] = fontString
        self.configure(font = fontString)




class Font_wm(object):
    def __init__(self, master):
        self.win = tkinter.Toplevel(master)
        self.win.resizable(False, False)
        self.win.overrideredirect(True)
        self.win.attributes({'toolwindow':True})
        
    def init_win(self):
        self.font_lab = tkinter.LableFrame(self.win, text = 'Font')
        self.effect_lab = tkinter.LableFrame(self.win, text = 'Effects')
        self.style_lab = tkinter.LableFrame(self.win, text = 'Font style')
        self.size_lab = tkinter.LableFrame(self.win, text = 'Font Size')
        self.sample_lab = tkinter.LableFrame(self.win, text = 'Sample')

        self.list = tix.ScrolledListBox(self.font_lab, height = 10)
        for i, font in enumerate(sorted(tkfont.families(self.win)), start = 1):
            self.list.insert(i, font)
        for i, style in enumerate(['bold', 'underline', 'italic', 'normal']):
            pass



class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tip_win = None

    def showtip(self, tip):
        '''display text in a tooltip window'''
        if self.tip_win or not tip:
            return

        x,y,cx,cy = self.widget.bbox(tkinter.INSERT)
        x += self.widget.winfo_rootx() +25
        y += cy + self.widget.winfo_rooty() +25
        self.tip_win = tw = tkinter.Toplevel(self.widget)
        tw.overrideredirect(True)  #remove all WM decorations
        tw.wm_geometry('+%d+%d'%(x, y))
        tkinter.Label(tw, text = tip, justify = tkinter.LEFT, bg = '#FFFFE0', relief = tkinter.SOLID,
              borderwidth = 1, font = ('tahoma', 8, 'normal')).pack(ipadx = 1)

    def hidetip(self):
            tw = self.tip_win
            self.tip_win = None
            if tw:
                tw.destroy()
                
              
def create_tool_tip(widget, tip_text):
    tooltip = ToolTip(widget)

    def enter(ev):
        tooltip.showtip(tip_text)

    def leave(ev):
        tooltip.hidetip()
    widget.bind('<Enter>', enter,add='+')
    widget.bind('<Leave>', leave, add='+')




class Window(tkinter.Tk):
    '''
        initialises and creates a window with simple parameters that will or may be overridden
        in the Editor class itself

        Remember to call the mainloop after creating an instance of the Editor class
        eg 
        
    '''

    def __init__(self, screenName, iconName, initialSize):
        tkinter.Tk.__init__(self, screenName, None, 'Tk', 1, 0, None)
        self.title(screenName)
        self.iconbitmap(iconName)
       # Center the window
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        # For left-allign and  right-allign

        left = (screenWidth / 2) - (initialSize[0] / 2)

        top = (screenHeight / 2) - (initialSize[-1] / 2)
        # For top and bottom
        self.geometry('%dx%d+%d+%d' % (*(initialSize), left, top))
        # To make the textarea auto resizable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)



