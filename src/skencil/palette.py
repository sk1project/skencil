# -*- coding: utf-8 -*-
#
#    Copyright (C) 2011 by Igor E. Novikov
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. 

import gtk

class Palette(gtk.Frame):
    
    def __init__(self, mw):
        gtk.Frame.__init__(self)
        self.mw = mw
        self.app = mw.app
        
        hbox = gtk.HBox()
        
        self.pal_widget = gtk.Frame(label=None)
        self.pal_widget.set_property('shadow_type', gtk.SHADOW_NONE)
        self.pal_widget.set_size_request(-1, 18)
        hbox.pack_end(self.pal_widget, True, False, 0)
        self.add(hbox)
        
