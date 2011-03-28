# Sketch - A Python-based interactive drawing program
# Copyright (C) 1998, 1999, 2001 by Bernhard Herzog
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


import sys
import string
import traceback

from types import StringType, DictionaryType

from skencil import _, config

INTERNAL = 'INTERNAL'
USER = 'USER'


def write_error(message):
    sys.stderr.write(message)
    if message and message[-1] != '\n':
        sys.stderr.write('\n')

def flexible_format(format, args, kw):
    try:
        if args:
            text = format % args
        elif kw:
            text = format % kw
        else:
            text = format
    except TypeError:
        if args:
            text = string.join([format] + map(str, args))
        elif kw:
            text = string.join([format] + map(str, kw.items()))
        else:
            text = format

    return text


def warn(_level, _message, *args, **kw):
    _message = flexible_format(_message, args, kw)

    if _level == INTERNAL:
        if config.preferences.print_internal_warnings:
            write_error(_message)
    else:
#        app = main.application
        app = False
        if app and config.preferences.warn_method == 'dialog':
            pass
#            app.MessageBox(title=_("Warning"), message=_message,
#                           icon='warning')
        else:
            write_error(_message)
    return _message

def warn_tb(_level, _message='', *args, **kw):
    _message = flexible_format(_message, args, kw)

    if _level == INTERNAL:
        if config.preferences.print_internal_warnings:
            write_error(_message)
            traceback.print_exc()
    else:
#        app = main.application
        app = False
        if app:
            pass
#            tb = _("Print Traceback")
#            result = app.MessageBox(title=_("Warning"), message=_message,
#                                    icon='warning', buttons=(_("OK"), tb))
#            if result == tb:
#                from cStringIO import StringIO
#                file = StringIO()
#                traceback.print_exc(file=file)
#                _message = file.getvalue()
#                app.MessageBox(title=_("Traceback"), message=_message,
#                               icon='warning')
        else:
            write_error(_message)
            traceback.print_exc()
    return _message




def Dict(**kw):
    return kw

_levels = Dict(default=1,
               __del__=0,
               Graphics=1,
               properties=0,
               DND=1,
               context_menu=0,
               Load=Dict(default=1,
                           PSK=1,
                           AI=1,
                           echo_messages=1),
               PS=1,
               bezier=1,
               styles=1,
               tkext=0,
               handles=0,
               timing=0)

def pdebug(level, message, *args, **kw):
    if not config.preferences.print_debug_messages:
        return
    if level:
        if type(level) == StringType:
            level = (level,)
        enabled = _levels
        for item in level:
            try:
                enabled = enabled[item]
            except:
                break
        if type(enabled) == DictionaryType:
            enabled = enabled['default']
        if not enabled:
            return
    message = flexible_format(message, args, kw)
    write_error(message)



