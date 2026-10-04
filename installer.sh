#!/bin/sh
##setup command=wget https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/installer.sh -O - | /bin/sh
###########
version="14.0"
description="
What is NEW :
- all 218 Windows keyboard layouts, drawn like the real keyboard (ISO 48 keys)
- numeric keypad for number fields, key help for all keys
- YELLOW = AltGr, BLUE = Shift, TEXT = language, PVR = switch lists
- MENU opens the settings directly, search history size (1-99999)
- more settings (font size, alignment, flags, background, suggestions)
- search suggestions: Google, YouTube, Bing, DuckDuckGo, IMDb
- translations follow the enigma2 language (gettext)
- WQHD support, fixes for openATV and Python 2 images
"

PLUGINPATH=/usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard
TMPDIR=/tmp/NewVirtualKeyBoard_update

# Download and check first - the box is only touched when the download is ok
echo " ** Download and install NewVirtualKeyBoard ** "
rm -rf "$TMPDIR"
mkdir -p "$TMPDIR"
cd "$TMPDIR" || exit 1
if ! wget -q "https://github.com/fairbird/NewVirtualKeyBoard/archive/refs/heads/main.tar.gz" -O main.tar.gz \
   || ! tar -xzf main.tar.gz \
   || [ ! -f "NewVirtualKeyBoard-main$PLUGINPATH/VirtualKeyBoard.py" ]; then
	echo "Download failed .. nothing was changed"
	cd /tmp
	rm -rf "$TMPDIR"
	exit 1
fi

# No full wipe: Screens/VirtualKeyBoard.py may be a symlink into the plugin
# folder and skins/kle/ holds the user's downloaded layouts. Remove only what
# 13.9 dropped and stale compiled files.
rm -rf "$PLUGINPATH/language" "$PLUGINPATH"/language_config.py* "$PLUGINPATH"/compat.py* \
	"$PLUGINPATH"/skins/NewVirtualKeyBoard*.py* "$PLUGINPATH"/skins/__init__.py* "$PLUGINPATH/skins/icons/vk"
for tier in hd fhd wqhd; do
	rm -f "$PLUGINPATH/skins/icons/menus/$tier/flag.png" "$PLUGINPATH/skins/icons/menus/$tier/history.png" "$PLUGINPATH/skins/icons/menus/$tier/settings.png"
done
for tier in nvk nvk_hd nvk_wqhd; do
	for name in key_red key_green key_yellow key_blue key_plus key_minus vkey_country; do
		rm -f "$PLUGINPATH/skins/icons/$tier/$name.png"
	done
done
find "$PLUGINPATH" -name '*.py[co]' -exec rm -f {} \; 2>/dev/null
find "$PLUGINPATH" -type d -name __pycache__ -prune -exec rm -rf {} \; 2>/dev/null

# the translation sources are not needed on the box, only the .mo files
find "NewVirtualKeyBoard-main$PLUGINPATH/locale" \( -name '*.po' -o -name '*.pot' -o -name '*.sh' \) -exec rm -f {} \; 2>/dev/null
if ! cp -r "NewVirtualKeyBoard-main/usr" /; then
	echo "Copying the files failed .. the plugin may be incomplete, run the installer again"
	cd /tmp
	rm -rf "$TMPDIR"
	exit 1
fi
cd /tmp
rm -rf "$TMPDIR"

### Check if plugin installed correctly
if [ ! -f "$PLUGINPATH/VirtualKeyBoard.py" ]; then
	echo "Some thing wrong .. Plugin not installed"
	exit 1
fi

sync
echo
echo
echo "###########################################################################"
echo "#                 NewVirtualKeyBoard INSTALLED SUCCESSFULLY               #"
echo "#                       mfaraj57 & RAED (fairbird)                        #"
echo "#                               support                                   #"
echo "#                         https://www.tunisia-sat.com                     #"
echo "#  restart enigma2 and select New virtual keyboard setup from menu-system #"
echo "###########################################################################"
echo
killall enigma2
exit 0
