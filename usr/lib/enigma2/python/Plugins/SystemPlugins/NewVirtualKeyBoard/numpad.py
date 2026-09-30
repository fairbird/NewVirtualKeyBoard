#!/usr/bin/python
# -*- coding: utf-8 -*-

# Digits-only keypad, shown instead of the full keyboard when the caller only
# wants a number (see numPadMode()). Ported from the E2iPlayer numeric
# keypad, drawn with the keyboard's own key art. Same result as the keyboard:
# the entered text, or None on EXIT.

from enigma import gRGB, getPrevAsciiCode
from Screens.Screen import Screen
from Components.ActionMap import NumberActionMap
from Components.Input import Input
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap

from Plugins.SystemPlugins.NewVirtualKeyBoard import _
from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import BACKGROUND_COLORS, PixmapWidget, desktopFactor, iconPath, keyArtDir, scaleSkin, setting, trace_error


def numPadMode(session, inputType):
    # None = full keyboard, 'number' = digits, 'pin' = digits shown as *
    if not setting('numpad', True):
        return None
    pinType = getattr(Input, 'PIN', None)
    numberType = getattr(Input, 'NUMBER', None)
    if inputType is not None:
        # the caller said what it wants (Input.TEXT: the full keyboard)
        if inputType == pinType:
            return 'pin'
        if inputType == numberType:
            return 'number'
        return None
    # the images open the keyboard for number fields with only title/text
    # (TEXT key on a ConfigNumber in setup lists and wizards, OpenViX's
    # InputBox) - look at the screen that opens us instead
    try:
        dialog = session.current_dialog
    except Exception:
        return None
    try:
        from Components.config import ConfigNumber
        if 'config' in dialog:
            current = dialog['config'].getCurrent()
            if current and len(current) > 1 and isinstance(current[1], ConfigNumber):
                return 'number'
    except Exception:
        pass
    try:
        if 'input' in dialog:
            dialogType = getattr(dialog['input'], 'type', None)
            if dialogType is not None and dialogType == pinType:
                return 'pin'
            if dialogType is not None and dialogType == numberType:
                return 'number'
    except Exception:
        pass
    return None


