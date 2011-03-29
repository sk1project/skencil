# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011 by Igor E. Novikov
#	
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>. 

import gtk


from skencil.view.canvas import SketchCanvas
from ruler import RulerCorner, Ruler

class DocArea(gtk.Frame):
	
	def __init__(self, mw):
		gtk.Frame.__init__(self)
		self.mw = mw
		self.app = mw.app

		self.set_property('shadow_type', gtk.SHADOW_NONE)
		
		da_box = gtk.Table(3, 3, False)
		
		self.corner = RulerCorner(self)
		da_box.attach(self.corner, 0, 1, 0, 1, gtk.SHRINK, gtk.SHRINK)
		
		self.hruler = Ruler(self, 0)
		da_box.attach(self.hruler, 1, 3, 0, 1, gtk.EXPAND | gtk.FILL, gtk.SHRINK)
		
		self.vruler = Ruler(self, 1)
		da_box.attach(self.vruler, 0, 1, 1, 3, gtk.SHRINK, gtk.EXPAND | gtk.FILL)
		
		self.v_adj = gtk.Adjustment()
		self.vscroll = gtk.VScrollbar(self.v_adj) 
		da_box.attach(self.vscroll, 2, 3, 1, 2, gtk.SHRINK, gtk.EXPAND | gtk.FILL)	
		
		self.h_adj = gtk.Adjustment()
		self.hscroll = gtk.HScrollbar(self.h_adj) 
		da_box.attach(self.hscroll, 1, 2, 2, 3, gtk.EXPAND | gtk.FILL, gtk.SHRINK)   
		
		self.canvas = SketchCanvas(self)
		da_box.attach(self.canvas, 1, 2, 1, 2, gtk.FILL | gtk.EXPAND,
			gtk.FILL | gtk.EXPAND, 0, 0)	  
		
		self.add(da_box)
