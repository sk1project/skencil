# Sketch - A Python-based interactive drawing program
# Copyright (C) 1998, 1999, 2000, 2002 by Bernhard Herzog
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#
#	PropertyPanel for plugin properties
#

#
# The parameters are described by a sequence of tuples like this
#
#	(NAME, TYPE, VALUE, RANGE, LABEL)
#
# LABEL is text suitable for a label in a dialog box. NAME is the
# internal name for that property. The constructor of the plugin object
# must accept a keyword argument NAME. Also, the plugin object must have
# a method CAPNAME to read the current value of that property and a
# method SetParameters accepting a dictionary of parameters. CAPNAME is
# a `Capitalized' version of the lowercase NAME (if NAME is
# `the_parameter', CAPNAME is `TheParameter')
#
# TYPE describes the type of the parameter, VALUE is the initial value
# and RANGE describes the valid values.
#
# Supported types:
#
#	type	range
#
#	int	(MIN, MAX)	The minimal and maximal value. MIN and/or MAX
#				may be None indicating no limit (apart from the
#				builtin limits).
#	float	(MIN, MAX)	same as for int.
#
#	length	(MIN, MAX)	A length in pt. The user can change the unit.
#
#	text	ignored		A text string (the range should be None for
#				now)
#

from string import split, join, capitalize

from Sketch.warn import warn, USER
from Sketch.const import SELECTION
from Sketch import _

from Tkinter import Label, IntVar, DoubleVar, StringVar, RIGHT, E
from tkext import MyEntry
from miniscroll import MiniScroller

from sketchdlg import PropertyPanel
from lengthvar import create_length_widgets



def capwords(ident):
    return join(map(capitalize, split(ident, '_')), '')

class Parameter:

    def __init__(self, panel, name, value, range, label):
        self.name = name
        self.value = value
        self.range = range
        self.label = label
        self.var = None
        self.panel = panel


    def build_widgets(self, master, row):
        label = Label(master, text = self.label)
        label.grid(row = row, column = 0, sticky = E)

    def __call__(self, *args):
        if args:
            self.var.set(args[0])
        else:
            return self.var.get()

parameter_types = {}

class NumberParameter(Parameter):

    def is_valid(self):
        value = self.var.get()
        min, max = self.range
        if min is not None and min > value:
            return 0
        if max is not None and max < value:
            return 0
        return 1

    def init_var(self):
        lo, hi = self.range
        value = self.value
        if lo is None:
            if hi is not None:
                if value > hi:
                    value = hi
        else:
            if hi is None:
                if value < lo:
                    value = lo
            else:
                value = max(lo, min(hi, value))
        if value != self.value:
            warn(USER,
                 'Initial value in parameter %s of plugin %s out of range',
                 self.name, self.panel.title)
        self.var.set(value)

    def var_changed(self, *rest):
        if self.is_valid():
            self.panel.set_parameter(self)

    def build_widgets(self, master, row, build_entry = 1):
        self.init_var()
        Parameter.build_widgets(self, master, row)
        if build_entry:
            entry = MyEntry(master, textvariable = self.var, justify = RIGHT,
                            width = 6, command = self.var_changed)
            entry.grid(row = row, column = 1, sticky = 'ew')
            min, max = self.range
            scroll = MiniScroller(master, variable = self.var,
                                  min = min, max = max, step = 1)
            scroll.grid(row = row, column = 2, sticky = 'news')


class IntParameter(NumberParameter):

    def build_widgets(self, master, row):
        self.var = IntVar(master)
        NumberParameter.build_widgets(self, master, row)

parameter_types['int'] = IntParameter

class FloatParameter(NumberParameter):

    def build_widgets(self, master, row):
        self.var = DoubleVar(master)
        NumberParameter.build_widgets(self, master, row)

parameter_types['float'] = FloatParameter

