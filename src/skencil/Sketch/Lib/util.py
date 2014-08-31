# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2002, 2003 by Bernhard Herzog
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
#	Some useful functions used in various places...
#


import os, string, re, stat

# Return the value of the environment variable S if present, None
# otherwise. In Python 1.5 one might use os.environ.get(S) instead...
def getenv(s):
    if os.environ.has_key(s):
        return os.environ[s]
    return None


# Return the pwd entry for the current user in the format of
# pwd.getpwuid.
def get_pwd():
    import pwd
    user = getenv("USER") or getenv("LOGNAME")
    if not user:
        return pwd.getpwuid(os.getuid())
    else:
        return pwd.getpwnam(user)

# Return the user's home directory. If it can't be determined from the
# environment or from the password database, return the current
# directory.
def gethome():
    try:
        home = getenv("HOME")
        if not home:
            home = get_pwd()[5]
        return home
    except (KeyError, ImportError):
        return os.curdir

# Return the real user name (the gecos field of passwd)
def get_real_username():
    try:
        return get_pwd()[4]
    except:
        return None

# Return the hostname
def gethostname():
    name = getenv('HOSTNAME')
    if not name:
        try:
            import socket
            name = socket.gethostname()
        except:
            pass
    return name


# sh_quote taken almost verbatim from the python standard library with
# the only difference that it doesn't prepend a space
def sh_quote(x):
    """Return a unix shell quoted version of the string x.

    The result is of a form that can be inserted into an argument to
    os.system so that it looks like a single word to the shell.
    """
    # Two strategies: enclose in single quotes if it contains none;
    # otherwise, enclose in double quotes and prefix quotable characters
    # with backslash.
    if '\'' not in x:
        return '\'' + x + '\''
    s = '"'
    for c in x:
        if c in '\\$"`':
            s = s + '\\'
        s = s + c
    s = s + '"'
    return s


#
#	Filename manipulation
#

# return the longest common prefix of path1 and path2 that is a
# directory.
def commonbasedir(path1, path2):
    if path1[-1] != os.sep:
        path1 = path1 + os.sep
    return os.path.split(os.path.commonprefix([path1, path2]))[0]



# return the absolute path PATH2 as a path relative to the directory
# PATH1. PATH1 must be an absoulte filename. If commonbasedir(PATH1,
# PATH2) is '/', return PATH2. Doesn't take symbolic links into
# account...
def relpath(path1, path2):
    if not os.path.isabs(path2):
        return path2
    basedir = commonbasedir(path1, path2)
    if basedir == os.sep:
        return path2
    path2 = path2[len(basedir) + 1 : ]
    curbase = path1
    while curbase != basedir:
        curbase = os.path.split(curbase)[0]
        path2 = os.pardir + os.sep + path2
    return path2


# find a file FILE in one of the directories listed in PATHS. If a file
# is found, return its full name, None otherwise.
def find_in_path(paths, file):
    for path in paths:
        fullname = os.path.join(path, file)
        if os.path.isfile(fullname):
            return fullname

# find one of the files listed in FILES in one of the directories in
# PATHS. Return the name of the first one found, None if no file is
# found.
def find_files_in_path(paths, files):
    for path in paths:
        for file in files:
            fullname = os.path.join(path, file)
            if os.path.isfile(fullname):
                return fullname


# Create the directory dir and its parent dirs when necessary
def create_directory(dir):
    if os.path.isdir(dir):
        return

    parent, base = os.path.split(dir)
    create_directory(parent)
    os.mkdir(dir, 0777)

# Make a backup of FILENAME if it exists by renaming it to its
# backupname (a ~ appended)

class BackupError(Exception):
    def __init__(self, errno, strerror, filename = ''):
        self.errno = errno
        self.strerror = strerror
        self.filename = filename


def make_backup(filename):
    if os.path.isfile(filename):
        backupname = filename + '~'
        try:
            os.rename(filename, backupname)
        except os.error, value:
            raise BackupError(value[0], value[1], backupname)

#
#
#

# Return the current local date and time as a string. The optional
# parameter format is used as the format parameter of time.strftime and
# defaults to '%c'.
# Currently this is used for the CreationTime comment in a PostScript
# file.
def current_date(format = '%c'):
    import time
    return time.strftime(format, time.localtime(time.time()))


#
#
#

#An empty class...
class Empty:
    def __init__(self, **kw):
        for key, value in kw.items():
            setattr(self, key, value)

#
#	List Manipulation
#

from types import ListType
def flatten(list):
    result = []
    for item in list:
        if type(item) == ListType:
            result = result + flatten(item)
        else:
            result.append(item)
    return result


#
#       String Manipulation
#

rx_format = re.compile(r'%\((?P<item>[a-zA-Z_0-9]+)\)'
                       r'\[(?P<converter>[a-zA-Z_]+)\]')

def format(template, converters, dict):
    result = []
    pos = 0
    while pos < len(template):
        match = rx_format.search(template, pos)
        if match:
            result.append(template[pos:match.start()] % dict)
            converter = converters[match.group('converter')]
            item = dict[match.group('item')]
            result.append(converter(item))
            pos = match.end()
        else:
            result.append(template[pos:] % dict)
            pos = len(template)

    return string.join(result, '')

# convert a bitmap to a string containing an xbm file. The linedlg uses
# this for instance to convert bitmap objects to Tk bitmap images.
def xbm_string(bitmap):
    import string
    width, height = bitmap.GetGeometry()[3:5]
    lines = ['#define sketch_width %d' % width,
             '#define sketch_height %d' % height,
             'static unsigned char sketch_bits[] = {']
    lines = lines + bitmap.GetXbmStrings() + ['}', '']
    return string.join(lines, '\n')
