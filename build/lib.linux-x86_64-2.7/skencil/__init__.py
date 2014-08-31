#! /usr/bin/python
# -*- coding: utf-8 -*-

def skencil_run():
    import sys, os, warnings
        
    warnings.filterwarnings("ignore")
    
    _pkgdir = __path__[0]
    sys.path.insert(1, _pkgdir)
    
    import Sketch
    
    Sketch.config.sketch_command = sys.argv[0]
    
    Sketch.main.main()