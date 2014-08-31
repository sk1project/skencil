# Sketch - A Python-based interactive drawing program
# -*- encoding: iso-latin-1 -*-
# Copyright (C) 1997, 1998, 1999, 2000, 2001, 2002 by Bernhard Herzog
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
#       Converters
#

import math
from Sketch import config
from Sketch.Lib.units import unit_dict, unit_names
from Sketch.Lib.util import format

length_formats = {'mm': '%.1fmm',
                  'cm': '%.2fcm',
                  'pt': '%.1fpt',
                  'in': '%.3f"'}

def conv_length(length):
    unit = config.preferences.default_unit
    factor = unit_dict[unit]
    return length_formats.get(unit, "%f") % (length / factor)

pos_format = '(%(x)[length], %(y)[length])'
def conv_position(position):
    x, y = position
    return format(pos_format, converters, locals())

size_format = '(%(width)[length] x %(height)[length])'
def conv_size(size):
    width, height = size
    return format(size_format, converters, locals())

factor_format = '%.1f%%'
def conv_factor(factor):
    return factor_format % (100 * factor)

angle_format = '%.1f°'
def conv_angle(angle):
    angle = angle * 180 / math.pi
    while angle > 180:
        angle = angle - 360
    return angle_format % angle

converters = {'length': conv_length,
              'position': conv_position,
              'size': conv_size,
              'factor': conv_factor,
              'angle': conv_angle,
              }

