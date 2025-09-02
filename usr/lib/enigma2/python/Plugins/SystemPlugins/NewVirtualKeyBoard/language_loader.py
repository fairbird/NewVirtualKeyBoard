#!/usr/bin/python
# -*- coding: utf-8 -*-
# Code RAED (Fairbird)

from Components.config import config, ConfigSubsection, ConfigSelection

# Initialize config.NewVirtualKeyBoard if not already initialized
if not hasattr(config, 'NewVirtualKeyBoard'):
    print("[language_loader] Initializing config.NewVirtualKeyBoard")
    config.NewVirtualKeyBoard = ConfigSubsection()
    config.NewVirtualKeyBoard.lang = ConfigSelection(default="EN", choices=[
        ("EN", "English"),
        ("AR", "عربي"),
        ("EL", "Ελληνικά"),
        ("DE", "Deutsch"),
        ("CN", "中國人"),
        ("FR", "française")
    ])

# Import language modules
try:
    from Plugins.SystemPlugins.NewVirtualKeyBoard.language import en, ar, el, de, zh, fr
except ImportError as e:
    print("[language_loader] Error importing language modules:", e)
    from Plugins.SystemPlugins.NewVirtualKeyBoard.language import en  # Fallback to English

def load_language():
    """
    Load the appropriate language module based on config.NewVirtualKeyBoard.lang.value
    and return its module object.
    """
    try:
        if not hasattr(config.NewVirtualKeyBoard, 'lang'):
            print("[language_loader] config.NewVirtualKeyBoard.lang not found, falling back to English")
            return en
        lang = config.NewVirtualKeyBoard.lang.value
        print("[language_loader] Selected language:", lang)
        if lang == "EN":
            return en
        elif lang == "AR":
            return ar
        elif lang == "EL":
            return el
        elif lang == "DE":
            return de
        elif lang == "CN":
            return zh
        elif lang == "FR":
            return fr
        else:
            print("[language_loader] Unknown language, falling back to English")
            return en
    except Exception as e:
        print("[language_loader] Error in load_language:", e)
        return en  # Fallback to English

# Load the language module and update globals
try:
    language_module = load_language()
    globals().update(vars(language_module))
except Exception as e:
    print("[language_loader] Error updating globals:", e)
    from Plugins.SystemPlugins.NewVirtualKeyBoard.language import en
    globals().update(vars(en))  # Fallback to English
