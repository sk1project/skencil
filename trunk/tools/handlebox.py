# -*- coding: utf-8 -*-
 
#!/usr/bin/env python

import gtk

class HandleBox:
    def __init__(self):
        window = gtk.Window()
        window.set_default_size( 200,-1)
        
        handlebox = gtk.HandleBox()
        handlebox.set_snap_edge(gtk.POS_TOP | gtk.POS_LEFT)
        
        toolbar = gtk.Toolbar()
        toolbar.set_size_request(200, -1)
        
        toolbutton1 = gtk.ToolButton(gtk.STOCK_NEW)
        toolbutton2 = gtk.ToolButton(gtk.STOCK_OPEN)
        toolbutton3 = gtk.ToolButton(gtk.STOCK_SAVE_AS)
        toolbar.insert(toolbutton1, 0)
        toolbar.insert(toolbutton2, 1)
        toolbar.insert(toolbutton3, 2)
        
        window.connect("destroy", lambda w: gtk.main_quit())

        window.add(handlebox)
        handlebox.add(toolbar)
        window.show_all()

HandleBox()
gtk.main()