class LengthParameter(NumberParameter):

    def build_widgets(self, master, row):
        self.var, entry, scroll, menu = create_length_widgets(master, master,
                                                              self.var_changed)
        NumberParameter.build_widgets(self, master, row, build_entry = 0)
        entry.grid(row = row, column = 1, sticky = 'ew')
        scroll.grid(row = row, column = 2, sticky = 'ns')
        menu.grid(row = row, column = 3)

parameter_types['length'] = LengthParameter

class TextParameter(Parameter):

    def build_widgets(self, master, row):
        Parameter.build_widgets(self, master, row)
        self.var = StringVar(master)
        self.var.set(self.value)
        entry = MyEntry(master, textvariable = self.var, width = 0,
                        command = self.var_changed)
        entry.grid(row = row, column = 1, columnspan = 3, sticky = 'ew')

    def var_changed(self, *rest):
        self.panel.set_parameter(self)

parameter_types['text'] = TextParameter

class PluginPanel(PropertyPanel):

    def __init__(self, master, main_window, doc, info):
        self.var_auto_update = IntVar(master)
        self.var_auto_update.set(1)
        self.info = info
        self.title = info.menu_text
        self.vars = []
        name = 'dlg' + info.class_name
        PropertyPanel.__init__(self, master, main_window, doc, name = name)

    def build_dlg(self):
        top = self.top
        row = 0

        for row in range(len(self.info.parameters)):
            name, type, value, prange, label = self.info.parameters[row]
            try:
                #print name, type, value, prange, label
                var = parameter_types[type](self, name, value, prange, label)
                var.build_widgets(top, row)
                self.vars.append(var)
            except KeyError:
                warn(USER, 'Unknown plugin parameter type %s' % type)
                continue
        row = row + 1
        top.columnconfigure(0, weight = 0)
        top.columnconfigure(1, weight = 1)
        top.columnconfigure(2, weight = 0)
        top.columnconfigure(3, weight = 0)


        frame = self.create_std_buttons(top)
        frame.grid(row = row, columnspan = 4, sticky = 'ew')

    def set_parameter(self, var):
        if not self.current_is_plugin():
            return
        doc = self.document
        doc.BeginTransaction(_("Set %s") % var.label) # NLS
        try:
            try:
                kw = {var.name: var()}
                doc.AddUndo(self.current_object().SetParameters(kw))
            except:
                doc.AbortTransaction()
        finally:
            doc.EndTransaction()

    def can_apply(self):
        return 1

    def do_apply(self):
        if self.current_is_plugin():
            doc = self.document
            doc.BeginTransaction(_("Set Parameters"))
            try:
                try:
                    kw = {}
                    for var in self.vars:
                        kw[var.name] = var()
                    doc.AddUndo(self.current_object().SetParameters(kw))
                except:
                    doc.AbortTransaction()
            finally:
                doc.EndTransaction()
        else:
            # create that object
            dict = {}
            for var in self.vars:
                dict[var.name] = var()
            obj = apply(self.info.Constructor(), (), dict)
            text = 'Create ' + self.info.menu_text # NLS
            self.main_window.canvas.PlaceObject(obj, text)


    def current_is_plugin(self):
        o = self.document.CurrentObject()
        return o is not None and o.is_Plugin and \
               o.class_name == self.info.class_name

    def current_object(self):
        return self.document.CurrentObject()

    def init_from_doc(self):
        self.Update()
        self.issue(SELECTION)

    def Update(self):
        if self.current_is_plugin():
            object = self.current_object()
            for var in self.vars:
                var(getattr(object, capwords(var.name))())

    def update_from_object_cb(self, obj):
        print 'update_from_object_cb', obj
        while not obj.is_Plugin and not obj.is_Layer:
            obj = obj.parent
        if obj.is_Plugin and obj.class_name == self.info.class_name:
            for var in self.vars:
                print 'update_from_object_cb', var
                var(getattr(obj, capwords(var.name))())

    def close_dlg(self):
        self.vars = []
        PropertyPanel.close_dlg(self)
