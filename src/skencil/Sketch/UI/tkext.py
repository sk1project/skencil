# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2002 by Bernhard Herzog
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

import os
from types import TupleType, ListType, InstanceType, StringType

import pax

from Sketch import _, Publisher, StandardColors, config
from Sketch.const import CHANGED, DROP_COLOR, COMMAND, SELECTION
from Sketch.warn import warn_tb, INTERNAL


from Tkinter import Widget, Menu, Menubutton, Frame
from Tkinter import LEFT, DISABLED, NORMAL, END, RAISED, Y, X, TOP
import Tkinter
import tkFileDialog

import command
from skpixmaps import PixmapTk

class SketchDropTarget:

    accept_drop = ()

    def DropAt(self, x, y, what, data):
        pass


class AutoUpdate:

    update_field = 'text'
    updatecb = None
    sensitivecb = None

    def __init__(self, sensitivecb=None, updatecb=None,
                 update_field=None, kw=None):
        if kw is None:
            kw = {}

        if kw.has_key('sensitivecb'):
            self.sensitivecb = kw['sensitivecb']
            del kw['sensitivecb']
        else:
            self.sensitivecb = sensitivecb

        if kw.has_key('updatecb'):
            self.updatecb = kw['updatecb']
            del kw['updatecb']
        else:
            self.updatecb = updatecb

        if kw.has_key('update_field'):
            self.update_field = kw['update_field']
            del kw['update_field']
        else:
            if update_field is not None:
                self.update_field = update_field

    def clean_up(self):
        self.sensitivecb = None
        self.updatecb = None

    def SetSensitiveCallback(self, sensitivecb):
        self.sensitivecb = sensitivecb

    def SetUpdateCallback(self, updatecb):
        self.updatecb = updatecb

    def Update(self, *rest):
        if self.sensitivecb:
            self.SetSensitive(self.sensitivecb())
        if self.updatecb and self.update_field:
            self[self.update_field] = self.updatecb()

    def SetSensitive(self, on):
        # for ordinary TkWidgets:
        if on:
            self['state'] = NORMAL
        else:
            self['state'] = DISABLED

class WidgetWithCommand(Publisher):

    # true, iff the underlying Tk-widget has a command option.
    tk_widget_has_command = 1

    def __init__(self):
        pass

    def clean_up(self):
        Publisher.Destroy(self)
        pax.unregister_object(self)

    def set_command(self, command, args=()):
        if self.tk_widget_has_command and not self['command']:
            self['command'] = MakeMethodCommand(self._call_cmd)
        if type(args) != TupleType:
            args = (args,)
        apply(self.Subscribe, (COMMAND, command,) + args)

    def _call_cmd(self, *args):
        try:
            apply(self.issue, (COMMAND,) + args)
        except:
            warn_tb(INTERNAL)


class MenuEntry:

    tk_entry_type = None
    index = None
    menu = None

    def __init__(self, kw_args):
        self.rest = kw_args

    def clean_up(self):
        self.rest = {}
        pax.unregister_object(self)
        self.variable = None

    def AddToMenu(self, menu):
        if menu:
            apply(menu.add, (self.tk_entry_type,), self.rest)
        self.menu = menu

    def SetIndex(self, index):
        self.index = index

    def Update(self):
        pass

    def __setitem__(self, key, item):
        if self.menu is not None:
            self.menu.entryconfig(self.index, {key:item})
        else:
            self.rest[key] = item

    def __getitem__(self, key):
        if self.menu is not None:
            self.menu.entryconfig(self.index, key)
        else:
            return self.rest[key]

    def configure(self, **kw):
        if self.menu is not None:
            self.menu.entryconfig(self.index, kw)

    def IgnoreEntry(self):
        return 0




