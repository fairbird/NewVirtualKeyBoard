#!/usr/bin/python
# -*- coding: utf-8 -*-

# Code mfaraj57 and Fairbird

import os
from Components.config import *
from enigma import getDesktop
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

config.NewVirtualKeyBoard = ConfigSubsection()
config.NewVirtualKeyBoard.fontssize = ConfigInteger(default = 0, limits = (0, 30))

from sys import version_info
PY3 = version_info[0] == 3

try:
	FONTSSIZE = config.NewVirtualKeyBoard.fontssize.value
except:
	FONTSSIZE = 0

def DreamOS():
    if os.path.exists('/var/lib/dpkg/status'):
        return DreamOS

def getDesktopSize():
    s = getDesktop(0).size()
    return (s.width(), s.height())

def isFHD():
    desktopSize = getDesktopSize()
    return desktopSize[0] > 1280 and desktopSize[0] <= 1920

def isHD():
    desktopSize = getDesktopSize()
    return desktopSize[0] <= 1280

def getversioninfo():
    currversion = '1.0'
    version_file = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/version")
    if os.path.exists(version_file):
        try:
            fp = open(version_file, 'r').readlines()
            for line in fp:
                if 'version' in line:
                    currversion=line.split('=')[1].strip()
        except:
            pass
    return (currversion)

def logdata(label_name = '', data = None):
    try:
        data=str(data)
        fp = open('/tmp/VirtualKeyBoard.log', 'a')
        fp.write( str(label_name) + ': ' + data+"\n")
        fp.close()
    except:
        trace_error()    
        pass

def trace_error():
    import sys
    import traceback
    try:
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=open('/tmp/VirtualKeyBoard.log', 'a'))
    except:
        pass
