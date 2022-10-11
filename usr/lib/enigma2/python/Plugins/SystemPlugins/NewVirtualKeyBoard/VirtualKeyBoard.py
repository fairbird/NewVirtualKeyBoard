#!/usr/bin/python
# -*- coding: utf-8 -*-

# Original concept and code - samsamsam /e2iplayer
# Code modifications - mfaraj57 and Fairbird
# Support Python 3 by Fairbird
# project continued by madmax88 and linuxsat-support forum
# code streamlined for kiddac's plugins - kiddac

import os
from enigma import loadPNG, ePoint, gRGB, eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, RT_VALIGN_CENTER, getDesktop, RT_WRAP, getPrevAsciiCode
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap, ActionMap
from Components.GUIComponent import GUIComponent
from Components.Language import language
from Components.config import config, configfile
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest, MultiContentEntryPixmapAlphaBlend
from Components.Label import Label
from Components.Input import Input
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
#from skin import loadSkin
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

from Plugins.SystemPlugins.NewVirtualKeyBoard.tools import *

VER = getversioninfo()

if isFHD():
        from Plugins.SystemPlugins.NewVirtualKeyBoard.skins.NewVirtualKeyBoardfhd import *
else:
        from Plugins.SystemPlugins.NewVirtualKeyBoard.skins.NewVirtualKeyBoard import *

try:
	FONTSSIZE = config.NewVirtualKeyBoard.fontssize.value
except:
	FONTSSIZE = 0

if PY3:
    # Python 3
    compat_str = str
    from urllib.parse import quote as compat_quote
    from urllib.request import urlopen as compat_urlopen
else:
    # Python 2
    compat_str = unicode
    from urllib import quote as compat_quote
    from urllib2 import urlopen as compat_urlopen

#if isFHD():
#    skin_xml = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/NewVirtualKeyBoardfhd.xml")
#else:
#    skin_xml = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/NewVirtualKeyBoard.xml")

#if os.path.exists(skin_xml):
#    loadSkin(skin_xml)
#    pass
#else:
#    print('skin.xml is not present')

# local saved kle layout files
vkLayoutDir = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/kle/")

# external kle layout files
#ServerUrl = 'http://tunisia-dreambox.info/TSplugins/NewVirtualKeyBoard/kle/'
ServerUrl = 'https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/kle/'

# keyboardlayout website
# http://kbdlayout.info/


# saved search history
hfile = '/etc/history'

parameters = {}
kblayout_loading_error = '%s kblayout load failed'


def getLayoutFile(KBLayoutId):
    return vkLayoutDir + '%s.kle' % KBLayoutId


def getSLayoutFile(KBLayoutId):
    file = 'kle%s.kle' % KBLayoutId
    return ServerUrl + file


def pathExists(path):
    if os.path.exists(path):
        return True
    else:
        return False


def downloadFile(url, target):
    try:
        response = compat_urlopen(url)
        with open(target, 'wb') as output:
            output.write(response.read())
        return True
    except:
        print("language download error")
        return False


def iconsDir(file=''):
    return resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/icons/") + file

class languageSelectionList(GUIComponent, object):

    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildEntry)
        self.onSelectionChanged = []
        if isFHD():
            fontSize = 32
            itemHeight = 54
        else:
            fontSize = 24
            itemHeight = 46
        self.font = ('Regular', fontSize, itemHeight, 0)
        self.l.setFont(0, gFont('Regular', 60))
        self.l.setFont(1, gFont(self.font[0], self.font[1]))
        self.l.setItemHeight(self.font[2])
        self.dictPIX = {}

    def onCreate(self):
        pass

    def onDestroy(self):
        pass

    def connectSelChanged(self, fnc):
        if fnc not in self.onSelectionChanged:
            self.onSelectionChanged.append(fnc)

    def disconnectSelChanged(self, fnc):
        if fnc in self.onSelectionChanged:
            self.onSelectionChanged.remove(fnc)

    def selectionChanged(self):
        for x in self.onSelectionChanged:
            x()

    def getCurrent(self):
        cur = self.l.getCurrentSelection()
        return cur and cur[0]

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        self.selectionChanged_conn = eConnectCallback(instance.selectionChanged, self.selectionChanged)
        self.onCreate()

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        self.selectionChanged_conn = None
        self.onDestroy()
        return

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def setList(self, list):
        self.l.setList(list)

    def setSelectionState(self, enabled):
        self.instance.setSelectionEnable(enabled)

    def buildEntry(self, item):
        res = [None]
        width = self.l.getItemSize().width()
        height = self.l.getItemSize().height()
        y = (height - 16) / 2
        png = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/icons/menus/hd40/grey18.png")
        try:
            id = str(item['val'][2])
            if os.path.exists(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/kle/") + id + ".kle"):
                png = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/icons/menus/hd40/green18.png")
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 3, y, 16, 16, loadPNG(png)))
            else:
                png = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/icons/menus/hd40/grey18.png")
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 3, y, 16, 16, loadPNG(png)))
            res.append((eListboxPythonMultiContent.TYPE_TEXT, 40, 0, width - 4, height, 1, RT_HALIGN_LEFT | RT_VALIGN_CENTER, str(item['val'][0])))
        except Exception:
            pass
        return res
    GUI_WIDGET = eListbox
    currentIndex = property(getCurrentIndex, moveToIndex)
    currentSelection = property(getCurrent)


class KBLayoutLanguages():

    def __init__(self, LoadVKLayout_callback=None):
        self.defaultKBLAYOUT = defaultKBLAYOUT
        self.KbLayouts = KbLayouts
        self.KBLayoutId_installed = []
        self.LoadVKLayout_callback = LoadVKLayout_callback
        self.KBsettings = config.NewVirtualKeyBoard

    def GetSystemLang(self, int=False):
        if int:
            try:
                defaultLanguage = language.getActiveLanguage()
            except Exception:
                pass
                defaultLanguage = 'en_EN'
        else:
            try:
                defaultLanguage = language.getActiveLanguage().split('_')[0]
            except Exception:
                defaultLanguage = 'en'
        return defaultLanguage

    def getDefault_KBLayout(self, KBLayoutId=''):
        if KBLayoutId == '':
            e2Locale = GetSystemLang(True)
            langMap = {'pl_PL': '00000415', 'en_EN': '00020409'}
            KBLayoutId = langMap.get(e2Locale, '')
            if KBLayoutId == '':
                for item in self.KbLayouts:
                    if e2Locale == item[1]:
                        KBLayoutId = item[2]
                        break
            if KBLayoutId == '':
                e2lang = GetSystemLang() + '_'
                for item in self.KbLayouts:
                    if item[1].startswith(e2lang):
                        KBLayoutId = item[2]
                        break
        return KBLayoutId

    def saveInstalled_keylayout(self):
        self.KBLayoutId_installed = []
        path = vkLayoutDir
        try:
            self.KBLayoutId_installed = [f for f in os.listdir(path) if os.path.isfile(f)]
        except:
            self.KBLayoutId_installed = []
        if pathExists(path):
            for x in os.listdir(path):
                item = os.path.join(path, x)
                if os.path.isfile(item):
                    layoutid = x.replace('.kle', '')
                    self.KBLayoutId_installed.append(layoutid)
        else:
            self.KBLayoutId_installed = []

    def getActive_keylayout(self):
        selectedKBLayoutId = self.KBsettings.keys_layout.value
        return selectedKBLayoutId

    def saveActive_keylayout(self, selectedKBLayoutId):
        if selectedKBLayoutId != self.KBsettings.keys_layout.value:
            self.KBsettings.keys_layout.value = selectedKBLayoutId
            self.KBsettings.keys_layout.save()
            configfile.save()
        self.saveInstalled_keylayout()
        return selectedKBLayoutId

    def KeyLayoutExists(self, KBLayoutId):
        path = vkLayoutDir
        if pathExists(path):
            return True
        else:
            return False

    def downloadKBlayout(self, KBLayoutId):
        ret = downloadFile(getSLayoutFile(KBLayoutId), getLayoutFile(KBLayoutId))
        return ret

    def setActive_Layout(self, KBLayoutId):
        loadErrorNo = 0
        filePath = vkLayoutDir + '%s.kle' % KBLayoutId
        if KBLayoutId == self.defaultKBLAYOUT['id']:
            self.LoadVKLayout_callback(self.defaultKBLAYOUT)
            return 0
        else:
            if pathExists(filePath):
                try:
                    from ast import literal_eval
                    import codecs
                    with codecs.open(filePath, encoding='utf-16') as f:
                        data = f.read()
                    data = literal_eval(data)
                    if data['id'] != KBLayoutId:
                        vkLayoutItem = self.getKeyboardLayoutItem(KBLayoutId)
                        raise Exception(_(kblayout_loading_error) % vkLayoutItem[0])
                        return 1
                    self.saveActive_keylayout(KBLayoutId)
                    self.LoadVKLayout_callback(data)
                    return 0
                except ImportError as e:
                    print(e)
            else:
                loadErrorNo = 2
            return loadErrorNo

    def getKeyboardLayoutItem(self, KBLayoutId):
        retItem = None
        for item in self.KbLayouts:
            if KBLayoutId == item[2]:
                retItem = item
                break
        return retItem

    def getKeyboardLayoutFlag(self, KBLayoutId):
        lang = self.getKeyboardLayoutItem(KBLayoutId)

        try:
            lang = lang[1]
        except:
            lang = 'missing'

        if isFHD():
            flag = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/flagshd/") + str(lang) + '.png'

            if not pathExists(flag):
                flag = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/flagshd/missing.png")
            
        else:
            flag = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/flags/") + str(lang) + '.png'

            if not pathExists(flag):
                flag = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/flags/missing.png")

        return flag


