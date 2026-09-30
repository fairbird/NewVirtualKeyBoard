#!/usr/bin/python
# -*- coding: utf-8 -*-

# Code mfaraj57 and Fairbird

# Helpers shared by the plugin's modules: desktop tiers and skin scaling,
# settings, paths, URL fetching, logging and small GUI helpers.

import os
import re
import sys

from enigma import getDesktop
from Components.Pixmap import Pixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

PY3 = sys.version_info[0] == 3

PLUGIN_DIR = 'SystemPlugins/NewVirtualKeyBoard'
LOG_FILE = '/tmp/VirtualKeyBoard.log'
INSTALLER_URL = 'https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/installer.sh'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0'

# keyboard / keypad background colours (setting "bgcolor")
BACKGROUND_COLORS = {'default': '#34000000', 'transparent': '#ff000000', 'black': '#00000000', 'semi': '#80000000', 'light': '#cc000000'}


def pluginPath(*parts):
    return resolveFilename(SCOPE_PLUGINS, '/'.join((PLUGIN_DIR,) + parts))


def setting(name, default):
    # config.NewVirtualKeyBoard.<name>.value; the settings are defined in
    # setup.py - the default covers a keyboard opened before it was imported
    try:
        from Components.config import config
        return getattr(config.NewVirtualKeyBoard, name).value
    except Exception:
        return default


def DreamOS():
    return os.path.exists('/var/lib/dpkg/status')


def fontOffset():
    # setting "fontssize" (-10..30), read on every open
    try:
        return int(setting('fontssize', 0))
    except (TypeError, ValueError):
        return 0


def offsetFont(base):
    return max(8, base + fontOffset())


# ---- desktop tiers -------------------------------------------------------
# HD = 1280, FHD = 1920, WQHD = 2560 px wide. The skins are written for FHD
# (and HD); WQHD uses the FHD layout scaled by 4/3. Asset folders per tier:
#   key art    nvk (HD)    nvk_hd (FHD)    nvk_wqhd (WQHD)
#   flags      flags (HD)  flagshd (FHD)   flagswqhd (WQHD)
#   menu icons menus/hd    menus/fhd       menus/wqhd

def getDesktopSize():
    size = getDesktop(0).size()
    return (size.width(), size.height())


def isFHD():
    # FHD and WQHD (WQHD uses the FHD layouts, scaled)
    return getDesktopSize()[0] > 1280


def isWQHD():
    return getDesktopSize()[0] > 1920


def byTier(fhd, wqhd, hd):
    # picks the value for the current desktop (folder names, sizes, ...)
    if isWQHD():
        return wqhd
    if isFHD():
        return fhd
    return hd


def desktopFactor():
    # FHD layout -> current desktop, for skins without an own HD layout
    return getDesktopSize()[0] / 1920.0


def skinScale():
    # FHD layout -> current desktop for skins that have an HD layout (1.0 on
    # HD and FHD, 4/3 on WQHD)
    return desktopFactor() if isWQHD() else 1.0


def sc(value, factor=None):
    # scales an FHD pixel value (default factor: skinScale())
    return int(round(value * (skinScale() if factor is None else factor)))


def scaleSkin(skin, factor=None):
    # scales the numbers of an FHD skin string (position, size, fonts,
    # itemHeight); "center" and other non-numbers stay
    if factor is None:
        factor = skinScale()
    if factor == 1.0:
        return skin

    def _num(value):
        value = value.strip()
        if value.isdigit():
            return str(int(round(int(value) * factor)))
        return value

    def _pair(m):
        return '%s="%s"' % (m.group(1), ','.join([_num(v) for v in m.group(2).split(',')]))

    def _font(m):
        return '%s="%s;%s"' % (m.group(1), m.group(2), _num(m.group(3)))

    skin = re.sub(r'\b(position|size)="([^"]*)"', _pair, skin)
    skin = re.sub(r'\b(font|secondfont)="([^";]*);(\d+)"', _font, skin)
    skin = re.sub(r'\b(itemHeight)="([^"]*)"', _pair, skin)
    return skin


def keyArtDir():
    return byTier('nvk_hd', 'nvk_wqhd', 'nvk')


def menuIconsDir():
    return byTier('menus/fhd', 'menus/wqhd', 'menus/hd')


def iconPath(folder, name):
    return pluginPath('skins', 'icons', folder, name + '.png')


# ---- network ---------------------------------------------------------------

def urlread(url, timeout):
    # (data, Content-Type) of an https URL. Certificates are not checked:
    # many boxes have no CA bundle, and only public, non-secret data is read.
    if PY3:
        from urllib.request import urlopen, Request
    else:
        from urllib2 import urlopen, Request
    request = Request(url, headers={'User-Agent': USER_AGENT})
    try:
        import ssl
        response = urlopen(request, timeout=timeout, context=ssl._create_unverified_context())
    except (ImportError, AttributeError, TypeError):
        response = urlopen(request, timeout=timeout)
    try:
        contentType = response.info().get('Content-Type', '') or ''
    except Exception:
        contentType = ''
    return response.read(), contentType


# ---- misc ------------------------------------------------------------------

def getversioninfo():
    version = '1.0'
    try:
        with open(pluginPath('version')) as f:
            for line in f:
                if line.startswith('version='):
                    version = line.split('=', 1)[1].strip()
    except Exception:
        pass
    return version


def versionTuple(version):
    # "13.10" > "13.9" (float() had it the other way round)
    try:
        return tuple(int(part) for part in str(version).strip().split('.'))
    except ValueError:
        return None


def logdata(label='', data=None):
    try:
        with open(LOG_FILE, 'a') as f:
            f.write('%s: %s\n' % (label, data))
    except Exception:
        trace_error()


def trace_error():
    import traceback
    try:
        traceback.print_exc(file=sys.stdout)
        with open(LOG_FILE, 'a') as f:
            traceback.print_exc(file=f)
    except Exception:
        pass


class PixmapWidget(Pixmap):
    # a Pixmap whose picture is set from code (LoadPixmap result)
    def setPixmap(self, ptr):
        self.instance.setPixmap(ptr)


class eConnectCallbackObj:
    # keeps an enigma2 signal connection alive (connect() on newer images,
    # the list of callbacks on older ones and DreamOS)
    def __init__(self, obj=None, connectHandler=None):
        self.connectHandler = connectHandler
        self.obj = obj

    def __del__(self):
        try:
            if 'connect' not in dir(self.obj):
                if 'get' in dir(self.obj):
                    self.obj.get().remove(self.connectHandler)
                else:
                    self.obj.remove(self.connectHandler)
            else:
                del self.connectHandler
        except Exception:
            pass
        self.connectHandler = None
        self.obj = None


def eConnectCallback(obj, callbackFun):
    try:
        if 'connect' in dir(obj):
            return eConnectCallbackObj(obj, obj.connect(callbackFun))
        if 'get' in dir(obj):
            obj.get().append(callbackFun)
        else:
            obj.append(callbackFun)
        return eConnectCallbackObj(obj, callbackFun)
    except Exception:
        pass
    return eConnectCallbackObj()
