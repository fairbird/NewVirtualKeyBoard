# -*- coding: utf-8 -*-
# Logic test for NewVirtualKeyBoard with stubbed enigma2 modules - runs
# without a box, on Python 2.7 and 3 (no pytest needed).
# usage: python tests/test_keyboard.py [desktop width: 1280|1920|2560] [--net]
#   --net also queries the real suggestion endpoints
from __future__ import print_function
import ast
import io
import json
import os
import re
import shutil
import sys
import tempfile
import types
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True  # keep the plugin folder free of .pyc/__pycache__
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(REPO, 'usr', 'lib', 'enigma2', 'python', 'Plugins', 'SystemPlugins', 'NewVirtualKeyBoard')
KLE = os.path.join(REPO, 'kle')
WIDTH = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1920
NET = '--net' in sys.argv
PY3 = sys.version_info[0] == 3
FAILS = []


def check(name, cond, extra=''):
    print('%s %s %s' % ('OK  ' if cond else 'FAIL', name, extra))
    if not cond:
        FAILS.append(name)


def section(name):
    # requests queued by an earlier section are never run
    del QUEUE[:]
    print('---------- %s ----------' % name)


def native(text):
    # what enigma2 hands out on Python 2: UTF-8 byte strings
    return text if PY3 else text.encode('utf-8')


def readText(path):
    with io.open(path, encoding='utf-8') as f:
        return f.read()


def readKle(layoutId):
    with io.open(os.path.join(KLE, 'kle%s.kle' % layoutId), encoding='utf-16') as f:
        return ast.literal_eval(f.read())


# ==== stubbed enigma2 ============================================================

def mod(name, **attrs):
    m = types.ModuleType(name)
    m.__dict__.update(attrs)
    sys.modules[name] = m
    parent, dot, child = name.rpartition('.')
    if parent:
        if parent not in sys.modules:
            mod(parent)
        setattr(sys.modules[parent], child, m)
    return m


class Anything(object):
    def __init__(self, *a, **k):
        pass

    def __call__(self, *a, **k):
        return Anything()

    def __getattr__(self, name):
        return Anything()


class Size(object):
    def __init__(self, w, h):
        self.w, self.h = w, h

    def width(self):
        return self.w

    def height(self):
        return self.h


