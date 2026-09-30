#!/usr/bin/python
# -*- coding: utf-8 -*-

# Keyboard layouts: the key grid, the layout list, the built-in layout,
# reading/downloading .kle files and the flag of a layout.
#
# .kle file: a Python dict literal (UTF-16 with BOM, or UTF-8) with
#   'id'       Windows KLID, e.g. '00000407'
#   'name', 'desc', 'locale' ('de-DE')
#   'layout'   {keyId: {shiftState: text}} - keyId as in KEY_GRID
#   'deadkeys' {deadChar: {baseChar: composed}}
# The files are generated from the Windows layouts (kbdlayout.info) and
# mapped by physical key, so every layout looks like its real keyboard.

import os
import re

from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import pluginPath, byTier, urlread

LAYOUT_DIR = pluginPath('skins', 'kle') + '/'
SERVER_URL = 'https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/kle/'

# ---- key ids -------------------------------------------------------------
KEY_TEXT = 0        # the input field
KEY_ESC = 1
KEY_BACKSPACE = 15
KEY_CLEAR = 16
KEY_DELETE = 29
KEY_CAPS = 30
KEY_ENTER = 42
KEY_SHIFT_L = 43
KEY_SHIFT_R = 55
KEY_LANGUAGE = 56
KEY_CTRL = 57
KEY_ALT = 58
KEY_SPACE = 59
KEY_ALTGR = 60
KEY_LEFT = 61
KEY_RIGHT = 62
KEY_ISO = 63        # key next to Enter (German #')

# on-screen grid, 15 columns; a key spanning several columns repeats its id
# (ISO layout: 48 character keys - 44 is the <> key, 63 the one next to Enter)
KEY_GRID = [
    (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15),
    (16, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29),
    (30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 63, 42, 42),
    (43, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 55),
    (56, 56, 57, 58, 59, 59, 59, 59, 59, 59, 59, 59, 60, 61, 62),
]
KEY_ROWS = len(KEY_GRID)
KEY_COLUMNS = len(KEY_GRID[0])
# keys at the left/right edge: LEFT/RIGHT there moves to the side panels
LEFT_KEYS = [row[0] for row in KEY_GRID[1:]]
RIGHT_KEYS = [row[-1] for row in KEY_GRID[1:]]
# keys that type characters (labelled from the layout)
CHARACTER_KEYS = list(range(2, 15)) + list(range(17, 29)) + list(range(31, 42)) + [KEY_ISO] + list(range(44, 55)) + [KEY_SPACE]

# shift states of a key in a .kle file (bit flags)
SK_NONE = 0
SK_SHIFT = 1
SK_CTRL = 2
SK_ALT = 4          # SK_CTRL | SK_ALT = AltGr
SK_CAPSLOCK = 8


def keySpan(keyId):
    # (row, first column, number of columns) of a key in KEY_GRID
    for rowIdx, row in enumerate(KEY_GRID):
        if keyId in row:
            first = row.index(keyId)
            return rowIdx, first, row.count(keyId)
    return None


# ---- layout files ------------------------------------------------------------

def layoutFile(layoutId):
    return LAYOUT_DIR + '%s.kle' % layoutId


def serverLayoutFile(layoutId):
    return SERVER_URL + 'kle%s.kle' % layoutId


def installedLayoutIds():
    # ids of the downloaded layouts, sorted
    try:
        return sorted(name[:-4] for name in os.listdir(LAYOUT_DIR) if name.endswith('.kle'))
    except OSError:
        return []


def readLayoutFile(layoutId):
    # the layout dict of an installed .kle; raises on a broken file
    import codecs
    from ast import literal_eval
    path = layoutFile(layoutId)
    try:
        with codecs.open(path, encoding='utf-16') as f:
            data = f.read()
    except UnicodeError:
        # UTF-8 file (Python 2 raises a plain UnicodeError for a missing BOM,
        # not UnicodeDecodeError)
        with codecs.open(path, encoding='utf-8') as f:
            data = f.read()
    layout = literal_eval(data)
    if layout.get('id') != layoutId:
        raise ValueError('Locale ID mismatched! %s <> %s' % (layout.get('id'), layoutId))
    return layout


