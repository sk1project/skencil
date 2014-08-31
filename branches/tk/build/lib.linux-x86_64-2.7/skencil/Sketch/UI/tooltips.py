# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999 by Bernhard Herzog
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307	USA

#
# A very primitive balloon help mechanism for Python/Tk
#

from types import InstanceType

from Tkinter import Toplevel, Label

from Sketch import config

import tkext


class Tooltips:

    def __init__(self):
        self.descriptions = {}
        self.balloon = None
        self.balloon_label = None
        self.last_widget = ''
        self.after_id = None

    def AddDescription(self, widget, description):
        self.descriptions[widget._w] = description
        if widget._w == self.last_widget:
            self.balloon_label['text'] = description

    def RemoveDescription(self, widget):
        if type(widget) == InstanceType:
            widget = widget._w
        if self.descriptions.has_key(widget):
            del self.descriptions[widget]

    def GetDescription(self, widget):
        if type(widget) == InstanceType:
            widget = widget._w
        if self.descriptions.has_key(widget):
            return self.descriptions[widget]
        return ''


    def create_balloon(self, root):
        self.root = root
        self.balloon = Toplevel(self.root, name='tooltips')
        self.balloon.withdraw()
        self.balloon.overrideredirect(1)
        label = Label(self.balloon, name='label', text='Tooltip')
        label.pack()
        self.balloon_label = label


    def popup_balloon(self, widget_name, x, y, text):
        self.last_widget = widget_name
        self.balloon.withdraw()
        self.balloon_label['text'] = text

        width = self.balloon_label.winfo_reqwidth()
        height = self.balloon_label.winfo_reqheight()
        
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        
        x = self.root.winfo_pointerx() + 10
        y = self.root.winfo_pointery() + 20
        
        if screenwidth < (x + width):
            x = x - width

        if screenheight < (y + height):
            y = y - height - 25 
        
        self.balloon.geometry('%+d%+d' % (x, y))
        self.balloon.update()
        self.balloon.deiconify()
        self.balloon.tkraise()

    def popup_delayed(self, widget_name, x, y, text, *args):
        self.after_id = None
        self.popup_balloon(widget_name, x, y, text)

    def enter_widget(self, widget_name):
        text = self.GetDescription(widget_name)
        if text:
            widget = self.root.nametowidget(widget_name)
            x = widget.winfo_rootx() + widget.winfo_width() / 2
            y = widget.winfo_rooty() + widget.winfo_height()
            
            if self.after_id:
                print 'after_id in enter'
                self.root.after_cancel(self.after_id)
            self.after_id = self.root.after(config.preferences.tooltip_delay,
                                            self.popup_delayed,
                                            widget_name, x, y, text)

    def leave_widget(self, widget_name):
        global last_widget, after_id
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
            self.last_widget = ''
        last_widget = ''
        self.balloon.withdraw()

    button_press = leave_widget


    def destroy_widget(self, event):
        self.RemoveDescription(event.widget)


_tooltips = Tooltips()
AddDescription = _tooltips.AddDescription


def Init(root):
    if config.preferences.activate_tooltips:
        root.tk.call('bind', 'all', '<Enter>',
                     tkext.MakeMethodCommand(_tooltips.enter_widget, '%W'))
        root.tk.call('bind', 'all', '<Leave>',
                     tkext.MakeMethodCommand(_tooltips.leave_widget, '%W'))
        root.tk.call('bind', 'all', '<ButtonPress>',
                     tkext.MakeMethodCommand(_tooltips.button_press, '%W'))
        _tooltips.create_balloon(root)

