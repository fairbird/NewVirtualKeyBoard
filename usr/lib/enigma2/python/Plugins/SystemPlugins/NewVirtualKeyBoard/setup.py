#!/usr/bin/python
# -*- coding: utf-8 -*-

# Code mfaraj57 and RAED (Fairbird)

import os
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Input import Input
from Components.Pixmap import Pixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

from Plugins.SystemPlugins.NewVirtualKeyBoard.Console import Console
from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import *
VER = getversioninfo()

config.NewVirtualKeyBoard = ConfigSubsection()
config.NewVirtualKeyBoard.keys_layout = ConfigText(default='', fixed_size=False)
config.NewVirtualKeyBoard.lastsearchText = ConfigText(default='Enter search word', fixed_size=False)
config.NewVirtualKeyBoard.firsttime = ConfigYesNo(default=True)
config.NewVirtualKeyBoard.textinput = ConfigSelection(default='VirtualKeyBoard', choices=[('VirtualKeyBoard', _('Image virtual keyboard')), ('NewVirtualKeyBoard', _('New Virtual Keyboard'))])
config.NewVirtualKeyBoard.showinplugins = ConfigYesNo(default = True)
config.NewVirtualKeyBoard.showsuggestion = ConfigYesNo(default=True)
config.NewVirtualKeyBoard.fontssize = ConfigInteger(default = 0, limits = (0, 30))
config.NewVirtualKeyBoard.updateonline = ConfigYesNo(default=True)

try:
        FONTSSIZE = config.NewVirtualKeyBoard.fontssize.value
except:
        FONTSSIZE = 0

