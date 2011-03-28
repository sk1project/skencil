# Sketch - A Python-based interactive drawing program
# Copyright (C) 1998 by Bernhard Herzog
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

# Sketch specific exceptions

class SketchError(Exception):
    pass

class SketchInternalError(SketchError):
    pass

class SketchLoadError(SketchError):
    pass


class SketchIOError(SketchError):

    def __init__(self, errno, strerror, filename = ''):
        self.errno = errno
        self.strerror = strerror
        self.filename = filename
