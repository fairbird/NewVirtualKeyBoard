#!/usr/bin/python
# -*- coding: utf-8 -*-
# Centralized language configuration for NewVirtualKeyBoard

import os
from Components.config import ConfigSelection, ConfigSubsection, configfile

# Define supported languages and their display names
LANGUAGES = {
    "EN": "English",
    "AR": "عربي",
    "EL": "Ελληνικά",
    "DE": "Deutsch",
    "CN": "中國人",
    "IT": "Italiano",
    "FR": "française",
    "HU": "magyar",
    "CS": "čeština",
    "RU": "Россия",
    "SK": "slovenčina",
}

def get_language_choices():
    """Return list of tuples for ConfigSelection: [(code, name), ...]"""
    return [(code, name) for code, name in LANGUAGES.items()]

def import_language(lang_code):
    """Import the language module based on lang_code, default to EN"""
    try:
        if lang_code in LANGUAGES:
            module = __import__("Plugins.SystemPlugins.NewVirtualKeyBoard.language." + lang_code.lower(), fromlist=['*'])
            print("Imported %s.py" % lang_code.lower())
            return module
        else:
            print("Language %s not found, defaulting to en.py" % lang_code)
            return __import__("Plugins.SystemPlugins.NewVirtualKeyBoard.language.en", fromlist=['*'])
    except ImportError as e:
        print("Error importing language %s: %s, defaulting to en.py" % (lang_code, str(e)))
        return __import__("Plugins.SystemPlugins.NewVirtualKeyBoard.language.en", fromlist=['*'])

def initialize_config(config):
    """Initialize and save config.NewVirtualKeyBoard.lang if not set"""
    if not hasattr(config, 'NewVirtualKeyBoard'):
        config.NewVirtualKeyBoard = ConfigSubsection()
    if not hasattr(config.NewVirtualKeyBoard, 'lang'):
        config.NewVirtualKeyBoard.lang = ConfigSelection(default="EN", choices=get_language_choices())
        config.NewVirtualKeyBoard.lang.save()
        configfile.save()
