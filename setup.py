#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

PLUGIN_DIR = 'SystemPlugins.NewVirtualKeyBoard'

setup(name='enigma2-plugin-systemplugins-NewVirtualKeyBoard',
       version='1.0',
       author='RAED',
       author_email='rrrr53@hotmail.com',
       description='plugin by (mfaraj57 & RAED) to New VirtualKeyBoard Based on E2iplayer VirtualKeyBoard (Thanks SSS)',
       packages=[PLUGIN_DIR],
       package_dir={PLUGIN_DIR: 'usr'},
       package_data={PLUGIN_DIR: ['plugin.png', '*/*.png']},
      )