class MenuCommand(AutoUpdate, WidgetWithCommand, MenuEntry):

    tk_entry_type = 'command'
    update_field = 'label'

    def __init__(self, text='', command=None, args=(),
                 sensitivecb=None, updatecb=None, bitmap=None,
                 **rest):
        AutoUpdate.__init__(self, sensitivecb, updatecb)
        WidgetWithCommand.__init__(self)
        rest['command'] = ''
        MenuEntry.__init__(self, rest)
        if bitmap:
            rest['bitmap'] = bitmap
        else:
            rest['label'] = text
        self.set_command(command, args)

    def clean_up(self):
        AutoUpdate.clean_up(self)
        WidgetWithCommand.clean_up(self)
        MenuEntry.clean_up(self)

class MenuCommand2(MenuEntry):

    tk_entry_type = 'command'

    def __init__(self, command, **rest):
        self.command = command
        rest = self.add_kw_args(rest)
        rest['command'] = MakeMethodCommand(self.command.Invoke)
        MenuEntry.__init__(self, rest)
        command.Subscribe(CHANGED, self._update)
        self._update()

    def add_kw_args(self, dict, no_active=0):
        cmd = self.command
        dict['label'] = cmd.menu_name
        dict['state'] = cmd.sensitive and NORMAL or DISABLED
        key_stroke = cmd.key_stroke
        if key_stroke:
            if type(key_stroke) == TupleType:
                dict['accelerator'] = key_stroke[0]
            else:
                dict['accelerator'] = key_stroke
        return dict

    def _update(self):
        self.rest = self.add_kw_args(self.rest)
        apply(self.configure, (), self.rest)

    def IgnoreEntry(self):
        return not self.command.menu_name




class MenuCheck(AutoUpdate, WidgetWithCommand, MenuEntry):

    tk_entry_type = 'checkbutton'
    update_field = ''

    def __init__(self, text='', command=None, args=(),
                 sensitivecb=None, updatecb=None, bitmap=None,
                 **rest):
        self.var_on = Tkinter.IntVar()
        rest['variable'] = self.var_on
        AutoUpdate.__init__(self, sensitivecb, updatecb)
        WidgetWithCommand.__init__(self)
        rest['command'] = ''
        MenuEntry.__init__(self, rest)
        if bitmap:
            rest['bitmap'] = bitmap
        else:
            rest['label'] = text
        self.set_command(command, args)

    def Update(self):
        AutoUpdate.Update(self)
        if self.updatecb:
            self.var_on.set(self.updatecb())

class MenuCheck2(MenuEntry):

    tk_entry_type = 'checkbutton'

    def __init__(self, command, **rest):
        self.command = command
        self.var_value = Tkinter.IntVar()
        self.var_value.set(command.IsOn())
        rest['variable'] = self.var_value
        rest = self.add_kw_args(rest)
        rest['command'] = MakeMethodCommand(self.command.Invoke)
        MenuEntry.__init__(self, rest)

        command.Subscribe(CHANGED, self._update)

    def add_kw_args(self, dict):
        cmd = self.command
        dict['label'] = cmd.menu_name
        dict['state'] = cmd.sensitive and NORMAL or DISABLED
        key_stroke = cmd.key_stroke
        if key_stroke:
            if type(key_stroke) == TupleType:
                dict['accelerator'] = key_stroke[0]
            else:
                dict['accelerator'] = key_stroke
        return dict

    def _update(self):
        self.var_value.set(self.command.IsOn())
        apply(self.configure, (), self.add_kw_args(self.rest))


class MenuSeparator(MenuEntry):

    tk_entry_type = 'separator'

    def __init__(self, **rest):
        MenuEntry.__init__(self, rest)


