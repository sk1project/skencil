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
import cairo

from skencil import _, config

SIZE = 18

class RulerCorner(gtk.DrawingArea):
    
    def __init__(self, docarea):
        gtk.DrawingArea.__init__(self)
        self.docarea = docarea  
        
        self.set_size_request(SIZE, SIZE)
        self.connect('expose_event', self.repaint)
        
    def repaint(self, *args):
        color = self.get_style().bg[gtk.STATE_ACTIVE]
        r = color.red / 65535.0
        g = color.green / 65535.0
        b = color.blue / 65535.0
        painter = self.window.cairo_create()
        painter.set_antialias(cairo.ANTIALIAS_NONE)
        painter.set_source_rgb(r, g, b)
        painter.set_line_width(1)
        painter.rectangle(-1, -1, SIZE, SIZE)
        painter.stroke()
        

HORIZONTAL = 0
VERTICAL = 1

class Ruler(gtk.DrawingArea):
    
    def __init__(self, docarea, orient):
        gtk.DrawingArea.__init__(self)
        self.docarea = docarea  
        self.orient = orient
        if self.orient:
            self.set_size_request(SIZE, -1)
        else:
            self.set_size_request(-1, SIZE)
        self.connect('expose_event', self.repaint)
        
    def repaint(self, *args):
        color = self.get_style().bg[gtk.STATE_ACTIVE]
        border_color = [color.red / 65535.0,
                        color.green / 65535.0,
                        color.blue / 65535.0]
        
        x, y, w, h = self.allocation
        r, g, b = border_color
        painter = self.window.cairo_create()
        painter.set_antialias(cairo.ANTIALIAS_NONE)
        painter.set_line_width(1)
        if self.orient:
            grad = cairo.LinearGradient(0, 0, SIZE, 0)
            grad.add_color_stop_rgba(0, r, g, b, 0)            
            grad.add_color_stop_rgba(1, r, g, b, .8)
            painter.set_source(grad)
            painter.rectangle(-1, -1, SIZE, h)
            painter.fill ()            
            
            painter.set_source_rgb(r, g, b)
            painter.rectangle(-1, -1, SIZE, h)
            painter.stroke()
        else:
            grad = cairo.LinearGradient(0, 0, 0, SIZE)
            grad.add_color_stop_rgba(0, r, g, b, 0)            
            grad.add_color_stop_rgba(1, r, g, b, .8)
            painter.set_source(grad)
            painter.rectangle(-1, -1, w , SIZE)
            painter.fill ()
            
            painter.set_source_rgb(r, g, b)
            painter.rectangle(-1, -1, w , SIZE)
            painter.stroke()
    
