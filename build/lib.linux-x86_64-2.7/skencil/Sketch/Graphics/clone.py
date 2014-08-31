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

#
#	The Clone Object
#

#from traceback import print_stack

from Sketch import Translation, NullPoint, Trafo
from Sketch import PointType, Undo, NullUndo
from Sketch.const import CHANGED
from base import Bounded, HierarchyNode



_clone_registry = {}

def _register_clone(original):
    original = id(original)
    _clone_registry[original] = _clone_registry.get(original, 0) + 1

def _unregister_clone(original):
    original = id(original)
    _clone_registry[original]= _clone_registry[original] - 1
    if _clone_registry[original] == 0:
        del _clone_registry[original]

class Clone(Bounded, HierarchyNode):

    is_Clone = 1

    def __init__(self, original = None, duplicate = None):
        HierarchyNode.__init__(self, duplicate = duplicate)
        if original is not None and original.is_Clone:
            duplicate = original
            original = None
        if duplicate is not None:
            self._original = duplicate._original
            self._center = duplicate._center
            self._offset = duplicate._offset
        else:
            self._original = original
            self._center = self._original.coord_rect.center()
            self._offset = NullPoint
        self.register()

    def register(self):
        _register_clone(self._original)
        self._original.Subscribe(CHANGED, self.orig_changed)

    def unregister(self):
        self._original.Unsubscribe(CHANGED, self.orig_changed)
        _unregister_clone(self._original)

    def __getattr__(self, attr):
        if self._lazy_attrs.has_key(attr):
            return Bounded.__getattr__(self, attr)
        #print 'Clone.__getattr__: from original:', attr
        #if attr in ('__nonzero__', 'document'):
        #    print_stack()
        return getattr(self._original, attr)

    def update_rects(self):
        off = self._offset
        self.bounding_rect = self._original.bounding_rect.translated(off)
        self.coord_rect = self._original.coord_rect.translated(off)

    def Translate(self, offset):
        self._offset = self._offset + offset
        self.del_lazy_attrs()
        return self.Translate, -offset

    def _set_offset(self, offset):
        undo = (self._set_offset, self._offset)
        self._offset = offset
        self.del_lazy_attrs()
        return undo

    def offset_center(self, offset):
        undo = (self.offset_center, -offset)
        self._center = self._center + offset
        return undo

    def Transform(self, trafo):
        center = self._center + self._offset
        offset = trafo(center) - center
        if self.document is not None:
            self.document.AddAfterHandler(_transform,
                                          (self._original, trafo.matrix()), -1)
        return self.offset_center(offset)

    def orig_changed(self, *args):
        if self.document is not None:
            self.document.AddClearRect(self.bounding_rect)
        self.del_lazy_attrs()
        center = self._center
        self._center = self._original.coord_rect.center()
        self._offset = self._offset + center - self._center
        if self.document is not None:
            self.document.AddClearRect(self.bounding_rect)

    def DrawShape(self, device, rect = None):
        device.PushTrafo()
        try:
            device.Translate(self._offset)
            self._original.DrawShape(device, rect)
        finally:
            device.PopTrafo()

    def Hit(self, p, rect, device):
        off = -self._offset
        return self._original.Hit(p + off, rect.translated(off), device)


    def Info(self):
        return 'Clone of ' + self._original.Info()


    # overwrite Selectable methods
    def SelectSubobject(self, p, rect, device, path = None, *rest):
        return self

    def GetObjectHandle(self, multiple):
        trafo = Translation(self._offset)
        handle = self._original.GetObjectHandle(multiple)
        if type(handle) == PointType:
            return trafo(handle)
        else:
            return map(trafo, handle)

    # overwrite Bounded methods
    def LayoutPoint(self):
        return self._original.LayoutPoint() + self._offset

    def GetSnapPoints(self):
        return map(Translation(self._offset), self._original.GetSnapPoints())


def _transform(original, matrix):
    trafo = apply(Trafo, matrix)
    undo = original.Transform(trafo)
    doc = original.document
    doc.AddUndo((_undo, doc, [undo]))

def _after_handler(undo, list):
    list[0] = Undo(undo)

def _undo(doc, undo):
    list = [NullUndo]
    doc.AddAfterHandler(_after_handler, (undo[0], list), -1)
    return (_undo, doc, list)

def CreateClone(object):
    clone = Clone(object)
    undo = object.parent.ReplaceChild(object, clone)
    return clone.Duplicate(), undo
