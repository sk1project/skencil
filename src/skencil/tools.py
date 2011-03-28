# -*- coding: utf-8 -*-
#
#    Copyright (C) 2011 by Igor E. Novikov
#    
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 3 of the License, or (at your option) any later version.
#    
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the GNU
#    Library General Public License for more details.
#    
#    You should have received a copy of the GNU Library General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os
import gtk

from skencil import _, config

class AppTools(gtk.HandleBox):
    
    def __init__(self, mw):
        gtk.HandleBox.__init__(self)
        self.mw = mw
        self.app = mw.app
        self.actions = self.app.actions

        self.set_snap_edge(gtk.POS_TOP | gtk.POS_LEFT)
        self.set_handle_position(gtk.POS_TOP)
        
        self.toolbar = gtk.Toolbar()
        self.toolbar.set_orientation(gtk.ORIENTATION_VERTICAL)
        self.toolbar.set_property('toolbar-style', gtk.TOOLBAR_ICONS)
        
        icons = ['select.png',
               'shaper.png',
               'zoom.png',
               'create_rect.png',
               'create_ellipse.png',
               'create_poly.png',
               'create_curve.png',
               'create_text.png'
               ]
        index = 0
        for icon_file in icons:
            icon_file = os.path.join(config.resource_dir,
                                     'icons', 'tools', icon_file)
            icon = gtk.Image()
            icon.set_from_file(icon_file)
            toolbutton = gtk.ToolButton(icon)
            self.toolbar.insert(toolbutton, index)
            index += 1
            
        x, y, h, w = toolbutton.allocation

        self.toolbar.set_size_request(-1, 40 * index)
        self.add(self.toolbar)
        
        
#        self.build()
        
    def create_entries(self):
        return [
                'ZOOM_IN',
                'ZOOM_OUT',
               ]
        
    def build(self):
        entries = self.create_entries()
        index = 0
        for entry in entries:
            if entry is None:
                button = gtk.SeparatorToolItem()
            else:
                action = self.actions[entry]
                button = action.create_tool_item()
            self.insert(button, index)
            index += 1
