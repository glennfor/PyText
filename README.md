# PyText
Text editor written in Python with Tkinter


## Structure of Menu

File
    New
    Open
    Save
    Save As(saves an already saved file in a new dir or with  different name or both
    save all(when tabbed window comes to play)
    ------------------------
    recent files (recently opend files)
        .......
        .......
    ------------
    export
        to html(use a module if any to convert  text to html or remove funtion if none)
        to Json
        to rft(find out the format and the meaning)
        to Pdf
    --------------
    print
    ---------------
    close all  (when tabbed window comes to play)-closes all tabs but does not exit the window
    close(when tabbed window comes to play)
    exit (exit the window after saving - gives a prompt that can be disabeled in settings

    
`Edit`   most edit functions have to do with the text widget and        will therefore be defined as such
    Undo
    Redo
    ---
    cut
    copy
    paste
    select all
    ----------
    insert
            date/time
            filename
search
    find
    find next
    find in selection
    -------------
    replace
    --------
    goto line
Format
    indent region
    dedent region
    comment out   -- language support
    uncomment  ---- lnaguage support
    ---------
    new indent width(may be implemented in options)
    strip trailing white spaces
view
    status bar    #always true , will complicate matters if choosable but will upgrade later
    line numbers
Options
    Font...
    -------
    Editor options(configure 'App Name'(bg, fg)

Help
    Help Index// (pdf/text/html/...) file  
    --help on how to use 
    About 'App Name' describing application atrributes]


## TODO
--Tooltip window
Addtitions
-pop up menu on right click
-search dialog
-replace dialog
-find dialog
-configure dialog
-font chnage dialog
-editor options dialog