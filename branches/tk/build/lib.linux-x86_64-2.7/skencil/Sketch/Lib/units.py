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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307	USA


# some factors to convert between different length units and the base
# unit of sketch, PostScript points

in_to_pt = 72.0
cm_to_pt = in_to_pt / 2.54
mm_to_pt = cm_to_pt / 10
m_to_pt	 = 100 * cm_to_pt

pt_to_in = 1.0 / 72.0
pt_to_cm = 2.54 * pt_to_in
pt_to_mm = pt_to_cm * 10
pt_to_m	 = pt_to_cm / 100


unit_dict = {'pt': 1.0, 'in': in_to_pt, 'cm': cm_to_pt, 'mm': mm_to_pt}
unit_names = ['pt', 'in', 'cm', 'mm']
