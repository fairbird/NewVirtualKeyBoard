#!/usr/bin/python
# -*- coding: utf-8 -*-

# Code mfaraj57 and RAED (Fairbird)

# The settings (config.NewVirtualKeyBoard), the settings screen, switching
# between the image keyboard and this one, and the online update check.

import os

from enigma import gFont
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.config import (config, configfile, getConfigListEntry, ConfigSubsection, ConfigText, ConfigYesNo, ConfigSelection,
    ConfigInteger, ConfigSelectionNumber, ConfigNothing)
from Components.ConfigList import ConfigListScreen
from Components.Label import Label

from Plugins.SystemPlugins.NewVirtualKeyBoard import _
from Plugins.SystemPlugins.NewVirtualKeyBoard.Console import Console
from Plugins.SystemPlugins.NewVirtualKeyBoard.suggestions import SUGGESTION_PROVIDERS, SearchHistory
from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import (PY3, INSTALLER_URL, DreamOS, byTier, getversioninfo, isFHD, logdata,
    pluginPath, scaleSkin, sc, trace_error, urlread, versionTuple)

VER = getversioninfo()

config.NewVirtualKeyBoard = ConfigSubsection()
config.NewVirtualKeyBoard.keys_layout = ConfigText(default='', fixed_size=False)
config.NewVirtualKeyBoard.lastsearchText = ConfigText(default='', fixed_size=False)
config.NewVirtualKeyBoard.firsttime = ConfigYesNo(default=True)
config.NewVirtualKeyBoard.textinput = ConfigSelection(default='VirtualKeyBoard', choices=[('VirtualKeyBoard', _("Image virtual keyboard")), ('NewVirtualKeyBoard', _("New Virtual Keyboard"))])
config.NewVirtualKeyBoard.showinplugins = ConfigYesNo(default=True)
config.NewVirtualKeyBoard.showsuggestion = ConfigYesNo(default=True)
config.NewVirtualKeyBoard.suggestionsprovider = ConfigSelection(default='google', choices=SUGGESTION_PROVIDERS)
config.NewVirtualKeyBoard.showhistory = ConfigYesNo(default=True)
config.NewVirtualKeyBoard.rememberlast = ConfigYesNo(default=True)
config.NewVirtualKeyBoard.historysize = ConfigInteger(default=100, limits=(1, 99999))
# a selection instead of ConfigInteger: number keys can't type "-"
config.NewVirtualKeyBoard.fontssize = ConfigSelectionNumber(min=-10, max=30, stepwidth=1, default=0, wraparound=False)
config.NewVirtualKeyBoard.textalign = ConfigSelection(default='right', choices=[('left', _("Left")), ('right', _("Right"))])
config.NewVirtualKeyBoard.showflags = ConfigYesNo(default=True)
config.NewVirtualKeyBoard.bgcolor = ConfigSelection(default='default', choices=[('default', _("Default")), ('transparent', _("Transparent")), ('black', _("Black")), ('semi', _("Semi-transparent")), ('light', _("Mostly transparent"))])
config.NewVirtualKeyBoard.numpad = ConfigYesNo(default=True)
config.NewVirtualKeyBoard.updateonline = ConfigYesNo(default=True)

# ---- image keyboard <-> this keyboard ------------------------------------------
# Screens/VirtualKeyBoard.py becomes a symlink to this plugin's file; the
# image's own file (.py, or only .pyo/.pyc) is kept as VirtualKeyBoard_backup.*

SCREENS_DIR = '/usr/lib/enigma2/python/Screens/'
KEYBOARD_LINK = SCREENS_DIR + 'VirtualKeyBoard.py'


def newKeyboardActive():
    return os.path.islink(KEYBOARD_LINK)


