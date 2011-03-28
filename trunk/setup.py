#!/usr/bin/env python
#
# Setup script for Skencil
#
# Copyright (C) 2010 Igor E. Novikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA
#

# Usage: 
# --------------------------------------------------------------------------
#  to build package:   python setup.py build
#  to install package:   python setup.py install
# --------------------------------------------------------------------------
#  to create source distribution:   python setup.py sdist
# --------------------------------------------------------------------------
#  to create binary RPM distribution:  python setup.py bdist_rpm
# --------------------------------------------------------------------------
#  to create localization .mo files: python setup.py build_locales (Linux only)
# --------------------------------------------------------------------------
#
#  help on available distribution formats: python setup.py bdist --help-formats
#

import os, sys


COPY = False
DEBIAN = False
VERSION = '2.0alpha'

############################################################
#
# Routines for build procedures
#
############################################################

#Return directory list for provided path
def get_dirs(path='.'):
    list = []
    if path:
        if os.path.isdir(path):
            try:
                names = os.listdir(path)
            except os.error:
                return []
        names.sort()
        for name in names:
            if os.path.isdir(os.path.join(path, name)):
                list.append(name)
        return list
            
#Return full  directory names list for provided path    
def get_dirs_withpath(path='.'):
    list = []
    names = []
    if os.path.isdir(path):
        try:
            names = os.listdir(path)
        except os.error:
            return names
    names.sort()
    for name in names:
        if os.path.isdir(os.path.join(path, name)) and not name == '.svn':
            list.append(os.path.join(path, name))
    return list

#Return file list for provided path
def get_files(path='.', ext='*'):    
    list = []
    if path:
        if os.path.isdir(path):
            try:
                names = os.listdir(path)
            except os.error:
                return []
        names.sort()
        for name in names:
            if not os.path.isdir(os.path.join(path, name)):
                if ext == '*':
                    list.append(name)
                elif '.' + ext == name[-1 * (len(ext) + 1):]:
                    list.append(name)                
    return list

#Return full file names list for provided path
def get_files_withpath(path='.', ext='*'):
    import glob
    list = glob.glob(os.path.join(path, "*." + ext))
    list.sort()
    result = []
    for file in list:
        if os.path.isfile(file):
            result.append(file)
    return result

#Return recursive directories list for provided path
def get_dirs_tree(path='.'):
    tree = get_dirs_withpath(path)
    res = [] + tree
    for node in tree:
        subtree = get_dirs_tree(node)
        res += subtree
    return res    
    
#Return recursive files list for provided path
def get_files_tree(path='.', ext='*'):
    tree = []
    dirs = [path, ]    
    dirs += get_dirs_tree(path)
    for dir in dirs:
        list = get_files_withpath(dir, ext)
        list.sort()
        tree += list
    return tree
 
#Generates *.mo files Resources/Messages
def generate_locales():
    print 'LOCALES BUILD'
    files = get_files('po', 'po')
    if len(files):
        for file in files:
            lang = file.split('.')[0]    
            po_file = os.path.join('po', file)        
            mo_file = os.path.join('src', 'Resources', 'Messages', lang, 'LC_MESSAGES', 'skencil.mo')
            if not os.path.lexists(os.path.join('src', 'Resources', 'Messages', lang, 'LC_MESSAGES')):
                os.makedirs(os.path.join('src', 'share', 'Messages', lang, 'LC_MESSAGES'))
            print po_file, '==>', mo_file
            os.system('msgfmt -o ' + mo_file + ' ' + po_file)        

############################################################
#
# Main build procedure
#
############################################################

