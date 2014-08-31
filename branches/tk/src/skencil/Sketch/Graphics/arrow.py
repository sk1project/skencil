# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2001 by Bernhard Herzog
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
#	Arrows
#

import os
from types import TupleType, ListType
from math import atan2, sin, cos

from Sketch.warn import warn_tb, USER, pdebug
from Sketch import config
from Sketch import _, Trafo, CreatePath

from Sketch.loadres import read_resource_file

class Arrow:

    def __init__(self, path, closed = 0):
        self.path = CreatePath()
        if type(path) in (ListType, TupleType):
            for segment in path:
                if len(segment) == 2:
                    apply(self.path.AppendLine, segment)
                else:
                    apply(self.path.AppendBezier, segment)
        else:
            self.path = path
        if closed:
            self.path.load_close()

    def BoundingRect(self, pos, dir, width):
        try:
            angle = atan2(dir.y, dir.x)
        except ValueError:
            angle = 0
        if width < 1.0:
            width = 1.0
        s = width * sin(angle)
        c = width * cos(angle)
        trafo = Trafo(c, s, -s, c, pos.x, pos.y)
        return self.path.accurate_rect(trafo)

    def Draw(self, device, rect = None):
        if self.path.closed:
            device.FillBezierPath(self.path, rect)
        else:
            device.DrawBezierPath(self.path, rect)

    def Paths(self):
        return (self.path,)

    def IsFilled(self):
        return self.path.closed

    def SaveRepr(self):
        path = map(lambda t: t[:-1], self.path.get_save())
        return (path, self.path.closed)

    def __hash__(self):
        return hash(id(self.path))

    def __cmp__(self, other):
        if __debug__:
            pdebug(None, 'Arrow.__cmp__, %s', other)
        if isinstance(other, self.__class__):
            return cmp(self.path, other.path)
        return cmp(id(self), id(other))


def read_arrows(filename):
    arrows = []
    def arrow(path, closed, list = arrows):
        list.append(Arrow(path, closed))
    dict = {'arrow': arrow}

    read_resource_file(filename, '##Sketch Arrow 0',
                       _("%s is not an arrow definition file"), dict)

    return arrows


std_arrows = None
def StandardArrows():
    global std_arrows
    if std_arrows is None:
        filename = os.path.join(config.std_res_dir, config.preferences.arrows)
        try:
            std_arrows = read_arrows(filename)
        except:
            warn_tb(USER, _("Error trying to read arrows from %s\n"
                            "Using builtin defaults"), filename)
            std_arrows = []
    return std_arrows