def switchKeyboard(useNew):
    # True when done; raises OSError, returns False when the image keyboard
    # can't be restored (no backup - the new keyboard stays then)
    if useNew:
        if newKeyboardActive():
            return True
        for ext in ('.py', '.pyo', '.pyc'):
            image = SCREENS_DIR + 'VirtualKeyBoard' + ext
            if os.path.exists(image):
                os.rename(image, SCREENS_DIR + 'VirtualKeyBoard_backup' + ext)
                break
        # compiled copies of the image's .py would be loaded instead of the link
        for ext in ('.pyo', '.pyc'):
            if os.path.exists(SCREENS_DIR + 'VirtualKeyBoard' + ext):
                os.remove(SCREENS_DIR + 'VirtualKeyBoard' + ext)
        os.symlink(pluginPath('VirtualKeyBoard.py'), KEYBOARD_LINK)
        return True
    if not newKeyboardActive():
        return True
    for ext in ('.py', '.pyo', '.pyc'):
        backup = SCREENS_DIR + 'VirtualKeyBoard_backup' + ext
        if os.path.exists(backup):
            os.remove(KEYBOARD_LINK)
            os.rename(backup, SCREENS_DIR + 'VirtualKeyBoard' + ext)
            return True
    return False


# ---- online update check -----------------------------------------------------------

def parseInstaller(data):
    # (version, description) from installer.sh: version="x.y" and a
    # description="..." that may span several lines
    if PY3 and isinstance(data, bytes):
        data = data.decode('utf-8', 'replace')
    version, description, descLines = None, '', None
    for line in data.splitlines():
        if descLines is not None:
            # inside the description - a "version=" line there is text
            if line.rstrip().endswith('"'):
                descLines.append(line.rstrip()[:-1])
                description = '\n'.join(descLines).strip()
                descLines = None
            else:
                descLines.append(line)
            continue
        line = line.strip()
        if line.startswith('version='):
            version = line[len('version='):].strip('"\' ')
        elif line.startswith('description='):
            rest = line[len('description='):]
            if rest.startswith('"'):
                rest = rest[1:]
            if rest.endswith('"'):
                description = rest[:-1].strip()
            else:
                descLines = [rest] if rest else []
    return version, description


# ---- settings screen ------------------------------------------------------------------

# FHD and HD geometry; WQHD scales the FHD one
SETUP_GEOMETRY = {
    'fhd': {'size': (1080, 830), 'title': (1076, 50, 35), 'config': (30, 55, 1020, 675), 'list': (45, 30),  # row height, font
            'buttonX': (30, 290, 550, 810), 'buttonY': 770, 'icon': 38, 'label': (48, 222, 68, 28)},  # label: x offset, width, height, font
    'hd': {'size': (720, 555), 'title': (720, 50, 20), 'config': (20, 60, 680, 450), 'list': (30, 20),
           'buttonX': (20, 195, 370, 545), 'buttonY': 520, 'icon': 25, 'label': (32, 140, 44, 18)},
}


def setupSkin():
    g = SETUP_GEOMETRY['fhd' if isFHD() else 'hd']
    width, height = g['size']
    titleW, titleH, titleFont = g['title']
    out = ['<screen name="nvKeyboardSetup" position="center,center" size="%d,%d" backgroundColor="#16000000" title="New Virtual Keyboard Settings" flags="wfNoBorder">' % (width, height)]
    out.append('<widget source="Title" render="Label" position="0,0" size="%d,%d" font="Regular;%d" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#16000000" />' % (titleW, titleH, titleFont))
    # no itemHeight/font on the list: older images (VTi) reject them in the
    # skin - set from code (nvKeyboardSetup.setListFonts)
    out.append('<widget name="config" position="%d,%d" size="%d,%d" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />' % g['config'])
    icon = g['icon']
    labelOffset, labelW, labelH, labelFont = g['label']
    # two lines high, centred on the icon: longer translations (Greek) wrap
    # instead of being cut off
    labelY = g['buttonY'] + (icon - labelH) // 2
    # each tier has its own button pictures (images/key_red_sd.png, ...)
    suffix = byTier('', '_wqhd', '_sd')
    for x, colour in zip(g['buttonX'], ('red', 'green', 'yellow', 'blue')):
        out.append('<ePixmap position="%d,%d" size="%d,%d" pixmap="%s" zPosition="3" transparent="1" alphatest="blend" />' % (x, g['buttonY'], icon, icon, pluginPath('images', 'key_%s%s.png' % (colour, suffix))))
        out.append('<widget name="key_%s" position="%d,%d" size="%d,%d" zPosition="4" halign="left" valign="center" font="Regular;%d" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" />' % (colour, x + labelOffset, labelY, labelW, labelH, labelFont))
    out.append('</screen>')
    return scaleSkin('\n'.join(out))