class LanguageListScreen(Screen, KBLayoutLanguages):

    def __init__(self, session, listValue=[], selIdx=None, loadVKLayout_callback=None):
        Screen.__init__(self, session)
        self.loadVKLayout_callback = loadVKLayout_callback
        KBLayoutLanguages.__init__(self, LoadVKLayout_callback=self.loadVKLayout_callback)
        self.skin = Skin_LanguageListScreen
        self.skinName = 'LanguageListScreen'
        self['languageList'] = languageSelectionList()
        self['actions'] = ActionMap(['ColorActions', 'WizardActions'], {
            'back': self.close,
            'ok': self.keyok,
        }, -1)
        self['info'] = Label(' ')
        self.languageList = self['languageList']
        self.languageList.onSelectionChanged.append(self.listselectionChanged)
        self.listselectionChanged = self.languageList.selectionChanged
        self.listValue = listValue
        self.selIdx = selIdx
        self.lastdownloaded_index = None
        self.onShown.append(self.settitle)
        return

    def settitle(self):
        self.setTitle(_("Language selection"))
        self.showLanguageList()

    def listselectionChanged(self):
        cur = self.languageList.getCurrent()
        id = cur['val'][2]
        langFile = str(vkLayoutDir) + str(id) + ".kle"
        if pathExists(langFile):
            self['info'].setText(_('Press ok to remove language'))
        else:
            self['info'].setText(_('Press ok to install language'))

    def showLanguageList(self, index=None):
        self.languageList.setList(self.listValue)
        self.languageList.setSelectionState(True)
        if index is not None:
            self.languageList.moveToIndex(index)
        elif self.selIdx is not None:
            self.languageList.moveToIndex(self.selIdx)
        else:
            self.languageList.moveToIndex(0)
        self.languageList.show()
        return

    def keyok(self):
        index = self.languageList.getCurrentIndex()
        cur = self.languageList.getCurrent()
        KBLayoutId = cur['val'][2]
        langFile = str(vkLayoutDir) + str(KBLayoutId) + ".kle"
        if pathExists(langFile):
            os.remove(langFile)
            self.showLanguageList(index)
            self['info'].setText(_('Language removed from installed package'))
            activeKBLayoutId = self.getActive_keylayout()
            if activeKBLayoutId == KBLayoutId:
                KBLayoutId = self.getDefault_KBLayout()
            else:
                KBLayoutId = activeKBLayoutId
                self.setActive_Layout(KBLayoutId)
        else:
            index = self.languageList.getCurrentIndex()
            ret = self.downloadKBlayout(KBLayoutId)
            if ret:
                self.showLanguageList(index)
                self['info'].setText(_('Language downloaded successfully ,exit to install'))
                self.setActive_Layout(KBLayoutId)
            else:
                self['info'].setText(_('Failed to download language,try later'))

    def exit(self):
        self.close()


class eConnectCallbackObj:
    OBJ_ID = 0
    OBJ_NUM = 0

    def __init__(self, obj=None, connectHandler=None):
        eConnectCallbackObj.OBJ_ID += 1
        eConnectCallbackObj.OBJ_NUM += 1
        self.objID = eConnectCallbackObj.OBJ_ID
        self.connectHandler = connectHandler
        self.obj = obj

    def __del__(self):
        eConnectCallbackObj.OBJ_NUM -= 1
        try:
            if 'connect' not in dir(self.obj):
                if 'get' in dir(self.obj):
                    self.obj.get().remove(self.connectHandler)
                else:
                    self.obj.remove(self.connectHandler)
            else:
                del self.connectHandler
        except Exception:
            pass
        self.connectHandler = None
        self.obj = None


def eConnectCallback(obj, callbackFun, withExcept=False):
    try:
        if 'connect' in dir(obj):
            return eConnectCallbackObj(obj, obj.connect(callbackFun))
        if 'get' in dir(obj):
            obj.get().append(callbackFun)
        else:
            obj.append(callbackFun)
        return eConnectCallbackObj(obj, callbackFun)
    except Exception:
        pass
    return eConnectCallbackObj()


def TranslateTXT(txt):
    return txt


_ = TranslateTXT


def mkdirs(newdir, raiseException=False):
    try:
        if os.path.isdir(newdir):
            pass
        elif os.path.isfile(newdir):
            raise OSError("cannot create directory, file already exists: '%s'" % newdir)
        else:
            head, tail = os.path.split(newdir)
            if head and not os.path.isdir(head) and not os.path.ismount(head) and not os.path.islink(head):
                mkdirs(head)
            if tail:
                os.mkdir(newdir)
        return True
    except Exception as e:
        if raiseException:
            raise e
    return False


def GetSystemLang(int=False):
    if int:
        try:
            defaultLanguage = language.getActiveLanguage()
        except Exception:
            defaultLanguage = 'en_EN'
    else:
        try:
            defaultLanguage = language.getActiveLanguage().split('_')[0]
        except Exception:
            defaultLanguage = 'en'

    return defaultLanguage


class textINput(Input):

    def __init__(self, *args, **kwargs):
        self.nvkTimeoutCallback = None
        Input.__init__(self, *args, **kwargs)
        return

    def timeout(self, *args, **kwargs):
        """
        callCallback = False
        try:
            callCallback = True if self.lastKey != -1 else False
        except Exception:
            pass
            """
        try:
            Input.timeout(self, *args, **kwargs)
        except Exception:
            pass
        if self.nvkTimeoutCallback:
            self.nvkTimeoutCallback()