class UpdatedMenu:

    entries = None
    menu = None

    rebuild_func = None

    def __init__(self, master, entries, auto_update=1, auto_rebuild=None,
                 **rest):
        if auto_update:
            rest['postcommand'] = MakeMethodCommand(self.Update)
        if auto_rebuild is not None:
            rest['postcommand'] = MakeMethodCommand(self.RebuildMenu)
            self.rebuild_func = auto_rebuild
        rest['tearoffcommand'] = MakeMethodCommand(self._tearoff)
        self.menu = apply(Menu, (master,), rest)
        self.SetEntries(entries)

    def __del__(self):
        self.clean_up()

    def clean_up(self):
        if self.entries:
            for entry in self.entries:
                entry.clean_up()
        self.entries = None
        self.menu = None
        pax.unregister_object(self)

    destroy = clean_up

    def _tearoff(self, menu, tearoff):
        # tk8 needs this on my machine... (afterstep 1.4)
        # in tk4.2 this wasn't necessary.
        try:
            call = self.menu.tk.call
            # Set the group and transient window properties so that
            # torn-off menus stay on top of the main window. It seems
            # that tk4.2 did this itself, but not tk8.
            call('wm', 'group', tearoff, '.')
            call('wm', 'transient', tearoff, '.')
            # withdraw and deiconify needed for `braindead' Window
            # managers that don't recognize property changes after
            # windows are mapped.
            if config.preferences.menu_tearoff_fix:
                call('wm', 'withdraw', tearoff)
                call('wm', 'deiconify', tearoff)
        except:
            warn_tb(INTERNAL, 'tearoffcommand')

    def Update(self):
        try:
            for entry in self.entries:
                entry.Update()
        except:
            warn_tb(INTERNAL, 'Updating menu Entries')

    def __build_menu(self):
        if self.menu['tearoff'] == '1':
            index = 1
        else:
            index = 0
        last_was_sep = 0
        for entry in self.entries:
            if not entry.IgnoreEntry():
                if last_was_sep and isinstance(entry, MenuSeparator):
                    continue
                entry.AddToMenu(self.menu)
                entry.SetIndex(index)
                index = index + 1
                last_was_sep = isinstance(entry, MenuSeparator)
            else:
                entry.AddToMenu(None)

    def RebuildMenu(self):
        if self.entries is not None:
#        self.menu.delete(0, END)
            self.menu.tk.call(self.menu._w, 'delete', 0, END)
        if self.rebuild_func is not None:
            try:
                self.entries = self.rebuild_func()
            except:
                warn_tb(INTERNAL, 'Trying to rebuild menu')
        self.__build_menu()
        self.Update()

    def SetEntries(self, entries):
        if self.entries is not None:
#        self.menu.delete(0, END)
            self.menu.tk.call(self.menu._w, 'delete', 0, END)
            for entry in self.entries:
                entry.clean_up()
        self.entries = entries
        self.__build_menu()

    def Popup(self, x, y):
        self.menu.tk_popup(x, y)

class MenuCascade(MenuEntry):

    def __init__(self, text, entries, **kw):
        self.entries = entries
        self.label = text
        self.submenu = None
        self.kwargs = kw

    def AddToMenu(self, menu):
        if menu:
            self.submenu = apply(UpdatedMenu, (menu, self.entries), self.kwargs)
            menu.add('cascade', label=self.label, menu=self.submenu.menu)
        self.menu = menu


def AppendMenu(mbar, text, menu_list):
    button = Menubutton(mbar, text=text)
    button.pack(side=LEFT)

    menu = UpdatedMenu(button, menu_list)
    button.menu = menu
    button['menu'] = menu.menu
    return menu



#
#      Simpler menu creation
#

cmd_classes = (command.Command, command.ObjectCommand)

def MakeCommand(label, func=None, args=(), sensitive=None, update=None):
    if label:
        if type(label) == TupleType:
            return apply(MakeCommand, label)
        elif type(label) == ListType:
            text = label[0]
            if type(text) == TupleType:
                text, kwargs = text
            else:
                kwargs = {}
            return apply(MenuCascade, (text, map(MakeCommand, label[1:])),
                         kwargs)
        elif type(label) == InstanceType:
            if label.__class__ in cmd_classes:
                if label.is_command:
                    return MenuCommand2(label)
                elif label.is_check:
                    return MenuCheck2(label)
                raise ValueError, 'invalid menu specifier'

            else:
                return label
        elif label[0] == '*':
            return MenuCheck(label[1:], func, args,
                             sensitivecb=sensitive, updatecb=update)
        else:
            return MenuCommand(label, func, args,
                               sensitivecb=sensitive, updatecb=update)
    else:
        return MenuSeparator()


