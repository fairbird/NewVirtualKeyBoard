import os
from gettext import bindtextdomain, dgettext, gettext

from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS

# a fresh log per enigma2 start
try:
    os.remove('/tmp/VirtualKeyBoard.log')
except OSError:
    pass

# translations: the same gettext setup as other enigma2 plugins -
# locale/<lang>/LC_MESSAGES/NewVirtualKeyBoard.mo, following the enigma2
# language; texts the plugin doesn't translate itself fall back to enigma2's
PluginLanguageDomain = "NewVirtualKeyBoard"
PluginLanguagePath = "SystemPlugins/NewVirtualKeyBoard/locale"


def localeInit():
    bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


def _(txt):
    t = dgettext(PluginLanguageDomain, txt)
    if t == txt:
        t = gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)
