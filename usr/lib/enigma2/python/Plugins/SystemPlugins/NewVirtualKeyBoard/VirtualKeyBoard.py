#!/usr/bin/python
# -*- coding: utf-8 -*-

# Original concept and code - samsamsam /e2iplayer
# Code modifications - mfaraj57 and RAED (Fairbird)
# Support Python 3 by RAED (Fairbird)
# project continued by madmax88 and linuxsat-support forum
# code streamlined for kiddac's plugins - kiddac

# The keyboard screen, the layout list and the help screen. This file is also
# loaded as Screens/VirtualKeyBoard.py (symlink), so it imports absolutely and
# keeps the names other code imports from there: VirtualKeyBoard,
# VirtualKeyboard, NewVirtualKeyBoard, LanguageListScreen, KbLayouts, hfile.

import os

from enigma import ePoint, gRGB, eListboxPythonMultiContent, eListbox, gFont, loadPNG, RT_HALIGN_LEFT, RT_VALIGN_CENTER, RT_WRAP, getPrevAsciiCode
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap, ActionMap
from Components.GUIComponent import GUIComponent
from Components.Language import language
from Components.config import config, configfile
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Components.Label import Label
from Components.Input import Input
from Tools.LoadPixmap import LoadPixmap

from Plugins.SystemPlugins.NewVirtualKeyBoard import _
from Plugins.SystemPlugins.NewVirtualKeyBoard.layouts import (KbLayouts, defaultKBLAYOUT, KEY_TEXT, KEY_ESC, KEY_BACKSPACE, KEY_CLEAR,
    KEY_DELETE, KEY_CAPS, KEY_ENTER, KEY_SHIFT_L, KEY_SHIFT_R, KEY_LANGUAGE, KEY_CTRL, KEY_ALT, KEY_SPACE, KEY_ALTGR, KEY_LEFT,
    KEY_RIGHT, KEY_GRID, KEY_ROWS, KEY_COLUMNS, LEFT_KEYS, RIGHT_KEYS, CHARACTER_KEYS, SK_NONE, SK_SHIFT, SK_CTRL, SK_ALT,
    SK_CAPSLOCK, layoutFile, installedLayoutIds, readLayoutFile, downloadLayout, layoutItem, systemLayoutId, flagFileForLocale,
    flagFileForLayout)
from Plugins.SystemPlugins.NewVirtualKeyBoard.skin import KEY_IDS, MARKERS, KEY_ICONS, keyArt, keyMarker, keyboardSkin
from Plugins.SystemPlugins.NewVirtualKeyBoard.suggestions import HISTORY_FILE, SearchHistory, SuggestionsFetcher
from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import (PY3, BACKGROUND_COLORS, PixmapWidget, byTier, desktopFactor,
    eConnectCallback, fontOffset, getversioninfo, iconPath, isFHD, keyArtDir, menuIconsDir, offsetFont, scaleSkin, sc, setting,
    trace_error)

VER = getversioninfo()

# saved search history (other code imports this name)
hfile = HISTORY_FILE

# which part of the keyboard screen has the focus
FOCUS_KEYBOARD = 0
FOCUS_HISTORY = 1
FOCUS_SUGGESTIONS = 2

# key label colours
COLOR_TEXT = gRGB(0xffffff)
COLOR_ACTIVE = gRGB(0x39b54a)       # modifier key switched on
COLOR_LIGATURE = gRGB(0xed1c24)     # key types more than one character
COLOR_DEAD = gRGB(0x0275a0)         # dead key (accent for the next key)
COLOR_UNAVAILABLE = gRGB(0x979697)  # no character with the pending dead key

# modifier key -> (shift state bit, keys shown as switched on)
MODIFIERS = {
    KEY_CAPS: (SK_CAPSLOCK, [KEY_CAPS]),
    KEY_SHIFT_L: (SK_SHIFT, [KEY_SHIFT_L, KEY_SHIFT_R]),
    KEY_SHIFT_R: (SK_SHIFT, [KEY_SHIFT_L, KEY_SHIFT_R]),
    KEY_ALT: (SK_ALT, [KEY_ALT, KEY_ALTGR]),
    KEY_ALTGR: (SK_ALT, [KEY_ALT, KEY_ALTGR]),
    KEY_CTRL: (SK_CTRL, [KEY_CTRL]),
}


def toNative(text):
    # enigma2 widgets take UTF-8 byte strings on Python 2
    if not PY3 and not isinstance(text, str):
        return text.encode('utf-8')
    return text


def systemLocale():
    try:
        locale = language.getActiveLanguage()
    except Exception:
        locale = None
    return locale if isinstance(locale, str) else 'en_EN'


def activeLayoutId():
    return setting('keys_layout', '')


def saveActiveLayoutId(layoutId):
    try:
        keysLayout = config.NewVirtualKeyBoard.keys_layout
    except AttributeError:
        return
    if layoutId and keysLayout.value != layoutId:
        keysLayout.value = layoutId
        keysLayout.save()
        configfile.save()