class UpdatedLabel(Tkinter.Label, AutoUpdate):

    def __init__(self, master, **kw):
        AutoUpdate.__init__(self, kw=kw)
        apply(Tkinter.Label.__init__, (self, master), kw)

    def destroy(self):
        AutoUpdate.clean_up(self)
        Tkinter.Label.destroy(self)


class UpdatedButton(Tkinter.Button, AutoUpdate, WidgetWithCommand):

    def __init__(self, master, command=None, args=(), **kw):
        AutoUpdate.__init__(self, kw=kw)
        WidgetWithCommand.__init__(self)
        apply(Tkinter.Button.__init__, (self, master), kw)
        if command:
            self.set_command(command, args)

    def destroy(self):
        AutoUpdate.clean_up(self)
        WidgetWithCommand.clean_up(self)
        Tkinter.Button.destroy(self)

class MultiButton(UpdatedButton):

    def __init__(self, *arg, **kw):
        apply(UpdatedButton.__init__, (self,) + arg, kw)
        self.bind('<ButtonPress-3>', self.press)
        self.bind('<ButtonRelease-3>', self.release)
        self.two = 0

    def press(self, event):
        self.event_generate('<ButtonPress-1>')

    def release(self, event):
        self.two = 1
        try:
            self.event_generate('<ButtonRelease-1>')
        finally:
            self.two = 0


    def _call_cmd(self, *args):
        if self.two:
            try:
                apply(self.issue, ('COMMAND2',) + args)
            except:
                warn_tb(INTERNAL)
        else:
            apply(UpdatedButton._call_cmd, (self,) + args)


import tooltips

class CommandButton(Tkinter.Button):

    def __init__(self, master, command=None, args=(), **kw):
        self.command = command
        if type(args) != TupleType:
            args = (args,)
        self.args = args
        kw['command'] = MakeMethodCommand(self.command.Invoke)
        if command.bitmap:
            bitmap = PixmapTk.load_image(command.bitmap)
            if type(bitmap) == StringType:
                kw['bitmap'] = bitmap
            else:
                kw['image'] = bitmap
        else:
            kw['text'] = command.button_name
        command.Subscribe(CHANGED, self._update)
        apply(Tkinter.Button.__init__, (self, master), kw)
        tooltips.AddDescription(self, command.menu_name)
        self._update()

    def _update(self):
        state = self.command.sensitive and NORMAL or DISABLED
        if self.command.bitmap:
            bitmap = PixmapTk.load_image(self.command.bitmap)
            if type(bitmap) == StringType:
                self.configure(bitmap=bitmap, state=state)
            else:
                self.configure(image=bitmap, state=state)
        else:
            self.configure(text=self.command.button_name, state=state)
        tooltips.AddDescription(self, self.command.menu_name)

    def destroy(self):
        self.command.Unsubscribe(CHANGED, self._update)
        pax.unregister_object(self.command)
        self.command = self.args = None
        Tkinter.Button.destroy(self)
        pax.unregister_object(self)

class CommandCheckbutton(CommandButton):

    def __init__(self, master, command=None, args=(), **kw):
        if not command.is_check:
            raise TypeError, ("command %s is not a check-command" % command)
        apply(CommandButton.__init__, (self, master, command, args), kw)

    def _update(self):
        if self.command.IsOn():
            self.configure(relief='sunken')
        else:
            self.configure(relief=self.option_get('relief', 'Relief'))
        CommandButton._update(self)


