# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998 by Bernhard Herzog
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
# A dictionary with undo capability. This is used for the styles, so
# this dictionary assumes, that objects stored in it have SetName() and
# Name() methods.
#

from undo import NullUndo

class UndoDict:

    def __init__(self):
        self.dict = {}

    def __getitem__(self, key):
        return self.dict[key]

    def __len__(self):
        return len(self.dict)

    def keys(self):
        return self.dict.keys()

    def items(self):
        return self.dict.items()

    def values(self):
        return self.dict.values()

    def has_key(self, key):
        return self.dict.has_key(key)

    def SetItem(self, key, item):
        # Add ITEM to self using KEY.
        #      
        # Two cases:
        #
        #	1. ITEM is stored in self under item.Name(): Store it under
        #	KEY, rename ITEM and remove the old entry.
        #
        #	2. ITEM is not stored in self: Store it under KEY and rename
        #	ITEM.
        if self.dict.has_key(key):
            if self.dict[key] is item:
                return NullUndo
            # name conflict
            raise ValueError, '%s already used' % key
        oldname = item.Name()
        if self.dict.has_key(oldname):
            del self.dict[oldname]
            undo = (self.SetItem, oldname, item)
        else:
            undo = (self.DelItem, key)
        item.SetName(key)
        self.dict[key] = item
        return undo

    def DelItem(self, key):
        item = self.dict[key]
        del self.dict[key]
        return (self.SetItem, key, item)