def downloadLayout(layoutId):
    # fetches a layout from the server into LAYOUT_DIR (runs in the GUI
    # thread, so with a timeout)
    try:
        data, contentType = urlread(serverLayoutFile(layoutId), 10)
        # the package ships no layouts, so the folder may not exist yet
        if not os.path.isdir(LAYOUT_DIR):
            os.makedirs(LAYOUT_DIR)
        with open(layoutFile(layoutId), 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print('[NewVirtualKeyBoard] downloading layout %s failed: %s' % (layoutId, e))
        return False


def layoutItem(layoutId):
    # (name, locale, id) of a layout, None for an unknown id
    return LAYOUTS_BY_ID.get(layoutId)


def systemLayoutId(systemLocale):
    # layout for an enigma2 language like 'de_DE': the base layout of that
    # locale (0000xxxx - "US" for en_US, not "Colemak"), else any layout of the
    # locale, else any layout of the language
    special = {'pl_PL': '00000415', 'en_EN': '00020409'}
    if systemLocale in special:
        return special[systemLocale]
    candidates = [item[2] for item in KbLayouts if item[1] == systemLocale]
    if not candidates:
        prefix = systemLocale.split('_')[0] + '_'
        candidates = [item[2] for item in KbLayouts if item[1].startswith(prefix)]
    for layoutId in candidates:
        if layoutId.startswith('0000'):
            return layoutId
    return candidates[0] if candidates else defaultKBLAYOUT['id']


# ---- flags -------------------------------------------------------------------

_flagCache = {}


def flagFileForLocale(locale):
    # flag of a layout locale for the current desktop tier: exact, then
    # without the script part (sr_Cyrl-CS -> sr_CS), then the same country
    # (as_IN -> hi_IN), then the same language, else missing.png
    flagsDir = pluginPath('skins', byTier('flagshd', 'flagswqhd', 'flags')) + '/'
    key = (flagsDir, locale)
    if key not in _flagCache:
        _flagCache[key] = flagsDir + _flagName(flagsDir, locale)
    return _flagCache[key]


def _flagName(flagsDir, locale):
    try:
        names = set(os.listdir(flagsDir))
    except OSError:
        return 'missing.png'
    if locale + '.png' in names:
        return locale + '.png'
    parts = re.split('[_-]', locale)
    if len(parts) > 2 and '%s_%s.png' % (parts[0], parts[-1]) in names:
        return '%s_%s.png' % (parts[0], parts[-1])
    ordered = sorted(names)
    if len(parts) > 1:
        for name in ordered:
            if name.endswith('_%s.png' % parts[-1]):
                return name
    for name in ordered:
        if name.startswith(parts[0] + '_'):
            return name
    return 'missing.png'


def flagFileForLayout(layoutId):
    item = layoutItem(layoutId)
    return flagFileForLocale(item[1] if item else 'missing')


# ---- data --------------------------------------------------------------------

# (name, locale, KLID) - every Windows keyboard layout (kbdlayout.info)
KbLayouts = [
    ('ADLaM', 'ff_Adlm-GN', '00140c00'),
    ('Albanian', 'sq_AL', '0000041c'),
    ('Arabic (101)', 'ar_SA', '00000401'),
    ('Arabic (101, Legacy)', 'ar_SA', '00030401'),
    ('Arabic (102)', 'ar_SA', '00010401'),
    ('Arabic (102) AZERTY', 'ar_SA', '00020401'),
    ('Armenian Eastern (Legacy)', 'hy_AM', '0000042b'),
    ('Armenian Phonetic', 'hy_AM', '0002042b'),
    ('Armenian Typewriter', 'hy_AM', '0003042b'),
    ('Armenian Western (Legacy)', 'hy_AM', '0001042b'),
    ('Assamese - INSCRIPT', 'as_IN', '0000044d'),
    ('Azerbaijani (Standard)', 'az_Latn-AZ', '0001042c'),
    ('Azerbaijani Cyrillic', 'az_Cyrl-AZ', '0000082c'),
    ('Azerbaijani Latin', 'az_Latn-AZ', '0000042c'),
    ('Bangla', 'bn_IN', '00000445'),
    ('Bangla - INSCRIPT', 'bn_IN', '00020445'),
    ('Bangla - INSCRIPT (Legacy)', 'bn_IN', '00010445'),
    ('Bashkir', 'ba_RU', '0000046d'),
    ('Belarusian', 'be_BY', '00000423'),
    ('Belgian (Comma)', 'fr_BE', '0001080c'),
    ('Belgian (Period)', 'nl_BE', '00000813'),
    ('Belgian French', 'fr_BE', '0000080c'),
    ('Bosnian (Cyrillic)', 'bs_Cyrl-BA', '0000201a'),
    ('Buginese', 'bug_Bugi-ID', '000b0c00'),
    ('Bulgarian', 'bg_BG', '00030402'),
    ('Bulgarian (Latin)', 'bg_BG', '00010402'),
    ('Bulgarian (Phonetic Traditional)', 'bg_BG', '00040402'),
    ('Bulgarian (Phonetic)', 'bg_BG', '00020402'),
    ('Bulgarian (Typewriter)', 'bg_BG', '00000402'),
    ('Canadian French', 'en_CA', '00001009'),
    ('Canadian French (Legacy)', 'fr_CA', '00000c0c'),
    ('Canadian Multilingual Standard', 'en_CA', '00011009'),
    ('Central Atlas Tamazight', 'tzm_Latn-DZ', '0000085f'),
    ('Central Kurdish', 'ku_Arab-IQ', '00000492'),
    ('Cherokee Nation', 'chr_Cher-US', '0000045c'),
    ('Cherokee Phonetic', 'chr_Cher-US', '0001045c'),
    ('Chinese (Simplified) - US', 'zh_CN', '00000804'),
    ('Chinese (Simplified, Singapore) - US', 'zh_SG', '00001004'),
    ('Chinese (Traditional) - US', 'zh_TW', '00000404'),
    ('Chinese (Traditional, Hong Kong S.A.R.) - US', 'zh_HK', '00000c04'),
    ('Chinese (Traditional, Macao S.A.R.) - US', 'zh_MO', '00001404'),
    ('Colemak', 'en_US', '00060409'),
    ('Czech', 'cs_CZ', '00000405'),
    ('Czech (QWERTY)', 'cs_CZ', '00010405'),
    ('Czech Programmers', 'cs_CZ', '00020405'),
    ('Danish', 'da_DK', '00000406'),
    ('Devanagari - INSCRIPT', 'hi_IN', '00000439'),
    ('Divehi Phonetic', 'dv_MV', '00000465'),
    ('Divehi Typewriter', 'dv_MV', '00010465'),
    ('Dutch', 'nl_NL', '00000413'),
    ('Dzongkha', 'dz_BT', '00000c51'),
    ('English (India)', 'en_IN', '00004009'),
    ('Estonian', 'et_EE', '00000425'),
    ('Faeroese', 'fo_FO', '00000438'),
    ('Finnish', 'fi_FI', '0000040b'),
    ('Finnish with Sami', 'se_SE', '0001083b'),
    ('French (Legacy, AZERTY)', 'fr_FR', '0000040c'),
    ('French (Standard, AZERTY)', 'fr_FR', '0001040c'),
    ('French (Standard, BÉPO)', 'fr_FR', '0002040c'),
    ('Futhark', 'gem_Runr', '00120c00'),
    ('Georgian (Ergonomic)', 'ka_GE', '00020437'),
    ('Georgian (Legacy)', 'ka_GE', '00000437'),
    ('Georgian (MES)', 'ka_GE', '00030437'),
    ('Georgian (Old Alphabets)', 'ka_GE', '00040437'),
    ('Georgian (QWERTY)', 'ka_GE', '00010437'),
    ('German', 'de_DE', '00000407'),
    ('German (IBM)', 'de_DE', '00010407'),
    ('German Extended (E1)', 'de_DE', '00020407'),
    ('German Extended (E2)', 'de_DE', '00030407'),
    ('Gothic', 'got_Goth', '000c0c00'),
    ('Greek', 'el_GR', '00000408'),
    ('Greek (220)', 'el_GR', '00010408'),
    ('Greek (220) Latin', 'el_GR', '00030408'),
    ('Greek (319)', 'el_GR', '00020408'),
    ('Greek (319) Latin', 'el_GR', '00040408'),
    ('Greek Latin', 'el_GR', '00050408'),
    ('Greek Polytonic', 'el_GR', '00060408'),
    ('Greenlandic', 'kl_GL', '0000046f'),
    ('Guarani', 'gn_PY', '00000474'),
    ('Gujarati', 'gu_IN', '00000447'),
    ('Hausa', 'ha_Latn-NG', '00000468'),
    ('Hawaiian', 'haw_US', '00000475'),
    ('Hebrew', 'he_IL', '0000040d'),
    ('Hebrew (Standard)', 'he_IL', '0002040d'),
    ('Hebrew (Standard, 2018)', 'he_IL', '0003040d'),
    ('Hindi Traditional', 'hi_IN', '00010439'),
    ('Hungarian', 'hu_HU', '0000040e'),
    ('Hungarian 101-key', 'hu_HU', '0001040e'),
    ('Icelandic', 'is_IS', '0000040f'),
    ('Igbo', 'ig_NG', '00000470'),
    ('Inuktitut - Latin', 'iu_Latn-CA', '0000085d'),
    ('Inuktitut - Naqittaut', 'iu_Cans-CA', '0001045d'),
    ('Inuktitut - Nattilik', 'iu_Cans-CA', '0002045d'),
    ('Irish', 'en_IE', '00001809'),
    ('Italian', 'it_IT', '00000410'),
    ('Italian (142)', 'it_IT', '00010410'),
    ('Japanese', 'ja_JP', '00000411'),
    ('Javanese', 'jv_Java-ID', '00110c00'),
    ('Kannada', 'kn_IN', '0000044b'),
    ('Kazakh', 'kk_KZ', '0000043f'),
    ('Khmer', 'km_KH', '00000453'),
    ('Khmer (NIDA)', 'km_KH', '00010453'),
    ('Korean', 'ko_KR', '00000412'),
    ('Kyrgyz Cyrillic', 'ky_KG', '00000440'),
    ('Lao', 'lo_LA', '00000454'),
    ('Latin American', 'es_MX', '0000080a'),
    ('Latvian', 'lv_LV', '00000426'),
    ('Latvian (QWERTY)', 'lv_LV', '00010426'),
    ('Latvian (Standard)', 'lv_LV', '00020426'),
    ('Lisu (Basic)', 'lis_Lisu-CN', '00070c00'),
    ('Lisu (Standard)', 'lis_Lisu-CN', '00080c00'),
    ('Lithuanian', 'lt_LT', '00010427'),
    ('Lithuanian IBM', 'lt_LT', '00000427'),
    ('Lithuanian Standard', 'lt_LT', '00020427'),
    ('Luxembourgish', 'lb_LU', '0000046e'),
    ('Macedonian', 'mk_MK', '0000042f'),
    ('Macedonian - Standard', 'mk_MK', '0001042f'),
    ('Malayalam', 'ml_IN', '0000044c'),
    ('Maltese 47-Key', 'mt_MT', '0000043a'),
    ('Maltese 48-Key', 'mt_MT', '0001043a'),
    ('Maori', 'mi_NZ', '00000481'),
    ('Marathi', 'mr_IN', '0000044e'),
    ('Mongolian (Mongolian Script)', 'mn_Mong-CN', '00000850'),
    ('Mongolian Cyrillic', 'mn_MN', '00000450'),
    ('Myanmar (Phonetic order)', 'my_MM', '00010c00'),
    ('Myanmar (Visual order)', 'my_MM', '00130c00'),
    ('Nepali', 'ne_NP', '00000461'),
    ('New Tai Lue', 'khb_Talu-CN', '00020c00'),
    ('Norwegian', 'nb_NO', '00000414'),
    ('Norwegian with Sami', 'se_NO', '0000043b'),
    ('NZ Aotearoa', 'en_NZ', '00001409'),
    ('N’Ko', 'nqo_GN', '00090c00'),
    ('Odia', 'or_IN', '00000448'),
    ('Ogham', 'sga_Ogam-IE', '00040c00'),
    ('Ol Chiki', 'sat_Olck-IN', '000d0c00'),
    ('Old Italic', 'ett_Ital-IT', '000f0c00'),
    ('Osage', 'osa_Osge-US', '00150c00'),
    ('Osmanya', 'so_Osma-SO', '000e0c00'),
    ('Pashto (Afghanistan)', 'ps_AF', '00000463'),
    ('Persian', 'fa_IR', '00000429'),
    ('Persian (Standard)', 'fa_IR', '00050429'),
    ('Phags-pa', 'mn_Phag-CN', '000a0c00'),
    ('Polish (214)', 'pl_PL', '00010415'),
    ('Polish (Programmers)', 'pl_PL', '00000415'),
    ('Portuguese', 'pt_PT', '00000816'),
    ('Portuguese (Brazil ABNT)', 'pt_BR', '00000416'),
    ('Portuguese (Brazil ABNT2)', 'pt_BR', '00010416'),
    ('Punjabi', 'pa_IN', '00000446'),
    ('Romanian (Legacy)', 'ro_RO', '00000418'),
    ('Romanian (Programmers)', 'ro_RO', '00020418'),
    ('Romanian (Standard)', 'ro_RO', '00010418'),
    ('Russian', 'ru_RU', '00000419'),
    ('Russian (Typewriter)', 'ru_RU', '00010419'),
    ('Russian - Mnemonic', 'ru_RU', '00020419'),
    ('Sakha', 'sah_RU', '00000485'),
    ('Sami Extended Finland-Sweden', 'se_SE', '0002083b'),
    ('Sami Extended Norway', 'se_NO', '0001043b'),
    ('Scottish Gaelic', 'en_IE', '00011809'),
    ('Serbian (Cyrillic)', 'sr_Cyrl-CS', '00000c1a'),
    ('Serbian (Latin)', 'sr_Latn-CS', '0000081a'),
    ('Sesotho sa Leboa', 'nso_ZA', '0000046c'),
    ('Setswana', 'tn_ZA', '00000432'),
    ('Sinhala', 'si_LK', '0000045b'),
    ('Sinhala - Wij 9', 'si_LK', '0001045b'),
    ('Slovak', 'sk_SK', '0000041b'),
    ('Slovak (QWERTY)', 'sk_SK', '0001041b'),
    ('Slovenian', 'sl_SI', '00000424'),
    ('Sora', 'srb_Sora-IN', '00100c00'),
    ('Sorbian Extended', 'hsb_DE', '0001042e'),
    ('Sorbian Standard', 'hsb_DE', '0002042e'),
    ('Sorbian Standard (Legacy)', 'hsb_DE', '0000042e'),
    ('Spanish', 'es_ES', '0000040a'),
    ('Spanish Variation', 'es_ES', '0001040a'),
    ('Standard', 'hr_HR', '0000041a'),
    ('Swedish', 'sv_SE', '0000041d'),
    ('Swedish with Sami', 'se_SE', '0000083b'),
    ('Swiss French', 'fr_CH', '0000100c'),
    ('Swiss German', 'de_CH', '00000807'),
    ('Syriac', 'syr_SY', '0000045a'),
    ('Syriac Phonetic', 'syr_SY', '0001045a'),
    ('Tai Le', 'tdd_Tale-CN', '00030c00'),
    ('Tajik', 'tg_Cyrl-TJ', '00000428'),
    ('Tamil', 'ta_IN', '00000449'),
    ('Tamil 99', 'ta_IN', '00020449'),
    ('Tamil Anjal', 'ta_IN', '00030449'),
    ('Tatar', 'tt_RU', '00010444'),
    ('Tatar (Legacy)', 'tt_RU', '00000444'),
    ('Telugu', 'te_IN', '0000044a'),
    ('Thai Kedmanee', 'th_TH', '0000041e'),
    ('Thai Kedmanee (non-ShiftLock)', 'th_TH', '0002041e'),
    ('Thai Pattachote', 'th_TH', '0001041e'),
    ('Thai Pattachote (non-ShiftLock)', 'th_TH', '0003041e'),
    ('Tibetan (PRC)', 'bo_CN', '00000451'),
    ('Tibetan (PRC) - Updated', 'bo_CN', '00010451'),
    ('Tifinagh (Basic)', 'tzm_Tfng-MA', '0000105f'),
    ('Tifinagh (Extended)', 'tzm_Tfng-MA', '0001105f'),
    ('Traditional Mongolian (MNS)', 'mn_Mong-CN', '00020850'),
    ('Traditional Mongolian (Standard)', 'mn_Mong-CN', '00010850'),
    ('Turkish F', 'tr_TR', '0001041f'),
    ('Turkish Q', 'tr_TR', '0000041f'),
    ('Turkmen', 'tk_TM', '00000442'),
    ('Ukrainian', 'uk_UA', '00000422'),
    ('Ukrainian (Enhanced)', 'uk_UA', '00020422'),
    ('United Kingdom', 'en_GB', '00000809'),
    ('United Kingdom Extended', 'cy_GB', '00000452'),
    ('United States-Dvorak', 'en_US', '00010409'),
    ('United States-Dvorak for left hand', 'en_US', '00030409'),
    ('United States-Dvorak for right hand', 'en_US', '00040409'),
    ('United States-International', 'en_US', '00020409'),
    ('Urdu', 'ur_PK', '00000420'),
    ('US', 'en_US', '00000409'),
    ('US English Table for IBM Arabic 238_L', 'en_US', '00050409'),
    ('Uyghur', 'ug_CN', '00010480'),
    ('Uyghur (Legacy)', 'ug_CN', '00000480'),
    ('Uzbek Cyrillic', 'uz_Cyrl-UZ', '00000843'),
    ('Vietnamese', 'vi_VN', '0000042a'),
    ('Wolof', 'wo_SN', '00000488'),
    ('Yoruba', 'yo_NG', '0000046a'),
]
LAYOUTS_BY_ID = dict((item[2], item) for item in KbLayouts)

# built-in fallback layout (United Kingdom), same as kle/kle00000809.kle
defaultKBLAYOUT = {
    'id': u'00000809',
    'name': u'English (United Kingdom)',
    'desc': u'United Kingdom',
    'locale': u'en-GB',
    'layout': {
        2: {0: u'`', 1: u'\xac', 6: u'\xa6', 8: u'`', 9: u'\xac', 14: u'\xa6'},
        3: {0: u'1', 1: u'!', 8: u'1', 9: u'!'},
        4: {0: u'2', 1: u'"', 8: u'2', 9: u'"'},
        5: {0: u'3', 1: u'\xa3', 8: u'3', 9: u'\xa3'},
        6: {0: u'4', 1: u'$', 6: u'\u20ac', 8: u'4', 9: u'$', 14: u'\u20ac'},
        7: {0: u'5', 1: u'%', 8: u'5', 9: u'%'},
        8: {0: u'6', 1: u'^', 8: u'6', 9: u'^'},
        9: {0: u'7', 1: u'&', 8: u'7', 9: u'&'},
        10: {0: u'8', 1: u'*', 8: u'8', 9: u'*'},
        11: {0: u'9', 1: u'(', 8: u'9', 9: u'('},
        12: {0: u'0', 1: u')', 8: u'0', 9: u')'},
        13: {0: u'-', 1: u'_', 8: u'-', 9: u'_'},
        14: {0: u'=', 1: u'+', 8: u'=', 9: u'+'},
        17: {0: u'q', 1: u'Q', 8: u'Q', 9: u'q'},
        18: {0: u'w', 1: u'W', 8: u'W', 9: u'w'},
        19: {0: u'e', 1: u'E', 6: u'\xe9', 7: u'\xc9', 8: u'E', 9: u'e', 14: u'\xc9', 15: u'\xe9'},
        20: {0: u'r', 1: u'R', 8: u'R', 9: u'r'},
        21: {0: u't', 1: u'T', 8: u'T', 9: u't'},
        22: {0: u'y', 1: u'Y', 8: u'Y', 9: u'y'},
        23: {0: u'u', 1: u'U', 6: u'\xfa', 7: u'\xda', 8: u'U', 9: u'u', 14: u'\xda', 15: u'\xfa'},
        24: {0: u'i', 1: u'I', 6: u'\xed', 7: u'\xcd', 8: u'I', 9: u'i', 14: u'\xcd', 15: u'\xed'},
        25: {0: u'o', 1: u'O', 6: u'\xf3', 7: u'\xd3', 8: u'O', 9: u'o', 14: u'\xd3', 15: u'\xf3'},
        26: {0: u'p', 1: u'P', 8: u'P', 9: u'p'},
        27: {0: u'[', 1: u'{', 2: u'\x1b', 8: u'[', 9: u'{', 10: u'\x1b'},
        28: {0: u']', 1: u'}', 2: u'\x1d', 8: u']', 9: u'}', 10: u'\x1d'},
        31: {0: u'a', 1: u'A', 6: u'\xe1', 7: u'\xc1', 8: u'A', 9: u'a', 14: u'\xc1', 15: u'\xe1'},
        32: {0: u's', 1: u'S', 8: u'S', 9: u's'},
        33: {0: u'd', 1: u'D', 8: u'D', 9: u'd'},
        34: {0: u'f', 1: u'F', 8: u'F', 9: u'f'},
        35: {0: u'g', 1: u'G', 8: u'G', 9: u'g'},
        36: {0: u'h', 1: u'H', 8: u'H', 9: u'h'},
        37: {0: u'j', 1: u'J', 8: u'J', 9: u'j'},
        38: {0: u'k', 1: u'K', 8: u'K', 9: u'k'},
        39: {0: u'l', 1: u'L', 8: u'L', 9: u'l'},
        40: {0: u';', 1: u':', 8: u';', 9: u':'},
        41: {0: u"'", 1: u'@', 8: u"'", 9: u'@'},
        44: {0: u'\\', 1: u'|', 2: u'\x1c', 8: u'\\', 9: u'|', 10: u'\x1c'},
        45: {0: u'z', 1: u'Z', 8: u'Z', 9: u'z'},
        46: {0: u'x', 1: u'X', 8: u'X', 9: u'x'},
        47: {0: u'c', 1: u'C', 8: u'C', 9: u'c'},
        48: {0: u'v', 1: u'V', 8: u'V', 9: u'v'},
        49: {0: u'b', 1: u'B', 8: u'B', 9: u'b'},
        50: {0: u'n', 1: u'N', 8: u'N', 9: u'n'},
        51: {0: u'm', 1: u'M', 8: u'M', 9: u'm'},
        52: {0: u',', 1: u'<', 8: u',', 9: u'<'},
        53: {0: u'.', 1: u'>', 8: u'.', 9: u'>'},
        54: {0: u'/', 1: u'?', 8: u'/', 9: u'?'},
        59: {0: u' ', 1: u' ', 2: u' ', 8: u' ', 9: u' ', 10: u' '},
        63: {0: u'#', 1: u'~', 2: u'\x1c', 6: u'\\', 7: u'|', 8: u'#', 9: u'~', 10: u'\x1c', 14: u'\\', 15: u'|'},
    },
    'deadkeys': {
    },
}
