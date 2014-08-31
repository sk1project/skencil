# Sketch - A Python-based interactive drawing program
# Copyright (C) 1998, 1999 by Bernhard Herzog
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


from Sketch import config
from Sketch.const import CHANGED
from Sketch.Lib.units import unit_dict, unit_names
from tkext import UpdatedLabel, UpdatedMenu, MenuCommand

# NLS:
formats = {'in': '(%3.3f", %3.3f")',
           'pt': '(%3.1fpt, %3.1fpt)',
           'cm': '(%2.2fcm, %2.2fcm)',
           'mm': '(%3.1fmm, %3.1fmm)',
           }

class PositionLabel(UpdatedLabel):

    context_menu = None

    def __init__(self, *args, **kw):
        apply(UpdatedLabel.__init__, (self,) + args, kw)
        self.bind('<ButtonPress-3>', self.popup_context_menu)
        self.set_unit(config.preferences.default_unit)
        config.preferences.Subscribe(CHANGED, self.preference_changed)

    def Update(self, *rest):
        if self.sensitivecb:
            self.SetSensitive(self.sensitivecb())
        if self.updatecb and self.update_field:
            x, y = self.updatecb()
            x = x / self.factor
            y = y / self.factor
            self[self.update_field] = self.format % (x, y)

    def popup_context_menu(self, event):
        if self.context_menu is None:
            items = []
            set_unit = self.SetUnit
            for unit in unit_names:
                items.append(MenuCommand(unit, set_unit, unit))
            self.context_menu = UpdatedMenu(self, items, tearoff = 0)
        self.context_menu.Popup(event.x_root, event.y_root)

    def set_unit(self, unit):
        self.factor = unit_dict[unit]
        self.format = formats[unit]
        self.Update()

    def SetUnit(self, unit):
        self.unit = unit
        if config.preferences.poslabel_sets_default_unit:
            config.preferences.default_unit = unit
        else:
            self.set_unit(unit)

    def preference_changed(self, pref, value):
        if pref == 'default_unit':
            self.set_unit(value)