def settingRows():
    # (text, config element) of every setting in the screen
    s = config.NewVirtualKeyBoard
    return [
        (_("Text input method-keyboard") + ':', s.textinput),
        (_("Font size (-10 to +30)") + ':', s.fontssize),
        (_("Show suggestions") + ':', s.showsuggestion),
        (_("Suggestions provider") + ':', s.suggestionsprovider),
        (_("Show search history") + ':', s.showhistory),
        (_("Search history entries (1-99999)") + ':', s.historysize),
        (_("Remember last search entry") + ':', s.rememberlast),
        (_("Text field alignment") + ':', s.textalign),
        (_("Show flags") + ':', s.showflags),
        (_("Background color") + ':', s.bgcolor),
        (_("Numeric keypad for numbers") + ':', s.numpad),
        (_("Enable/Disable Checking Online Update") + ':', s.updateonline),
        (_("Show plugin in Plugin Browser") + ':', s.showinplugins),
    ]


class nvKeyboardSetup(ConfigListScreen, Screen):

    def __init__(self, session, fromkeyboard=False, keyboard=None):
        # keyboard: the open keyboard when started with MENU from it
        self.skin = setupSkin()
        Screen.__init__(self, session)
        self.keyboard = keyboard
        self.closed = False
        # the setting follows the symlink (changed by hand or by the installer)
        config.NewVirtualKeyBoard.textinput.value = 'NewVirtualKeyBoard' if newKeyboardActive() else 'VirtualKeyBoard'
        config.NewVirtualKeyBoard.textinput.save()
        self.startTextinput = config.NewVirtualKeyBoard.textinput.value
        self.startShowinplugins = config.NewVirtualKeyBoard.showinplugins.value
        # value-less rows that run something on OK
        self.actionInstallLanguage = ConfigNothing()
        self.actionClearHistory = ConfigNothing()
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
        # "ok" goes to keyActionRow first; for the other rows it returns 0 and
        # the image's own ConfigListScreen.keyOK runs (it must not be
        # overridden here, that made OK dead on older images)
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {
            'cancel': self.keyClose,
            'green': self.keySave,
            'ok': self.keyActionRow,
            'yellow': self.showNewkeyboard,
            'blue': self.showNumpad,
        }, -2)
        self['key_red'] = Label(_("Cancel"))
        self['key_green'] = Label(_("Save"))
        self['key_yellow'] = Label(_("Virtual Keyboard"))
        self['key_blue'] = Label(_("Numeric keypad"))
        self.onClose.append(self.setClosed)
        self.onLayoutFinish.append(self.onStart)
        self.createConfigList()

    def onStart(self):
        # the skin's title attribute can't be translated
        self.setTitle('%s  V %s' % (_("New Virtual Keyboard Settings"), VER))
        self.setListFonts()
        if config.NewVirtualKeyBoard.updateonline.value:
            self.checkupdates()

    def setListFonts(self):
        # row height and font of the list (DreamOS keeps its own)
        if DreamOS():
            return
        itemHeight, font = [sc(v) for v in SETUP_GEOMETRY['fhd' if isFHD() else 'hd']['list']]
        instance = getattr(self['config'], 'instance', None)
        if instance is None:
            return
        for method, value in (('setItemHeight', itemHeight), ('setFont', gFont('Regular', font))):
            try:
                getattr(instance, method)(value)
            except Exception:
                trace_error()

    def setClosed(self):
        self.closed = True

    def changedEntry(self):
        # rebuilds for the rows that depend on others (suggestions provider)
        self.createConfigList()

    def createConfigList(self):
        # action rows (OK) on top, then all settings
        self.list = [getConfigListEntry(_("Install language") + ' ...', self.actionInstallLanguage),
                     getConfigListEntry(_("Clear search history") + ' ...', self.actionClearHistory)]
        for text, element in settingRows():
            if element is config.NewVirtualKeyBoard.suggestionsprovider and not config.NewVirtualKeyBoard.showsuggestion.value:
                continue
            self.list.append(getConfigListEntry(text, element))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def keyActionRow(self):
        current = self['config'].getCurrent()
        if current and current[1] is self.actionInstallLanguage:
            self.installLanguage()
        elif current and current[1] is self.actionClearHistory:
            self.clearHistory()
        else:
            return 0

    def keySave(self):
        # all settings, also the ones hidden right now
        for text, element in settingRows():
            element.save()
        configfile.save()
        textinput = config.NewVirtualKeyBoard.textinput
        if textinput.value != self.startTextinput:
            try:
                done = switchKeyboard(textinput.value == 'NewVirtualKeyBoard')
            except OSError as e:
                trace_error()
                done = False
                self.session.open(MessageBox, '%s\n\n%s' % (_("Switching the keyboard failed"), e), MessageBox.TYPE_ERROR)
            else:
                if not done:
                    self.session.open(MessageBox, _("The backup of the image keyboard is missing, the New Virtual Keyboard stays active."), MessageBox.TYPE_ERROR)
            if not done:
                textinput.value = 'NewVirtualKeyBoard' if newKeyboardActive() else 'VirtualKeyBoard'
                textinput.save()
                configfile.save()
                if textinput.value == self.startTextinput:
                    return
        elif config.NewVirtualKeyBoard.showinplugins.value == self.startShowinplugins:
            # font size, suggestions etc. apply on the next open of the
            # keyboard; the keyboard switch and the plugin list need a restart
            self.close(True)
            return
        self.session.openWithCallback(self.restartenigma, MessageBox, _("Restart enigma2 to load new settings?"), MessageBox.TYPE_YESNO)

    def keyClose(self):
        for text, element in settingRows():
            element.cancel()
        self.close()

    def restartenigma(self, result):
        if result:
            from Screens.Standby import TryQuitMainloop
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close(True)

    def showNewkeyboard(self):
        # try the keyboard (also when opened from it: a second one on top,
        # the settings being edited are kept)
        try:
            from Plugins.SystemPlugins.NewVirtualKeyBoard.VirtualKeyBoard import NewVirtualKeyBoard
            self.session.open(NewVirtualKeyBoard, title=_("Virtual Keyboard"), text='')
        except Exception:
            trace_error()

    def showNumpad(self):
        # try the numeric keypad (shown for number fields)
        from Plugins.SystemPlugins.NewVirtualKeyBoard.numpad import NVKNumPad
        self.session.open(NVKNumPad, title=_("Numeric keypad"), text='', mode='number')

    def installLanguage(self):
        if self.keyboard is not None:
            self.keyboard.switchToLanguageSelection()
            return
        from Plugins.SystemPlugins.NewVirtualKeyBoard.VirtualKeyBoard import LanguageListScreen
        self.session.open(LanguageListScreen)

    def clearHistory(self):
        self.session.openWithCallback(self.clearHistoryConfirmed, MessageBox, _("Delete the search history?"), MessageBox.TYPE_YESNO)

    def clearHistoryConfirmed(self, answer=False):
        if not answer:
            return
        if self.keyboard is not None:
            self.keyboard.clearSearchHistory()
        else:
            SearchHistory().clear()

    # ---- online update ----------------------------------------------------------------

    def checkupdates(self):
        try:
            from twisted.internet import threads
            threads.deferToThread(urlread, INSTALLER_URL, 10).addCallback(lambda result: self.parseData(result[0])).addErrback(self.errBack)
        except Exception:
            trace_error()

    def errBack(self, error=None):
        logdata('errBack-error', error)

    def parseData(self, data):
        if self.closed:
            return
        version, description = parseInstaller(data)
        new, current = versionTuple(version), versionTuple(VER)
        if new is None or current is None:
            logdata('Updates', 'version check failed')
            return
        if new <= current:
            logdata('Updates', 'No new version available')
            return
        self.session.openWithCallback(self.install, MessageBox, '%s %s %s.\n\n%s\n\n%s' % (_("New version"), version, _("is available"), description, _("Do you want to install it now?")), MessageBox.TYPE_YESNO)

    def install(self, answer=False):
        if answer:
            self.session.open(Console, title=_("Installing last update, enigma will be started after install"), cmdlist=['wget %s -O - | /bin/sh' % INSTALLER_URL], closeOnSuccess=False)
