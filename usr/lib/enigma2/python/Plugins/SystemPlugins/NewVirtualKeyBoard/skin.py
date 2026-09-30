#!/usr/bin/python
# -*- coding: utf-8 -*-

# Skin of the keyboard screen, built from the key grid (layouts.KEY_GRID):
# a picture and a label widget per key plus the fixed parts (header, text
# field, history and suggestion lists, selection frames). FHD and HD have
# their own geometry; WQHD scales the FHD skin (tools.scaleSkin).

from xml.sax.saxutils import escape

from Plugins.SystemPlugins.NewVirtualKeyBoard.layouts import (KEY_GRID, KEY_TEXT, KEY_BACKSPACE, KEY_DELETE, KEY_LEFT, KEY_RIGHT,
    KEY_LANGUAGE, KEY_ENTER, KEY_ALTGR, KEY_SHIFT_L, KEY_SPACE, CHARACTER_KEYS, keySpan)
from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import pluginPath

# every key below the text field (1..63)
KEY_IDS = sorted(set(k for row in KEY_GRID[1:] for k in row))
# selection frames (moved onto the selected key) and the icons drawn on keys
MARKERS = ('vkey_text_sel', 'vkey_single_sel', 'vkey_double_sel', 'vkey_space_sel')
KEY_ICONS = (('vkey_backspace', KEY_BACKSPACE), ('vkey_delete', KEY_DELETE), ('vkey_left', KEY_LEFT), ('vkey_right', KEY_RIGHT))

# colour bar under the key a colour button presses: (widget, key, colour)
COLOUR_BARS = (('m_0', KEY_BACKSPACE, '#ed1c24'),   # RED = Backspace
               ('m_1', KEY_ENTER, '#22b14c'),       # GREEN = Enter
               ('m_2', KEY_ALTGR, '#fff200'),       # YELLOW = AltGr
               ('m_3', KEY_SHIFT_L, '#3f48cc'))     # BLUE = Shift

GEOMETRY = {
    'fhd': {
        'screen': ('center,476', 1920, 630),
        'keys': (450, 207, 68),                     # x, y of key 1, key size
        'textBox': (440, 114, 1020, 72),            # key 0 = the text field
        'text': (445, 120, 1010, 60),
        'headerBack': (450, 21, 1020, 72),
        'header': (471, 21, 965, 72, 36),           # x, y, w, h, font
        'history': (90, 21, 339, 72, 30, 114, 429),  # header x, y, w, h, font, list y, h
        'suggestions': (1491, 21, 339, 72, 30, 114, 429),
        'credits': (450, 547, 882, 38),
        'helpIcons': (1384, 1432, 547, 38),         # INFO x, MENU x, y, size
        'bar': (9, 56, 3),                          # inset, offset from the key top, height
        'flag': (11, 12, 60, 40),                   # offset in the language key, size
    },
    'hd': {
        'screen': ('center,317', 1280, 420),
        'keys': (300, 138, 45),
        'textBox': (320, 76, 638, 45),
        'text': (325, 80, 630, 40),
        'headerBack': (300, 14, 680, 48),
        'header': (314, 14, 650, 48, 20),
        'history': (60, 14, 226, 48, 20, 76, 286),
        'suggestions': (994, 14, 226, 48, 20, 76, 286),
        'credits': (300, 364, 588, 25),
        'helpIcons': (922, 954, 364, 25),
        'bar': (6, 38, 2),
        'flag': (7, 9, 40, 27),
    },
}


def keyArt(keyId):
    # picture of a key (skins/icons/<tier>/<name>.png)
    if keyId == KEY_TEXT:
        return 'vkey_text'
    if keyId == KEY_SPACE:
        return 'vkey_space'
    if keySpan(keyId)[2] == 2:
        return 'vkey_double'
    return 'vkey_single' if keyId in CHARACTER_KEYS else 'vkey_modifier'


def keyMarker(keyId):
    # selection frame of a key (same size as its picture)
    art = keyArt(keyId)
    return 'vkey_single_sel' if art == 'vkey_modifier' else art + '_sel'


def keyRect(tier, keyId):
    # (x, y, w, h) of a key
    g = GEOMETRY[tier]
    if keyId == KEY_TEXT:
        return g['textBox']
    x0, y0, size = g['keys']
    row, col, span = keySpan(keyId)
    return x0 + col * size, y0 + (row - 1) * size, span * size, size


