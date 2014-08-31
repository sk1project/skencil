# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 2001 by Bernhard Herzog
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


from types import StringType, TupleType, FunctionType

from Sketch import Publisher
from Sketch.const import CHANGED, SELECTION
from Sketch.warn import warn, warn_tb, INTERNAL

#
#	Command Class
#


class Command(Publisher):

    def __init__(self, cmd_class, object):
        self.cmd_class = cmd_class
        self.object = object

    def __getattr__(self, attr):
        try:
            return getattr(self.cmd_class, attr)
        except AttributeError:
            if attr == 'button_name':
                return self.menu_name
        raise AttributeError, attr

    def get_method(self, path):
        if callable(path):
            return path
        method = self.object
        if type(path) != TupleType:
            path = (path,)
        for name in path:
            method = getattr(method, name)
        return method

    def Invoke(self, args = ()):
        if type(args) != TupleType:
            args = (args,)
        try:
            apply(self.get_method(self.command), self.args + args)
        except:
            warn_tb(INTERNAL)

    def Update(self):
        # XXX: bitmaps and key_strokes should probably be also changeable
        changed = self.set_name(self.get_name())
        changed = self.set_sensitive(self.get_sensitive()) or changed
        changed = self.set_value(self.get_value()) or changed
        if changed:
            self.issue(CHANGED)

    def get_name(self):
        if self.name_cb:
            method = self.get_method(self.name_cb)
            if method:
                return method()
        return self.menu_name

    def set_name(self, menu_name = None):
        changed = self.menu_name != menu_name
        if changed:
            self.menu_name = menu_name
        return changed

    def get_sensitive(self):
        #print 'get_sensitive', self
        if self.sensitive_cb:
            method = self.get_method(self.sensitive_cb)
            if method:
                return method()
            else:
                warn(INTERNAL, 'no method for sensitive_cb (%s)',
                     self.sensitive_cb)
                return 0
        return 1

    def set_sensitive(self, sensitive):
        changed = self.sensitive != sensitive
        if changed:
            self.sensitive = sensitive
        return changed

    def get_value(self):
        if self.value_cb:
            method = self.get_method(self.value_cb)
            if method:
                return method()
        return self.value

    def set_value(self, value):
        changed = self.value != value
        if changed:
            self.value = value
        return changed

    def GetKeystroke(self):
        return self.key_stroke

    def GetValue(self):
        return self.value

    def IsOn(self):
        return self.value == self.value_on

    def InContext(self):
        return 1

    def set_bitmap(self, bitmap):
        if bitmap:
            changed = self.bitmap != bitmap
            self.bitmap = bitmap
            return changed
        return 0

    def __repr__(self):
        return 'Command: %s' % self.name



class CommandClass:

    cmd_class = Command

    # default attributes
    menu_name = '???'
    bitmap = None
    key_stroke = None

    name_cb = None
    sensitive_cb = None
    sensitive = 1
    value_cb = None
    value = 0
    value_on = 1
    value_off = 0

    is_command = 1
    is_check = 0
    invoke_with_keystroke = 0


    callable_attributes = ('name_cb', 'sensitive_cb', 'value_cb')

    def __init__(self, name, command, subscribe_to = None, args = (),
                 is_check = 0, **rest):
        self.name = name
        self.command = command
        self.subscribe_to = subscribe_to
        if type(args) != TupleType:
            self.args = (args,)
        else:
            self.args = args
        for key, value in rest.items():
            setattr(self, key, value)

        if is_check:
            self.is_check = 1
            self.is_command = 0


    def InstantiateFor(self, object):
        cmd = self.cmd_class(self, object)
        if self.subscribe_to:
            if type(self.subscribe_to) == TupleType:
                attrs = self.subscribe_to[:-1]
                for attr in attrs:
                    object = getattr(object, attr)
                subscribe_to = self.subscribe_to[-1]
            else:
                subscribe_to = self.subscribe_to
            object.Subscribe(subscribe_to, cmd.Update)
        return cmd

    def __repr__(self):
        return 'CommandClass: %s' % self.name



class ObjectCommand(Command):

    def get_method(self, path):
        if type(path) == type(""):
            return self.object.document.GetObjectMethod(self.object_class,path)
        return Command.get_method(self, path)

    def Invoke(self, args = ()):
        if type(args) != TupleType:
            args = (args,)
        try:
            apply(self.object.document.CallObjectMethod,
                  (self.object_class, self.menu_name, self.command) \
                  + self.args + args)
        except:
            warn_tb(INTERNAL)

    def get_sensitive(self):
        if self.object.document.CurrentObjectCompatible(self.object_class):
            return Command.get_sensitive(self)
        return 0

    def GetKeystroke(self):
        return self.key_stroke

    def GetValue(self):
        return self.value

    def InContext(self):
        return self.object.document.CurrentObjectCompatible(self.object_class)

    def __repr__(self):
        return 'ObjectCommand: %s' % self.name


class ObjectCommandClass(CommandClass):

    cmd_class = ObjectCommand
    object_class = None

    def SetClass(self, aclass):
        if self.object_class is None:
            self.object_class = aclass


#
#
#

class Commands:

    def Update(self):
        for item in self.__dict__.values():
            item.Update()

    def __getitem__(self, key):
        return getattr(self, key)

    def Get(self, name):
        try:
            return getattr(self, name)
        except AttributeError:
            for item in self.__dict__.values():
                if item.__class__ == Commands:
                    cmd = item.Get(name)
                    if cmd:
                        return cmd
            else:
                return None
#
#
#

class Keymap:

    def __init__(self):
        self.map = {}

    def AddCommand(self, command):
        key_stroke = command.GetKeystroke()
        if key_stroke:
            if type(key_stroke) == StringType:
                key_stroke = (key_stroke,)
            for stroke in key_stroke:
                if self.map.has_key(stroke):
                    # XXX: should be user visible if keybindings can be
                    # changed by user
                    warn(INTERNAL, 'Warning: Binding %s to %s replaces %s',
                         command.name, stroke, self.map[stroke].name)
                self.map[stroke] = command

    def MapKeystroke(self, stroke):
        if self.map.has_key(stroke):
            return self.map[stroke]


#
#
#

def AddCmd(list, name, menu_name, method = None, **kw):
    if type(name) == FunctionType:
        name = name.func_name
    if method is None:
        method = name
    elif type(method) == FunctionType:
        method = method.func_name
    kw['menu_name'] = menu_name
    kw['subscribe_to'] = SELECTION
    cmd = apply(ObjectCommandClass, (name, method), kw)
    list.append(cmd)