class textInputSuggestions():

    def __init__(self, callback=None, hl='en'):
        self.hl = hl
        self.conn = None
        self.callback = callback
        return

    def prepareQuery(self):
        self.prepQuerry = '/complete/search?output=chrome&client=chrome&'
        if self.hl is not None:
            self.prepQuerry = self.prepQuerry + 'hl=' + self.hl + '&'
        self.prepQuerry = self.prepQuerry + 'jsonp=self.gotSuggestions&q='
        return

    def dataError(self, error):
        print('unable to get suggestion')
        self.callback([])

    def parseGoogleData(self, output):
        charsetCode = {'ar': 'windows-1256', 'ky': 'windows-1251', 'ru': 'windows-1251', 'el': 'windows-1253', 'tr': 'windows-1254', 'fa': 'windows-1256'}
        try:
            if output:
                data = output
                charset = charsetCode.get(self.hl, None)
                if charset:
                    try:
                        if PY3:
                            data = data.decode(charset)
                        else:
                            data = str(data.decode(charset)).encode('utf-8')
                    except:
                        pass
                else:
                    if PY3:
                        data = data.decode("utf-8")
                    else:
                        data = data.encode("utf-8")
                list = data.split(',')
                data2 = []
                for item in list:
                    if self.queryString in item:
                        item = item.replace('"', '').replace('[', '').replace(']', '').replace('self.gotSuggestions(', '')
                        data2.append(item)
                self.setGoogleSuggestions(data2)
            else:
                self.callback([])
        except:
            pass
        return

    def getGoogleSuggestions(self, queryString, hl='en'):
        self.hl = hl
        self.prepareQuery()
        self.queryString = queryString
        from twisted.internet import reactor
        from twisted.web.client import getPage
        self.reactor = reactor
        if queryString:
            query = self.prepQuerry + compat_quote(queryString)
            url = 'http://www.google.com' + query
            url = 'http://suggestqueries.google.com/complete/search?output=firefox&hl=%s&gl=%s%s&q=%s' % (self.hl, self.hl, '&ds=yt' if True else '', compat_quote(queryString))
            getPage(str.encode(url), headers={b'Content-Type': b'application/x-www-form-urlencoded'}).addCallback(self.parseGoogleData).addErrback(self.dataError)
        else:
            return []

    def displaySearchHistory(self, word=None):
        try:
            if not os.path.exists(hfile):
                return []
            lines = open(hfile).readlines()
            list1 = []
            if len(lines) == 0:
                return []
            if word and word != '':
                word = word.lower().strip()
                for line in lines:
                    line = line.strip()
                    if line != '':
                        if line.startswith(word):
                            list1.insert(0, line)
                        else:
                            list1.append(line)
            if not word or word.strip() == '':
                for line in lines:
                    line = line.strip()
                    list1.append(line)
            return list1
        except:
            pass

    def clearSearchHistory(self):
        if os.path.exists(hfile):
            os.remove(hfile)
            return

    def saveSearchHistory(self, txt):
        try:
            txt = txt.strip()
            if txt == '':
                return
            if os.path.exists(hfile) is False:
                f = open(hfile, 'w')
                f.write(txt)
                f.close()
                return
            with open(hfile, 'r+') as file:
                for line in file:
                    line = line.strip()
                    if line == '':
                        continue
                    if txt == line:
                        return
                file.write('\n' + txt)
        except:
            print('error writing to history')


class selectList(GUIComponent, object):

    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setBuildFunc(self.buildEntry)
        self.onSelectionChanged = []
        if isFHD():
            fontSize = 30 + FONTSSIZE
            itemHeight = 39 + FONTSSIZE
        else:
            fontSize = 20 + FONTSSIZE
            itemHeight = 26 + FONTSSIZE
        self.font = ('Regular', fontSize, itemHeight, 0)
        self.l.setFont(0, gFont('Regular', fontSize))
        self.l.setFont(1, gFont(self.font[0], self.font[1]))
        self.l.setItemHeight(self.font[2])
        self.dictPIX = {}

    def onCreate(self):
        pass

    def onDestroy(self):
        pass

    def connectSelChanged(self, fnc):
        if fnc not in self.onSelectionChanged:
            self.onSelectionChanged.append(fnc)

    def disconnectSelChanged(self, fnc):
        if fnc in self.onSelectionChanged:
            self.onSelectionChanged.remove(fnc)

    def selectionChanged(self):
        for x in self.onSelectionChanged:
            x()

    def getCurrent(self):
        cur = self.l.getCurrentSelection()
        return cur and cur[0]

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        self.selectionChanged_conn = eConnectCallback(instance.selectionChanged, self.selectionChanged)
        self.onCreate()

    def preWidgetRemove(self, instance):
        instance.setContent(None)
        self.selectionChanged_conn = None
        self.onDestroy()
        return

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def setList(self, list):
        self.l.setList(list)

    def setSelectionState(self, enabled):
        self.instance.setSelectionEnable(enabled)

    def buildEntry(self, item):
        res = [None]
        width = self.l.getItemSize().width()
        height = self.l.getItemSize().height()
        
        if isFHD():
            try:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 21, 0, width - 42, height, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, item))
            except Exception:
                pass
            return res
        else:
            try:
                res.append((eListboxPythonMultiContent.TYPE_TEXT, 14, 0, width - 28, height, 1, RT_HALIGN_LEFT|RT_VALIGN_CENTER, item))
            except Exception:
                pass
            return res  
               
    GUI_WIDGET = eListbox
    currentIndex = property(getCurrentIndex, moveToIndex)
    currentSelection = property(getCurrent)


class createPixmap(Pixmap):

    def __init__(self):
        Pixmap.__init__(self)
        self.visible = True

    def setPixmap(self, ptr):
        self.instance.setPixmap(ptr)


class kb_layoutComponent:

    def __init__(self):
        self.SK_NONE = 0
        self.SK_SHIFT = 1
        self.SK_CTRL = 2
        self.SK_ALT = 4
        self.SK_CAPSLOCK = 8
        self.LEFT_KEYS = [1, 0x10, 30, 43, 56]
        self.RIGHT_KEYS = [15, 29, 42, 55, 62]
        self.KbLayouts = KbLayouts

    def createKID(self):
        self.keyidMap = KBlayoutKeyID
        self.defaultKBLAYOUT = defaultKBLAYOUT

    def drawKeyMap(self):
        self.keys_pixmap = {}
        self.FHDSkin = getDesktop(0).size().width() == 1920
        for key in kbSkeysList:
            self.keys_pixmap[key] = LoadPixmap(iconsDir('nvk_hd/%s.png' if self.FHDSkin else 'nvk/%s.png') % key)
        for i in range(0, 63):
            try:
                self[str(i)] = createPixmap()
            except:
                pass
        for key in pixmapKeys:
            self[key] = createPixmap()

        for i in range(1, 63):
            self['_%s' % i] = Label(' ')


        for m in range(3):
            self['m_%d' % m] = Label(' ')

            
        self.keys_pixmapMap = SkeysMap
        self.markerMap = markerMap
        self.colMax = len(self.keyidMap[0])
        self.rowMax = len(self.keyidMap)
        self.rowIdx = 0
        self.colIdx = 0
        self.colors = colors
        self.specialKeyState = self.SK_NONE