if __name__ == "__main__":
        
    if len(sys.argv) > 1:    
        
        if sys.argv[1] == 'build_locales':
            generate_locales()
            sys.exit(0)
            
        if sys.argv[1] == 'build_and_copy':
            COPY = True
            sys.argv[1] = 'build'
            
        if sys.argv[1] == 'bdist_deb':
            DEBIAN = True
            sys.argv[1] = 'build'

        if sys.argv[1] in ['bdist_deb', 'bdist_rpm', 'build_and_copy']:    
            generate_locales()
        
    dirs = get_dirs_tree('src/share/Messages')
    messages_dirs = []
    for item in dirs:
        messages_dirs.append(os.path.join(item[4:], '*.*'))
        
    
    from distutils.core import setup, Extension

    src_path = 'src/'
    
    filter_src = src_path + 'extensions/Filter/'
                
    filter_module = Extension('skencil.modules.streamfilter',
            define_macros=[('MAJOR_VERSION', '0'),
                        ('MINOR_VERSION', '6')],
            sources=[filter_src + 'streamfilter.c', filter_src + 'filterobj.c', filter_src + 'linefilter.c',
                    filter_src + 'subfilefilter.c', filter_src + 'base64filter.c', filter_src + 'nullfilter.c',
                    filter_src + 'stringfilter.c', filter_src + 'binfile.c', filter_src + 'hexfilter.c'])
    
    intl_src = src_path + 'extensions/Pax/'
                
    intl_module = Extension('skencil.modules.intl',
            define_macros=[('MAJOR_VERSION', '0'),
                        ('MINOR_VERSION', '6')],
            sources=[intl_src + 'intl.c'])
    
    type1mod_src = src_path + 'extensions/Modules/'                
    type1mod_module = Extension('skencil.modules._type1module',
            define_macros=[('MAJOR_VERSION', '0'),
                        ('MINOR_VERSION', '6')],
            sources=[type1mod_src + '_type1module.c'])
    
    skread_src = src_path + 'extensions/Modules/'                
    skread_module = Extension('skencil.modules.skreadmodule',
            define_macros=[('MAJOR_VERSION', '0'),
                        ('MINOR_VERSION', '9')],
            sources=[skread_src + 'skreadmodule.c'])
    
    pstokenize_src = src_path + 'extensions/Modules/'                
    pstokenize_module = Extension('skencil.modules.pstokenize',
            define_macros=[('MAJOR_VERSION', '0'),
                        ('MINOR_VERSION', '6')],
            include_dirs=[filter_src],
            sources=[pstokenize_src + 'pstokenize.c', pstokenize_src + 'pschartab.c'])
    
    
    tcl_include_dirs = []
    tcl_ver = ''
    
    if len(sys.argv) > 1 and sys.argv[1] in ['bdist_deb', 'bdist_rpm', 'build_and_copy', 'build', 'install']:  
        
        #Fix for Debian based distros
        if os.path.isdir('/usr/include/tcl8.5'):
            tcl_include_dirs = ['/usr/include/tcl8.5']
            tcl_ver = '8.5'
            
        if os.path.isdir('/usr/include/tcl8.6'):
            tcl_include_dirs = ['/usr/include/tcl8.6']
            tcl_ver = '8.6'
        
        #Fix for OpenSuse
        if not tcl_ver:
            if os.path.isfile('/usr/lib/libtcl8.5.so'):
                tcl_ver = '8.5'
            if os.path.isfile('/usr/lib64/libtcl8.5.so'):
                tcl_ver = '8.5'
            if os.path.isfile('/usr/lib/libtcl8.6.so'):
                tcl_ver = '8.6'
            if os.path.isfile('/usr/lib64/libtcl8.6.so'):
                tcl_ver = '8.6'
                
        if not tcl_ver:
            print 'System tcl/tk =>8.5 libraries have not found!'
            sys.exit(1)
    
    
    paxtkinter_src = src_path + 'extensions/Pax/'                
    paxtkinter_module = Extension('skencil.modules.paxtkinter',
            define_macros=[('MAJOR_VERSION', '1'),
                        ('MINOR_VERSION', '0')],
            sources=[paxtkinter_src + 'paxtkinter.c'],
            include_dirs=tcl_include_dirs,
            libraries=['tk' + tcl_ver, 'tcl' + tcl_ver])
    
    
    pax_src = src_path + 'extensions/Pax/'
    pax_module = Extension('skencil.modules.paxmodule',
            define_macros=[('MAJOR_VERSION', '0'),
                        ('MINOR_VERSION', '6')],
            sources=[pax_src + 'borderobject.c', pax_src + 'clipmask.c', pax_src + 'cmapobject.c',
                    pax_src + 'fontobject.c', pax_src + 'gcobject.c', #  pax_src+'gcmethods.c',
                    pax_src + 'imageobject.c', pax_src + 'intl.c', pax_src + 'paxmodule.c',
                    pax_src + 'paxutil.c', pax_src + 'pixmapobject.c', pax_src + 'regionobject.c',
                    pax_src + 'tkwinobject.c'],
            include_dirs=tcl_include_dirs,
            libraries=['X11', 'Xext', 'tk' + tcl_ver, 'tcl' + tcl_ver])
    
    skmod_src = src_path + 'extensions/Modules/'    
    skmod_module = Extension('skencil.modules._sketchmodule',
            define_macros=[('MAJOR_VERSION', '0'),
                        ('MINOR_VERSION', '6')],
            include_dirs=[src_path + 'extensions/Pax/'],
            sources=[skmod_src + 'curvedraw.c', skmod_src + 'curvefunc.c', skmod_src + 'curvelow.c',
                    skmod_src + 'curvemisc.c', skmod_src + 'curveobject.c', skmod_src + 'skaux.c',
                    skmod_src + 'skcolor.c', skmod_src + 'skdither.c', skmod_src + '_sketchmodule.c',
                    skmod_src + 'skfm.c', skmod_src + 'skimage.c', skmod_src + 'skpoint.c',
                    skmod_src + 'skrect.c', skmod_src + 'sktrafo.c'],
            libraries=['m', 'X11'])
    
    
    setup (name='skencil',
            version=VERSION,
            description='Interactive vector drawing program',
            author='Bernhard Herzog',
            author_email='bh@intevation.de',
            maintainer='Igor E.Novikov',
            maintainer_email='igor.e.novikov@gmail.com',
            license='LGPL v2.0',
            url='http://www.skencil.org',
            download_url='',
            long_description='''
Skencil is an interactive vector drawing program for GNU/Linux and
other UNIX compatible systems. Skencil is implemented almost completely
in Python, a very high-level, object oriented, interpreted language,
with the rest written in C for speed.
Copyright (C) 1996-2005 by Bernhard Herzog
Copyright (C) 2010-2011 by Igor E. Novikov. sK1 Team (http://sk1project.org) 
            ''',
        classifiers=[
            'Development Status :: 5 - Stable',
            'Environment :: Desktop',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: LGPL v2',
            'License :: OSI Approved :: GPL v2',
            'Operating System :: POSIX',
            'Operating System :: MacOS :: MacOS X',
            'Programming Language :: Python',
            'Programming Language :: C',
            "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
            ],

            packages=['skencil',
                'skencil.base',
                'skencil.model',
                'skencil.view',
                'skencil.widgets',
            ],
            
            package_dir={'skencil': 'src/skencil',
            },

            scripts=['skencil'],

            ext_modules=[filter_module, intl_module, skread_module, type1mod_module,
                         pstokenize_module, paxtkinter_module, pax_module, skmod_module])
    
