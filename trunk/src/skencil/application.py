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

import gtk

from skencil import _, config
from proxy import AppProxy
from inspector import DocumentInspector
from mainwindow import MainWindow
from actions import create_actions


class Application:
    
    actions = {}
    docs = []
    current_doc = None
    
    proxy = None
    inspector = None
    
    
    def __init__(self, path):
        self.path = path
        
        self.proxy = AppProxy(self)
        self.inspector = DocumentInspector(self)
        
        
        self.accelgroup = gtk.AccelGroup()
        self.actiongroup = gtk.ActionGroup('BasicAction')
        
        self.actions = create_actions(self)
        self.mw = MainWindow(self)
        self.proxy.update_references()        
        
    def run(self):
        self.mw.show_all()
        gtk.main()

    def exit(self):
        gtk.main_quit()
        
    def new(self):
        pass
    
    def open(self):
        pass
    
    def save(self):
        pass
    
    def save_as(self):
        pass
    
    def insert_doc(self):
        pass
    
    