class NewVirtualKeyBoard(Screen, textInputSuggestions, kb_layoutComponent, KBLayoutLanguages):

    def __init__(self, session, title='', text=''):
        self.session = session
        self.focus_constants()
        kb_layoutComponent.__init__(self)
        KBLayoutLanguages.__init__(self, LoadVKLayout_callback=self.loadVKLayout)
        self.createKID()
        self.drawKeyMap()
        self.KBsettings = config.NewVirtualKeyBoard
        if text.strip() == '':
            text = self.KBsettings.lastsearchText.value
        try:
            self.showsuggestion = self.KBsettings.showsuggestion.value
        except:
            self.showsuggestion = True
        self.showHistory = self.showsuggestion
        self.showHistory = self.showsuggestion
        self.googleSuggestionList = []
        self.skin = Skin_NewVirtualKeyBoard
        self.skinName = 'NewVirtualKeyBoard'
        Screen.__init__(self, session)
        textInputSuggestions.__init__(self, callback=self.setGoogleSuggestions)
        self.beforeUpdateText = ''
        self.onLayoutFinish.append(self.loadKBpixmaps)
        self.onShown.append(self.onWindowShow)
        self.onClose.append(self.__onClose)
        self['suggestionList'] = selectList()
        self['actions'] = self.getActionMap()
        self['historyheader'] = Label(' ')
        self['historyList'] = selectList()
        self.getinstalledkeylayout()
        self.counter = 0
        self['suggestionheader'] = Label(' ')
        self['historyheader'] = Label(' ')
        self.header = title if title else _('NewVirtualKeyBoard  V %s' % VER)
        self.startText = text
        self['text'] = textINput(text=text)
        self['header'] = Label(' ')
        self['flag'] = Pixmap()
        self.currentVKLayout = self.defaultKBLAYOUT
        self.selectedKBLayoutId = self.KBsettings.keys_layout.value
        if PY3:
            self.emptykey = ''
        else:
            self.emptykey = u''
        self.vkRequestedId = ''
        self.focus = self.keyboard_hasfocus

    def getActionMap(self):
        return NumberActionMap(['WizardActions', 'DirectionActions', 'ColorActions', 'KeyboardInputActions', 'InputBoxActions', 'InputAsciiActions', 'SetupActions', 'MenuActions'], {
            'gotAsciiCode': self.keyGotAscii,
            'ok': self.keyOK,
            'ok_repeat': self.keyOK,
            'back': self.keyBack,
            'left': self.keyLeft,
            'right': self.keyRight,
            'up': self.keyUp,
            'down': self.keyDown,
            'red': self.keyRed,
            'red_repeat': self.keyRed,
            'green': self.keyGreen,
            'yellow': self.switchinstalledvklayout,
            'blue': self.togglesfocus,
            'deleteBackward': self.backClicked,
            'deleteForward': self.forwardClicked,
            'pageUp': self.insertSpace,
            'menu': self.listmenuoptions,
            'info': self.showHelp,
            'pageDown': self.clearText,
            '1': self.keyNumberGlobal,
            '2': self.keyNumberGlobal,
            '3': self.keyNumberGlobal,
            '4': self.keyNumberGlobal,
            '5': self.keyNumberGlobal,
            '6': self.keyNumberGlobal,
            '7': self.keyNumberGlobal,
            '8': self.keyNumberGlobal,
            '9': self.keyNumberGlobal,
            '0': self.keyNumberGlobal,
        }, -2)

    def onWindowShow(self):
        self.searchHistoryList = self.displaySearchHistory()
        self.showSearchHistory()
        self.onShown.remove(self.onWindowShow)
        self.setTitle(_('New Virtual Keyboard'))
        self['header'].setText(self.header)
        self['historyList'].setSelectionState(False)
        self['historyheader'].setText('Search history')
        self['suggestionList'].setSelectionState(False)
        self['suggestionheader'].setText('Google suggestions')
        self.setSuggestionVisible()
        self.isshowsuggestionEnabled = self.showsuggestion
        self.setText(self.startText)
        self.loadKBLayout()
        if self.KBsettings.firsttime.value is True:
            self.KBsettings.firsttime.value = False
            self.KBsettings.firsttime.save()
            self.showHelp()

    def __onClose(self):
        self.onClose.remove(self.__onClose)
        self['text'].nvkTimeoutCallback = None
        if self.selectedKBLayoutId != self.KBsettings.keys_layout.value:
            self.KBsettings.keys_layout.value = self.selectedKBLayoutId
            self.KBsettings.keys_layout.save()
            configfile.save()
        return

    def focus_constants(self):
        self.history_hasfocus = 1
        self.keyboard_hasfocus = 0
        self.suggestion_hasfocus = 2

    def clearText(self):
        self['text'].deleteAllChars()
        self['text'].update()
        self.input_updated()

    def insertSpace(self):
        self.processKeyId(59)

    def loadKBLayout(self):
        KBLayoutId = self.vkRequestedId if self.vkRequestedId else self.selectedKBLayoutId
        KBLayoutId = self.getDefault_KBLayout(KBLayoutId)
        if not self.getKeyboardLayoutItem(KBLayoutId):
            KBLayoutId = self.selectedKBLayoutId
        self.getKeyboardLayout(KBLayoutId)

    def setText(self, text):
        self['text'].setText(text)
        self['text'].right()
        if PY3:
            self['text'].currPos = len(text)
        else:
            self['text'].currPos = len(text.decode('utf-8'))
        self['text'].right()
        self.input_updated()

    def loadKBpixmaps(self):
        self.onLayoutFinish.remove(self.loadKBpixmaps)
        self['text'].nvkTimeoutCallback = self.input_updated
        for i in range(0, 63):
            key = self.keys_pixmapMap.get(str(i), 'vkey_single')
            self[str(i)].setPixmap(self.keys_pixmap[key])
        for key in ['vkey_text_sel', 'vkey_single_sel', 'vkey_double_sel', 'vkey_space_sel']:
            self[key].hide()
            self[key].setPixmap(self.keys_pixmap[key])
        self['vkey_backspace'].setPixmap(self.keys_pixmap['vkey_backspace'])
        self['vkey_delete'].setPixmap(self.keys_pixmap['vkey_delete'])
        self['vkey_left'].setPixmap(self.keys_pixmap['vkey_left'])
        self['vkey_right'].setPixmap(self.keys_pixmap['vkey_right'])
        self.currentKeyId = self.keyidMap[self.rowIdx][self.colIdx]
        self.move_KMarker(-1, self.currentKeyId)
        self.showSpecialText()

    def showSpecialText(self):
        self['_1'].setText('Esc')
        self['_16'].setText(_('Clear'))
        # self['_29'].setText('Del')
        self['_30'].setText('Caps')
        self['_42'].setText('Enter')
        self['_43'].setText('Shift')
        self['_55'].setText('Shift')
        self['_57'].setText('Ctrl')
        self['_58'].setText('Alt')
        self['_60'].setText('Alt')
        
        """
        if PY3:
            self['_61'].setText('\u2190')
            self['_62'].setText('\u2192')
        else:
            self['_61'].setText('\u2190'.encode('utf-8'))
            self['_62'].setText('\u2192'.encode('utf-8'))
            """

    def processArrowKey(self, dx=0, dy=0):
        oldKeyId = self.keyidMap[self.rowIdx][self.colIdx]
        keyID = oldKeyId
        if dx != 0 and keyID == 0:
            return
        if dx != 0:
            colIdx = self.colIdx
            while True:
                colIdx += dx
                if colIdx < 0:
                    colIdx = self.colMax - 1
                elif colIdx >= self.colMax:
                    colIdx = 0
                if keyID != self.keyidMap[self.rowIdx][colIdx]:
                    self.colIdx = colIdx
                    break
        elif dy != 0:
            rowIdx = self.rowIdx
            while True:
                rowIdx += dy
                if rowIdx < 0:
                    rowIdx = self.rowMax - 1
                elif rowIdx >= self.rowMax:
                    rowIdx = 0
                if keyID != self.keyidMap[rowIdx][self.colIdx]:
                    self.rowIdx = rowIdx
                    break
        if dx != 0:
            keyID = self.keyidMap[self.rowIdx][self.colIdx]
            maxKeyX = self.colIdx
            for idx in range(self.colIdx + 1, self.colMax):
                if keyID == self.keyidMap[self.rowIdx][idx]:
                    maxKeyX = idx
                else:
                    break
            minKeyX = self.colIdx
            for idx in range(self.colIdx - 1, -1, -1):
                if keyID == self.keyidMap[self.rowIdx][idx]:
                    minKeyX = idx
                else:
                    break
            if maxKeyX - minKeyX > 2:
                if PY3:
                    self.colIdx = int((maxKeyX + minKeyX) / 2)
                else:
                    self.colIdx = (maxKeyX + minKeyX) / 2
        self.currentKeyId = self.keyidMap[self.rowIdx][self.colIdx]
        self.move_KMarker(oldKeyId, self.currentKeyId)

    def move_KMarker(self, oldKeyId, newKeyId):
        if oldKeyId == -1 and newKeyId == -1:
            for key in ['vkey_text_sel', 'vkey_single_sel', 'vkey_double_sel', 'vkey_space_sel']:
                self[key].hide()
            return
        if oldKeyId != -1:
            keyid = str(oldKeyId)
            marker = self.markerMap.get(keyid, 'vkey_single_sel')
            self[marker].hide()
        if newKeyId != -1:
            keyid = str(newKeyId)
            marker = self.markerMap.get(keyid, 'vkey_single_sel')
            self[marker].instance.move(ePoint(self[keyid].position[0], self[keyid].position[1]))
            self[marker].show()

    def processKeyId(self, keyid):
        if keyid == 0:
            keyid = 42
        if keyid == 1:
            if self.emptykey:
                if PY3:
                    self.emptykey = ''
                else:
                    self.emptykey = u''
                self.updateKsText()
            else:
                self.close(None)
            return
        elif keyid == 15:
            self['text'].deleteBackward()
            self.input_updated()
            return
        elif keyid == 29:
            self['text'].delete()
            self.input_updated()
            return
        elif keyid == 16:
            self['text'].deleteAllChars()
            self['text'].update()
            self.input_updated()
            return
        elif keyid == 56:
            self.switchToLanguageSelection()
            return
        elif keyid == 61:
            self['text'].left()
            return
        elif keyid == 62:
            self['text'].right()
            return
        elif keyid == 42:
            try:
                if PY3:
                    text = self['text'].getText()
                else:
                    text = self['text'].getText().decode('UTF-8').encode('UTF-8')
            except Exception:
                text = ''
                pass
            if text.strip() != '':
                self.saveSearchHistory(text)
                self.KBsettings.lastsearchText.value = text
                self.KBsettings.lastsearchText.save()
            self.close(text)
            return
        elif keyid == 30:
            self.specialKeyState ^= self.SK_CAPSLOCK
            self.updateKsText()
            self.updateSKey([30], self.specialKeyState & self.SK_CAPSLOCK)
            return
        elif keyid in [43, 55]:
            self.specialKeyState ^= self.SK_SHIFT
            self.updateKsText()
            self.updateSKey([43, 55], self.specialKeyState & self.SK_SHIFT)
            return
        elif keyid in [58, 60]:
            self.specialKeyState ^= self.SK_ALT
            self.updateKsText()
            self.updateSKey([58, 60], self.specialKeyState & self.SK_ALT)
            return
        elif keyid == 57:
            self.specialKeyState ^= self.SK_CTRL
            self.updateKsText()
            self.updateSKey([57], self.specialKeyState & self.SK_CTRL)
            return
        else:
            updateKsText = False
            ret = 0
            if PY3:
                text = ''
            else:
                text = u''
            val = self.getKeyChar(keyid)
            if val:
                for special in [(self.SK_CTRL, [57]), (self.SK_ALT, [58, 60]), (self.SK_SHIFT, [43, 55])]:
                    if self.specialKeyState & special[0]:
                        self.specialKeyState ^= special[0]
                        self.updateSKey(special[1], 0)
                        ret = None
                        updateKsText = True
            if val:
                if self.emptykey:
                    if val in self.currentVKLayout['deadkeys'].get(self.emptykey, {}):
                        text = self.currentVKLayout['deadkeys'][self.emptykey][val]
                    else:
                        text = self.emptykey + val
                    if PY3:
                        self.emptykey = ''
                    else:
                        self.emptykey = u''
                    updateKsText = True
                elif val in self.currentVKLayout['deadkeys']:
                    self.emptykey = val
                    updateKsText = True
                else:
                    text = val
                self.insertText(text)
                ret = None
            if updateKsText:
                self.updateKsText()
            return ret
            return

    def getinstalledkeylayout(self):
        path = vkLayoutDir
        import os.path
        try:
            self.KBLayoutId_installed = [f for f in os.listdir(path) if os.path.isfile(f)]
        except:
            self.KBLayoutId_installed = []
        if os.path.exists(path):
            for x in os.listdir(path):
                item = os.path.join(path, x)
                if os.path.isfile(item):
                    layoutid = x.replace('.kle', '')
                    self.KBLayoutId_installed.append(layoutid)
        else:
            self.KBLayoutId_installed = []

    def switchinstalledvklayout(self):
        try:
            self.counter = self.counter + 1
            if self.counter > len(self.KBLayoutId_installed) - 1:
                self.counter = 0
            if self.counter < 0:
                self.counter = len(self.KBLayoutId_installed) - 1
            KBLayoutId = self.KBLayoutId_installed[self.counter]
            self.selectedKBLayoutId = KBLayoutId
            self.getKeyboardLayout(KBLayoutId)
        except:
            pass

    def getKeyboardLayout(self, KBLayoutId):
        ret = self.setActive_Layout(KBLayoutId)
        if ret == 1:
            vkLayoutItem = self.getKeyboardLayoutItem(KBLayoutId)
            self.session.open(MessageBox, text=_(kblayout_loading_error) % vkLayoutItem[0], type=MessageBox.TYPE_ERROR)
            return
        if ret == 2:
            success = self.downloadKBlayout(KBLayoutId)
            if not success:
                self.loadVKLayout(self.defaultKBLAYOUT)
        self.displayActiveLayoutFlag(KBLayoutId)

    def displayActiveLayoutFlag(self, KBLayoutId):
        flag = self.getKeyboardLayoutFlag(KBLayoutId)
        self['flag'].instance.setPixmapFromFile(flag)
        self['flag'].instance.show()

    def loadVKLayout(self, layout=None):
        if layout:
            self.currentVKLayout = layout
        self.updateKsText()
        if PY3:
            self['_56'].setText(self.currentVKLayout['locale'].split('-', 1)[0].upper())
        else:
            self['_56'].setText(self.currentVKLayout['locale'].encode('UTF-8').split('-', 1)[0].upper())
        self['_56'].show()

    def updateSKey(self, keysidTab, state):
        if state:
            color = self.colors['color0']
        else:
            color = self.colors['color1']
        for keyid in keysidTab:
            self['_%s' % keyid].instance.setForegroundColor(color)

    def getKeyChar(self, keyid):
        state = self.specialKeyState
        if self.specialKeyState & self.SK_ALT and not self.specialKeyState & self.SK_CTRL:
            state ^= self.SK_CTRL
        key = self.currentVKLayout['layout'].get(keyid, {})
        if state in key:
            val = key[state]
        else:
            if PY3:
                val = ''
            else:
                val = u''
        return val

    def updateNormalKText(self, keyid):
        val = self.getKeyChar(keyid)
        if not self.emptykey:
            if len(val) > 1:
                color = self.colors['color2']
            elif val in self.currentVKLayout['deadkeys']:
                color = self.colors['color3']
            else:
                color = self.colors['color1']
        elif val in self.currentVKLayout['deadkeys'].get(self.emptykey, {}):
            val = self.currentVKLayout['deadkeys'][self.emptykey][val]
            color = self.colors['color1']
        else:
            color = self.colors['color4']
        skinKey = self['_%s' % keyid]
        skinKey.instance.setForegroundColor(color)
        if PY3:
            skinKey.setText(val)
        else:
            skinKey.setText(val.encode('utf-8'))

    def updateKsText(self):
        for rangeItem in [(2, 14), (17, 28), (31, 41), (44, 54), (59, 59)]:
            for keyid in range(rangeItem[0], rangeItem[1] + 1):
                self.updateNormalKText(keyid)

    def showSearchHistory(self):
        if self.showHistory:
            leftList = self['historyList']
            leftList.setList([(x, ) for x in self.searchHistoryList])
            leftList.moveToIndex(0)
            leftList.show()
            self['historyheader'].setText(_('Search history'))
            self['historyheader'].show()

    def hideLefList(self):
        self['historyheader'].hide()
        self['historyList'].hide()
        self['historyList'].setList([])

    def switchToLanguageSelection(self):
        selIdx = None
        listValue = []
        for i in range(len(self.KbLayouts)):
            x = self.KbLayouts[i]
            if self.currentVKLayout['id'] == x[2]:
                sel = True
                selIdx = i
            else:
                sel = False
            listValue.append(({'sel': sel, 'val': x}, ))
        try:
            self.session.openWithCallback(self.languageSelectionBack, LanguageListScreen, listValue, selIdx, self.loadVKLayout)
        except:
            print ("switchToLanguageSelection error")
        return

    def languageSelectionBack(self, index=None):
        self.selectedKBLayoutId = self.getActive_keylayout()
        self.getKeyboardLayout(self.selectedKBLayoutId)
        self.switchToKayboard()

    def togglesfocus(self):
        if self.showsuggestion is False:
            return
        if self.focus == self.keyboard_hasfocus and self.googleSuggestionList != []:
            self.switchToGoogleSuggestions()
        elif self.focus == self.keyboard_hasfocus and self.googleSuggestionList == [] and self.searchHistoryList != []:
            self.switchToSearchHistory()
        elif self.focus == self.suggestion_hasfocus and self.searchHistoryList != []:
            self.switchToSearchHistory()
        elif self.focus == self.suggestion_hasfocus and self.searchHistoryList == [] and self.googleSuggestionList != []:
            self.switchToGoogleSuggestions()
        elif self.focus == self.history_hasfocus:
            self.switchToKayboard()

    def switchToKayboard(self):
        self.setFocus(self.keyboard_hasfocus)
        self.move_KMarker(-1, self.currentKeyId)

    def switchToGoogleSuggestions(self):
        if self.showsuggestion is True:
            self.setFocus(self.suggestion_hasfocus)
            self['suggestionList'].moveToIndex(0)
            self['suggestionList'].setSelectionState(True)
        else:
            self.switchToKayboard()

    def switchToSearchHistory(self):
        if self.showsuggestion is True:
            self.setFocus(self.history_hasfocus)
            self['historyList'].moveToIndex(0)
            self['historyList'].setSelectionState(True)
        else:
            self.switchToKayboard()

    def setFocus(self, focus):
        self['text'].timeout()
        if self.focus != focus:
            if self.focus == self.keyboard_hasfocus:
                self.move_KMarker(-1, -1)
            elif self.focus == self.suggestion_hasfocus:
                self['suggestionList'].setSelectionState(False)
            elif self.focus == self.history_hasfocus:
                self['historyList'].setSelectionState(False)
            self.focus = focus

    def keyRed(self):
        if self.focus == self.keyboard_hasfocus:
            self.processKeyId(15)
        else:
            return 0

    def keyGreen(self):
        self.processKeyId(42)

    def keyYellow(self):
        if self.focus == self.keyboard_hasfocus:
            self.processKeyId(60)
        else:
            return 0

    def keyBlue(self):
        if self.focus == self.keyboard_hasfocus:
            self.processKeyId(43)
        else:
            return 0

    def keyOK(self):
        if self.focus in (self.suggestion_hasfocus, self.history_hasfocus):
            text = self['suggestionList' if self.focus == self.suggestion_hasfocus else 'historyList'].getCurrent()
            if text:
                self.setText(text)
            self.currentKeyId = 0
            self.rowIdx = 0
            self.colIdx = 7
            self.switchToKayboard()
        elif self.focus == self.keyboard_hasfocus:
            self.processKeyId(self.currentKeyId)
        else:
            return 0

    def keyBack(self):
        if self.focus == self.keyboard_hasfocus:
            if self.emptykey:
                if PY3:
                    self.emptykey = ''
                else:
                    self.emptykey = u''
                self.updateKsText()
            else:
                self.saveActive_keylayout(self.selectedKBLayoutId)
                self.close(None)
        elif self.focus in (self.suggestion_hasfocus, self.history_hasfocus):
            self.switchToKayboard()
        else:
            return 0
        return

    def keyUp(self):
        if self.focus == self.keyboard_hasfocus:
            self.processArrowKey(0, -1)
        elif self.focus == self.history_hasfocus:
            item = self['historyList']
            if item.instance is not None:
                item.instance.moveSelection(item.instance.moveUp)
        elif self.focus == self.suggestion_hasfocus:
            item = self['suggestionList']
            if item.instance is not None:
                item.instance.moveSelection(item.instance.moveUp)
        else:
            return 0
        return

    def keyDown(self):
        if self.focus == self.keyboard_hasfocus:
            self.processArrowKey(0, 1)
        elif self.focus == self.history_hasfocus:
            item = self['historyList']
            if item.instance is not None:
                item.instance.moveSelection(item.instance.moveDown)
        elif self.focus == self.suggestion_hasfocus:
            item = self['suggestionList']
            if item.instance is not None:
                item.instance.moveSelection(item.instance.moveDown)
        else:
            return 0
        return

    def keyLeft(self):
        if self.focus == self.history_hasfocus:
            if self.showsuggestion:
                self.switchToGoogleSuggestions()
            else:
                self.switchToKayboard()
                if self.currentKeyId in self.LEFT_KEYS:
                    self.processArrowKey(-1, 0)
        elif self.focus == self.suggestion_hasfocus:
            self.switchToKayboard()
            if self.currentKeyId in self.LEFT_KEYS:
                self.processArrowKey(-1, 0)
        elif self.focus == self.keyboard_hasfocus:
            if self.currentKeyId in self.LEFT_KEYS or self.currentKeyId == 0 and self['text'].currPos == 0:
                if self.showHistory and self.showsuggestion is True:
                    self.switchToSearchHistory()
                    return
                if self.showsuggestion is True:
                    self.switchToGoogleSuggestions()
                    return
            if self.currentKeyId == 0:
                self['text'].left()
            else:
                self.processArrowKey(-1, 0)
        else:
            return 0

    def keyRight(self):
        if self.focus == self.history_hasfocus:
            self.switchToKayboard()
            if self.currentKeyId in self.RIGHT_KEYS:
                self.processArrowKey(1, 0)
        elif self.focus == self.suggestion_hasfocus:
            if self.showHistory:
                self.switchToSearchHistory()
            else:
                self.switchToKayboard()
                if self.currentKeyId in self.RIGHT_KEYS:
                    self.processArrowKey(1, 0)
        elif self.focus == self.keyboard_hasfocus:
            if self.currentKeyId in self.RIGHT_KEYS or self.currentKeyId == 0 and self['text'].currPos == len(self['text'].text):
                if self.showsuggestion:
                    self.switchToGoogleSuggestions()
                    return
                if self.showHistory:
                    self.switchToSearchHistory()
                    return
            if self.currentKeyId == 0:
                self['text'].right()
            else:
                self.processArrowKey(1, 0)
        else:
            return 0

    def cursorRight(self):
        if self.focus == self.keyboard_hasfocus:
            self.processKeyId(62)
        else:
            return 0

    def cursorLeft(self):
        if self.focus == self.keyboard_hasfocus:
            self.processKeyId(61)
        else:
            return 0

    def backClicked(self):
        if self.focus == self.keyboard_hasfocus:
            self.processKeyId(15)
        else:
            return 0

    def forwardClicked(self):
        if self.focus == self.keyboard_hasfocus:
            self.processKeyId(29)
        else:
            return 0

    def keyNumberGlobal(self, number):
        if self.currentKeyId == 0:
            try:
                self['text'].number(number)
            except Exception:
                pass

    def keyGotAscii(self):
        if self.currentKeyId == 0:
            try:
                self['text'].handleAscii(getPrevAsciiCode())
            except Exception:
                pass

    def setSuggestionVisible(self):
        if self.showsuggestion is True:
            self['suggestionheader'].show()
            self['suggestionList'].show()
            self['historyheader'].show()
            self['historyList'].show()
            self.showSearchHistory()
        else:
            self['suggestionheader'].hide()
            self['historyheader'].hide()
            self['suggestionList'].hide()
            self['historyList'].hide()

    def insertText(self, text):
        for letter in text:
            try:
                self['text'].insertChar(letter, self['text'].currPos, False, True)
                try:
                	self['text'].innerRight() # py3
                except:
                	self['text'].innerright() # py3
                self['text'].update()
            except Exception:
                pass
        self.input_updated()

    def input_updated(self):
        #if self['text'].text == self.beforeUpdateText:
        #    return
        #else:
        #    self.beforeUpdateText = self['text'].text
        self.updateGHSuggestions()

    def updateGHSuggestions(self):
        if not self['text'].text:
            self.setSuggestionVisible()
            self['suggestionList'].setList([])
        else:
            self.getsuggestion()

    def getsuggestion(self):
        word = self['text'].getText()
        list1 = self.displaySearchHistory(word)
        self.searchHistoryList = list1
        if list1:
            self['historyList'].setList([(x, ) for x in list1])
        lang = self.getKeyboardLayoutItem(self.selectedKBLayoutId)
        try:
            lang = lang[1].split('_')[0]
        except:
            lang = 'en'
        self.getGoogleSuggestions(word, hl=lang)

    def setGoogleSuggestions(self, list=[]):
        self.googleSuggestionList = list
        if list:
            self['suggestionList'].setList([(x, ) for x in list])
        self.setSuggestionVisible()

    def listmenuoptions(self):

        def getmenuData():
            menuData = []
            menuData.append((0, 'Install language', 'flag'))
            menuData.append((1, 'Clear history', 'history'))
            menuData.append((2, 'Settings', 'settings'))
            return menuData

        def optionsback(index=None):
            if index == 0:
                self.switchToLanguageSelection()
            elif index == 2:
                from Plugins.SystemPlugins.NewVirtualKeyBoard.setup import nvKeyboardSetup
                self.session.openWithCallback(self.settings_back, nvKeyboardSetup)
                return
            if index == 1:
                self.clearSearchHistory()
                self['historyList'].setList([])
        self.session.openWithCallback(optionsback, vkOptionsScreen, _('select task'), getmenuData())
        return

    def settings_back(self, result=None):
        if result:
            self.showsuggestion = self.KBsettings.showsuggestion.value
            self.setSuggestionVisible()

    def showHelp(self):

        def getmenuData():
            menuData = []
            menuData.append((0, 'Yellow - Switch language', 'key_yellow'))
            menuData.append((1, 'Blue - Toggle focus between suggestions & keyboard', 'key_blue'))
            menuData.append((2, 'Menu - Show more functions - Install languages...', 'key_menu'))
            menuData.append((3, 'Info - Show this screen again', 'key_info'))
            menuData.append((4, 'Page Up - Insert space', 'key_plus'))
            menuData.append((5, 'Page Down - Clear input text', 'key_minus'))
            return menuData

        def optionsback(index=None):
            return
        self.session.openWithCallback(optionsback, vkOptionsScreen, _('Help'), getmenuData())
        return


