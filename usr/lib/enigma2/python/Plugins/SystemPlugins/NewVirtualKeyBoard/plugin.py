#!/usr/bin/python
# -*- coding: utf-8 -*-

from Plugins.Plugin import PluginDescriptor
from Components.config import config

from Plugins.SystemPlugins.NewVirtualKeyBoard import _
from Plugins.SystemPlugins.NewVirtualKeyBoard.setup import nvKeyboardSetup  # also defines config.NewVirtualKeyBoard
from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import isFHD


def main(session, **kwargs):
    session.open(nvKeyboardSetup)


def menu(menuid, **kwargs):
    if menuid == 'system':
        return [(_('NewVirtualKeyBoard setup'), main, 'virtulkeyBoard_setup', None)]
    return []


def Plugins(**kwargs):
    # the plugin's name, not translated (was "VirtualKeyboard", like the
    # image's own keyboard)
    name = 'NewVirtualKeyBoard'
    description = _('Setup virtual keyboard')
    result = [PluginDescriptor(name=name, description=description, where=PluginDescriptor.WHERE_MENU, fnc=menu, needsRestart=False)]
    if config.NewVirtualKeyBoard.showinplugins.value:
        icon = 'images/plugin-icon.png' if isFHD() else 'images/plugin-icon_sd.png'
        result.append(PluginDescriptor(name=name, description=description, where=PluginDescriptor.WHERE_PLUGINMENU, icon=icon, fnc=main, needsRestart=False))
    return result