class ListBase(GUIComponent, object):
    # eListbox with a MultiContent build function (buildEntry of the subclass)
    GUI_WIDGET = eListbox

    def __init__(self, fontSize, itemHeight):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildEntry)
        self.l.setFont(0, gFont('Regular', fontSize))
        self.l.setItemHeight(itemHeight)
        self.onSelectionChanged = []

    def buildEntry(self, item):
        return [None]

    def selectionChanged(self):
        for callback in self.onSelectionChanged:
            callback()

    def getCurrent(self):
        cur = self.l.getCurrentSelection()
        return cur and cur[0]

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        self.selectionChanged_conn = eConnectCallback(instance.selectionChanged, self.selectionChanged)

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        self.selectionChanged_conn = None

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def setList(self, items):
        self.l.setList(items)

    def setSelectionState(self, enabled):
        self.instance.setSelectionEnable(enabled)

    def moveSelection(self, step):
        instance = getattr(self, 'instance', None)
        if instance is not None:
            instance.moveSelection(instance.moveUp if step < 0 else instance.moveDown)

    currentIndex = property(getCurrentIndex, moveToIndex)
    currentSelection = property(getCurrent)


class TextList(ListBase):
    # search history and suggestions: one text per row

    def __init__(self):
        if isFHD():
            ListBase.__init__(self, sc(offsetFont(30)), sc(max(24, 39 + fontOffset())))
            self.margin = sc(21)
        else:
            ListBase.__init__(self, offsetFont(20), max(16, 26 + fontOffset()))
            self.margin = 14

    def buildEntry(self, text):
        size = self.l.getItemSize()
        return [None, (eListboxPythonMultiContent.TYPE_TEXT, self.margin, 0, size.width() - 2 * self.margin, size.height(), 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, text)]