class nvKeyboardSetup(ConfigListScreen, Screen):

    def __init__(self, session, fromkeyboard=False):
        if not DreamOS():
        	if isFHD():
        		self.skin = """
				<screen name="nvKeyboardSetup" position="center,center" size="1080,400" backgroundColor="#16000000" title="New Virtual Keyboard Settings  V %s" flags="wfNoBorder">
    				<widget source="Title" render="Label" position="0,0" size="1076,50" itemHeight="40" font="Regular;35" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#16000000"/>
	
				<widget name="config" position="30,55" size="1020,298" itemHeight="45" font="Regular;30" secondfont="Regular;28" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />

				<ePixmap position="30,360" size="38,38" pixmap="~/images/key_red.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="78,360" zPosition="4" size="300,38" valign="center" font="Regular;30" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Cancel" />

				<ePixmap position="330,360" size="38,38" pixmap="~/images/key_green.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="378,360" zPosition="4" size="300,38" valign="center" font="Regular;30" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Save" />

				<ePixmap position="630,360" size="38,38" pixmap="~/images/key_yellow.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="678,360" zPosition="4" size="420,38" valign="center" font="Regular;30" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Virtual keyboard" />
				</screen>""" % VER
        	else:
        		self.skin = """
				<screen name="nvKeyboardSetup" position="center,center" size="720,280" backgroundColor="#16000000" title="New Virtual Keyboard Settings  V %s" flags="wfNoBorder">
    				<widget source="Title" render="Label" position="0,0" size="720,50" itemHeight="30" font="Regular;20" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#16000000"/>
	
				<widget name="config" position="20,60" size="680,182" itemHeight="30" font="Regular;20" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />

				<ePixmap position="20,250" size="25,25" pixmap="~/images/key_red_sd.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="52,250" zPosition="4" size="200,25" valign="center" font="Regular;20" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Cancel" />

				<ePixmap position="220,250" size="25,25" pixmap="~/images/key_green_sd.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="252,250" zPosition="4" size="200,25" valign="center" font="Regular;20" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Save" />

				<ePixmap position="420,250" size="25,25" pixmap="~/images/key_yellow_sd.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="452,250" zPosition="4" size="280,25" valign="center" font="Regular;20" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Virtual keyboard" />
				</screen>""" % VER
        else:
        	if isFHD():
        		self.skin = """
				<screen name="nvKeyboardSetup" position="center,center" size="1080,400" backgroundColor="#16000000" title="New Virtual Keyboard Settings  V %s" flags="wfNoBorder">
    				<widget source="Title" render="Label" position="0,0" size="1076,50" font="Regular;35" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#16000000"/>
	
				<widget name="config" position="30,55" size="1020,298" font="Regular;30" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />

				<ePixmap position="30,360" size="38,38" pixmap="~/images/key_red.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="78,360" zPosition="4" size="300,38" valign="center" font="Regular;30" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Cancel" />

				<ePixmap position="330,360" size="38,38" pixmap="~/images/key_green.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="378,360" zPosition="4" size="300,38" valign="center" font="Regular;30" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Save" />

				<ePixmap position="630,360" size="38,38" pixmap="~/images/key_yellow.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="678,360" zPosition="4" size="420,38" valign="center" font="Regular;30" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Virtual keyboard" />
				</screen>""" % VER
        	else:
        		self.skin = """
				<screen name="nvKeyboardSetup" position="center,center" size="720,280" backgroundColor="#16000000" title="New Virtual Keyboard Settings  V %s" flags="wfNoBorder">
    				<widget source="Title" render="Label" position="0,0" size="720,50" font="Regular;20" halign="center" valign="center" foregroundColor="#00ffffff" backgroundColor="#16000000"/>
	
				<widget name="config" position="20,60" size="680,182" font="Regular;20" scrollbarMode="showOnDemand" transparent="1" zPosition="2" />

				<ePixmap position="20,250" size="25,25" pixmap="~/images/key_red_sd.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="52,250" zPosition="4" size="200,25" valign="center" font="Regular;20" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Cancel" />

				<ePixmap position="220,250" size="25,25" pixmap="~/images/key_green_sd.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="252,250" zPosition="4" size="200,25" valign="center" font="Regular;20" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Save" />

				<ePixmap position="420,250" size="25,25" pixmap="~/images/key_yellow_sd.png" zPosition="3" transparent="1" alphatest="blend" />
				<eLabel position="452,250" zPosition="4" size="280,25" valign="center" font="Regular;20" transparent="1" foregroundColor="#ffffff" backgroundColor="#41000000" text="Virtual keyboard" />
				</screen>""" % VER
        Screen.__init__(self, session)
        self.list = []
        py_link = ("/usr/lib/enigma2/python/Screens/VirtualKeyBoard.py")
        if not os.path.islink(py_link):
            config.NewVirtualKeyBoard.textinput.value = "VirtualKeyBoard"
            config.NewVirtualKeyBoard.textinput.save()
        else:
            config.NewVirtualKeyBoard.textinput.value = "NewVirtualKeyBoard"
            config.NewVirtualKeyBoard.textinput.save()
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard")
        self.fromkeyboard = fromkeyboard
        self['config'] = MenuList([])
        ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {
            'green': self.keySave,
            'yellow': self.showNewkeyboard,
            'cancel': self.keyClose
            #"left": self.keyLeft,
            #"right": self.keyRight
        }, -2)
        self.fontssize = config.NewVirtualKeyBoard.fontssize.value
        self.currKeyoboard = config.NewVirtualKeyBoard.textinput.value
        self.showKeyoboard = config.NewVirtualKeyBoard.showsuggestion.value
        self.createConfigList()

    def changedEntry(self):
        cur = self['config'].list[0]
        curval = cur[1].value
        print("curval", curval)
        if 'NewVirtualKeyBoard' == curval:
            self.createConfigList(True)
        else:
            self.createConfigList(False)

    def createConfigList(self, value=False):
        if config.NewVirtualKeyBoard.updateonline.value:
                self.checkupdates()

        self.list = []
        self.list.append(getConfigListEntry(_('Text input method-keyboard:'), config.NewVirtualKeyBoard.textinput))
        self.list.append(getConfigListEntry(_('Increase and Decrease font size (from 01 to 30):'), config.NewVirtualKeyBoard.fontssize))
        if config.NewVirtualKeyBoard.textinput.value == 'NewVirtualKeyBoard' or value is True:
            self.list.append(getConfigListEntry(_('Show google and history suggestion:'), config.NewVirtualKeyBoard.showsuggestion))
        else:
            pass
        self.list.append(getConfigListEntry(_('Enable/Disable Checking Online Update:'), config.NewVirtualKeyBoard.updateonline))
        self.list.append(getConfigListEntry(_('Show plugin in Plugin Browser (Need restart E2):'), config.NewVirtualKeyBoard.showinplugins))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    def keySave(self):
        for x in self['config'].list:
            x[1].save()
        configfile.save()
        py_link = ("/usr/lib/enigma2/python/Screens/VirtualKeyBoard.py")
        pyc_link = ("/usr/lib/enigma2/python/Screens/VirtualKeyBoard.pyc")
        py_image = ("/usr/lib/enigma2/python/Screens/VirtualKeyBoard.py")
        py_backup = ("/usr/lib/enigma2/python/Screens/VirtualKeyBoard_backup.py")
        pyo_image = ("/usr/lib/enigma2/python/Screens/VirtualKeyBoard.pyo")
        pyc_image = ("/usr/lib/enigma2/python/Screens/VirtualKeyBoard.pyc")
        pyo_backup = ("/usr/lib/enigma2/python/Screens/VirtualKeyBoard_backup.pyo")
        pyc_backup = ("/usr/lib/enigma2/python/Screens/VirtualKeyBoard_backup.pyc")
        py_NewVirtualKeyBoard = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/VirtualKeyBoard.py")

        if not config.NewVirtualKeyBoard.textinput.value == self.currKeyoboard or config.NewVirtualKeyBoard.showsuggestion.value == self.showKeyoboard or not config.NewVirtualKeyBoard.fontssize.value == self.fontssize:
            if config.NewVirtualKeyBoard.textinput.value == "NewVirtualKeyBoard":
                #if os.path.exists(pyc_link):
                #    os.remove(pyc_link)
                if not os.path.islink(py_link):
                    if os.path.exists(py_image):
                        os.rename(py_image, py_backup)
                        if os.path.exists(pyo_image):
                            os.remove(pyo_image)
                        elif os.path.exists(pyc_image):
                            os.remove(pyc_image)
                    elif os.path.exists(pyo_image):
                        os.rename(pyo_image, pyo_backup)
                    elif os.path.exists(pyc_image):
                        os.rename(pyc_image, pyc_backup)
                    os.symlink(py_NewVirtualKeyBoard, py_link)

            elif config.NewVirtualKeyBoard.textinput.value == "VirtualKeyBoard":
                if os.path.islink(py_link):
                    if os.path.exists(py_backup):
                        os.remove(py_link)
                        os.rename(py_backup, py_image)
                    elif os.path.exists(pyo_backup):
                        os.remove(py_link)
                        os.rename(pyo_backup, pyo_image)
                    elif os.path.exists(pyc_backup):
                        os.remove(py_link)
                        os.rename(pyc_backup, pyc_image)
                else:
                    pass

            self.session.openWithCallback(self.restartenigma, MessageBox, _('Restart enigma2 to load new settings?'), MessageBox.TYPE_YESNO)
        else:
            self.close(True)

    def showNewkeyboard(self):
        if self.fromkeyboard:
            self.close()
        else:
            try:
                from Plugins.SystemPlugins.NewVirtualKeyBoard.VirtualKeyBoard import VirtualKeyBoard
                self.session.open(VirtualKeyBoard)
            except Exception as e:
                print(e)

    def restartenigma(self, result):
        if result:
            from Screens.Standby import TryQuitMainloop
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close(True)

    def keyClose(self):
        for x in self['config'].list:
            x[1].cancel()
        self.close()

    def checkupdates(self):
        try:
                from twisted.web.client import getPage, error
                #url = b"http://tunisia-dreambox.info/TSplugins/NewVirtualKeyBoard/installer.sh"
                url = b"https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/installer.sh"
                getPage(url,timeout=10).addCallback(self.parseData).addErrback(self.errBack)
        except Exception as error:
                trace_error()

    def errBack(self,error=None):
        logdata("errBack-error",error)

    def parseData(self, data):
        if PY3:
                data = data.decode("utf-8")
        else:
                data = data.encode("utf-8")
        if data:
                lines = data.split("\n")
                for line in lines:
                       if line.startswith("version"):
                          self.new_version = line.split("=")[1]
                          break
        if float(VER) == float(self.new_version) or float(VER)>float(self.new_version):
                logdata("Updates","No new version available")
        else :
                new_version = self.new_version
                self.session.openWithCallback(self.install, MessageBox, _('New version %s is available.\n\nDo want ot install now.' % new_version), MessageBox.TYPE_YESNO)

    def install(self,answer=False):
        try:
                if answer:
                        cmdlist = []
                        #cmd="wget http://tunisia-dreambox.info/TSplugins/NewVirtualKeyBoard/installer.sh -O - | /bin/sh"
                        cmd="wget https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/installer.sh -O - | /bin/sh"
                        cmdlist.append(cmd)
                        self.session.open(Console, title='Installing last update, enigma will be started after install', cmdlist=cmdlist, finishedCallback=self.myCallback, closeOnSuccess=False)
        except:
                trace_error()
        
    def myCallback(self,result):
        return
