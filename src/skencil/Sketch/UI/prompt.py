# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 2002 by Bernhard Herzog
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

import sys, os, string
import Sketch


def get_sketch_modules():
    # return the sketch specific modules that are already imported.
    # Sketch specific means that the module comes from a file below the
    # sketch directory or that it has a name starting with "Sketch.".
    sketch_dir = Sketch.config.sketch_dir
    if sketch_dir[-1] != '/':
        sketch_dir = sketch_dir + '/'
    sketch_dir = os.path.normpath(os.path.abspath(sketch_dir))
    length = len(sketch_dir)
    result = []
    for module in sys.modules.values():
        try:
            mod_file = module.__file__
        except AttributeError:
            continue
        mod_file = os.path.normpath(os.path.abspath(mod_file))
        if mod_file[:length] == sketch_dir or module.__name__[:7] == "Sketch.":
            result.append(module)
    return result



user_functions = {}
def add_sketch_objects(dict):
    from Sketch import main, connector
    # some useful variables and functions
    dict['app'] = main.application
    dict['canv'] = main.application.main_window.canvas
    dict['doc'] = main.application.main_window.document
    dict['connections'] = connector._the_connector.print_connections
    dict['get_sketch_modules'] = get_sketch_modules
    for key, val in user_functions.items():
        dict[key] = val




locals = {}

def PythonPrompt(prompt = '>>>', prompt2 = '...'):
    # try to import readline in Python 1.5
    have_readline = 0
    try:
        import readline
        have_readline = 1
        Sketch.Issue(None, Sketch.const.INIT_READLINE)
    except ImportError:
        pass
    globals = {}
    # put all of Sketch.main and Sketch into the globals
    exec 'from Sketch.main import *' in globals
    exec 'from Sketch import *' in globals
    # put all sketch specific modules into the globals
    for module in get_sketch_modules():
        globals[module.__name__] = module
    add_sketch_objects(globals)
    if have_readline:
        from Sketch.Lib import skcompleter
        skcompleter.install(globals, locals)
    while 1:
        try:
            cmd = raw_input(prompt)
            #cmd = string.strip(cmd)
            if cmd:
                if cmd[-1] == ':':
                    # a compound statement
                    lines = []
                    while string.strip(cmd):
                        lines.append(cmd)
                        cmd = raw_input(prompt2)
                    cmd = string.join(lines + [''], '\n')
                    kind = 'exec'
                else:
                    kind = 'single'

                c = compile(cmd, '<string>', kind)
                exec c in globals, locals
        except EOFError:
            print '----- returning to Sketch'
            return
        except:
            import traceback
            traceback.print_tb(sys.exc_traceback)
            print 'Exception %s: %s' % (sys.exc_type, sys.exc_value)
