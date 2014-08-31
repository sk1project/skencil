# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2003 by Bernhard Herzog
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
# Base Classes for Panels
#
# A Panel is an additional toplevel window that allows the user to
# manipulate properties of the document or the current selection. Panels
# are usually also additional Views of the document.
#
#
# Classes:
#
#
# SketchPanel
#
# Base class for all panels. Implements some standard behaviour and
# features, auch as managing the current document, passing document
# messages on to its widgets, saving preferences when the window is
# closed and functions to create some standard buttons.
#
# SketchPanel is used as an immediate base class for panels that affect
# the document as a whole or are independent from properties of the
# currently selected objects (LayerPanel, GridPanel and LayoutPanel for
# instance).
#
#
# PropertyPanel(SketchPanel)
#
# A panel derived from PropertyPanel is a panel that shows properties of
# the current selected objects and allows the user to change them.
#
# Baseclass for dialogs that display and change properties of the
# current selection (FillPanel and StylePanel for instance).
#
#
# CommandPanel(SketchPanel)
#
# A base class for panels that basically offer some commands that are
# either not accesible fom the menu or are more convenient on a seperate
# Panel (CurvePanel and AlignPanel for instance)
#

from types import StringType

from Sketch.warn import pdebug, warn_tb, INTERNAL
from Sketch import _, Publisher
from Sketch.const import SELECTION, DOCUMENT, EDITED, CLOSED
from Sketch import config
import Sketch

from Tkinter import Toplevel, IntVar, Frame, Checkbutton, Label
from Tkinter import TOP, LEFT, RIGHT, BOTTOM, X, BOTH, TkVersion

from tkext import UpdatedButton
import tkext
import skpixmaps
pixmaps = skpixmaps.PixmapTk



class SketchPanel(Publisher):

    # SketchPanel.receivers is a list of tuples of the form
    #		(CHANNEL, FUNCTION[, ARG, ...])
    # SketchPanel automatically installs FUNCTION as a receiver for
    # CHANNEL. FUNCTION will be calles with ARG,.. as arguments. derived
    # classes should copy this list and append their own additional
    # receivers.

    receivers = [(SELECTION, 'issue', SELECTION)]

    title = 'Skencil'		# The window title
    class_name = 'SKPanel'	# the class_name for resources

    x_correction = 0
    y_correction = 0

    def __init__(self, master, main_window, doc, **kw):
        self.master = master
        self.main_window = main_window
        self.document = None

        kw['class'] = self.class_name
        top = apply(Toplevel, (master,), kw)
        top.title(self.title)
        self.pref_pos_name = 'dlg_pos_' + self.__class__.__name__
        if config.preferences.panel_use_coordinates:
            posx, posy = config.get_preference(self.pref_pos_name, (0.1, 0.1))
            # avoid confusing behaviour of panels if the position is negative
            # or > 1:
            posx = max(min(posx, 1), 0)
            posy = max(min(posy, 1), 0)

            posx = master.winfo_rootx() + int(posx * master.winfo_width())
            posy = master.winfo_rooty() + int(posy * master.winfo_height())
            top.geometry('%+d%+d' % (posx, posy))

        top.transient(master)
        top.group(master)
        top.iconname(self.title)
        top.iconbitmap(pixmaps.Icon)
        top.iconmask(pixmaps.Icon_mask)
        top.protocol('WM_DELETE_WINDOW',
                     tkext.MakeMethodCommand(self.close_dlg))
        # the following is a workaround for a Tkinter bug. Tkinter 1.63
        # doesn't like bindings for the Destroy event.
        top.tk.call('bind', top._w, '<Destroy>',
                    tkext.MakeMethodCommand(self.destroyed) + ('%W',))

        self.top = top
        self.build_dlg()
        self.SetDocument(doc)

        self.main_window.Subscribe(DOCUMENT, self.doc_changed)

        if config.preferences.panel_use_coordinates \
           and config.preferences.panel_correct_wm:
            if not top.winfo_ismapped():
                top.wait_visibility()
            self.x_correction = posx - top.winfo_rootx()
            self.y_correction = posy - top.winfo_rooty()

    if __debug__:
        def __del__(self):
            pdebug('__del__', '__del__', self)

    def deiconify_and_raise(self):
        self.top.deiconify()
        self.top.tkraise()

    def withdraw(self):
        self.top.withdraw()

    def doc_changed(self, doc):
        self.SetDocument(doc)

    def doc_has_selection(self):
        return self.document.HasSelection()

    def destroyed(self, widget, *args):
        if widget == self.top._w:
            self.save_prefs()

    def subscribe_receivers(self):
        for info in self.receivers:
            apply(self.document.Subscribe,
                  (info[0], getattr(self, info[1])) + info[2:])

    def unsubscribe_receivers(self):
        for info in self.receivers:
            apply(self.document.Unsubscribe,
                  (info[0], getattr(self, info[1])) + info[2:])

    def SetDocument(self, doc):
        if self.document:
            self.unsubscribe_receivers()
        self.document = doc
        self.init_from_doc()
        self.subscribe_receivers()

    def save_prefs(self):
        # Save preferences. Called when dialog is closed.
        master = self.master
        top = self.top
        width = float(master.winfo_width())
        height = float(master.winfo_height())
        posx = (top.winfo_rootx() + self.x_correction - master.winfo_rootx())\
             / width
        posy = (top.winfo_rooty() + self.y_correction - master.winfo_rooty())\
             / height
        setattr(config.preferences, self.pref_pos_name, (posx, posy))

    def close_dlg(self):
        self.issue(CLOSED, self)
        if self.document:
            self.unsubscribe_receivers()
        self.document = None
        try:
            self.main_window.Unsubscribe(DOCUMENT, self.doc_changed)
        except:
            warn_tb(INTERNAL)
        self.main_window = None
        Publisher.Destroy(self)
        self.save_prefs()
        self.top.destroy()
        self.master = None
        import pax
        pax.unregister_object(self)

    def create_std_buttons(self, master):
        frame = Frame(master)

        button = UpdatedButton(frame, text = _("Apply"),
                               command = self.do_apply,
                               sensitivecb = self.can_apply)
        button.pack(side = LEFT, expand = 1, fill = X)
        button = UpdatedButton(frame, text = _("Close"),
                               command = self.close_dlg)
        button.pack(side = RIGHT, expand = 1, fill = X)

        return frame

    def build_dlg(self):
        # Build the dialog window. Must be provided by the subclasses.
        pass

    def init_from_doc(self):
        # Called whenever the document changes and from __init__
        pass

    def Update(self):
        # Called when the selection changes.
        pass

    def do_apply(self):
        # called by the `Apply' standard button to apply the settings
        pass

    def can_apply(self):
        return 1