#################################################
# .py source compiling
#################################################
if sys.argv[1] == 'build':
    import compileall
    compileall.compile_dir('build/')
    
        
##############################################
# This section for developing purpose only
# Command 'python setup.py build&copy' allows
# automating build and native extension copying
# into package directory
##############################################    
            
if COPY:
    import string, platform, shutil
    version = (string.split(sys.version)[0])[0:3]
    
    shutil.copy('build/lib.linux-' + platform.machine() + '-' + version + '/skencil/modules/paxmodule.so', 'src/skencil/modules/')
    print '\n paxmodule.so has been copied to src/ directory'
    
    shutil.copy('build/lib.linux-' + platform.machine() + '-' + version + '/skencil/modules/paxtkinter.so', 'src/skencil/modules/')
    print '\n paxtkinter.so has been copied to src/ directory'
    
    shutil.copy('build/lib.linux-' + platform.machine() + '-' + version + '/skencil/modules/intl.so', 'src/skencil/modules/')
    print '\n intl.so has been copied to src/ directory'
    
    shutil.copy('build/lib.linux-' + platform.machine() + '-' + version + '/skencil/modules/pstokenize.so', 'src/skencil/modules/')
    print '\n pstokenize.so has been copied to src/ directory'
    
    shutil.copy('build/lib.linux-' + platform.machine() + '-' + version + '/skencil/modules/_sketchmodule.so', 'src/skencil/modules/')
    print '\n _sketchmodule.so has been copied to src/ directory'
    
    shutil.copy('build/lib.linux-' + platform.machine() + '-' + version + '/skencil/modules/skreadmodule.so', 'src/skencil/modules/')
    print '\n skreadmodule.so has been copied to src/ directory'
    
    shutil.copy('build/lib.linux-' + platform.machine() + '-' + version + '/skencil/modules/streamfilter.so', 'src/skencil/modules/')
    print '\n streamfilter.so has been copied to src/ directory'
    
    shutil.copy('build/lib.linux-' + platform.machine() + '-' + version + '/skencil/modules/_type1module.so', 'src/skencil/modules/')
    print '\n _type1module.so has been copied to src/ directory'
    
    os.system('rm -rf build')
    
    
#################################################
# Implementation of bdist_deb command
#################################################

if DEBIAN:
    print '\nDEBIAN PACKAGE BUILD'
    print '===================='
    import string, platform
    version = (string.split(sys.version)[0])[0:3]
    
    arch, bin = platform.architecture()
    if arch == '64bit':
        arch = 'amd64'
    else:
        arch = 'i386'
        
    target = 'build/deb-root/usr/lib/python' + version + '/dist-packages'
    
    if os.path.lexists(os.path.join('build', 'deb-root')):
        os.system('rm -rf build/deb-root')
    os.makedirs(os.path.join('build', 'deb-root', 'DEBIAN'))
    
    os.system("cat DEBIAN/control |sed 's/<PLATFORM>/" + arch + "/g'|sed 's/<VERSION>/" + VERSION + "/g'> build/deb-root/DEBIAN/control")    

    os.makedirs(target)
    os.makedirs('build/deb-root/usr/bin')
    os.makedirs('build/deb-root/usr/share/applications')
    os.makedirs('build/deb-root/usr/share/pixmaps')    
    
    os.system('cp -R build/lib.linux-' + platform.machine() + '-' + version + '/skencil ' + target)
    os.system('cp src/skencil.desktop build/deb-root/usr/share/applications')
    os.system('cp src/skencil.png build/deb-root/usr/share/pixmaps')    
    os.system('cp src/skencil.xpm build/deb-root/usr/share/pixmaps')
    os.system('cp src/skencil build/deb-root/usr/bin')
    os.system('chmod +x build/deb-root/usr/bin/skencil')
        
    if os.path.lexists('dist'):    
        os.system('rm -rf dist/*.deb')
    else:
        os.makedirs('dist')
    
    os.system('dpkg --build build/deb-root/ dist/python-skencil-' + VERSION + '_' + arch + '.deb')    