class vkOptionsScreen(Screen):

    def __init__(self, session, title, datalist=[]):
        Screen.__init__(self, session)
        self.skin = Skin_vkOptionsScreen
        self.skinName = 'vkOptionsScreen'
        self['menu'] = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self['actions'] = ActionMap(['ColorActions', 'WizardActions'], {
            'back': self.close,
            'ok': self.exit
        }, -1)
        self.settitle(title, datalist)

    def settitle(self, title, datalist):
        self.setTitle(title)
        self.showmenulist(datalist)

    def exit(self):
        index = self['menu'].getSelectionIndex()
        self.close(index)

    def showmenulist(self, datalist):
        cbcolor = 16753920
        cccolor = 15657130
        scolor = cbcolor
        res = []
        menulist = []
        if not isFHD():
            self['menu'].l.setItemHeight(48)
            self['menu'].l.setFont(0, gFont('Regular', 20))
        else:
            self['menu'].l.setItemHeight(72)
            self['menu'].l.setFont(0, gFont('Regular', 30))
        for i in range(0, len(datalist)):
            txt = datalist[i][1]
            if not isFHD():
                png = os.path.join(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/icons/menus/hd/%s.png") % datalist[i][2])
            else:
                png = os.path.join(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NewVirtualKeyBoard/skins/icons/menus/fhd/%s.png") % datalist[i][2])
            res.append(MultiContentEntryText(pos=(0, 1), size=(0, 0), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text='', color=scolor, color_sel=cccolor, border_width=3, border_color=806544))
            if not isFHD():
                res.append(MultiContentEntryText(pos=(60, 0), size=(723, 48), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=str(txt), color=16777215, color_sel=16777215))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(20, 12), size=(25, 25), png=loadPNG(png)))
            else:
                res.append(MultiContentEntryText(pos=(100, 0), size=(1080, 72), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER | RT_WRAP, text=str(txt), color=16777215, color_sel=16777215))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(30, 17), size=(38, 38), png=loadPNG(png)))
            menulist.append(res)
            res = []
        self['menu'].l.setList(menulist)
        self['menu'].show()