class PropertyPanel(SketchPanel):

    receivers = SketchPanel.receivers[:]

    def __init__(self, master, main_window, doc, *args, **kw):
        self.var_auto_update = IntVar(master)
        self.var_auto_update.set(1)
        apply(SketchPanel.__init__, (self, master, main_window, doc) +args, kw)

    receivers.append((SELECTION, 'selection_changed'))
    receivers.append((EDITED, 'selection_changed'))
    def selection_changed(self, *args):
        if self.var_auto_update.get():
            self.Update()

    def create_std_buttons(self, master, update_from = 1):
        button_frame = Frame(master)

        button = Checkbutton(button_frame, text = _("Auto Update"),
                             variable = self.var_auto_update)
        button.pack(side = TOP, expand = 1, fill = X)

        if update_from:
            button = UpdatedButton(button_frame, text = _("Update From..."),
                                   command = self.update_from_object)
            button.pack(side = TOP, expand = 1, fill = X)

        button = UpdatedButton(button_frame, text = _("Apply"),
                               command = self.do_apply,
                               sensitivecb = self.can_apply)
        button.pack(side = LEFT, expand = 1, fill = X)
        self.Subscribe(SELECTION, button.Update)
        button = UpdatedButton(button_frame, text = _("Close"),
                               command = self.close_dlg)
        button.pack(side = RIGHT, expand = 1, fill = X)

        return button_frame

    def update_from_object(self):
        self.main_window.canvas.PickObject(self.update_from_object_cb)

    def update_from_object_cb(self, obj):
        pass

    can_apply = SketchPanel.doc_has_selection

    def SetDocument(self, doc):
        SketchPanel.SetDocument(self, doc)
        self.selection_changed()


class StylePropertyPanel(PropertyPanel):

    def can_apply(self):
        return PropertyPanel.can_apply(self) \
               or config.preferences.set_default_properties

    def set_properties(self, title, category, kw):
        import styledlg
        styledlg.set_properties(self.master, self.document, title, category,
                                kw)