class LayoutList(ListBase):
    # the layout list: installed dot (green/grey), flag, name

    def __init__(self):
        if isFHD():
            ListBase.__init__(self, sc(32), sc(54))
        else:
            ListBase.__init__(self, 24, 46)
        self.pixmaps = {}

    def pixmap(self, path):
        if path not in self.pixmaps:
            self.pixmaps[path] = loadPNG(path)
        return self.pixmaps[path]

    def buildEntry(self, layout):
        name, locale, layoutId = layout
        size = self.l.getItemSize()
        width, height = size.width(), size.height()
        dot = byTier(18, 24, 18)
        png = iconPath(menuIconsDir(), 'green18' if os.path.exists(layoutFile(layoutId)) else 'grey18')
        res = [None, (eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, sc(3), (height - dot) // 2, dot, dot, self.pixmap(png))]
        textX = sc(40)
        if setting('showflags', True):
            # the flag's own size per tier (HD 40x27, FHD 60x40, WQHD 80x53)
            flagW, flagH = byTier((60, 40), (80, 53), (40, 27))
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, sc(28), (height - flagH) // 2, flagW, flagH, self.pixmap(flagFileForLocale(locale))))
            textX = sc(28) + flagW + sc(14)
        res.append((eListboxPythonMultiContent.TYPE_TEXT, textX, 0, width - textX - sc(4), height, 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, toNative(name)))
        return res


class LanguageListScreen(Screen):
    # all layouts; OK downloads a layout (and makes it the active one) or
    # removes an installed one. The keyboard loads the active layout when the
    # list closes. The arguments are the old interface: listValue = rows
    # ({'val': (name, locale, id)},), selIdx = selected row; the callback is
    # not needed any more.

    def __init__(self, session, listValue=None, selIdx=None, loadVKLayout_callback=None):
        if isFHD():
            self.skin = '''
                <screen name="LanguageListScreen" position="center,center" size="900,826" backgroundColor="#16000000" transparent="0" title="Select Language" flags="wfNoBorder">
                <widget source="Title" render="Label" position="0,0" size="900,60" font="Regular;34" halign="center" valign="center" foregroundColor="#ffffff" backgroundColor="#3f434f" transparent="0" />
                <widget name="languageList" position="0,66" size="900,702" backgroundColor="#3f4450" transparent="0" scrollbarMode="showOnDemand" />
                <widget name="info" zPosition="2" position="0,776" size="900,40" transparent="0" noWrap="1" font="Regular;30" valign="center" halign="center" foregroundColor="#ffffff" backgroundColor="#0f64b2" />
                </screen>'''
        else:
            self.skin = '''
                <screen name="LanguageListScreen" position="center,center" size="600,546" backgroundColor="#16000000" transparent="0" title="Select Language" flags="wfNoBorder">
                <widget source="Title" render="Label" position="0,0" size="600,40" font="Regular;24" halign="center" valign="center" foregroundColor="#ffffff" backgroundColor="#3f434f" transparent="0" />
                <widget name="languageList" position="0,44" size="600,460" backgroundColor="#3f4450" transparent="0" scrollbarMode="showOnDemand" />
                <widget name="info" zPosition="2" position="0,512" size="600,26" transparent="0" noWrap="1" font="Regular;20" valign="center" halign="center" foregroundColor="#ffffff" backgroundColor="#0f64b2" />
                </screen>'''
        self.skin = scaleSkin(self.skin)
        Screen.__init__(self, session)
        self.skinName = 'LanguageListScreen'
        self.layouts = [row[0]['val'] for row in listValue] if listValue else list(KbLayouts)
        self.selIdx = selIdx
        self['languageList'] = LayoutList()
        self['languageList'].onSelectionChanged.append(self.updateInfo)
        self['info'] = Label(' ')
        self['actions'] = ActionMap(['WizardActions'], {
            'back': self.close,
            'ok': self.keyOK,
        }, -1)
        self.onLayoutFinish.append(self.onStart)

    def onStart(self):
        self.setTitle(_("Keyboard layout selection"))
        self.showList(self.selIdx or 0)

    def showList(self, index):
        self['languageList'].setList([(layout,) for layout in self.layouts])
        self['languageList'].setSelectionState(True)
        self['languageList'].moveToIndex(index)

    def updateInfo(self):
        layout = self['languageList'].getCurrent()
        if layout and os.path.exists(layoutFile(layout[2])):
            self['info'].setText(_("Press ok to remove language"))
        else:
            self['info'].setText(_("Press ok to install language"))

    def keyOK(self):
        layout = self['languageList'].getCurrent()
        if not layout:
            return
        layoutId = layout[2]
        index = self['languageList'].getCurrentIndex()
        if os.path.exists(layoutFile(layoutId)):
            os.remove(layoutFile(layoutId))
            if activeLayoutId() == layoutId:
                # the built-in layout, not a new download of the removed one
                saveActiveLayoutId(defaultKBLAYOUT['id'])
            info = _("Language removed from installed package")
        elif downloadLayout(layoutId):
            saveActiveLayoutId(layoutId)
            info = _("Language downloaded successfully, exit from install")
        else:
            info = _("Failed to download language, try later")
        # redraws the dots (the new list selection sets the info text too)
        self.showList(index)
        self['info'].setText(info)


class TextInput(Input):
    # Input that reports the end of a multi-tap (0-9) character

    def __init__(self, *args, **kwargs):
        self.nvkTimeoutCallback = None
        Input.__init__(self, *args, **kwargs)

    def timeout(self, *args, **kwargs):
        try:
            Input.timeout(self, *args, **kwargs)
        except Exception:
            pass
        if self.nvkTimeoutCallback:
            self.nvkTimeoutCallback()


class NewVirtualKeyBoard(Screen, SuggestionsFetcher):

    # openATV's VirtualKeyboard constants - its screens pass style= and
    # PackageFeedEditor (Screens/Opkg.py) subclasses the keyboard, uses
    # VKB_SAVE_ICON and overrides save(); NVK draws its own Enter key and
    # ignores the style itself
    VKB_DONE_ICON = 0
    VKB_ENTER_ICON = 1
    VKB_OK_ICON = 2
    VKB_SAVE_ICON = 3
    VKB_SEARCH_ICON = 4
    VKB_DONE_TEXT = 5
    VKB_ENTER_TEXT = 6
    VKB_OK_TEXT = 7
    VKB_SAVE_TEXT = 8
    VKB_SEARCH_TEXT = 9

    def __new__(cls, session=None, *args, **kwargs):
        # digits-only fields get the numeric keypad instead (numpad.py);
        # not for subclasses, they expect the keyboard itself
        if cls is NewVirtualKeyBoard and session is not None:
            try:
                from Plugins.SystemPlugins.NewVirtualKeyBoard.numpad import numPadMode, NVKNumPad
                mode = numPadMode(session, kwargs.get('type', args[8] if len(args) > 8 else None))
                if mode:
                    title = kwargs.get('title', args[0] if args else '')
                    text = kwargs.get('text', args[1] if len(args) > 1 else '')
                    maxSize = kwargs.get('maxSize', args[2] if len(args) > 2 else False)
                    return NVKNumPad(session, title=title, text=text, mode=mode, maxSize=maxSize)
            except Exception:
                trace_error()
        return super(NewVirtualKeyBoard, cls).__new__(cls)

    def __init__(self, session, title='', text='', maxSize=False, visible_width=False, visibleWidth=False, currPos=None, windowTitle=None, allMarked=False, type=Input.TEXT, style=None, **kwargs):
        self.skin = self.buildSkin()
        Screen.__init__(self, session)
        SuggestionsFetcher.__init__(self, self.setSuggestions)
        self.skinName = 'NewVirtualKeyBoard'
        self.settings = config.NewVirtualKeyBoard
        text = text or ''
        if not text.strip() and setting('rememberlast', True):
            text = self.settings.lastsearchText.value
        self.startText = text
        self.header = title or _('NewVirtualKeyBoard  V %s') % VER
        self.showsuggestion = setting('showsuggestion', True)
        self.showHistory = setting('showhistory', True)
        self.history = SearchHistory(hfile)
        self.searchHistoryList = []
        self.suggestions = []
        self.pendingSuggestions = None     # answer that came while the list had the focus
        self.beforeUpdateText = ''
        self.currentVKLayout = defaultKBLAYOUT
        self.selectedKBLayoutId = self.settings.keys_layout.value
        self.cycleFromId = None            # TEXT key: layout that failed to load
        self.specialKeyState = SK_NONE
        self.deadKey = u''                 # pending dead key (accent)
        self.focus = FOCUS_KEYBOARD
        self.rowIdx = 0
        self.colIdx = 0
        self.currentKeyId = KEY_TEXT

        self['actions'] = self.getActionMap()
        self['header'] = Label(' ')
        self['text'] = TextInput(text=text, maxSize=maxSize, visible_width=visible_width, type=type)
        self['flag'] = PixmapWidget()
        self['historyheader'] = Label(' ')
        self['historyList'] = TextList()
        self['suggestionheader'] = Label(' ')
        self['suggestionList'] = TextList()
        self['0'] = PixmapWidget()
        for keyId in KEY_IDS:
            self[str(keyId)] = PixmapWidget()
            self['_%d' % keyId] = Label(' ')
        for name in MARKERS:
            self[name] = PixmapWidget()
        for name, keyId in KEY_ICONS:
            self[name] = PixmapWidget()
        for bar in range(4):
            self['m_%d' % bar] = Label(' ')

        self.onLayoutFinish.append(self.loadKBpixmaps)
        self.onShown.append(self.onWindowShow)
        self.onClose.append(self.__onClose)

    def buildSkin(self):
        if isFHD():
            tier, fonts = 'fhd', (offsetFont(36), offsetFont(21), offsetFont(27), 2, offsetFont(12))
        else:
            tier, fonts = 'hd', (offsetFont(24), offsetFont(14), offsetFont(18), 1, offsetFont(10))
        credits = _("New Virtual Keyboard - Original code SamSamSam (e2iplayer). Contributors: mfaraj57 and Fairbird. Skin and amends: KiddaC")
        skin = keyboardSkin(tier, fonts, credits, textAlign='left' if setting('textalign', 'right') == 'left' else 'right',
                            background=BACKGROUND_COLORS.get(setting('bgcolor', 'default'), BACKGROUND_COLORS['default']), iconDir=keyArtDir())
        return scaleSkin(skin)

    def getActionMap(self):
        # NVKActions: keymap.xml in the plugin folder (loaded by enigma2's
        # plugin scan) - PREVIOUS/NEXT, FAST FORWARD/REWIND, PVR, TEXT, INFO
        return NumberActionMap(['WizardActions', 'DirectionActions', 'ColorActions', 'KeyboardInputActions', 'InputBoxActions', 'InputAsciiActions', 'SetupActions', 'MenuActions', 'NVKActions'], {
            'gotAsciiCode': self.keyGotAscii,
            'ok': self.keyOK,
            'ok_repeat': self.keyOK,
            'back': self.keyBack,
            'left': self.keyLeft,
            'right': self.keyRight,
            'up': self.keyUp,
            'down': self.keyDown,
            'red': self.keyRed,
            'red_repeat': self.keyRed,
            'green': self.keyGreen,
            # the colour keys type AltGr / Shift (changed far more often than
            # the language or the list)
            'yellow': self.keyYellow,
            'blue': self.keyBlue,
            'deleteBackward': self.keyRed,
            'deleteForward': self.keyDelete,
            'pageUp': self.insertSpace,
            'pageDown': self.clearText,
            'menu': self.showSettings,
            'vk_help': self.showHelp,
            'vk_prevpanel': self.togglesfocusBack,
            'vk_nextpanel': self.togglesfocus,
            'vk_space': self.insertSpace,
            'vk_cleartext': self.clearText,
            'vk_language': self.switchinstalledvklayout,
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

    # ---- start / end -----------------------------------------------------------

    def loadKBpixmaps(self):
        self.onLayoutFinish.remove(self.loadKBpixmaps)
        self['text'].nvkTimeoutCallback = self.input_updated
        artDir = keyArtDir()
        pixmaps = {}
        for name in set(keyArt(keyId) for keyId in [KEY_TEXT] + KEY_IDS) | set(MARKERS) | set(name for name, keyId in KEY_ICONS):
            pixmaps[name] = LoadPixmap(iconPath(artDir, name))
        for keyId in [KEY_TEXT] + KEY_IDS:
            self[str(keyId)].setPixmap(pixmaps[keyArt(keyId)])
        for name in MARKERS:
            self[name].hide()
            self[name].setPixmap(pixmaps[name])
        for name, keyId in KEY_ICONS:
            self[name].setPixmap(pixmaps[name])
        self.move_KMarker(-1, self.currentKeyId)
        # TRANSLATORS: key caps of the on-screen keyboard - keep them as
        # short as the English ones, the keys are small
        for keyId, text in ((KEY_ESC, _('Esc')), (KEY_CLEAR, _('Clear')), (KEY_CAPS, _('Caps')), (KEY_ENTER, _('Enter')),
                            (KEY_SHIFT_L, _('Shift')), (KEY_SHIFT_R, _('Shift')), (KEY_CTRL, _('Ctrl')), (KEY_ALT, _('Alt')), (KEY_ALTGR, _('Alt'))):
            self['_%d' % keyId].setText(text)

    def onWindowShow(self):
        self.onShown.remove(self.onWindowShow)
        self.setTitle(_('New Virtual Keyboard'))
        self['header'].setText(self.header)
        self['historyheader'].setText(_("Search history"))
        self['historyList'].setSelectionState(False)
        self['suggestionList'].setSelectionState(False)
        self.setSuggestionsHeader()
        self.searchHistoryList = self.history.entries()
        self.setPanelsVisible()
        self.setText(self.startText)
        self.loadKBLayout()
        if self.settings.firsttime.value:
            self.settings.firsttime.value = False
            self.settings.firsttime.save()
            self.showHelp()

    def __onClose(self):
        self.onClose.remove(self.__onClose)
        self['text'].nvkTimeoutCallback = None
        self.cancelSuggestions()
        saveActiveLayoutId(self.selectedKBLayoutId)

    def save(self):
        # Enter; subclasses (openATV's PackageFeedEditor) override it
        try:
            text = self['text'].getText()
        except Exception:
            text = ''
        if text.strip():
            self.history.add(text)
            self.settings.lastsearchText.value = text
            self.settings.lastsearchText.save()
        self.close(text)

    # ---- layouts -----------------------------------------------------------------

    def loadKBLayout(self):
        layoutId = self.selectedKBLayoutId
        if not layoutItem(layoutId):
            # first start (no layout saved yet): the enigma2 language's layout
            layoutId = systemLayoutId(systemLocale())
        self.getKeyboardLayout(layoutId)

    def getKeyboardLayout(self, layoutId):
        # shows a layout (downloaded first if it is not installed); on an
        # error the old layout stays, with an error message
        layout, error = None, ''
        if layoutId == defaultKBLAYOUT['id']:
            layout = defaultKBLAYOUT
        else:
            if not os.path.exists(layoutFile(layoutId)):
                downloadLayout(layoutId)
            if os.path.exists(layoutFile(layoutId)):
                try:
                    layout = readLayoutFile(layoutId)
                except Exception as e:
                    print('[NewVirtualKeyBoard] loading layout %s failed: %s' % (layoutId, e))
                    error = str(e)
        if layout is None:
            item = layoutItem(layoutId)
            message = _("Loading the keyboard layout %s failed") % (item[0] if item else layoutId)
            if error:
                message += '\n\n' + error
            self.loadVKLayout()
            self.displayActiveLayoutFlag(self.currentVKLayout['id'])
            self.session.open(MessageBox, text=message, type=MessageBox.TYPE_ERROR, timeout=5)
            return False
        self.selectedKBLayoutId = layoutId
        self.loadVKLayout(layout)
        self.displayActiveLayoutFlag(layoutId)
        return True

    def loadVKLayout(self, layout=None):
        if layout:
            self.currentVKLayout = layout
        self.updateKsText()
        self['_%d' % KEY_LANGUAGE].setText(toNative(self.currentVKLayout['locale'].split('-', 1)[0].upper()))

    def displayActiveLayoutFlag(self, layoutId):
        self['flag'].instance.setPixmapFromFile(flagFileForLayout(layoutId))
        if setting('showflags', True):
            self['flag'].instance.show()
        else:
            self['flag'].instance.hide()

    def switchinstalledvklayout(self):
        # TEXT: the next installed layout (the built-in one included)
        ids = installedLayoutIds()
        if defaultKBLAYOUT['id'] not in ids:
            ids = sorted(ids + [defaultKBLAYOUT['id']])
        start = self.cycleFromId or self.currentVKLayout['id']
        layoutId = ids[(ids.index(start) + 1) % len(ids)] if start in ids else ids[0]
        if layoutId == self.currentVKLayout['id']:
            return
        # after a failed layout the next TEXT press goes on after it
        self.cycleFromId = None if self.getKeyboardLayout(layoutId) else layoutId

    def switchToLanguageSelection(self):
        # the list works with the saved layout: save the one shown first
        saveActiveLayoutId(self.selectedKBLayoutId)
        ids = [item[2] for item in KbLayouts]
        current = self.currentVKLayout['id']
        self.session.openWithCallback(self.languageSelectionBack, LanguageListScreen, None, ids.index(current) if current in ids else None)

    def languageSelectionBack(self, *args):
        # a layout was installed (-> active) or the shown one removed
        # (-> the built-in one is active)
        layoutId = activeLayoutId()
        if layoutId and layoutId != self.currentVKLayout['id']:
            self.getKeyboardLayout(layoutId)
        self.switchToKeyboard()

    # ---- typing ------------------------------------------------------------------

    def processKeyId(self, keyId):
        if keyId == KEY_TEXT:
            keyId = KEY_ENTER
        handler = {
            KEY_ESC: self.keyEsc,
            KEY_BACKSPACE: self.deleteBackward,
            KEY_DELETE: self.deleteForward,
            KEY_CLEAR: self.clearText,
            KEY_LANGUAGE: self.switchToLanguageSelection,
            KEY_LEFT: self['text'].left,
            KEY_RIGHT: self['text'].right,
            # through save(), so a subclass that overrides it gets Enter
            KEY_ENTER: self.save,
        }.get(keyId)
        if handler:
            handler()
        elif keyId in MODIFIERS:
            self.toggleModifier(*MODIFIERS[keyId])
        else:
            self.typeKey(keyId)

    def keyEsc(self):
        # cancels a pending dead key, else closes without the text
        if self.deadKey:
            self.deadKey = u''
            self.updateKsText()
        else:
            self.close(None)

    def toggleModifier(self, state, keys):
        self.specialKeyState ^= state
        self.updateKsText()
        self.updateSKey(keys, self.specialKeyState & state)

    def typeKey(self, keyId):
        char = self.getKeyChar(keyId)
        if not char:
            return
        relabel = False
        # a typed character releases Shift, Alt and Ctrl (not Caps Lock)
        for state, keys in ((SK_CTRL, [KEY_CTRL]), (SK_ALT, [KEY_ALT, KEY_ALTGR]), (SK_SHIFT, [KEY_SHIFT_L, KEY_SHIFT_R])):
            if self.specialKeyState & state:
                self.specialKeyState ^= state
                self.updateSKey(keys, 0)
                relabel = True
        deadkeys = self.currentVKLayout['deadkeys']
        if self.deadKey:
            # accent + character, or both as they are if they don't combine
            text = deadkeys[self.deadKey].get(char, self.deadKey + char)
            self.deadKey = u''
            relabel = True
        elif char in deadkeys:
            text = u''
            self.deadKey = char
            relabel = True
        else:
            text = char
        if text:
            self.insertText(text)
        if relabel:
            self.updateKsText()

    def getKeyChar(self, keyId):
        state = self.specialKeyState
        # Alt alone types like AltGr (Ctrl+Alt), as on Windows
        if state & SK_ALT:
            state |= SK_CTRL
        return self.currentVKLayout['layout'].get(keyId, {}).get(state, u'')

    def insertText(self, text):
        field = self['text']
        try:
            for char in text:
                field.insertChar(char, field.currPos, False, True)
                # innerRight on openATV, innerright on OpenPLi and the others
                (getattr(field, 'innerRight', None) or field.innerright)()
            field.update()
        except Exception:
            trace_error()
        self.input_updated()

    def deleteBackward(self):
        self['text'].deleteBackward()
        self.input_updated()

    def deleteForward(self):
        self['text'].delete()
        self.input_updated()

    def clearText(self):
        self['text'].deleteAllChars()
        self['text'].update()
        self.input_updated()

    def insertSpace(self):
        self.processKeyId(KEY_SPACE)

    def setText(self, text):
        text = toNative(text)
        field = self['text']
        field.setText(text)
        # right() once to drop a "whole text marked" state (it would move the
        # cursor to the start), then the cursor to the end
        field.right()
        field.currPos = len(text if PY3 else text.decode('utf-8', 'ignore'))
        field.right()
        self.input_updated()

    def textLength(self):
        text = self['text'].getText()
        if not PY3:
            text = text.decode('utf-8', 'ignore')
        return len(text)

    # ---- key labels --------------------------------------------------------------

    def updateSKey(self, keys, on):
        for keyId in keys:
            self['_%d' % keyId].instance.setForegroundColor(COLOR_ACTIVE if on else COLOR_TEXT)

    def updateKeyLabel(self, keyId):
        char = self.getKeyChar(keyId)
        deadkeys = self.currentVKLayout['deadkeys']
        if self.deadKey:
            # what the key types after the pending dead key
            combined = deadkeys.get(self.deadKey, {})
            if char in combined:
                char, color = combined[char], COLOR_TEXT
            else:
                color = COLOR_UNAVAILABLE
        elif len(char) > 1:
            color = COLOR_LIGATURE
        elif char in deadkeys:
            color = COLOR_DEAD
        else:
            color = COLOR_TEXT
        label = self['_%d' % keyId]
        label.instance.setForegroundColor(color)
        label.setText(toNative(char))

    def updateKsText(self):
        for keyId in CHARACTER_KEYS:
            self.updateKeyLabel(keyId)

    # ---- moving on the keyboard ---------------------------------------------------

    def processArrowKey(self, dx=0, dy=0):
        # moves the selection one key; a key spanning several columns is
        # left in one step, and a wide key (space) is entered in its middle
        oldKeyId = KEY_GRID[self.rowIdx][self.colIdx]
        if dx and oldKeyId == KEY_TEXT:
            return
        if dx:
            while KEY_GRID[self.rowIdx][self.colIdx] == oldKeyId:
                self.colIdx = (self.colIdx + dx) % KEY_COLUMNS
            row = KEY_GRID[self.rowIdx]
            keyId = row[self.colIdx]
            first = row.index(keyId)
            last = KEY_COLUMNS - 1 - row[::-1].index(keyId)
            if last - first > 2:
                self.colIdx = (first + last) // 2
        elif dy:
            while KEY_GRID[self.rowIdx][self.colIdx] == oldKeyId:
                self.rowIdx = (self.rowIdx + dy) % KEY_ROWS
        self.currentKeyId = KEY_GRID[self.rowIdx][self.colIdx]
        self.move_KMarker(oldKeyId, self.currentKeyId)

    def move_KMarker(self, oldKeyId, newKeyId):
        if oldKeyId == -1 and newKeyId == -1:
            for name in MARKERS:
                self[name].hide()
            return
        if oldKeyId != -1:
            self[keyMarker(oldKeyId)].hide()
        if newKeyId != -1:
            marker = self[keyMarker(newKeyId)]
            x, y = self[str(newKeyId)].position
            marker.instance.move(ePoint(x, y))
            marker.show()

    # ---- focus: keyboard, search history (left), suggestions (right) -------------

    def panelList(self, focus):
        return self['historyList' if focus == FOCUS_HISTORY else 'suggestionList']

    def panelAvailable(self, focus):
        # shown and not empty
        if focus == FOCUS_HISTORY:
            return bool(self.showHistory and self.searchHistoryList)
        if focus == FOCUS_SUGGESTIONS:
            return bool(self.showsuggestion and self.suggestions)
        return True

    def setFocus(self, focus):
        self['text'].timeout()
        if self.focus == focus:
            return
        if self.focus == FOCUS_KEYBOARD:
            self.move_KMarker(-1, -1)
        else:
            self.panelList(self.focus).setSelectionState(False)
        leftSuggestions = self.focus == FOCUS_SUGGESTIONS
        self.focus = focus
        if leftSuggestions and self.pendingSuggestions is not None:
            self.setSuggestions(self.pendingSuggestions)

    def switchToKeyboard(self):
        self.setFocus(FOCUS_KEYBOARD)
        self.move_KMarker(-1, self.currentKeyId)

    def switchToPanel(self, focus):
        self.setFocus(focus)
        self.panelList(focus).moveToIndex(0)
        self.panelList(focus).setSelectionState(True)

    def togglesfocusBack(self):
        self.togglesfocus(-1)

    def togglesfocus(self, step=1):
        # PVR / NEXT: keyboard -> suggestions -> search history -> keyboard,
        # skipping hidden and empty panels (PREVIOUS: the other way)
        panels = [focus for focus in (FOCUS_KEYBOARD, FOCUS_SUGGESTIONS, FOCUS_HISTORY) if self.panelAvailable(focus)]
        if len(panels) < 2:
            return
        idx = panels.index(self.focus) if self.focus in panels else 0
        focus = panels[(idx + step) % len(panels)]
        if focus == FOCUS_KEYBOARD:
            self.switchToKeyboard()
        else:
            self.switchToPanel(focus)

    def moveHorizontal(self, step):
        # LEFT/RIGHT past the keyboard edge or a list: the next shown panel
        # in the row history | keyboard | suggestions (wrapping around)
        ring = [FOCUS_HISTORY, FOCUS_KEYBOARD, FOCUS_SUGGESTIONS]
        idx = ring.index(self.focus)
        for _step in range(len(ring)):
            idx = (idx + step) % len(ring)
            if self.panelAvailable(ring[idx]):
                break
        if ring[idx] != FOCUS_KEYBOARD:
            self.switchToPanel(ring[idx])
            return
        self.switchToKeyboard()
        # coming in from the other side: continue on the far edge's keys
        if self.currentKeyId in (RIGHT_KEYS if step > 0 else LEFT_KEYS):
            self.processArrowKey(step, 0)

    # ---- remote control keys --------------------------------------------------------

    def keyboardKey(self, keyId):
        # the colour keys etc. type on the keyboard only
        if self.focus == FOCUS_KEYBOARD:
            self.processKeyId(keyId)

    def keyRed(self):
        self.keyboardKey(KEY_BACKSPACE)

    def keyDelete(self):
        self.keyboardKey(KEY_DELETE)

    def keyGreen(self):
        self.processKeyId(KEY_ENTER)

    def keyYellow(self):
        self.keyboardKey(KEY_ALTGR)

    def keyBlue(self):
        self.keyboardKey(KEY_SHIFT_L)

    def keyOK(self):
        if self.focus == FOCUS_KEYBOARD:
            self.processKeyId(self.currentKeyId)
            return
        # a suggestion or history entry becomes the text
        text = self.panelList(self.focus).getCurrent()
        if text:
            self.setText(text)
        self.currentKeyId = KEY_TEXT
        self.rowIdx, self.colIdx = 0, KEY_COLUMNS // 2
        self.switchToKeyboard()

    def keyBack(self):
        if self.focus == FOCUS_KEYBOARD:
            self.keyEsc()
        else:
            self.switchToKeyboard()

    def keyUp(self):
        self.moveVertical(-1)

    def keyDown(self):
        self.moveVertical(1)

    def moveVertical(self, step):
        if self.focus == FOCUS_KEYBOARD:
            self.processArrowKey(0, step)
        else:
            self.panelList(self.focus).moveSelection(step)

    def keyLeft(self):
        if self.focus == FOCUS_KEYBOARD:
            if self.currentKeyId == KEY_TEXT:
                if self['text'].currPos > 0:
                    self['text'].left()
                    return
            elif self.currentKeyId not in LEFT_KEYS:
                self.processArrowKey(-1, 0)
                return
        self.moveHorizontal(-1)

    def keyRight(self):
        if self.focus == FOCUS_KEYBOARD:
            if self.currentKeyId == KEY_TEXT:
                if self['text'].currPos < self.textLength():
                    self['text'].right()
                    return
            elif self.currentKeyId not in RIGHT_KEYS:
                self.processArrowKey(1, 0)
                return
        self.moveHorizontal(1)

    def keyNumberGlobal(self, number):
        # multi-tap input like on a phone, on the text field
        if self.currentKeyId == KEY_TEXT:
            try:
                self['text'].number(number)
            except Exception:
                trace_error()

    def keyGotAscii(self):
        # USB keyboard, on the text field
        if self.currentKeyId == KEY_TEXT:
            try:
                self['text'].handleAscii(getPrevAsciiCode())
            except Exception:
                trace_error()

    # ---- history and suggestions ------------------------------------------------------

    def setPanelsVisible(self):
        for name, shown in (('suggestion', self.showsuggestion), ('history', self.showHistory)):
            for widget in (name + 'header', name + 'List'):
                if shown:
                    self[widget].show()
                else:
                    self[widget].hide()
        if self.showHistory:
            self['historyList'].setList([(x,) for x in self.searchHistoryList])

    def setSuggestionsHeader(self):
        self['suggestionheader'].setText('%s (%s)' % (_("Suggestions"), self.suggestionsProviderName()))

    def input_updated(self):
        text = self['text'].getText()
        if text == self.beforeUpdateText:
            return
        self.beforeUpdateText = text
        self.updateSuggestions(text)

    def updateSuggestions(self, word):
        if self.showHistory:
            # re-sorted on every change, also with the suggestions turned off
            self.searchHistoryList = self.history.sortedFor(word)
            self['historyList'].setList([(x,) for x in self.searchHistoryList])
        if not self.showsuggestion:
            return
        if not word:
            # an answer for the old text must not fill the list again
            self.cancelSuggestions()
            self.setSuggestions([])
            return
        self.requestSuggestions(word, str(self.currentVKLayout.get('locale') or 'en-US'))

    def setSuggestions(self, suggestions):
        if self.focus == FOCUS_SUGGESTIONS:
            # don't swap the list under the user's selection; shown when the
            # focus leaves the list
            self.pendingSuggestions = suggestions
            return
        self.pendingSuggestions = None
        self.suggestions = suggestions
        self['suggestionList'].setList([(x,) for x in suggestions])

    def clearSearchHistory(self):
        self.history.clear()
        self.searchHistoryList = []
        self['historyList'].setList([])

    # ---- settings and help ------------------------------------------------------------

    def showSettings(self):
        from Plugins.SystemPlugins.NewVirtualKeyBoard.setup import nvKeyboardSetup
        self.session.openWithCallback(self.settingsBack, nvKeyboardSetup, True, self)

    def settingsBack(self, result=None):
        # applies the changed settings to the open keyboard (fonts and
        # colours on the next open)
        if not result:
            return
        self.switchToKeyboard()
        self.showsuggestion = setting('showsuggestion', True)
        self.showHistory = setting('showhistory', True)
        provider = setting('suggestionsprovider', 'google')
        if provider != self.suggestionsProvider:
            self.setSuggestionsProvider(provider)
            self.setSuggestions([])
        self.setSuggestionsHeader()
        self.setPanelsVisible()
        self.beforeUpdateText = None
        self.input_updated()
        try:
            self.displayActiveLayoutFlag(self.currentVKLayout['id'])
            # eLabel alignLeft = 0, alignRight = 2
            self['text'].instance.setHAlign(0 if setting('textalign', 'right') == 'left' else 2)
        except Exception:
            trace_error()

    def showHelp(self):
        rows = [
            (_("OK - Type the selected key / take the selected suggestion or history entry"), 'key_ok'),
            (_("Green - Enter: confirm the text and close"), 'key_green'),
            (_("Red - Backspace"), 'key_red'),
            (_("Yellow - AltGr"), 'key_yellow'),
            (_("Blue - Shift"), 'key_blue'),
            (_("Text - Switch language"), 'key_text'),
            (_("PVR - Switch between keyboard, suggestions and search history"), 'key_pvr'),
            (_("Previous / Next - Switch between keyboard, suggestions and search history"), 'key_prevnext'),
            (_("Left / Right at the edge of the keyboard - Switch to the suggestions or the search history"), 'key_leftright'),
            (_("Page Up - Insert space"), 'key_plus'),
            (_("Fast forward - Insert space"), 'key_ff'),
            (_("Page Down - Clear input text"), 'key_minus'),
            (_("Rewind - Clear input text"), 'key_rew'),
            (_("0-9 - Text input like on a phone, when the input field is selected"), 'key_0-9'),
            (_("Menu - Settings, install languages, clear the search history"), 'key_menu'),
            (_("Info - Show this screen again"), 'key_info'),
            (_("Exit - Close without taking the text"), 'key_exit'),
        ]
        self.session.open(HelpScreen, _('Help'), rows)


class HelpScreen(Screen):
    # remote control keys: icon + text per row, all rows without scrolling

    ROW_H = 54      # FHD reference, scaled to the desktop
    FONT = 26
    WIDTH = 1400
    TITLE_H = 60

    def __init__(self, session, title, rows):
        # own title bar (wfNoBorder): the image's window border cut the title
        # off on WQHD
        listH = min(max(len(rows), 1) * self.ROW_H, 1000 - self.TITLE_H - 16)
        height = self.TITLE_H + 6 + listH + 10
        self.skin = '''
            <screen name="vkOptionsScreen" position="center,center" size="%d,%d" backgroundColor="#16000000" transparent="0" title="Help" flags="wfNoBorder">
            <widget source="Title" render="Label" position="0,0" size="%d,%d" font="Regular;34" halign="center" valign="center" foregroundColor="#ffffff" backgroundColor="#3f434f" transparent="0" />
            <widget name="menu" position="5,%d" size="%d,%d" backgroundColor="#3f4450" backgroundColorSelected="#0f64b2" transparent="0" />
            </screen>''' % (self.WIDTH, height, self.WIDTH, self.TITLE_H, self.TITLE_H + 6, self.WIDTH - 10, listH)
        self.factor = desktopFactor()
        self.skin = scaleSkin(self.skin, self.factor)
        Screen.__init__(self, session)
        self.skinName = 'vkOptionsScreen'
        self.helpTitle = title
        self.rows = rows
        self['menu'] = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self['actions'] = ActionMap(['WizardActions'], {
            'back': self.close,
            'ok': self.close,
        }, -1)
        self.onLayoutFinish.append(self.onStart)

    def onStart(self):
        self.setTitle(self.helpTitle)
        self['menu'].l.setList(self.buildRows())

    def buildRows(self):
        def s(value):
            return int(round(value * self.factor))
        self['menu'].l.setItemHeight(s(self.ROW_H))
        self['menu'].l.setFont(0, gFont('Regular', s(self.FONT)))
        iconDir = menuIconsDir()
        entries = []
        for text, icon in self.rows:
            # the first element of a MultiContent row is its data, not drawn
            entries.append([
                None,
                MultiContentEntryText(pos=(s(90), 0), size=(s(self.WIDTH - 110), s(self.ROW_H)), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=text, color=0xffffff, color_sel=0xffffff),
                MultiContentEntryPixmapAlphaBlend(pos=(s(30), s((self.ROW_H - 38) // 2)), size=(s(38), s(38)), png=loadPNG(iconPath(iconDir, icon))),
            ])
        return entries


VirtualKeyBoard = VirtualKeyboard = NewVirtualKeyBoard