class NVKNumPad(Screen):
    # FHD reference geometry, scaled to the desktop (HD 2/3, WQHD 4/3)
    KEY_W = 136
    KEY_H = 68
    COLS = 3
    MARGIN = 24
    MAX_DIGITS = 16

    COLOR_TEXT = 0xFFFFFF
    COLOR_TEXT_PRESET = 0x8A8F9C

    def __init__(self, session, title='', text='', mode='number', maxSize=False):
        self.session = session
        self.mask = mode == 'pin'
        # row 5 is a full-width OK bar
        self.keyRows = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['clear', '0', 'back'], ['ok']]
        self.maxDigits = maxSize if isinstance(maxSize, int) and not isinstance(maxSize, bool) and maxSize > 0 else self.MAX_DIGITS
        self.skin = self.prepareSkin()
        Screen.__init__(self, session)
        self.skinName = 'NVKNumPad'
        self.setTitle(title or _('New Virtual Keyboard'))

        self['actions'] = NumberActionMap(['WizardActions', 'DirectionActions', 'ColorActions', 'NumberActions', 'KeyboardInputActions', 'InputAsciiActions'], {
            'ok': self.keyOK,
            'back': self.keyBack,
            'up': self.keyUp,
            'down': self.keyDown,
            'left': self.keyLeft,
            'right': self.keyRight,
            'green': self.accept,
            'red': self.backspace,
            'deleteBackward': self.backspace,
            'gotAsciiCode': self.keyGotAscii,
            '1': self.keyNumberGlobal,
            '2': self.keyNumberGlobal,
            '3': self.keyNumberGlobal,
            '4': self.keyNumberGlobal,
            '5': self.keyNumberGlobal,
            '6': self.keyNumberGlobal,
            '7': self.keyNumberGlobal,
            '8': self.keyNumberGlobal,
            '9': self.keyNumberGlobal,
            '0': self.keyNumberGlobal,
        }, -2)

        self['header'] = Label(title or '')
        self['text'] = Label('')
        self['text_bg'] = PixmapWidget()
        self['hint'] = Label(_('OK / GREEN - accept, EXIT - cancel'))
        for rowIdx, row in enumerate(self.keyRows):
            for colIdx, key in enumerate(row):
                name = self.keyName(rowIdx, colIdx)
                self[name] = PixmapWidget()
                self[name + '_m'] = PixmapWidget()
                self[name + '_l'] = Label(self.keyLabel(key))
        self['back_icon'] = PixmapWidget()

        # the preset (current value) is shown greyed out and the first digit
        # replaces it, so a new value needs no backspaces first
        self.text = ''.join([c for c in str(text or '') if c.isdigit()])[:self.maxDigits]
        self.preset = bool(self.text)
        # start on the OK bar: OK right away keeps the preset, the digits
        # come from the remote's number keys anyway
        self.rowIdx = len(self.keyRows) - 1
        self.colIdx = 0
        self.onLayoutFinish.append(self.onStart)

    def prepareSkin(self):
        m, kw, kh = self.MARGIN, self.KEY_W, self.KEY_H
        gridW = self.COLS * kw
        width = gridW + 2 * m
        headerY, headerH = m, 56
        textY, textH = headerY + headerH + 16, 72
        gridY = textY + textH + 16
        # two lines: translations are longer than the English hint
        hintY, hintH = gridY + len(self.keyRows) * kh + 12, 60
        height = hintY + hintH + m
        bg = BACKGROUND_COLORS.get(setting('bgcolor', 'default'), BACKGROUND_COLORS['default'])
        parts = ['<screen name="NVKNumPad" position="center,center" size="%d,%d" title="NewVirtualKeyBoard" backgroundColor="%s" flags="wfNoBorder">' % (width, height, bg)]
        parts.append('<eLabel position="%d,%d" size="%d,%d" backgroundColor="#3f434f" transparent="0" />' % (m, headerY, gridW, headerH))
        parts.append('<widget name="header" position="%d,%d" size="%d,%d" zPosition="2" font="Regular;30" halign="center" valign="center" noWrap="1" transparent="1" foregroundColor="#ffffff" backgroundColor="#3f434f" />' % (m + 10, headerY, gridW - 20, headerH))
        parts.append('<widget name="text_bg" position="%d,%d" size="%d,%d" zPosition="1" scale="1" alphatest="blend" transparent="1" />' % (m, textY, gridW, textH))
        parts.append('<widget name="text" position="%d,%d" size="%d,%d" zPosition="2" font="Regular;40" halign="center" valign="center" noWrap="1" transparent="1" foregroundColor="#ffffff" backgroundColor="#263238" />' % (m + 10, textY, gridW - 20, textH))
        for rowIdx, row in enumerate(self.keyRows):
            keyW = gridW // len(row)
            for colIdx, key in enumerate(row):
                name = self.keyName(rowIdx, colIdx)
                x, y = m + colIdx * keyW, gridY + rowIdx * kh
                parts.append('<widget name="%s" position="%d,%d" size="%d,%d" zPosition="1" scale="1" alphatest="blend" transparent="1" />' % (name, x, y, keyW, kh))
                parts.append('<widget name="%s_m" position="%d,%d" size="%d,%d" zPosition="5" scale="1" alphatest="blend" transparent="1" />' % (name, x, y, keyW, kh))
                font = 36 if key.isdigit() else 27
                parts.append('<widget name="%s_l" position="%d,%d" size="%d,%d" zPosition="3" font="Regular;%d" halign="center" valign="center" noWrap="1" transparent="1" foregroundColor="#ffffff" backgroundColor="#263238" />' % (name, x, y, keyW, kh, font))
                if key == 'back':
                    parts.append('<widget name="back_icon" position="%d,%d" size="%d,%d" zPosition="3" scale="1" alphatest="blend" transparent="1" />' % (x + (keyW - kh) // 2, y, kh, kh))
        parts.append('<widget name="hint" position="%d,%d" size="%d,%d" zPosition="2" font="Regular;22" halign="center" valign="center" transparent="1" foregroundColor="#b6b6b6" backgroundColor="#000000" />' % (m, hintY, gridW, hintH))
        parts.append('</screen>')
        return scaleSkin('\n'.join(parts), desktopFactor())

    def keyName(self, rowIdx, colIdx):
        return 'key_%d_%d' % (rowIdx, colIdx)

    def keyLabel(self, key):
        if key == 'ok':
            return 'OK'
        if key == 'clear':
            return _('Clear')
        if key == 'back':
            return ''
        return key

    def onStart(self):
        self.onLayoutFinish.remove(self.onStart)
        try:
            artDir = keyArtDir()
            pix = dict((name, LoadPixmap(iconPath(artDir, name))) for name in ('vkey_text', 'vkey_double', 'vkey_double_sel', 'vkey_space', 'vkey_space_sel', 'vkey_backspace'))
            self['text_bg'].setPixmap(pix['vkey_text'])
            for rowIdx, row in enumerate(self.keyRows):
                for colIdx, key in enumerate(row):
                    name = self.keyName(rowIdx, colIdx)
                    if key == 'ok':
                        self[name].setPixmap(pix['vkey_space'])
                        self[name + '_m'].setPixmap(pix['vkey_space_sel'])
                    else:
                        self[name].setPixmap(pix['vkey_double'])
                        self[name + '_m'].setPixmap(pix['vkey_double_sel'])
                    self[name + '_m'].hide()
            self['back_icon'].setPixmap(pix['vkey_backspace'])
        except Exception:
            trace_error()
        self.moveMarker(-1, -1)
        self.updateText()

    def moveMarker(self, oldRow, oldCol):
        if oldRow >= 0:
            self[self.keyName(oldRow, oldCol) + '_m'].hide()
        self[self.keyName(self.rowIdx, self.colIdx) + '_m'].show()

    def updateText(self):
        try:
            self['text'].instance.setForegroundColor(gRGB(self.COLOR_TEXT_PRESET if self.preset else self.COLOR_TEXT))
        except Exception:
            pass
        self['text'].setText('*' * len(self.text) if self.mask else self.text)

    def takeOverPreset(self):
        if self.preset:
            self.preset = False
            self.text = ''

    def addDigit(self, digit):
        self.takeOverPreset()
        if len(self.text) < self.maxDigits:
            # leading zeros stay (PINs, "0815")
            self.text += str(digit)
        self.updateText()

    def backspace(self):
        self.preset = False
        self.text = self.text[:-1]
        self.updateText()

    def clear(self):
        self.preset = False
        self.text = ''
        self.updateText()

    def accept(self):
        self.close(self.text)

    def keyNumberGlobal(self, number):
        self.addDigit(number)

    def keyGotAscii(self):
        try:
            char = getPrevAsciiCode()
        except Exception:
            return
        if 48 <= char <= 57:
            self.addDigit(char - 48)
        elif char == 8:
            self.backspace()
        elif char in (10, 13):
            self.accept()

    def keyOK(self):
        key = self.keyRows[self.rowIdx][self.colIdx]
        if key.isdigit():
            self.addDigit(int(key))
        elif key == 'back':
            self.backspace()
        elif key == 'clear':
            self.clear()
        elif key == 'ok':
            self.accept()

    def keyBack(self):
        self.close(None)

    def moveTo(self, rowIdx, colIdx):
        oldRow, oldCol = self.rowIdx, self.colIdx
        self.rowIdx = rowIdx
        self.colIdx = min(colIdx, len(self.keyRows[rowIdx]) - 1)
        self.moveMarker(oldRow, oldCol)

    def keyUp(self):
        # leaving the one-key OK bar lands on the middle key (0 / 8)
        colIdx = self.COLS // 2 if len(self.keyRows[self.rowIdx]) == 1 else self.colIdx
        self.moveTo((self.rowIdx - 1) % len(self.keyRows), colIdx)

    def keyDown(self):
        colIdx = self.COLS // 2 if len(self.keyRows[self.rowIdx]) == 1 else self.colIdx
        self.moveTo((self.rowIdx + 1) % len(self.keyRows), colIdx)

    def keyLeft(self):
        self.moveTo(self.rowIdx, (self.colIdx - 1) % len(self.keyRows[self.rowIdx]))

    def keyRight(self):
        self.moveTo(self.rowIdx, (self.colIdx + 1) % len(self.keyRows[self.rowIdx]))
