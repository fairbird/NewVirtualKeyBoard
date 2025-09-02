#!/usr/bin/python
# -*- coding: utf-8 -*-

from Plugins.Plugin import PluginDescriptor
from Components.config import config

from Plugins.SystemPlugins.NewVirtualKeyBoard.setup import *
from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import *
from Plugins.SystemPlugins.NewVirtualKeyBoard.language_config import initialize_config

# Initialize and save configuration
initialize_config(config)
configfile.save()

def main(session, **kwargs):
	from .setup import nvKeyboardSetup
	session.open(nvKeyboardSetup)


def menu(menuid, **kwargs):
	if menuid == 'system':
		return [(_('VirtualKeyBoard setup'), main, 'virtulkeyBoard_setup', None)]
	else:
		return []

if isFHD():
	ICONFILE = 'images/plugin-icon.png'
else:
	ICONFILE = 'images/plugin-icon_sd.png'
	
DES = (_('Setup virtual keyboard'))
PNAME = (_('VirtualKeyboard'))
pluginlist = PluginDescriptor(name=PNAME, description=DES, where=PluginDescriptor.WHERE_PLUGINMENU, icon=ICONFILE, fnc=main, needsRestart=False)

def Plugins(**kwargs):
	result = [
		PluginDescriptor(
			name=PNAME,
			description = DES,
			where = PluginDescriptor.WHERE_MENU,
			fnc = menu,
			needsRestart=False
		),
	]
	if config.NewVirtualKeyBoard.showinplugins.value:
		result.append(pluginlist)
	return result
