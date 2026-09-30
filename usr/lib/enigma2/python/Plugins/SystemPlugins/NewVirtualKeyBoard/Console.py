#!/usr/bin/python
# -*- coding: utf-8 -*-
# RAED & mfaraj57 &  (c) 2018

# Runs the update (installer.sh) and shows its output.

from __future__ import print_function

from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText

from Plugins.SystemPlugins.NewVirtualKeyBoard import _
from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import PY3, isFHD, scaleSkin


class Console(Screen):

    def __init__(self, session, title='Console', cmdlist=None, finishedCallback=None, closeOnSuccess=False, showStartStopText=True, skin=None):
        if isFHD():
            self.skin = '''<screen position="center,center" size="1886,1051" title="Command execution..." backgroundColor="#16000000" flags="wfNoBorder">
                <widget source="Title" render="Label" position="8,3" size="1163,80" font="Regular;45" foregroundColor="#00ffffff" backgroundColor="#16000000" zPosition="4" />
                <widget name="text" position="9,93" size="1868,897" backgroundColor="#16000000" foregroundColor="#00ffffff" font="Console;33" />
                <eLabel position="10,1043" size="250,5" backgroundColor="#00ff2525" zPosition="1" />
                <eLabel position="353,1043" size="250,5" backgroundColor="#00389416" zPosition="1" />
                <eLabel position="1626,1043" size="250,5" backgroundColor="#000080ff" zPosition="1" />
                <widget source="key_red" render="Label" position="10,1004" size="250,40" zPosition="2" font="Regular;28" halign="center" valign="center" backgroundColor="#16000000" foregroundColor="#00ffffff" transparent="1" />
                <widget source="key_green" render="Label" position="353,1004" size="250,40" zPosition="2" font="Regular;28" halign="center" valign="center" backgroundColor="#16000000" foregroundColor="#00ffffff" transparent="1" />
                <widget source="key_blue" render="Label" position="1626,1004" size="250,40" zPosition="2" font="Regular;28" halign="center" valign="center" backgroundColor="#16000000" foregroundColor="#00ffffff" transparent="1" />
                </screen>'''
        else:
            self.skin = '''<screen position="17,center" size="1245,681" title="Command execution..." backgroundColor="#16000000" flags="wfNoBorder">
                <widget source="Title" render="Label" position="8,3" size="1000,40" font="Regular;30" foregroundColor="#00ffffff" backgroundColor="#16000000" zPosition="4" />
                <widget name="text" position="9,48" size="1237,587" backgroundColor="#16000000" foregroundColor="#00ffffff" font="Console;24" />
                <eLabel position="10,674" size="165,5" backgroundColor="#00ff2525" zPosition="1" />
                <eLabel position="238,674" size="165,5" backgroundColor="#00389416" zPosition="1" />
                <eLabel position="1068,674" size="165,5" backgroundColor="#000080ff" zPosition="1" />
                <widget source="key_red" render="Label" position="10,646" size="165,30" zPosition="2" font="Regular;24" halign="center" valign="center" backgroundColor="#16000000" foregroundColor="#00ffffff" transparent="1" />
                <widget source="key_green" render="Label" position="238,646" size="165,30" zPosition="2" font="Regular;24" halign="center" valign="center" backgroundColor="#16000000" foregroundColor="#00ffffff" transparent="1" />
                <widget source="key_blue" render="Label" position="1068,646" size="165,30" zPosition="2" font="Regular;24" halign="center" valign="center" backgroundColor="#16000000" foregroundColor="#00ffffff" transparent="1" />
                </screen>'''
        self.skin = scaleSkin(self.skin)
        Screen.__init__(self, session)
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.showStartStopText = showStartStopText
        if skin:
            self.skinName = [skin, 'Console']
        self.errorOcurred = False
        self['text'] = ScrollLabel('')
        self['key_red'] = StaticText(_('Cancel'))
        self['key_green'] = StaticText(_('Hide'))
        self['key_blue'] = StaticText(_('Restart GUI'))
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {
            'ok': self.cancel,
            'up': self['text'].pageUp,
            'down': self['text'].pageDown,
            'red': self.cancel,
            'green': self.toggleHideShow,
            'blue': self.restartenigma,
            'exit': self.cancel,
        }, -1)
        self.cmdlist = cmdlist if isinstance(cmdlist, list) else [cmdlist]
        self.newtitle = _('Console') if title == 'Console' else title
        self.cancel_msg = None
        self.onShown.append(self.updateTitle)
        self.container = eConsoleAppContainer()
        self.run = 0
        self.finished = False
        try:
            # DreamOS
            self.container.appClosed.append(self.runFinished)
            self.container.dataAvail.append(self.dataAvail)
        except AttributeError:
            self.container.appClosed_conn = self.container.appClosed.connect(self.runFinished)
            self.container.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)
        self.onLayoutFinish.append(self.startRun)

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        if self.showStartStopText:
            self['text'].setText(_('Execution progress:') + '\n\n')
        print('[Console] executing in run', self.run, ' the command:', self.cmdlist[self.run])
        if self.container.execute(self.cmdlist[self.run]):
            self.runFinished(-1)

    def runFinished(self, retval):
        if retval:
            self.errorOcurred = True
            self.show()
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):
                self.runFinished(-1)
            return
        self.show()
        self.finished = True
        if self.cancel_msg:
            self.cancel_msg.close()
        if self.showStartStopText:
            self['text'].appendText(_('Execution finished!!'))
        if self.finishedCallback is not None:
            self.finishedCallback()
        if not self.errorOcurred and self.closeOnSuccess:
            self.closeConsole()
        else:
            self['text'].appendText(_('\nPress OK or Exit to abort!'))
            self['key_red'].setText(_('Exit'))
            self['key_green'].setText('')

    def toggleHideShow(self):
        if self.finished:
            return
        if self.shown:
            self.hide()
        else:
            self.show()

    def cancel(self):
        if self.finished:
            self.closeConsole()
        else:
            self.cancel_msg = self.session.openWithCallback(self.cancelCallback, MessageBox, _('Cancel execution?'), type=MessageBox.TYPE_YESNO, default=False)

    def disconnect(self):
        try:
            # DreamOS
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)
        except AttributeError:
            self.container.appClosed_conn = None
            self.container.dataAvail_conn = None

    def cancelCallback(self, ret=None):
        self.cancel_msg = None
        if ret:
            self.disconnect()
            self.container.kill()
            self.close()

    def closeConsole(self):
        if self.finished:
            self.disconnect()
            self.close()
        else:
            self.show()

    def dataAvail(self, data):
        # a UTF-8 character may be split between two chunks
        self['text'].appendText(data.decode('utf-8', 'ignore') if PY3 else data)

    def restartenigma(self):
        from Screens.Standby import TryQuitMainloop
        self.session.open(TryQuitMainloop, 3)
