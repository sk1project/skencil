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
# Miscellaneous functions for PostScript creation
#

from string import join
import operator

def make_ps_quote_table():
    table = [''] * 256
    quote = (ord('('), ord(')'), ord('\\'))
    for i in range(128):
        if i in quote:
            table[i] = '\\' + chr(i)
        else:
            table[i] = chr(i)
    for i in range(128, 256):
        table[i] = '\\' + oct(i)[1:]
    return table

quote_table = make_ps_quote_table()

def quote_ps_string(text):
    return join(map(operator.getitem, [quote_table]*len(text), map(ord, text)),
                '')

def make_textline(text):
    # return text unchanged if no character needs to be quoted, as a
    # PS-string (with enclosing parens) otherwise.
    quoted = quote_ps_string(text)
    if quoted == text:
        return text
    return "(%s)" % quoted