class Desktop(object):
    def size(self):
        return Size(WIDTH, WIDTH * 9 // 16)


class MultiContent(object):
    TYPE_PIXMAP_ALPHABLEND = 'PIX'
    TYPE_TEXT = 'TXT'

    def __init__(self, *a):
        pass

    def __getattr__(self, name):
        return Anything()


class Instance(object):
    # widget instance: remembers colour, alignment, pixmap file, visibility
    def __init__(self):
        self.color = None
        self.visible = True
        self.path = None

    def setForegroundColor(self, c):
        self.color = c

    def setPixmapFromFile(self, p):
        self.path = p

    def setPixmap(self, p):
        self.path = p

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def __getattr__(self, name):
        return Anything()


class Language(object):
    active = 'en_GB'

    def getActiveLanguage(self):
        return self.active

    def addCallback(self, fn):
        pass


LANGUAGE = Language()
mod('enigma', loadPNG=lambda p: ('png', p), ePoint=Anything, gRGB=lambda *a: a, eListboxPythonMultiContent=MultiContent,
    eListbox=Anything, gFont=lambda *a: a, RT_HALIGN_LEFT=0, RT_VALIGN_CENTER=0, RT_WRAP=0,
    getDesktop=lambda n: Desktop(), getPrevAsciiCode=lambda: 65, eTimer=Anything, eConsoleAppContainer=Anything)
mod('Components.ScrollLabel', ScrollLabel=Anything)
mod('Components.Sources.StaticText', StaticText=Anything)


class ConfigElement(object):
    def __init__(self, default=None, **k):
        self.value = default
        self.default = default
        self.saved = self.cancelled = 0

    def save(self):
        self.saved += 1

    def cancel(self):
        self.cancelled += 1


class ConfigSubsection(object):
    pass


class Config(object):
    pass


mod('Components.config', config=Config(), configfile=Anything(),
    ConfigSubsection=ConfigSubsection, ConfigText=ConfigElement, ConfigYesNo=ConfigElement,
    ConfigSelection=ConfigElement, ConfigInteger=ConfigElement, ConfigSelectionNumber=ConfigElement,
    ConfigNumber=type('ConfigNumber', (ConfigElement,), {}), ConfigNothing=ConfigElement, getConfigListEntry=lambda *a: a)


class Screen(dict):
    # like enigma2's Screen: a dict of widgets
    def __init__(self, session, *a, **k):
        self.session = session
        self.onLayoutFinish = []
        self.onShown = []
        self.onClose = []

    def setTitle(self, t):
        self.title = t

    def close(self, *a):
        self.closed = a
        for fn in list(self.onClose):
            fn()


class MessageBox(object):
    TYPE_YESNO = 0
    TYPE_INFO = 1
    TYPE_ERROR = 3


class Label(object):
    def __init__(self, text=''):
        self.text = text
        self.visible = True
        self.instance = Instance()

    def setText(self, t):
        self.text = t

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False


class Pixmap(object):
    def __init__(self):
        self.instance = Instance()
        self.visible = True

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False


class FakeList(object):
    def __init__(self):
        self.items = []
        self.visible = True
        self.sel = False
        self.current = None

    def setList(self, items):
        self.items = list(items)

    def getCurrent(self):
        return self.current

    def moveToIndex(self, i):
        pass

    def moveSelection(self, step):
        pass

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def setSelectionState(self, s):
        self.sel = s


class FakeInput(object):
    # enigma2's Input, enough to type into: the text is unicode inside,
    # getText() gives a native string, .text has a trailing space (cursor)
    def __init__(self, text=u''):
        self.Text = text
        self.currPos = len(text)
        self.instance = Instance()

    @property
    def text(self):
        return native(self.Text + u' ')

    def getText(self):
        return native(self.Text)

    def setText(self, text):
        self.Text = text if PY3 else text.decode('utf-8')
        self.currPos = 0

    def insertChar(self, ch, pos, owr, ins):
        self.Text = self.Text[:pos] + ch + self.Text[pos:]

    def innerright(self):
        if self.currPos < len(self.Text):
            self.currPos += 1

    def right(self):
        self.innerright()

    def left(self):
        if self.currPos > 0:
            self.currPos -= 1

    def deleteBackward(self):
        if self.currPos > 0:
            self.Text = self.Text[:self.currPos - 1] + self.Text[self.currPos:]
            self.currPos -= 1

    def delete(self):
        self.Text = self.Text[:self.currPos] + self.Text[self.currPos + 1:]

    def deleteAllChars(self):
        self.Text = u''
        self.currPos = 0

    def update(self):
        pass

    def timeout(self):
        pass


mod('Screens.Screen', Screen=Screen)
mod('Screens.MessageBox', MessageBox=MessageBox)
mod('Screens.Standby', TryQuitMainloop=Anything)
mod('Components.ActionMap', NumberActionMap=lambda contexts, actions, prio: actions, ActionMap=lambda contexts, actions, prio: actions)
mod('Components.GUIComponent', GUIComponent=type('GUIComponent', (object,), {'__init__': lambda self: None}))
mod('Components.Language', language=LANGUAGE)
mod('Components.MenuList', MenuList=Anything)
# like enigma2's: creates the "config" list widget, has its own keyOK
mod('Components.ConfigList', ConfigListScreen=type('ConfigListScreen', (object,), {'__init__': lambda self, *a, **k: self.__setitem__('config', Anything()), 'keyOK': lambda self: 'image keyOK'}))
mod('Components.MultiContent', MultiContentEntryText=lambda **k: ('T', k), MultiContentEntryPixmapAlphaBlend=lambda **k: ('B', k))
mod('Components.Label', Label=Label)
mod('Components.Input', Input=type('Input', (object,), {'TEXT': 0, 'PIN': 1, 'NUMBER': 2, '__init__': lambda self, *a, **k: None}))
mod('Components.Pixmap', Pixmap=Pixmap)
mod('Tools.LoadPixmap', LoadPixmap=lambda p, *a, **k: ('pix', p))
PLUGINS_ROOT = os.path.dirname(os.path.dirname(PLUGIN))
mod('Tools.Directories', SCOPE_PLUGINS=1,
    resolveFilename=lambda scope, path='': os.path.join(PLUGINS_ROOT, path.replace('/', os.sep)))
mod('Plugins.Plugin', PluginDescriptor=type('PluginDescriptor', (dict,), {'WHERE_MENU': 1, 'WHERE_PLUGINMENU': 2, '__init__': lambda self, **k: dict.__init__(self, k)}))
pkg = mod('Plugins.SystemPlugins.NewVirtualKeyBoard')
pkg.__path__ = [PLUGIN]
pkg.__file__ = os.path.join(PLUGIN, '__init__.py')
# the real package __init__ (gettext domain + _())
exec(compile(readText(pkg.__file__), pkg.__file__, 'exec'), pkg.__dict__)
sys.modules['Plugins'].__path__ = []
sys.modules['Plugins.SystemPlugins'].__path__ = []

# fake twisted threads: nothing runs until runQueue(), so the "typed while a
# request runs" and "answer after close" paths can be tested
QUEUE = []


class Failure(object):
    def __init__(self, e):
        self.e = e

    def getErrorMessage(self):
        return str(self.e)


class Deferred(object):
    def __init__(self, fn, args):
        self.fn, self.args, self.chain = fn, args, []
        QUEUE.append(self)

    def addCallbacks(self, cb, eb):
        self.chain.append((cb, eb))
        return self

    def addCallback(self, cb):
        return self.addCallbacks(cb, None)

    def addErrback(self, eb):
        return self.addCallbacks(None, eb)


def runQueue():
    while QUEUE:
        d = QUEUE.pop(0)
        try:
            result, failed = d.fn(*d.args), False
        except Exception as e:
            result, failed = Failure(e), True
        for cb, eb in d.chain:
            fn = eb if failed else cb
            if fn is None:
                continue
            try:
                result, failed = fn(result), False
            except Exception as e:
                result, failed = Failure(e), True


mod('twisted.internet.threads', deferToThread=lambda fn, *args: Deferred(fn, args))
try:
    import builtins
except ImportError:
    import __builtin__ as builtins
builtins._ = lambda s: s  # enigma2 installs gettext's _ globally

import Plugins.SystemPlugins.NewVirtualKeyBoard.setup as setupmod  # noqa: E402  (defines the config)
import Plugins.SystemPlugins.NewVirtualKeyBoard.VirtualKeyBoard as vk  # noqa: E402
from Plugins.SystemPlugins.NewVirtualKeyBoard import tools, layouts, suggestions, skin, numpad, plugin  # noqa: E402

cfg = sys.modules['Components.config'].config.NewVirtualKeyBoard
Input = sys.modules['Components.Input'].Input
ConfigNumber = sys.modules['Components.config'].ConfigNumber
print('--- desktop width', WIDTH, 'python', sys.version.split()[0])
TMP = tempfile.mkdtemp()


class Session(object):
    def __init__(self):
        self.opened = []
        self.current_dialog = {}

    def open(self, *a, **k):
        self.opened.append((a, k, None))
        return Anything()

    def openWithCallback(self, cb, *a, **k):
        self.opened.append((a, k, cb))
        return Anything()

    def last(self):
        return self.opened[-1]


def newKeyboard(**kwargs):
    # a keyboard as after its layout finished, with fake list/input widgets
    kb = vk.NewVirtualKeyBoard.__new__(vk.NewVirtualKeyBoard)
    kwargs.setdefault('title', 'Search')
    kwargs.setdefault('text', '')
    vk.NewVirtualKeyBoard.__init__(kb, session=Session(), **kwargs)
    kb['suggestionList'] = FakeList()
    kb['historyList'] = FakeList()
    kb['text'] = FakeInput()
    kb.move_KMarker = lambda *a: None
    kb.history = suggestions.SearchHistory(os.path.join(TMP, 'history'))
    return kb


# ==== tools ================================================================================
section('tools')
check('isFHD', tools.isFHD() == (WIDTH > 1280))
check('isWQHD', tools.isWQHD() == (WIDTH > 1920))
xml = '<screen position="center,476" size="1920,630"><widget position="450,21" size="68,68" font="Regular;36" itemHeight="45" secondfont="Regular;28" title="V 13.9"/></screen>'
out = tools.scaleSkin(xml)
if WIDTH == 2560:
    check('scaleSkin wqhd', out == '<screen position="center,635" size="2560,840"><widget position="600,28" size="91,91" font="Regular;48" itemHeight="60" secondfont="Regular;37" title="V 13.9"/></screen>', out)
else:
    check('scaleSkin no-op', out == xml)
check('versionTuple: 13.10 is newer than 13.9', tools.versionTuple('13.10') > tools.versionTuple('13.9') and tools.versionTuple('x') is None)
cfg.fontssize.value = -6
check('font offset -6', tools.offsetFont(36) == 30)
cfg.fontssize.value = -40
check('font clamps at 8', tools.offsetFont(36) == 8)
cfg.fontssize.value = 0

# ==== assets ================================================================================
section('assets')
artDir = tools.keyArtDir()
names = set(skin.keyArt(k) for k in [0] + skin.KEY_IDS) | set(skin.MARKERS) | set(n for n, k in skin.KEY_ICONS) | set(['key_info', 'key_menu'])
missingArt = [n for n in names if not os.path.exists(tools.iconPath(artDir, n))]
check('key art of every key exists (%s)' % artDir, not missingArt, missingArt)
for tier in ('nvk', 'nvk_hd', 'nvk_wqhd'):
    used = names | set(['vkey_text', 'vkey_double', 'vkey_double_sel', 'vkey_space', 'vkey_space_sel', 'vkey_backspace'])  # + numpad
    extra = sorted(set(f[:-4] for f in os.listdir(os.path.join(PLUGIN, 'skins', 'icons', tier))) - used)
    check('no unused key art in %s' % tier, not extra, extra)
for tier in ('hd', 'fhd', 'wqhd'):
    menuDir = os.path.join(PLUGIN, 'skins', 'icons', 'menus', tier)
    check('menu icons: green/grey dot (%s)' % tier, os.path.exists(os.path.join(menuDir, 'green18.png')) and os.path.exists(os.path.join(menuDir, 'grey18.png')))
for tierDir in ('flags', 'flagshd', 'flagswqhd'):
    check('%s has the same flag set as flagshd' % tierDir, set(os.listdir(os.path.join(PLUGIN, 'skins', tierDir))) == set(os.listdir(os.path.join(PLUGIN, 'skins', 'flagshd'))))
badPng = []
for root, dirs, files in os.walk(PLUGIN):
    for name in files:
        if name.endswith('.png'):
            with open(os.path.join(root, name), 'rb') as f:
                data = f.read()
            depth, colour = bytearray(data[24:26])
            # older loaders (VTi, Python 2 images) show nothing for grayscale
            # (+alpha) or palettes below 8 bit ("pixmap file not found"), and
            # pictures without alpha (RGB, palette without tRNS) invisible
            if depth != 8 or not (colour == 6 or (colour == 3 and b'tRNS' in data)):
                badPng.append('%s (%d bit, type %d)' % (os.path.relpath(os.path.join(root, name), PLUGIN), depth, colour))
check('every PNG is 8-bit RGBA or palette with transparency', not badPng, badPng[:5])
check('dropped files are gone', not [p for p in ('compat.py', 'skins/__init__.py', 'skins/NewVirtualKeyBoard.py', 'skins/icons/vk') if os.path.exists(os.path.join(PLUGIN, p))])

# ==== layouts ================================================================================
section('layouts')
check('all 218 Windows layouts', len(layouts.KbLayouts) == 218, len(layouts.KbLayouts))
check('layout ids unique', len(layouts.LAYOUTS_BY_ID) == len(layouts.KbLayouts))
check('every listed layout exists on the server', not [x for x in layouts.KbLayouts if not os.path.exists(os.path.join(KLE, 'kle%s.kle' % x[2]))])
check('vk keeps KbLayouts and hfile', vk.KbLayouts is layouts.KbLayouts and vk.hfile == '/etc/history')
check('every grid row has 15 columns', all(len(r) == layouts.KEY_COLUMNS for r in layouts.KEY_GRID))
check('grid has key 63 and caps is a single key', layouts.keySpan(63) == (3, 12, 1) and layouts.keySpan(layouts.KEY_CAPS)[2] == 1)
check('edge keys from the grid', layouts.LEFT_KEYS == [1, 16, 30, 43, 56] and layouts.RIGHT_KEYS == [15, 29, 42, 55, 62])
GRID_IDS = set(layouts.CHARACTER_KEYS)
badIds = [name for name in os.listdir(KLE) if not set(readKle(name[3:-4])['layout']) <= GRID_IDS]
check('every .kle uses only character key ids', not badIds, badIds[:5])
de = readKle('00000407')['layout']
check('German: QWERTZ, #\' next to Enter, <> left, CapsLock y/x', de[22][0] == u'z' and de[45][0] == u'y' and de[63][0] == u'#' and de[63][1] == u"'" and de[44][0] == u'<' and de[45][8] == u'Y' and de[46][8] == u'X', (de[22], de[45], de[63]))
fr = readKle('0000040c')['layout']
check('French: AZERTY', fr[17][0] == u'a' and fr[31][0] == u'q' and fr[45][0] == u'w')
check('built-in layout = United Kingdom .kle', layouts.defaultKBLAYOUT == readKle('00000809'))
check('system layout: en_US -> US (not Colemak)', layouts.systemLayoutId('en_US') == '00000409', layouts.systemLayoutId('en_US'))
check('system layout: de_DE German, pl_PL Polish (Programmers)', layouts.systemLayoutId('de_DE') == '00000407' and layouts.systemLayoutId('pl_PL') == '00000415')
check('system layout: unknown -> built-in', layouts.systemLayoutId('xx_XX') == layouts.defaultKBLAYOUT['id'])
check('system layout: language only (de_LU -> a German layout)', layouts.layoutItem(layouts.systemLayoutId('de_LU'))[1].startswith('de_'))
layouts.LAYOUT_DIR = os.path.join(TMP, 'kle') + os.sep
os.mkdir(layouts.LAYOUT_DIR)
with io.open(os.path.join(layouts.LAYOUT_DIR, '00000407.kle'), 'w', encoding='utf-8') as f:
    f.write(u"{'id': '00000407', 'layout': {}, 'deadkeys': {}, 'locale': 'de-DE'}")
check('readLayoutFile: UTF-8 file', layouts.readLayoutFile('00000407')['locale'] == 'de-DE')
shutil.copy(os.path.join(KLE, 'kle0000040c.kle'), os.path.join(layouts.LAYOUT_DIR, '0000040c.kle'))
check('readLayoutFile: UTF-16 file', layouts.readLayoutFile('0000040c')['id'] == '0000040c')
check('installed ids sorted', layouts.installedLayoutIds() == ['00000407', '0000040c'])
check('the package ships no layouts (an update brings no removed ones back)', not [n for n in os.listdir(os.path.join(PLUGIN, 'skins')) if n == 'kle'])
layoutDir, urlread = layouts.LAYOUT_DIR, layouts.urlread
layouts.LAYOUT_DIR = os.path.join(TMP, 'newkle') + os.sep
layouts.urlread = lambda url, timeout: (io.open(os.path.join(KLE, 'kle0000040c.kle'), 'rb').read(), 'text/plain')
check('download without the layout folder: created', layouts.downloadLayout('0000040c') and layouts.installedLayoutIds() == ['0000040c'])
layouts.LAYOUT_DIR, layouts.urlread = layoutDir, urlread

section('flags')
noFlag = [x for x in layouts.KbLayouts if layouts.flagFileForLayout(x[2]).endswith('missing.png') and x[2] not in ('00120c00', '000c0c00')]
check('every layout has a flag (Futhark and Gothic: no country)', not noFlag, noFlag[:5])
check('german flag', layouts.flagFileForLayout('00000407').endswith('de_DE.png'))
check('sr_Cyrl-CS -> sr_CS', os.path.basename(layouts.flagFileForLayout('00000c1a')) == 'sr_CS.png')
check('as_IN -> India via country', os.path.basename(layouts.flagFileForLayout('0000044d')) == 'hi_IN.png')

# ==== keyboard skin ===========================================================================
section('keyboard skin')
kb = newKeyboard()
root = ET.fromstring(kb.skin)
check('skin is valid XML, screen width == desktop', root.get('size').split(',')[0] == str(max(WIDTH, 1280)), root.get('size'))
widgets = [w.get('name') for w in root.findall('widget') if w.get('name')]
check('widget names unique', len(widgets) == len(set(widgets)), [n for n in widgets if widgets.count(n) > 1])
screenWidgets = set(k for k in kb.keys())
check('every screen widget is in the skin', screenWidgets <= set(widgets) | set(['actions']), sorted(screenWidgets - set(widgets)))
check('every skin widget is created by the screen', set(widgets) <= screenWidgets, sorted(set(widgets) - screenWidgets))
missingPix = [p.get('pixmap') for p in root.findall('ePixmap') if not os.path.exists(p.get('pixmap'))]
check('every ePixmap file exists', not missingPix, missingPix)
check('no vkey_country any more', 'vkey_country' not in kb.skin)


def rect(name):
    w = root.find(".//widget[@name='%s']" % name)
    return [int(v) for v in w.get('position').split(',') + w.get('size').split(',')]


expect = {1280: 45, 1920: 68, 2560: 91}[WIDTH]
check('key widget size', rect('1')[2:] == [expect, expect], rect('1'))
x30, y30, w30, h30 = rect('30')
check('caps single width, A right next to it', x30 + w30 == rect('31')[0])
check('space ends where AltGr starts', rect('59')[0] + rect('59')[2] == rect('60')[0])
check('language label on the right half, flag on the left', rect('_56')[0] == rect('56')[0] + rect('56')[3] and rect('flag')[0] < rect('_56')[0])
try:
    from PIL import Image
except ImportError:  # the portable py2.7 has no Pillow
    Image = None
if Image:
    for keyId in (0, 1, 16, 59):
        art = Image.open(tools.iconPath(artDir, skin.keyArt(keyId))).size
        check('art size == widget size (%s)' % skin.keyArt(keyId), list(art) == rect(str(keyId))[2:], (art, rect(str(keyId))))
    for name in skin.MARKERS:
        art = Image.open(tools.iconPath(artDir, name)).size
        check('marker size == art (%s)' % name, list(art) == rect(name)[2:], (art, rect(name)))
    check('flag size == flag widget', list(Image.open(layouts.flagFileForLayout('00000407')).size) == rect('flag')[2:])
cfg.textalign.value = 'left'
cfg.bgcolor.value = 'black'
kb3 = newKeyboard()
check('text field left aligned', 'halign="left"' in re.search(r'<widget name="text"[^>]*>', kb3.skin).group(0))
check('background black', 'backgroundColor="#00000000" flags' in kb3.skin)
cfg.textalign.value = 'right'
cfg.bgcolor.value = 'default'
check('default: right aligned, #34000000', 'halign="right"' in re.search(r'<widget name="text"[^>]*>', kb.skin).group(0) and 'backgroundColor="#34000000" flags' in kb.skin)
check('credits text escaped', '&amp;' in skin.keyboardSkin('fhd', (1, 2, 3, 4, 5), 'a & "b"') and '&quot;b&quot;' in skin.keyboardSkin('fhd', (1, 2, 3, 4, 5), 'a & "b"'))

# ==== typing ================================================================================
section('typing')
kb = newKeyboard()
kb.loadVKLayout(layouts.defaultKBLAYOUT)
for keyId in (36, 24):
    kb.processKeyId(keyId)
check('UK: h i', kb['text'].Text == u'hi', kb['text'].Text)
kb.processKeyId(layouts.KEY_SHIFT_L)
check('Shift on: label green, keys show capitals', kb['_43'].instance.color == vk.COLOR_ACTIVE and kb['_36'].text == native(u'H'))
kb.processKeyId(36)
kb.processKeyId(36)
check('Shift types one capital, then releases', kb['text'].Text == u'hiHh' and kb['_43'].instance.color == vk.COLOR_TEXT)
kb.processKeyId(layouts.KEY_CAPS)
kb.processKeyId(17)
kb.processKeyId(17)
check('Caps Lock stays on', kb['text'].Text == u'hiHhQQ')
kb.processKeyId(layouts.KEY_CAPS)
kb.processKeyId(layouts.KEY_ALTGR)
kb.processKeyId(19)
check('AltGr: e -> \xe9 (and releases)', kb['text'].Text == u'hiHhQQ\xe9' and not kb.specialKeyState, repr(kb['text'].Text))
kb.processKeyId(layouts.KEY_ALT)
kb.processKeyId(19)
check('Alt alone types like AltGr', kb['text'].Text.endswith(u'\xe9\xe9'))
kb.processKeyId(layouts.KEY_BACKSPACE)
kb.processKeyId(layouts.KEY_LEFT)
kb.processKeyId(layouts.KEY_DELETE)
check('Backspace, left, Delete', kb['text'].Text == u'hiHhQQ', repr(kb['text'].Text))
kb.processKeyId(layouts.KEY_CLEAR)
check('Clear', kb['text'].Text == u'')
kb.currentVKLayout = readKle('00000407')
kb.processKeyId(2)
check('German ^ is a dead key: nothing typed, labels show the combinations', kb['text'].Text == u'' and kb['_19'].text == native(u'\xea') and kb['_46'].instance.color == vk.COLOR_UNAVAILABLE)
kb.processKeyId(19)
check('^ + e -> \xea', kb['text'].Text == u'\xea')
kb.processKeyId(2)
kb.processKeyId(46)
check('^ + x -> ^x', kb['text'].Text == u'\xea^x', repr(kb['text'].Text))
kb.processKeyId(2)
kb.processKeyId(layouts.KEY_ESC)
check('Esc cancels a dead key, keyboard stays open', not kb.deadKey and not hasattr(kb, 'closed'))
kb.updateKsText()
check('dead key label blue', kb['_2'].instance.color == vk.COLOR_DEAD)
kb.insertSpace()
check('space', kb['text'].Text.endswith(u' '))
kb.processKeyId(layouts.KEY_ESC)
check('Esc closes without text', kb.closed == (None,))
kb = newKeyboard()
pressed = []
kb.processKeyId = lambda keyId: pressed.append(keyId)
kb.keyYellow()
kb.keyBlue()
kb.keyRed()
kb.focus = vk.FOCUS_HISTORY
kb.keyYellow()
check('YELLOW = AltGr, BLUE = Shift, RED = Backspace, only on the keyboard', pressed == [60, 43, 15], pressed)
kb = newKeyboard()
saved = []
kb.save = lambda: saved.append(1)
kb.processKeyId(layouts.KEY_ENTER)
kb.processKeyId(layouts.KEY_TEXT)
check('Enter and OK on the text field go through save() (PackageFeedEditor)', saved == [1, 1])

section('moving')
kb = newKeyboard()
kb.rowIdx, kb.colIdx, kb.currentKeyId = 5, 4, 59
kb.processArrowKey(-1, 0)
check('left from space -> Alt', kb.currentKeyId == layouts.KEY_ALT)
kb.processArrowKey(1, 0)
check('right onto space -> its middle column', kb.currentKeyId == 59 and kb.colIdx == 7, kb.colIdx)
kb.processArrowKey(0, -1)
check('up from the middle of space', kb.currentKeyId == layouts.KEY_GRID[4][7])
kb.rowIdx, kb.colIdx, kb.currentKeyId = 1, 14, 15
kb.processArrowKey(1, 0)
check('right wraps around the row', kb.currentKeyId == 1)
kb.processArrowKey(0, -1)
check('up to the text field', kb.currentKeyId == layouts.KEY_TEXT)
kb.processArrowKey(1, 0)
check('left/right do nothing on the text field', kb.currentKeyId == layouts.KEY_TEXT)

# ==== bugs of the review, one test each ===============================================================
section('bug 1: OK in the settings')
cfg.updateonline.value = False
st = setupmod.nvKeyboardSetup(Session(), True, None)
check('keyOK of ConfigListScreen is not overridden', 'keyOK' not in setupmod.nvKeyboardSetup.__dict__ and st.keyOK() == 'image keyOK')
st['config'] = FakeList()
st['config'].current = st.list[2]
check('OK on a normal row is left to the image (returns 0)', st.keyActionRow() == 0)

section('bug 2: layout id + suggestion locale')
LANGUAGE.active = 'de_DE'
cfg.keys_layout.value = ''
kb = newKeyboard()
downloads = []
vk.downloadLayout = lambda layoutId: downloads.append(layoutId) or shutil.copy(os.path.join(KLE, 'kle%s.kle' % layoutId), os.path.join(layouts.LAYOUT_DIR, '%s.kle' % layoutId)) or True
os.remove(os.path.join(layouts.LAYOUT_DIR, '00000407.kle'))
kb.loadKBLayout()
check('first start: layout of the enigma2 language, downloaded', kb.selectedKBLayoutId == '00000407' and downloads == ['00000407'] and kb.currentVKLayout['locale'] == 'de-DE', (kb.selectedKBLayoutId, downloads))
kb.showsuggestion = True
kb.showHistory = False
kb['text'].Text = u'matrix'
kb.input_updated()
check('suggestions asked in the layout language', QUEUE and QUEUE[-1].args[2] == 'de-DE', QUEUE and QUEUE[-1].args)
del QUEUE[:]
kb.close(None)
check('closing saves the layout id (not "")', cfg.keys_layout.value == '00000407')
LANGUAGE.active = 'en_GB'

section('bug 3: RIGHT at the end of the text')
kb = newKeyboard()
kb['text'] = FakeInput(u'abc')
kb.currentKeyId = layouts.KEY_TEXT
kb.searchHistoryList = ['x']
kb.suggestions = ['y']
kb.keyRight()
check('RIGHT at the end of the text goes to the suggestions', kb.focus == vk.FOCUS_SUGGESTIONS)
kb.switchToKeyboard()
kb['text'].currPos = 1
kb.keyRight()
check('RIGHT inside the text moves the cursor', kb['text'].currPos == 2 and kb.focus == vk.FOCUS_KEYBOARD)

section('bug 4: stale suggestions')
kb = newKeyboard()
kb.showHistory = False
kb.suggestionsProvider = 'bing'
vk_fetch = suggestions.fetchSuggestions
suggestions.fetchSuggestions = lambda provider, text, locale: ['%s-%s' % (provider, text)]
kb['text'].Text = u'ma'
kb.input_updated()
kb['text'].Text = u''
kb.input_updated()
runQueue()
check('answer for a cleared text is dropped', kb['suggestionList'].items == [], kb['suggestionList'].items)
kb['text'].Text = u'ma'
kb.input_updated()
kb.setSuggestionsProvider('google')
runQueue()
check('answer of the old provider is dropped', kb['suggestionList'].items == [])
kb['text'].Text = u'mat'
kb.input_updated()
kb['text'].Text = u'matr'
kb.input_updated()
kb['text'].Text = u'matri'
kb.input_updated()
check('one request in flight', len(QUEUE) == 1)
runQueue()
check('latest text fetched and shown', kb['suggestionList'].items == [('google-matri',)], kb['suggestionList'].items)

section('bug 5: answer while the list has the focus')
kb.focus = vk.FOCUS_SUGGESTIONS
kb.setSuggestions(['new'])
check('list untouched while focused', kb['suggestionList'].items == [('google-matri',)])
kb.switchToKeyboard()
check('shown when the focus leaves', kb['suggestionList'].items == [('new',)] and kb.suggestions == ['new'])
kb.suggestions = []
kb.searchHistoryList = []
kb.currentKeyId = 15
kb.rowIdx, kb.colIdx = 1, 14
kb.keyRight()
check('RIGHT at the edge skips empty panels (wraps on the keyboard)', kb.focus == vk.FOCUS_KEYBOARD and kb.currentKeyId == 1)
kb.showHistory = True
kb.searchHistoryList = ['a']
kb.currentKeyId = 15
kb.rowIdx, kb.colIdx = 1, 14
kb.keyRight()
check('RIGHT at the edge: empty suggestions skipped -> history', kb.focus == vk.FOCUS_HISTORY)
kb.keyRight()
check('RIGHT from the history -> keyboard, left edge', kb.focus == vk.FOCUS_KEYBOARD and kb.currentKeyId == 1)
kb.keyLeft()
check('LEFT at the left edge -> history', kb.focus == vk.FOCUS_HISTORY)

section('bug 6: removing the active layout')
cfg.keys_layout.value = '0000040c'
screen = vk.LanguageListScreen(Session())
screen['languageList'] = FakeList()
screen['languageList'].current = layouts.layoutItem('0000040c')
screen['languageList'].getCurrentIndex = lambda: 3
screen.keyOK()
check('removed, the built-in layout is active', not os.path.exists(layouts.layoutFile('0000040c')) and cfg.keys_layout.value == '00000809')
kb = newKeyboard()
kb.currentVKLayout = readKle('0000040c')
del downloads[:]
kb.languageSelectionBack()
check('keyboard shows the built-in layout, no new download', kb.currentVKLayout['id'] == '00000809' and not downloads, downloads)
screen.keyOK()
check('OK again installs it and makes it active', os.path.exists(layouts.layoutFile('0000040c')) and cfg.keys_layout.value == '0000040c' and screen['info'].text == 'Language downloaded successfully, exit from install')
vk.downloadLayout = lambda layoutId: False
screen['languageList'].current = layouts.layoutItem('00000410')
screen.keyOK()
check('failed download -> message', screen['info'].text == 'Failed to download language, try later')

section('bug 7: TEXT key')
kb = newKeyboard()
kb.loadVKLayout(layouts.defaultKBLAYOUT)
seen = []
for press in range(4):
    kb.switchinstalledvklayout()
    seen.append(kb.currentVKLayout['id'])
check('TEXT cycles installed + built-in layouts in order', seen == ['00000407', '0000040c', '00000809', '00000407'], seen)
with io.open(layouts.layoutFile('0000040c'), 'w', encoding='utf-8') as f:
    f.write(u"{'id': '0000040c', 'layout': {")
kb.session = Session()
kb.switchinstalledvklayout()
check('broken layout: error box, old layout stays', kb.currentVKLayout['id'] == '00000407' and kb.session.last()[0][0] is MessageBox)
kb.switchinstalledvklayout()
check('next TEXT goes on after the broken one', kb.currentVKLayout['id'] == '00000809')
kb.session = Session()
check('broken layout via getKeyboardLayout: False + error text', kb.getKeyboardLayout('0000040c') is False and 'failed' in kb.session.last()[1]['text'])
shutil.copy(os.path.join(KLE, 'kle0000040c.kle'), layouts.layoutFile('0000040c'))
kb = newKeyboard()
kb.loadVKLayout(layouts.defaultKBLAYOUT)
opened = []
kb.switchToLanguageSelection = lambda: opened.append(1)
kb.processKeyId(vk.KEY_LANGUAGE)
check('OK on the language key with installed layouts: next layout, no list', kb.currentVKLayout['id'] == '00000407' and not opened, (kb.currentVKLayout['id'], opened))
kb = newKeyboard()
kb.loadVKLayout(layouts.defaultKBLAYOUT)
kb.currentKeyId = vk.KEY_LANGUAGE
kb.keyOK()
kb.keyOKRepeat()
check('holding OK on the language key: one switch only', kb.currentVKLayout['id'] == '00000407', kb.currentVKLayout['id'])
kb.languageKeyLong()
args, kwargs, cb = kb.session.last()
check('OK long on the language key: back to the layout before, list of the installed ones',
      kb.currentVKLayout['id'] == '00000809' and args[0] is vk.LanguageListScreen and kwargs.get('installedIds') == kb.cycleLayoutIds(), (kb.currentVKLayout['id'], kwargs))
screen = vk.LanguageListScreen(Session(), None, args[2], installedIds=kwargs['installedIds'])
check('installed list: only those layouts, starts on the current one',
      sorted(x[2] for x in screen.layouts) == kb.cycleLayoutIds() and screen.layouts[args[2]][2] == '00000809', ([x[2] for x in screen.layouts], args[2]))
screen['languageList'] = FakeList()
screen['languageList'].current = layouts.layoutItem('00000407')
closed = []
screen.close = lambda *a: closed.append(1)
screen.keyOK()
check('installed list: OK makes it active and closes, nothing removed', cfg.keys_layout.value == '00000407' and closed and os.path.exists(layouts.layoutFile('00000407')))
kb.languageSelectionBack()
check('the keyboard shows the chosen layout', kb.currentVKLayout['id'] == '00000407', kb.currentVKLayout['id'])
count = len(kb.session.opened)
kb.languageKeyLong()
check('OK long without an OK press on the language key before: nothing', len(kb.session.opened) == count)
typed = []
kb.keyOK = lambda: typed.append(kb.currentKeyId)
kb.keyOKRepeat()
kb.currentKeyId = 1
kb.keyOKRepeat()
check('holding OK: repeats on other keys, not on the language key', typed == [1], typed)
kb = newKeyboard()
kb.loadVKLayout(layouts.defaultKBLAYOUT)
kb.switchToLanguageSelection = lambda: opened.append(1)
installed = [layouts.layoutFile(i) for i in layouts.installedLayoutIds()]
saved = dict((f, io.open(f, 'rb').read()) for f in installed)
for f in installed:
    os.remove(f)
kb.processKeyId(vk.KEY_LANGUAGE)
check('OK on the language key with only the built-in layout: the list', opened == [1], opened)
for f, data in saved.items():
    with io.open(f, 'wb') as out:
        out.write(data)

section('bug 8: numeric keypad only when asked for or guessed')
sess = Session()
sess.current_dialog = {'config': type('L', (object,), {'getCurrent': lambda self: ('Port', ConfigNumber())})()}
check('explicit Input.TEXT -> full keyboard, even on a number row', numpad.numPadMode(sess, Input.TEXT) is None)
check('no type -> guessed from the number row', numpad.numPadMode(sess, None) == 'number')
check('Input.PIN -> keypad', numpad.numPadMode(Session(), Input.PIN) == 'pin')

section('bug 9: CI package check')
for name in ('checks.yml', 'release.yml'):
    flow = readText(os.path.join(REPO, '.github', 'workflows', name))
    check('%s: no "! cmd" in run steps (does not fail with set -e)' % name, not re.search(r'^\s+! ', flow, re.M))
check('release only from main', "if: github.ref == 'refs/heads/main'" in readText(os.path.join(REPO, '.github', 'workflows', 'release.yml')))

section('bug 10: no callback after close')
kb = newKeyboard()
suggestions.fetchSuggestions = lambda *a: ['late']
kb['text'].Text = u'x'
kb.input_updated()
late = []
kb.suggestionsCallback = late.append
kb.close(None)
runQueue()
check('no callback after close', late == [])
suggestions.fetchSuggestions = vk_fetch

# ==== more ====================================================================================
section('history')
kb = newKeyboard()
with io.open(kb.history.path, 'w', encoding='utf-8') as f:
    f.write(u'Tatort\nMatrix\nterminator\n\nThe Office\n\xdcber\n')
kb.showsuggestion = False
kb['text'].Text = u'T'
kb.input_updated()
check('history sorted (case-insensitive, order kept)', kb['historyList'].items == [('Tatort',), ('terminator',), ('The Office',), ('Matrix',), (native(u'\xdcber'),)], kb['historyList'].items)
check('no suggestion request with suggestions off', not QUEUE)
kb.setPanelsVisible()
check('history visible, suggestions hidden', kb['historyList'].visible and not kb['suggestionList'].visible)
cfg.historysize.value = 3
h = suggestions.SearchHistory(os.path.join(TMP, 'history2'))
for word in ('one', 'two', 'three', 'four', 'two'):
    h.add(word)
check('history keeps the newest N, retyped entry moves to the top', h.entries() == ['two', 'four', 'three'], h.entries())
cfg.historysize.value = 100
kb['text'].Text = u'Matrix'
kb.save()
check('Enter saves the text in the history and as last search', kb.history.entries()[0] == 'Matrix' and cfg.lastsearchText.value == 'Matrix' and kb.closed == ('Matrix',))

section('remember last search / setText')
cfg.lastsearchText.value = 'Matrix'
cfg.rememberlast.value = False
check('rememberlast off -> empty field', newKeyboard().startText == '')
cfg.rememberlast.value = True
check('rememberlast on -> last search', newKeyboard().startText == 'Matrix')
check('text=None does not crash', newKeyboard(text=None).startText == 'Matrix')
kb = newKeyboard()
kb.setText(u'\xfcber')
check('setText with unicode (Python 2) and cursor at the end', kb['text'].Text == u'\xfcber' and kb['text'].currPos == 4)
kb.history.clear()
kb.focus = vk.FOCUS_HISTORY
kb['historyList'].current = native(u'Tatort')
kb.keyOK()
check('OK on a history entry takes it, back on the text field', kb['text'].Text == u'Tatort' and kb.focus == vk.FOCUS_KEYBOARD and kb.currentKeyId == layouts.KEY_TEXT)

section('panels (PVR / PREVIOUS / NEXT)')
kb.showsuggestion = kb.showHistory = True
kb.suggestions = ['x']
kb.searchHistoryList = ['a']
kb.togglesfocus()
check('NEXT: keyboard -> suggestions', kb.focus == vk.FOCUS_SUGGESTIONS)
kb.togglesfocus()
check('NEXT: suggestions -> history', kb.focus == vk.FOCUS_HISTORY)
kb.togglesfocusBack()
check('PREVIOUS: history -> suggestions', kb.focus == vk.FOCUS_SUGGESTIONS)
kb.keyBack()
check('EXIT in a list -> keyboard', kb.focus == vk.FOCUS_KEYBOARD)
kb.showsuggestion = False
kb.togglesfocus()
check('hidden suggestions are skipped', kb.focus == vk.FOCUS_HISTORY)

section('flag')
kb = newKeyboard()
cfg.showflags.value = False
kb.displayActiveLayoutFlag('00000407')
check('show flags off hides the flag', kb['flag'].instance.visible is False)
cfg.showflags.value = True
kb.displayActiveLayoutFlag('00000407')
check('show flags on shows it', kb['flag'].instance.visible is True and kb['flag'].instance.path.endswith('de_DE.png'))
kb.loadVKLayout(readKle('00000407'))
check('language key shows DE', kb['_56'].text == 'DE')

section('settings')
kb = newKeyboard()
kb.showSettings()
check('MENU opens the settings directly', kb.session.last()[0][0] is setupmod.nvKeyboardSetup and kb.session.last()[0][1:] == (True, kb))
st = setupmod.nvKeyboardSetup(Session(), True, kb)
st.onStart()
check('title with version', setupmod.VER in st.title)
check('settings colour keys: YELLOW keyboard, BLUE numpad', st['key_yellow'].text == 'Virtual Keyboard' and st['key_blue'].text == 'Numeric keypad')
rows = st.list
check('action rows on top', rows[0][1] is st.actionInstallLanguage and rows[1][1] is st.actionClearHistory)
check('all settings shown although the image keyboard is selected', cfg.textinput.value == 'VirtualKeyBoard' and any(r[1] is cfg.numpad for r in rows) and any(r[1] is cfg.historysize for r in rows))
cfg.showsuggestion.value = False
st.createConfigList()
check('provider row hidden with suggestions off', not any(r[1] is cfg.suggestionsprovider for r in st.list))
before = cfg.suggestionsprovider.saved
st.close = lambda *a: setattr(st, 'closedWith', a)
st.keySave()
check('SAVE also saves the hidden rows', cfg.suggestionsprovider.saved == before + 1 and st.closedWith == (True,))
cfg.showsuggestion.value = True
st['config'] = FakeList()
st.session = Session()
st['config'].current = st.list[1]
st.keyActionRow()
check('clear history asks first', st.session.last()[0][0] is MessageBox and st.session.last()[0][2] == MessageBox.TYPE_YESNO)
kb.history.add('x')
st.session.last()[2](False)
check('"no" keeps the history', kb.history.entries() == ['x'])
st.session.last()[2](True)
check('"yes" deletes the history and empties the open keyboard list', kb.history.entries() == [] and kb['historyList'].items == [] and kb.searchHistoryList == [])
languages = []
kb.switchToLanguageSelection = lambda: languages.append(1)
st['config'].current = st.list[0]
st.keyActionRow()
check('OK on "Install language" opens the layout list of the keyboard', languages == [1])
st.keyboard = None
st.installLanguage()
check('without a keyboard: the layout list itself', st.session.last()[0][0] is vk.LanguageListScreen)
del st.session.opened[:]
st.showNewkeyboard()
st.showNumpad()
check('YELLOW opens the keyboard, BLUE the keypad', st.session.opened[0][0][0] is vk.NewVirtualKeyBoard and st.session.opened[1][0][0] is numpad.NVKNumPad)
cfg.showsuggestion.value = False
cfg.suggestionsprovider.value = 'duckduckgo'
kb = newKeyboard()
kb.focus = vk.FOCUS_SUGGESTIONS
kb.settingsBack(True)
check('settings applied live', kb.showsuggestion is False and kb.suggestionsProvider == 'duckduckgo' and kb.focus == vk.FOCUS_KEYBOARD and kb['suggestionheader'].text == 'Suggestions (DuckDuckGo)')
cfg.showsuggestion.value = True
cfg.suggestionsprovider.value = 'google'
check('provider choices from suggestions.py', cfg.suggestionsprovider.default == 'google' and ('imdb', 'IMDb') in suggestions.SUGGESTION_PROVIDERS)
setupSkin = ET.fromstring(setupmod.setupSkin())
check('settings skin: valid XML, button pictures exist', all(os.path.exists(p.get('pixmap')) for p in setupSkin.findall('ePixmap')))
skins = [setupmod.setupSkin(), newKeyboard().skin, vk.LanguageListScreen(Session()).skin, vk.HelpScreen(Session(), 'Help', []).skin]
check('no itemHeight/secondfont in skins (VTi: "Attribute not implemented")', not [s for s in skins if 'itemHeight=' in s or 'secondfont=' in s])
calls = []
st['config'] = types.SimpleNamespace(instance=types.SimpleNamespace(setItemHeight=calls.append, setFont=calls.append)) if PY3 else Anything()
setupmod.DreamOS = lambda: False
st.setListFonts()
check('settings list: row height + font from code', not PY3 or (calls[0] == tools.sc(45 if WIDTH > 1280 else 30) and calls[1][1] == tools.sc(30 if WIDTH > 1280 else 20)), calls)
check('plugin descriptors, named NewVirtualKeyBoard', [d['name'] for d in plugin.Plugins()] == ['NewVirtualKeyBoard'] * 2)

section('keyboard switch (symlink)')
if hasattr(os, 'symlink') and os.name != 'nt':
    screens = os.path.join(TMP, 'Screens') + os.sep
    os.mkdir(screens)
    setupmod.SCREENS_DIR, setupmod.KEYBOARD_LINK = screens, screens + 'VirtualKeyBoard.py'
    with open(screens + 'VirtualKeyBoard.py', 'w') as f:
        f.write('# image\n')
    with open(screens + 'VirtualKeyBoard.pyc', 'w') as f:
        f.write('x')
    check('switch to the new keyboard', setupmod.switchKeyboard(True) and os.path.islink(setupmod.KEYBOARD_LINK) and os.path.exists(screens + 'VirtualKeyBoard_backup.py') and not os.path.exists(screens + 'VirtualKeyBoard.pyc'))
    check('and back', setupmod.switchKeyboard(False) and not os.path.islink(setupmod.KEYBOARD_LINK) and readText(screens + 'VirtualKeyBoard.py') == '# image\n')
    setupmod.switchKeyboard(True)
    os.remove(screens + 'VirtualKeyBoard_backup.py')
    check('no backup: the new keyboard stays (False)', setupmod.switchKeyboard(False) is False and os.path.islink(setupmod.KEYBOARD_LINK))
else:
    print('     (skipped: no symlinks here)')

section('update check')
installer = io.open(os.path.join(REPO, 'installer.sh'), 'rb').read()
check('installer.sh has LF line endings', b'\r' not in installer)
version, description = setupmod.parseInstaller(installer)
check('installer.sh version == plugin version', version == setupmod.VER, (version, setupmod.VER))
check('description read', description.startswith('What is NEW') and 'numeric keypad' in description)
check('"version=" inside the description is text', setupmod.parseInstaller(b'description="\nversion=99\n"\nversion="1.0"\n') == ('1.0', 'version=99'))
st = setupmod.nvKeyboardSetup(Session(), False, None)
st.parseData(installer)
check('same version -> no update prompt', not st.session.opened)
st.parseData(installer.replace(('version="%s"' % setupmod.VER).encode(), b'version="99.0"'))
check('newer version -> update prompt with the changelog', st.session.opened and '99.0' in st.session.last()[0][1] and 'numeric keypad' in st.session.last()[0][1])
st.parseData(b'no version here')
check('installer.sh without version -> no crash, no prompt', len(st.session.opened) == 1)
st.close()
st.parseData(installer.replace(('version="%s"' % setupmod.VER).encode(), b'version="99.0"'))
check('no prompt after the settings closed', len(st.session.opened) == 1)
cfg.updateonline.value = True
setupmod.urlread = lambda url, timeout: (installer.replace(('version="%s"' % setupmod.VER).encode(), b'version="13.10"'), 'text/plain')
pluginVer, setupmod.VER = setupmod.VER, '13.9'
st = setupmod.nvKeyboardSetup(Session(), False, None)
st.onStart()
runQueue()
check('online check: 13.10 is offered on 13.9 (float said no)', st.session.opened and '13.10' in st.session.last()[0][1])
setupmod.VER = pluginVer
cfg.updateonline.value = False

section('packaging')
bb = readText(os.path.join(REPO, 'enigma2-plugin-systemplugins-newvirtualkeyboard.bb'))
check('.bb version == plugin version', 'PV = "%s+git"' % setupmod.VER in bb)
prerm = readText(os.path.join(REPO, 'CI', 'prerm.sh'))
body = lambda text: text[text.index('case "$1"'):text.index('exit 0\n', text.index('fi\n')) + 7].replace('$D/', '/')
bbPrerm = bb[bb.index('pkg_prerm'):]
check('.bb prerm == CI/prerm.sh', body(bbPrerm) == body(prerm))
postinst = readText(os.path.join(REPO, 'CI', 'postinst.sh'))
bbPostinst = bb[bb.index('pkg_postinst'):]
bbPostinst = bbPostinst[bbPostinst.index('#!/bin/sh'):bbPostinst.index('\n}\n') + 1]
check('.bb postinst == CI/postinst.sh', bbPostinst == postinst)
check('installer.sh runs CI/postinst.sh', 'sh "NewVirtualKeyBoard-main/CI/postinst.sh"' in installer.decode('utf-8'))
fakeRoot = tempfile.mkdtemp()
fakeScreens = os.path.join(fakeRoot, 'usr/lib/enigma2/python/Screens')
os.makedirs(fakeScreens)
os.makedirs(os.path.join(fakeRoot, 'usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard'))
os.makedirs(os.path.join(fakeRoot, 'etc/enigma2'))
try:
    os.symlink(fakeRoot, os.path.join(fakeRoot, 'link'))
    canLink = True
except (AttributeError, NotImplementedError, OSError):
    canLink = False
if canLink and not (shutil.which('sh') if PY3 else os.path.exists('/bin/sh')):
    canLink = False
if canLink:
    import subprocess  # noqa: E402
    script = os.path.join(fakeRoot, 'postinst')
    with io.open(script, 'w', encoding='utf-8', newline='\n') as f:
        f.write(postinst.replace('/usr/lib', fakeRoot + '/usr/lib').replace('/etc/enigma2', fakeRoot + '/etc/enigma2'))
    with io.open(os.path.join(fakeScreens, 'VirtualKeyBoard.pyc'), 'wb') as f:
        f.write(b'image')

    def runPostinst(env=None):
        with open(os.devnull, 'w') as null:
            subprocess.call(['sh', script], stdout=null, env=env)
        return os.path.islink(os.path.join(fakeScreens, 'VirtualKeyBoard.py'))

    check('postinst without the setting: image keyboard stays', not runPostinst() and os.path.exists(os.path.join(fakeScreens, 'VirtualKeyBoard.pyc')))
    with io.open(os.path.join(fakeRoot, 'etc/enigma2/settings'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(u'config.NewVirtualKeyBoard.firsttime=False\nconfig.NewVirtualKeyBoard.textinput=NewVirtualKeyBoard\n')
    env = dict(os.environ, D='/image')
    check('postinst while an image is built: nothing', not runPostinst(env))
    check('postinst with the saved setting: the new keyboard, image one as backup',
          runPostinst() and not os.path.exists(os.path.join(fakeScreens, 'VirtualKeyBoard.pyc'))
          and io.open(os.path.join(fakeScreens, 'VirtualKeyBoard_backup.pyc'), 'rb').read() == b'image')
    check('postinst again: backup kept', runPostinst() and io.open(os.path.join(fakeScreens, 'VirtualKeyBoard_backup.pyc'), 'rb').read() == b'image')
else:
    print('     (postinst run skipped: no symlinks or sh here)')
shutil.rmtree(fakeRoot, ignore_errors=True)
check('installer.sh strips the translation sources', "-name '*.po'" in installer.decode('utf-8'))

# ==== translations (gettext, locale/) ============================================================
section('translations')
import gettext  # noqa: E402

LOCALE = os.path.join(PLUGIN, 'locale')


def readPo(path):
    # minimal .po reader: {msgid: msgstr} for the plain entries used here
    entries, cur, key = {}, {}, None
    for line in readText(path).splitlines() + ['']:
        line = line.strip()
        if line.startswith('msgid '):
            if 'msgid' in cur:
                entries[cur['msgid']] = cur.get('msgstr', '')
            cur, key = {'msgid': ast.literal_eval(line[6:])}, 'msgid'
        elif line.startswith('msgstr '):
            cur['msgstr'], key = ast.literal_eval(line[7:]), 'msgstr'
        elif line.startswith('"') and key:
            cur[key] += ast.literal_eval(line)
        elif not line and 'msgid' in cur:
            entries[cur['msgid']] = cur.get('msgstr', '')
            cur, key = {}, None
    entries.pop('', None)
    if not PY3:
        entries = dict((k.decode('utf-8'), v.decode('utf-8')) for k, v in entries.items())
    return entries


potIds = set(readPo(os.path.join(LOCALE, 'NewVirtualKeyBoard.pot')))
code = u''.join(readText(os.path.join(PLUGIN, name)) for name in os.listdir(PLUGIN) if name.endswith('.py'))
used = set(ast.literal_eval(m.group(0)[2:-1]) for m in re.finditer(r"""_\((?:'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")\)""", code))
if not PY3:
    used = set(u.decode('utf-8') if isinstance(u, bytes) else u for u in used)
check('every _("...") text is in the .pot (run locale/updateallpo.sh)', used <= potIds, sorted(used - potIds))
check('no unused .pot texts', potIds <= used, sorted(potIds - used))
langs = sorted(d for d in os.listdir(LOCALE) if os.path.isdir(os.path.join(LOCALE, d)))
check('10 translations', len(langs) == 10, langs)
for lang in langs:
    poPath = os.path.join(LOCALE, lang, 'LC_MESSAGES', 'NewVirtualKeyBoard.po')
    po = readPo(poPath)
    check('%s.po has the .pot texts' % lang, set(po) == potIds, sorted(set(po) ^ potIds))
    check('%s.po has no fuzzy (guessed) entries' % lang, '#, fuzzy' not in readText(poPath))
    t = gettext.translation('NewVirtualKeyBoard', LOCALE, languages=[lang])
    lookup = t.gettext if PY3 else t.ugettext
    stale = [k for k, v in po.items() if v and lookup(k) != v]
    check('%s .mo matches .po' % lang, not stale, stale[:3])
oldLanguage = os.environ.get('LANGUAGE')
os.environ['LANGUAGE'] = 'de'
check('_() uses the plugin translation', vk._('Search history') in ('Suchverlauf', u'Suchverlauf'), vk._('Search history'))
os.environ['LANGUAGE'] = 'xx'
check('_() falls back to English', vk._('Search history') == 'Search history')
if oldLanguage is None:
    del os.environ['LANGUAGE']
else:
    os.environ['LANGUAGE'] = oldLanguage

# ==== keymap / help / layout list ==================================================================
section('keymap')
keymap = ET.parse(os.path.join(PLUGIN, 'keymap.xml')).getroot()
maps = dict((m.get('context'), dict((k.get('id'), k.get('mapto')) for k in m)) for m in keymap)
check('keymap NVKActions', maps.get('NVKActions') == {'KEY_PREVIOUS': 'vk_prevpanel', 'KEY_NEXT': 'vk_nextpanel', 'KEY_FASTFORWARD': 'vk_space', 'KEY_REWIND': 'vk_cleartext', 'KEY_PVR': 'vk_nextpanel', 'KEY_TEXT': 'vk_language', 'KEY_OK': 'vk_languagelist', 'KEY_INFO': 'vk_help', 'KEY_HELP': 'vk_help'}, maps)
check('keymap: OK long only', [k.get('flags') for k in keymap.iter('key') if k.get('id') == 'KEY_OK'] == ['l'])
actions = newKeyboard()['actions']
check('actions: yellow/blue/TEXT/menu', actions['yellow'].__name__ == 'keyYellow' and actions['blue'].__name__ == 'keyBlue' and actions['vk_language'].__name__ == 'switchinstalledvklayout' and actions['menu'].__name__ == 'showSettings')
check('INFO only through the own keymap (no second "info" action: help would open twice)', actions['vk_help'].__name__ == 'showHelp' and 'info' not in actions)

section('help')
kb = newKeyboard()
kb.showHelp()
helpArgs = kb.session.last()[0]
rows = helpArgs[2]
check('help has 17 rows', len(rows) == 17, len(rows))
for tier in ('hd', 'fhd', 'wqhd'):
    missingIcons = [r[1] for r in rows if not os.path.exists(os.path.join(PLUGIN, 'skins', 'icons', 'menus', tier, r[1] + '.png'))]
    check('help icons exist (%s)' % tier, not missingIcons, missingIcons)
helpScreen = vk.HelpScreen(Session(), 'Help', rows)
m = re.search(r'size="(\d+),(\d+)"', helpScreen.skin)
check('help window fits the desktop', int(m.group(1)) <= WIDTH and int(m.group(2)) <= WIDTH * 9 // 16, m.group(0))
check('help window: own title bar, no image border', 'source="Title"' in helpScreen.skin and 'flags="wfNoBorder"' in helpScreen.skin)
menuH = int(re.search(r'<widget name="menu" position="[^"]+" size="\d+,(\d+)"', helpScreen.skin).group(1))
check('help window: all 17 rows fit without scrolling', menuH >= len(rows) * int(round(54 * WIDTH / 1920.0)) - 2, (menuH, len(rows)))
helpScreen['menu'] = types.SimpleNamespace(l=Anything()) if PY3 else Anything()
entries = helpScreen.buildRows()
# enigma2 draws a MultiContent row from its 2nd element on (the 1st is data)
check('help rows: data slot, text, icon', len(entries) == 17 and all(e[0] is None and e[1][0] == 'T' and e[2][0] == 'B' for e in entries), entries[0])
check('help rows: the text is drawn', all(e[1][1]['text'] == r[0] for e, r in zip(entries, rows)))
lst = vk.TextList()
lst.l = type('L', (object,), {'getItemSize': lambda self: Size(300, 40)})()
check('text list rows: data slot first', lst.buildEntry('x')[0] is None and lst.buildEntry('x')[1][7] == 'x')

section('layout list')
lst = vk.LayoutList()
lst.l = type('L', (object,), {'getItemSize': lambda self: Size(900, 54)})()
entry = lst.buildEntry(layouts.layoutItem('0000040c'))
check('layout row: installed dot, flag, name', entry[1][5][1].endswith('green18.png') and entry[2][5][1].endswith('fr_FR.png') and entry[3][7] == 'French (Legacy, AZERTY)', entry[1:])
entry = lst.buildEntry(layouts.layoutItem('00000410'))
check('not installed: grey dot', entry[1][5][1].endswith('grey18.png'))
cfg.showflags.value = False
check('show flags off: no flag in the row', len(lst.buildEntry(layouts.layoutItem('00000410'))) == 3)
cfg.showflags.value = True
check('dot pixmaps cached', len(lst.pixmaps) == 4, list(lst.pixmaps))
screen = vk.LanguageListScreen(Session(), None, 5)
check('layout list: own title bar, no image border', 'source="Title"' in screen.skin and 'flags="wfNoBorder"' in screen.skin)
check('layout list: old arguments still work', len(vk.LanguageListScreen(Session(), [({'sel': False, 'val': x},) for x in layouts.KbLayouts[:3]]).layouts) == 3)

# ==== openATV compatibility / numeric keypad ======================================================
section('openATV')
try:
    newKeyboard(style=vk.NewVirtualKeyBoard.VKB_SAVE_ICON, windowTitle='x', visibleWidth=40)
    check('style= / VKB_SAVE_ICON accepted', True)
except TypeError as e:
    check('style= / VKB_SAVE_ICON accepted', False, e)
check('VirtualKeyboard alias', vk.VirtualKeyboard is vk.NewVirtualKeyBoard and vk.VirtualKeyBoard is vk.NewVirtualKeyBoard)

section('numeric keypad')
sess = Session()
pad = vk.NewVirtualKeyBoard(sess, title='PIN', text='0012', type=Input.PIN)
check('Input.PIN -> keypad', isinstance(pad, numpad.NVKNumPad) and pad.mask, type(pad))
pad = vk.NewVirtualKeyBoard(sess, 'Port', '8001', False, False, False, None, None, False, Input.NUMBER)
check('Input.NUMBER (positional) -> keypad', isinstance(pad, numpad.NVKNumPad) and not pad.mask)
check('text -> full keyboard', isinstance(vk.NewVirtualKeyBoard(sess, title='Name', text='abc'), vk.NewVirtualKeyBoard))
sess.current_dialog = {'config': type('L', (object,), {'getCurrent': lambda self: ('Port', ConfigNumber())})()}
check('TEXT key on a ConfigNumber -> keypad', isinstance(vk.NewVirtualKeyBoard(sess, title='Port', text='80'), numpad.NVKNumPad))
sess.current_dialog = {'input': type('I', (object,), {'type': Input.PIN})()}
check('OpenViX InputBox PIN -> keypad', isinstance(vk.NewVirtualKeyBoard(sess, title='PIN', text=''), numpad.NVKNumPad))
sess.current_dialog = {}


class Sub(vk.NewVirtualKeyBoard):
    pass


check('subclasses keep the keyboard', isinstance(Sub(sess, title='x', text='', type=Input.NUMBER), Sub))
cfg.numpad.value = False
check('setting off -> full keyboard', isinstance(vk.NewVirtualKeyBoard(sess, title='x', text='1', type=Input.NUMBER), vk.NewVirtualKeyBoard))
cfg.numpad.value = True
pad = numpad.NVKNumPad(sess, title='Port', text='8001', mode='number')
pad.updateText = lambda: None
check('keypad preset', pad.text == '8001' and pad.preset)
pad.addDigit(0)
pad.addDigit(0)
check('first digit replaces the preset, leading zero kept', pad.text == '00')
pad.backspace()
check('backspace', pad.text == '0')
results = []
pad.close = lambda *a: results.append(a)
pad.accept()
check('accept returns the text', results[-1] == ('0',))
pad.keyBack()
check('EXIT returns None', results[-1] == (None,))
keyW = int(re.search(r'<widget name="key_0_0" position="[^"]+" size="(\d+),', pad.skin).group(1))
check('keypad key scaled to the desktop', keyW == int(round(136 * WIDTH / 1920.0)), keyW)
pin = numpad.NVKNumPad(sess, title='PIN', text='', mode='pin', maxSize=4)
labels = []
pin['text'] = types.SimpleNamespace(setText=labels.append, instance=None) if PY3 else type('T', (object,), {'setText': lambda self, t: labels.append(t), 'instance': None})()
for d in (1, 2, 3, 4, 5):
    pin.addDigit(d)
check('PIN masked and limited to maxSize', pin.text == '1234' and labels[-1] == '****', (pin.text, labels[-1:]))

# ==== suggestions: URLs and parsing (offline) =========================================================
section('suggestions')
url = suggestions.getSuggestionsUrl
check('google url: hl language, gl country', url('google', 'a b', 'ru_RU') == 'https://suggestqueries.google.com/complete/search?output=firefox&ie=utf-8&oe=utf-8&hl=ru&gl=ru&q=a%20b', url('google', 'a b', 'ru_RU'))
check('google url from a layout locale (de-AT)', '&hl=de&gl=at&' in url('google', 'x', 'de-AT'))
check('youtube url', '&ds=yt' in url('youtube', 'x', 'de_DE'))
check('bing url mkt', url('bing', 'x', 'sr-Cyrl-CS').endswith('mkt=sr-CS'))
check('imdb url', url('imdb', 'Der Pate', 'de_DE') == 'https://v3.sg.media-imdb.com/suggestion/d/der%20pate.json')
check('imdb url with umlaut', '/suggestion/x/' in url('imdb', native(u'\xfcber'), 'de_DE'))
parse = suggestions.parseSuggestions
check('parse google/bing', parse('google', b'["ma",["matrix","mad max"]]', 'application/json; charset=UTF-8') == ['matrix', 'mad max'])
check('parse google legacy code page', parse('google', u'["x",["\xfcber"]]'.encode('latin-1'), 'text/javascript; charset=ISO-8859-1') == [native(u'\xfcber')])
check('parse duckduckgo', parse('duckduckgo', b'[{"phrase":"matrix"},{"phrase":"matrix 4"}]') == ['matrix', 'matrix 4'])
check('parse imdb: titles only', parse('imdb', json.dumps({'d': [{'id': 'tt0133093', 'l': 'The Matrix'}, {'id': 'nm0000206', 'l': 'Keanu Reeves'}]}).encode('utf-8')) == ['The Matrix'])
check('parse: empty entries dropped', parse('bing', b'["x",["a","",null]]') == ['a'])

if NET:
    for provider, text, loc in (('google', 'matrix', 'de_DE'), ('youtube', 'matrix', 'de_DE'), ('bing', 'matrix', 'de_DE'), ('duckduckgo', 'matrix', 'en_US'), ('google', native(u'матрица'), 'ru_RU'), ('google', 'istanbul', 'tr_TR'), ('imdb', 'matrix', 'de_DE'), ('imdb', native(u'm\xfcnchen'), 'de_DE')):
        try:
            r = vk_fetch(provider, text, loc)
            check('live %s %s' % (provider, loc), isinstance(r, list) and len(r) > 0 and all(isinstance(x, str) for x in r), repr(r[:3]))
        except Exception as e:
            check('live %s %s' % (provider, loc), False, repr(e))

shutil.rmtree(TMP)
print('=== %d failures' % len(FAILS), FAILS)
sys.exit(1 if FAILS else 0)