class CommandPanel(SketchPanel):

    pass


#
#	Modal dialogs...
#

class SKModal:

    title = ''

    class_name = 'SKModal'

    old_focus = None
    focus_widget = None

    def __init__(self, master, **kw):
        self.master = master

        kw['class'] = self.class_name
        top = apply(Toplevel, (master,), kw)
        top.title(self.title)
        top.transient(master)
        top.group(master)
        top.iconname(self.title)
        top.iconbitmap(pixmaps.Icon)
        top.iconmask(pixmaps.Icon_mask)
        top.protocol('WM_DELETE_WINDOW', self.close_dlg)

        self.top = top
        self.build_dlg()
        mcx = master.winfo_rootx() + master.winfo_width()/ 2
        mcy = master.winfo_rooty() + master.winfo_height() / 2
        top.withdraw()
        top.update()
        width = top.winfo_reqwidth()
        height = top.winfo_reqheight()
        posx = max(min(top.winfo_screenwidth() - width, mcx - width / 2), 0)
        posy = max(min(top.winfo_screenheight() - height, mcy - height / 2), 0)
        top.geometry('%+d%+d' % (posx, posy))
        top.deiconify()

        self.result = None

    if __debug__:
        def __del__(self):
            pdebug('__del__', '__del__', self)

    def build_dlg(self):
        pass

    def ok(self, *args):
        self.close_dlg()

    def cancel(self):
        self.close_dlg(None)

    def close_dlg(self, result = None):
        self.result = result
        if self.old_focus is not None:
            self.old_focus.focus_set()
            self.old_focus = None
        self.top.destroy()

    def RunDialog(self, grab = 1):
        try:
            self.old_focus = self.top.focus_get()
        except KeyError:
            # focus_get fails when the focus widget is a torn-off menu,
            # since there#s no corresponding Tkinter object.
            self.old_focus = None
        grab_widget = None
        if grab:
            if not self.top.winfo_ismapped():
                self.top.wait_visibility()
            grab_widget = self.top.grab_current()
            if grab_widget is not None:
                grab_status = grab_widget.grab_status()
            self.top.grab_set()
        if self.focus_widget is not None:
            self.focus_widget.focus_set()
        else:
            self.top.focus_set()
        self.result = None
        self.master.wait_window(self.top)
        if grab_widget is not None:
            if grab_status == 'global':
                grab_widget.grab_set_global()
            else:
                grab_widget.grab_set()
        return self.result


class MessageDialog(SKModal):

    class_name = 'SKMessageDialog'

    def __init__(self, master, title, message, buttons = _("OK"), default = 0,
                 bitmap = 'warning', dlgname = '__dialog__'):
        self.title = title
        self.message = message
        if type(buttons) != type(()):
            buttons = (buttons,)
        self.buttons = buttons
        self.default = default
        self.bitmap = bitmap
        SKModal.__init__(self, master, name = dlgname)

    def build_dlg(self):
        top = self.top
        frame = Frame(top, name = 'top')
        frame.pack(side = TOP, fill = BOTH, expand = 1)
        bitmap = pixmaps.load_image(self.bitmap)
        if type(bitmap) == StringType:
            label = Label(frame, bitmap = bitmap, name = 'bitmap')
        else:
            label = Label(frame, image = bitmap, name = 'bitmap')
        label.pack(side = LEFT, padx = 5, pady = 5)
        label = Label(frame, text = self.message, name = 'msg')
        label.pack(side = RIGHT, fill = BOTH, expand = 1, padx = 5, pady = 5)

        frame = Frame(top, name = 'bot')
        frame.pack(side = BOTTOM, fill = X, expand = 1)
        command = self.ok
        for i in range(len(self.buttons)):
            button = UpdatedButton(frame, text = self.buttons[i],
                                   command = command, args = i)
            button.grid(column = i, row = 0, sticky = 'ew', padx = 10)
            if i == self.default:
                if TkVersion >= 8.0:
                    button['default'] = 'active'
                self.focus_widget = button
            else:
                if TkVersion >= 8.0:
                    button['default'] = 'normal'

        if self.default is not None:
            top.bind('<Return>', self.invoke_default)

    def ok(self, pos):
        self.close_dlg(pos)

    def invoke_default(self, *rest):
        self.ok(self.default)