class UpdatedCheckbutton(Tkinter.Checkbutton, AutoUpdate, WidgetWithCommand):

    def __init__(self, master, command=None, args=(), **kw):
        AutoUpdate.__init__(self, kw=kw)
        WidgetWithCommand.__init__(self)
        apply(Tkinter.Checkbutton.__init__, (self, master), kw)
        if command:
            self.set_command(command, args)

    def destroy(self):
        AutoUpdate.clean_up(self)
        WidgetWithCommand.clean_up(self)
        Tkinter.Checkbutton.destroy(self)

class UpdatedRadiobutton(Tkinter.Radiobutton, AutoUpdate, WidgetWithCommand):

    def __init__(self, master, command=None, args=(), **kw):
        AutoUpdate.__init__(self, kw=kw)
        WidgetWithCommand.__init__(self)
        apply(Tkinter.Radiobutton.__init__, (self, master), kw)
        if command:
            self.set_command(command, args)

    def destroy(self):
        AutoUpdate.clean_up(self)
        WidgetWithCommand.clean_up(self)
        Tkinter.Radiobutton.destroy(self)


class UpdatedListbox(Tkinter.Listbox, AutoUpdate, WidgetWithCommand):

    tk_widget_has_command = 0
    tk_command_event = '<Double-Button-1>'
    tk_select_event = '<ButtonRelease-1>'
    tk_event_bound = 0

    def __init__(self, master, command=None, args=(), **kw):
        AutoUpdate.__init__(self, kw=kw)
        apply(Tkinter.Listbox.__init__, (self, master), kw)
        WidgetWithCommand.__init__(self)
        if command:
            self.set_command(command, args)
        self.bind(self.tk_command_event, self._call_cmd)
        self.bind(self.tk_select_event, self._call_selection)

    def destroy(self):
        AutoUpdate.clean_up(self)
        WidgetWithCommand.clean_up(self)
        Tkinter.Listbox.destroy(self)

    def set_command(self, command, args=()):
        WidgetWithCommand.set_command(self, command, args)

    def SetList(self, list):
        self.delete(0, END)
        for item in list:
            self.insert(END, item)

    def SelectNone(self):
        self.select_clear(0, END)

    def Select(self, idx, view=0):
        self.select_clear(0, END)
        self.select_set(idx)
        if view:
            self.yview(idx)

    def _call_cmd(self, event, *rest):
        WidgetWithCommand._call_cmd(self)

    def _call_selection(self, event, *rest):
        self.issue(SELECTION)

class MyEntry(Tkinter.Entry, WidgetWithCommand):

    tk_widget_has_command = 0
    tk_command_event = '<Return>'
    tk_event_bound = 0

    def __init__(self, master, command=None, args=(), **kw):
        apply(Tkinter.Entry.__init__, (self, master), kw)
        WidgetWithCommand.__init__(self)
        if command:
            self.set_command(command, args)

    def destroy(self):
        WidgetWithCommand.clean_up(self)
        Tkinter.Entry.destroy(self)

    def SetText(self, text):
        self.delete(0, END)
        self.insert(0, text)

    def set_command(self, command, args=()):
        WidgetWithCommand.set_command(self, command, args)
        if command and not self.tk_event_bound:
            self.bind(self.tk_command_event, self._call_cmd)
            self.tk_event_bound = 1

    def _call_cmd(self, event, *rest):
        WidgetWithCommand._call_cmd(self, self.get())


class PyWidget(Widget, SketchDropTarget):

    def __init__(self, master=None, **kw):
        key = pax.register_object(self)
        kw['pyobject'] = key
        kw['class'] = self.__class__.__name__
        Widget.__init__(self, master, 'paxwidget', kw=kw)
        self.InitTkWinObject(pax.name_to_window(self._w, self.tk.interpaddr()))

    def DestroyMethod(self):
        self.tkwin = None
        self.tkborder = None
        pax.unregister_object(self)

    def MapMethod(self):
        pass

    def RedrawMethod(self, region=None):
        pass

    def ResizedMethod(self, width, height):
        pass

    def InitTkWinObject(self, tkwin):
        self.tkwin = tkwin

    def InitTkBorder(self, tkborder):
        self.tkborder = tkborder

    def UpdateWhenIdle(self):
        self.tk.call(self._w, 'update')