# name, iso code, kle code
KbLayouts = [
    ('Arabic', 'ar_AE', '00000401'),
    ('Bulgarian', 'bg_BG', '00030402'),
    ('Czech', 'cs_CZ', '00000405'),
    ('Danish', 'da_DK', '00000406'),
    ('German', 'de_DE', '00000407'),
    ('Greek', 'el_GR', '00000408'),
    ('United Kingdom', 'en_GB', '00000809'),
    ('United States', 'en_US', '00020409'),
    ('Spanish', 'es_ES', '0000040a'),
    ('Estonian', 'et_EE', '00000425'),
    ('Faeroese', 'fo_FO', '00000438'),
    ('Finnish', 'fi_FI', '0000040b'),
    ('French', 'fr_FR', '0000040c'),
    ('Hebrew', 'he_IL', '0000040d'),
    ('Croatian', 'hr_HR', '0000041a'),
    ('Hungarian', 'hu_HU', '0000040e'),
    ('Icelandic', 'is_IS', '0000040f'),
    ('Italian', 'it_IT', '00000410'),
    ('Lithuanian', 'lt_LT', '00010427'),
    ('Latvian', 'lv_LV', '00000426'),
    ('Norwegian', 'nb_NO', '00000414'),
    ('Dutch', 'nl_NL', '00000413'),
    ('Polish (214)', 'pl_PL', '00010415'),
    ('Portuguese (Brazilian)', 'pt_BR', '00000416'),
    ('Portuguese', 'pt_PT', '00000816'),
    ('Romanian', 'ro_RO', '00010418'),
    ('Russian', 'ru_RU', '00000419'),
    ('Slovak', 'sk_SK', '0000041b'),
    ('Slovenian', 'sl_SI', '00000424'),
    ('Serbian (Cyrillic)', 'sr_YU', '00000c1a'),
    ('Serbian (Latin)', 'sr_YU', '0000081a'),
    ('Swedish', 'sv_SE', '0000041d'),
    ('Thai Kedmanee', 'th_TH', '0000041e'),
    ('Turkish', 'tr_TR', '0000041f'),
    ('Ukrainian', 'uk_UA', '00020422')
]