def keyboardSkin(tier, fonts, credits, textAlign='right', background='#34000000', iconDir='nvk_hd'):
    # tier 'fhd' or 'hd'; fonts = (text field, word keys, character keys,
    # colour bars, credits line); iconDir = folder of key_info/key_menu
    g = GEOMETRY[tier]
    textFont, wordFont, charFont, barFont, creditsFont = fonts
    out = ['<screen name="NewVirtualKeyBoard" position="%s" size="%d,%d" title="NewVirtualKeyBoard" backgroundColor="%s" flags="wfNoBorder">' % (g['screen'] + (background,))]
    out.append('<eLabel position="%d,%d" size="%d,%d" backgroundColor="#3f434f" transparent="0" />' % g['headerBack'])
    out.append('<widget name="header" position="%d,%d" size="%d,%d" font="Regular;%s" foregroundColor="#ffffff" backgroundColor="#3f434f" transparent="1" noWrap="1" valign="center" halign="center" zPosition="2" />' % g['header'])
    out.append('<widget name="0" position="%d,%d" size="%d,%d" alphatest="blend" transparent="1" zPosition="1" />' % keyRect(tier, KEY_TEXT))
    out.append('<widget name="text" position="%d,%d" size="%d,%d" font="Regular;%s" noWrap="1" valign="center" halign="%s" transparent="1" zPosition="2" />' % (g['text'] + (textFont, textAlign)))
    for name in MARKERS:
        # same size as the picture: the frame of the text field, a single
        # key, a double key and the space bar
        keyId = {'vkey_text_sel': KEY_TEXT, 'vkey_single_sel': 2, 'vkey_double_sel': KEY_ENTER, 'vkey_space_sel': KEY_SPACE}[name]
        out.append('<widget name="%s" position="0,0" size="%d,%d" alphatest="blend" transparent="1" zPosition="5" />' % ((name,) + keyRect(tier, keyId)[2:]))
    for keyId in KEY_IDS:
        x, y, w, h = keyRect(tier, keyId)
        out.append('<widget name="%d" position="%d,%d" size="%d,%d" alphatest="blend" transparent="1" zPosition="1" />' % (keyId, x, y, w, h))
        if keyId == KEY_LANGUAGE:
            # the flag takes the left half, the language code the right one
            x, w = x + h, w - h
        font = charFont if keyId in CHARACTER_KEYS else wordFont
        out.append('<widget name="_%d" position="%d,%d" size="%d,%d" font="Regular;%s" foregroundColor="#ffffff" backgroundColor="#263238" valign="center" halign="center" noWrap="1" transparent="1" zPosition="3" />' % (keyId, x, y, w, h, font))
    for name, keyId in KEY_ICONS:
        out.append('<widget name="%s" position="%d,%d" size="%d,%d" alphatest="blend" transparent="1" zPosition="3" />' % ((name,) + keyRect(tier, keyId)))
    inset, offset, barH = g['bar']
    for name, keyId, colour in COLOUR_BARS:
        x, y, w, h = keyRect(tier, keyId)
        out.append('<widget name="%s" position="%d,%d" size="%d,%d" font="Regular;%s" foregroundColor="%s" backgroundColor="%s" noWrap="1" valign="center" halign="center" zPosition="2" />' % (name, x + inset, y + offset, w - 2 * inset, barH, barFont, colour, colour))
    x, y = keyRect(tier, KEY_LANGUAGE)[:2]
    fx, fy, fw, fh = g['flag']
    out.append('<widget name="flag" position="%d,%d" size="%d,%d" transparent="1" zPosition="2" />' % (x + fx, y + fy, fw, fh))
    infoX, menuX, iconY, iconSize = g['helpIcons']
    for iconX, icon in ((infoX, 'key_info'), (menuX, 'key_menu')):
        out.append('<ePixmap position="%d,%d" size="%d,%d" pixmap="%s" alphatest="blend" zPosition="3" />' % (iconX, iconY, iconSize, iconSize, pluginPath('skins', 'icons', iconDir, icon + '.png')))
    for name, zPos in (('history', 2), ('suggestion', 1)):
        hx, hy, hw, hh, hFont, listY, listH = g['history' if name == 'history' else 'suggestions']
        out.append('<widget name="%sheader" position="%d,%d" size="%d,%d" font="Regular;%s" foregroundColor="#ffffff" backgroundColor="#3f434f" noWrap="1" valign="center" halign="center" transparent="0" zPosition="2" />' % (name, hx, hy, hw, hh, hFont))
        out.append('<widget name="%sList" position="%d,%d" size="%d,%d" backgroundColor="#3f434f" enableWrapAround="1" scrollbarMode="showOnDemand" transparent="0" zPosition="%d" />' % (name, hx, listY, hw, listH, zPos))
    out.append('<eLabel position="%d,%d" size="%d,%d" font="Regular;%s" text="%s" foregroundColor="#ffffff" backgroundColor="#000000" valign="center" transparent="1" />' % (g['credits'] + (creditsFont, escape(credits, {'"': '&quot;'}))))
    out.append('</screen>')
    return '\n'.join(out)