def GetOpenFilename(master, **kw):
    cmd = "kdialog --getopenfilename"
    if 'initialdir' in kw:
        cmd += " " + kw['initialdir']
    filename = os.popen(cmd).read().strip()
#     filename = apply(master.tk.call,
#                      ('tk_getOpenFile', '-parent', master._w)
#                      + master._options(kw))
    return filename
#     return master.tk.utf8_to_system(filename)

def GetSaveFilename(master, **kw):
    cmd = "kdialog --getsavefilename"
    if 'initialdir' in kw:
        cmd += " " + kw['initialdir']
    filename = os.popen(cmd).read().strip()
#     filename = apply(master.tk.call,
#                      ('tk_getSaveFile', '-parent', master._w)
#                      + master._options(kw))
    return filename
#     return master.tk.utf8_to_system(filename)

# NLS:
#
# The MessageDialog should be iternationalized in such a way that
# programmers can still test the return value in a convenient way.
Ok = _("Ok")
Yes = _("Yes")
No = _("No")
Cancel	 = _("Cancel")
OkCancel = (Ok, Cancel)
YesNo = (Yes, No)
YesNoCancel = (Yes, No, Cancel)

def MessageDialog(master, title, message, buttons=Ok, default=0,
                  icon='warning'):
    if type(buttons) != TupleType:
        buttons = (buttons,)
    from sketchdlg import MessageDialog
    dlg = MessageDialog(master, title, message, buttons, default, icon)
    result = dlg.RunDialog()
    if result is not None:
        return buttons[result]
    return ''




def rgb_to_tk((r, g, b)):
    return '#%04x%04x%04x' % (65535 * r, 65535 * g, 65535 * b)

class ColorButton(WidgetWithCommand, Tkinter.Button, SketchDropTarget):

    color_option = 'bg'
    accept_drop = (DROP_COLOR,)

    def __init__(self, master, command=None, args=(),
                 color=None, dialog_master=None, **kw):
        WidgetWithCommand.__init__(self)
        apply(Tkinter.Button.__init__, (self, master), kw)
        if color is None:
            color = StandardColors.white
        self.set_color(color)
        if command:
            self.set_command(command, args)
        if dialog_master is None:
            self.dialog_master = master
        else:
            self.dialog_master = dialog_master

    def destroy(self):
        self.clean_up()
        Tkinter.Button.destroy(self)

    def set_color(self, color):
        self.color = color
        tk_color = rgb_to_tk(color)
        self[self.color_option] = tk_color
        self['activebackground'] = tk_color

    def SetColor(self, color):
        changed = self.color != color
        self.set_color(color)
        return changed

    def Color(self):
        return self.color

    def _call_cmd(self, *args):
        import colordlg
        new_color = colordlg.GetColor(self.dialog_master, self.color)
        if new_color:
            self.set_color(new_color)
            apply(WidgetWithCommand._call_cmd, (self,) + args)

    def DropAt(self, x, y, what, data):
        if what == DROP_COLOR:
            if self.SetColor(data):
                apply(WidgetWithCommand._call_cmd, (self,))