defaultKBLAYOUT = {
    'layout': {
        2: {0: u'`', 1: u'~', 8: u'`', 9: u'~'},
        3: {0: u'1', 1: u'!', 6: u'\xa1', 7: u'\xb9', 8: u'1', 9: u'!', 14: u'\xa1', 15: u'\xb9'},
        4: {0: u'2', 1: u'@', 6: u'\xb2', 8: u'2', 9: u'@', 14: u'\xb2'},
        5: {0: u'3', 1: u'#', 6: u'\xb3', 8: u'3', 9: u'#', 14: u'\xb3'},
        6: {0: u'4', 1: u'$', 6: u'\xa4', 7: u'\xa3', 8: u'4', 9: u'$', 14: u'\xa4', 15: u'\xa3'},
        7: {0: u'5', 1: u'%', 6: u'\u20ac', 8: u'5', 9: u'%', 14: u'\u20ac'},
        8: {0: u'6', 1: u'^', 6: u'\xbc', 8: u'6', 9: u'^', 14: u'\xbc'},
        9: {0: u'7', 1: u'&', 6: u'\xbd', 8: u'7', 9: u'&', 14: u'\xbd'},
        10: {0: u'8', 1: u'*', 6: u'\xbe', 8: u'8', 9: u'*', 14: u'\xbe'},
        11: {0: u'9', 1: u'(', 6: u'\u2018', 8: u'9', 9: u'(', 14: u'\u2018'},
        12: {0: u'0', 1: u')', 6: u'\u2019', 8: u'0', 9: u')', 14: u'\u2019'},
        13: {0: u'-', 1: u'_', 6: u'\xa5', 8: u'-', 9: u'_', 14: u'\xa5'},
        14: {0: u'=', 1: u'+', 6: u'\xd7', 7: u'\xf7', 8: u'=', 9: u'+', 14: u'\xd7', 15: u'\xf7'},
        17: {0: u'q', 1: u'Q', 6: u'\xe4', 7: u'\xc4', 8: u'Q', 9: u'q', 14: u'\xc4', 15: u'\xe4'},
        18: {0: u'w', 1: u'W', 6: u'\xe5', 7: u'\xc5', 8: u'W', 9: u'w', 14: u'\xc5', 15: u'\xe5'},
        19: {0: u'e', 1: u'E', 6: u'\xe9', 7: u'\xc9', 8: u'E', 9: u'e', 14: u'\xc9', 15: u'\xe9'},
        20: {0: u'r', 1: u'R', 6: u'\xae', 8: u'R', 9: u'r', 14: u'\xae'},
        21: {0: u't', 1: u'T', 6: u'\xfe', 7: u'\xde', 8: u'T', 9: u't', 14: u'\xde', 15: u'\xfe'},
        22: {0: u'y', 1: u'Y', 6: u'\xfc', 7: u'\xdc', 8: u'Y', 9: u'y', 14: u'\xdc', 15: u'\xfc'},
        23: {0: u'u', 1: u'U', 6: u'\xfa', 7: u'\xda', 8: u'U', 9: u'u', 14: u'\xda', 15: u'\xfa'},
        24: {0: u'i', 1: u'I', 6: u'\xed', 7: u'\xcd', 8: u'I', 9: u'i', 14: u'\xcd', 15: u'\xed'},
        25: {0: u'o', 1: u'O', 6: u'\xf3', 7: u'\xd3', 8: u'O', 9: u'o', 14: u'\xd3', 15: u'\xf3'},
        26: {0: u'p', 1: u'P', 6: u'\xf6', 7: u'\xd6', 8: u'P', 9: u'p', 14: u'\xd6', 15: u'\xf6'},
        27: {0: u'[', 1: u'{', 2: u'\x1b', 6: u'\xab', 8: u'[', 9: u'{', 10: u'\x1b', 14: u'\xab'},
        28: {0: u']', 1: u'}', 2: u'\x1d', 6: u'\xbb', 8: u']', 9: u'}', 10: u'\x1d', 14: u'\xbb'},
        31: {0: u'a', 1: u'A', 6: u'\xe1', 7: u'\xc1', 8: u'A', 9: u'a', 14: u'\xc1', 15: u'\xe1'},
        32: {0: u's', 1: u'S', 6: u'\xdf', 7: u'\xa7', 8: u'S', 9: u's', 14: u'\xa7', 15: u'\xdf'},
        33: {0: u'd', 1: u'D', 6: u'\xf0', 7: u'\xd0', 8: u'D', 9: u'd', 14: u'\xd0', 15: u'\xf0'},
        34: {0: u'f', 1: u'F', 8: u'F', 9: u'f'},
        35: {0: u'g', 1: u'G', 8: u'G', 9: u'g'},
        36: {0: u'h', 1: u'H', 8: u'H', 9: u'h'},
        37: {0: u'j', 1: u'J', 8: u'J', 9: u'j'},
        38: {0: u'k', 1: u'K', 8: u'K', 9: u'k'},
        39: {0: u'l', 1: u'L', 6: u'\xf8', 7: u'\xd8', 8: u'L', 9: u'l', 14: u'\xd8', 15: u'\xf8'},
        40: {0: u';', 1: u':', 6: u'\xb6', 7: u'\xb0', 8: u';', 9: u':', 14: u'\xb6', 15: u'\xb0'},
        41: {0: u"'", 1: u'"', 6: u'\xb4', 7: u'\xa8', 8: u"'", 9: u'"', 14: u'\xb4', 15: u'\xa8'},
        44: {0: u'z', 1: u'Z', 6: u'\xe6', 7: u'\xc6', 8: u'Z', 9: u'z', 14: u'\xc6', 15: u'\xe6'},
        45: {0: u'x', 1: u'X', 8: u'X', 9: u'x'},
        46: {0: u'c', 1: u'C', 6: u'\xa9', 7: u'\xa2', 8: u'C', 9: u'c', 14: u'\xa2', 15: u'\xa9'},
        47: {0: u'v', 1: u'V', 8: u'V', 9: u'v'},
        48: {0: u'b', 1: u'B', 8: u'B', 9: u'b'},
        49: {0: u'n', 1: u'N', 6: u'\xf1', 7: u'\xd1', 8: u'N', 9: u'n', 14: u'\xd1', 15: u'\xf1'},
        50: {0: u'm', 1: u'M', 6: u'\xb5', 8: u'M', 9: u'm', 14: u'\xb5'},
        51: {0: u',', 1: u'<', 6: u'\xe7', 7: u'\xc7'},
        52: {0: u'.', 1: u'>', 8: u'.', 9: u'>'},
        53: {0: u'/', 1: u'?', 6: u'\xbf', 8: u'/', 9: u'?', 14: u'\xbf'},
        54: {0: u'\\', 1: u'|', 2: u'\x1c', 6: u'\xac', 7: u'\xa6', 8: u'\\', 9: u'|', 10: u'\x1c', 14: u'\xac', 15: u'\xa6'},
        59: {0: u' ', 1: u' ', 2: u' ', 8: u' ', 9: u' ', 10: u' '}},
    'name': u'United Kingdom',
    'locale': u'en-UK',
    'id': u'00000809',
    'deadkeys': {
        u'~': {
            u'a': u'\xe3',
            u'A': u'\xc3',
            u' ': u'~',
            u'O': u'\xd5',
            u'N': u'\xd1',
            u'o': u'\xf5',
            u'n': u'\xf1',
            },
        u'`': {
            u'a': u'\xe0',
            u'A': u'\xc0',
            u'e': u'\xe8',
            u' ': u'`',
            u'i': u'\xec',
            u'o': u'\xf2',
            u'I': u'\xcc',
            u'u': u'\xf9',
            u'O': u'\xd2',
            u'E': u'\xc8',
            u'U': u'\xd9',
            },
        u'"': {
            u'a': u'\xe4',
            u'A': u'\xc4',
            u'e': u'\xeb',
            u' ': u'"',
            u'i': u'\xef',
            u'o': u'\xf6',
            u'I': u'\xcf',
            u'u': u'\xfc',
            u'O': u'\xd6',
            u'y': u'\xff',
            u'E': u'\xcb',
            u'U': u'\xdc',
            },
        u"'": {
            u'a': u'\xe1',
            u'A': u'\xc1',
            u'c': u'\xe7',
            u'e': u'\xe9',
            u' ': u"'",
            u'i': u'\xed',
            u'C': u'\xc7',
            u'o': u'\xf3',
            u'I': u'\xcd',
            u'u': u'\xfa',
            u'O': u'\xd3',
            u'y': u'\xfd',
            u'E': u'\xc9',
            u'U': u'\xda',
            u'Y': u'\xdd',
            },
        u'^': {
            u'a': u'\xe2',
            u'A': u'\xc2',
            u'e': u'\xea',
            u' ': u'^',
            u'i': u'\xee',
            u'o': u'\xf4',
            u'I': u'\xce',
            u'u': u'\xfb',
            u'O': u'\xd4',
            u'E': u'\xca',
            u'U': u'\xdb',
            },
        },
    'desc': u'United Kingdom'}

