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
# Read a Sketch resource file (dashes, arrows...)
#

from skexceptions import SketchError
from warn import warn_tb, USER

def read_resource_file(filename, magic, errmsg, functions):
    file = open(filename, 'r')
    try:
        line = file.readline()
        if line[:len(magic)] != magic:
            raise SketchError(errmsg % filename)

        from skread import parse_sk_line

        linenr = 1
        while 1:
            line = file.readline()
            if not line:
                break
            linenr = linenr + 1
            try:
                parse_sk_line(line, functions)
            except:
                warn_tb(USER, '%s:%d', filename, linenr)
    finally:
        file.close()