#
option_menu_defaults = {
    "borderwidth": 2,
    "indicatoron": 1,
    "relief": RAISED,
    "anchor": "c",
    "highlightthickness": 1
}
class MyOptionMenu(WidgetWithCommand, Menubutton):

    tk_widget_has_command = 0

    def __init__(self, master, values, command=None, args=(),
                 variable=None):
        kw = option_menu_defaults.copy()
        if variable is not None:
            kw['textvariable'] = variable
        self.variable = variable
        WidgetWithCommand.__init__(self)
        Widget.__init__(self, master, "menubutton", kw)
        # self.widgetName = 'tk_optionMenu'
        if command:
            self.set_command(command, args)

        entries = []
        for value in values:
            entries.append(MenuCommand(value, command=self.choose_opt,
                                       args=value))
        self.__menu = UpdatedMenu(self, entries, auto_update=0,
                                  name="menu", tearoff=0)
        menu = self.__menu.menu
        self.menuname = menu._w
        self["menu"] = menu

    def destroy(self):
        WidgetWithCommand.clean_up(self)
        Menubutton.destroy(self)
        self.__menu = None

    def choose_opt(self, value):
        self['text'] = value
        self._call_cmd(value)

    def __getitem__(self, name):
        if name == 'menu':
            return self.__menu.menu
        return Widget.__getitem__(self, name)


class MyOptionMenu2(WidgetWithCommand, Menubutton):

    tk_widget_has_command = 0

    def __init__(self, master, values, command=None, args=(),
                 entry_type='text', **rest):
        kw = option_menu_defaults.copy()
        kw.update(rest)
        WidgetWithCommand.__init__(self)
        Widget.__init__(self, master, "menubutton", kw)
        self.widgetName = 'tk_optionMenu'
        if command:
            self.set_command(command, args)

        entries = []
        value_dict = {}
        cfg = {'command' : self.choose_opt}
        for value in values:
            if type(value) == TupleType:
                text, value = value
            else:
                text = value
            value_dict[value] = text
            if not rest.has_key('initial'):
                rest['initial'] = value

            cfg[entry_type] = text
            cfg['args'] = (value,)
            entries.append(apply(MenuCommand, (), cfg))

        self.__menu = UpdatedMenu(self, entries, auto_update=0,
                                  name="menu", tearoff=0)
        menu = self.__menu.menu
        self.menuname = menu._w
        self["menu"] = menu
        self.entry_type = entry_type
        self.value_dict = value_dict
        if rest.has_key('initial'):
            self.SetValue(rest['initial'])

    def destroy(self):
        WidgetWithCommand.clean_up(self)
        Menubutton.destroy(self)
        self.__menu = None

    def choose_opt(self, value):
        self.SetValue(value)
        self._call_cmd(value)

    def SetValue(self, value, text=None):
        try:
            text = self.value_dict[value]
        except KeyError:
            if text is None:
                return
        self[self.entry_type] = text
        self.value = value

    def GetValue(self):
        return self.value

    def __getitem__(self, name):
        if name == 'menu':
            return self.__menu.menu
        return Widget.__getitem__(self, name)

class VSeparator(Frame):

    def __init__(self, master, **kw):
        kw['width'] = 2
        apply(Frame.__init__, (self, master), kw)
        darkline = Frame(self, class_='Darkline', width=1)
        darkline.pack(side=LEFT, fill=Y)
        lightline = Frame(self, class_='Lightline', width=1)
        lightline.pack(side=LEFT, fill=Y)

class HSeparator(Frame):

    def __init__(self, master, **kw):
        kw['height'] = 2
        apply(Frame.__init__, (self, master), kw)
        darkline = Frame(self, class_='Darkline', height=1)
        darkline.pack(side=TOP, fill=X)
        lightline = Frame(self, class_='Lightline', height=1)
        lightline.pack(side=TOP, fill=X)


def MakeMethodCommand(method, *args):
    obj = method.im_self
    name = method.__name__
    key = pax.register_object(obj)  # assuming that obj unregisters itself
    return ('call_py_method', key, name) + args


_tcl_commands_created = 0
def InitFromTkapp(tk):
    global _tcl_commands_created
    if not _tcl_commands_created:
        if hasattr(tk, 'interpaddr'):
            # introduced in Python 1.5.2
            pax.create_tcl_commands(tk.interpaddr())
        else:
            pax.create_tcl_commands(tk)
        # tk.call('load', pax.__file__, 'paxwidget')
    _tcl_commands_created = 1