KBlayoutKeyID = [(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                 (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15),
                 (16, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29),
                 (30, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 42),
                 (43, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 55),
                 (56, 56, 57, 58, 59, 59, 59, 59, 59, 59, 59, 59, 60, 61, 62)]

kbSkeysList = [
'vkey_country',
'vkey_backspace',
'vkey_text',
'vkey_text_sel',
'vkey_single',
'vkey_single_sel',
'vkey_modifier',
'vkey_double_sel',
'vkey_double',
'vkey_space',
'vkey_space_sel',
'vkey_left',
'vkey_right',
'vkey_delete'
]

pixmapKeys = [
'vkey_country',
'vkey_backspace',
'vkey_text_sel',
'vkey_single_sel',
'vkey_double_sel',
'vkey_space_sel',
'vkey_left',
'vkey_right',
'vkey_delete'
]

SkeysMap = {
    '0': 'vkey_text',  # text box
    '1': 'vkey_modifier',  # esc
    '15': 'vkey_modifier',  # backspace
    '29': 'vkey_modifier',  # del
    '57': 'vkey_modifier',  # ctrl l
    '58': 'vkey_modifier',  # alt l
    '60': 'vkey_modifier',  # alr r
    '61': 'vkey_modifier',  # <--
    '62': 'vkey_modifier',  # -->
    '59': 'vkey_space',  # space
    '16': 'vkey_double',  # clear
    '30': 'vkey_double',  # caps
    '42': 'vkey_double',  # enter
    '43': 'vkey_double',  # shift l
    '55': 'vkey_double',  # shift r
    '56': 'vkey_double',  # country
}

markerMap = {
    '0': 'vkey_text_sel',
    '59': 'vkey_space_sel',
    '16': 'vkey_double_sel',
    '30': 'vkey_double_sel',
    '42': 'vkey_double_sel',
    '43': 'vkey_double_sel',
    '55': 'vkey_double_sel',
    '56': 'vkey_double_sel',
}

colors = {
    'color1': gRGB(int('ffffff', 0x10)),  # white
    'color0': gRGB(int('39b54a', 0x10)),  # green
    'color3': gRGB(int('0275a0', 0x10)),  # blue
    'color2': gRGB(int('ed1c24', 0x10)),  # red
    'color4': gRGB(int('979697', 0x10)),  # grey
}

VirtualKeyBoard = NewVirtualKeyBoard
