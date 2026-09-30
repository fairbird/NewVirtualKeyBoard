#!/bin/sh
# postinst of the ipk/deb (CI/build_packages.py); the .bb has the same script
# and installer.sh runs it too (tests/test_keyboard.py checks that). Not
# while an image is built ($D set).
[ -n "$D" ] && exit 0
P=/usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard
S=/usr/lib/enigma2/python/Screens
# leftovers of versions installed with installer.sh before 13.9
rm -rf $P/language $P/language_config.py* $P/compat.py* $P/skins/NewVirtualKeyBoard*.py* $P/skins/__init__.py* $P/skins/icons/vk
# the new keyboard was selected before (settings restored after a new image
# or a reinstall): replace the image keyboard again, like the setup does
if grep -q '^config.NewVirtualKeyBoard.textinput=NewVirtualKeyBoard$' /etc/enigma2/settings 2>/dev/null && [ ! -L $S/VirtualKeyBoard.py ]; then
	for e in py pyo pyc; do
		if [ -e $S/VirtualKeyBoard.$e ]; then
			mv -f $S/VirtualKeyBoard.$e $S/VirtualKeyBoard_backup.$e
			break
		fi
	done
	rm -f $S/VirtualKeyBoard.pyo $S/VirtualKeyBoard.pyc
	ln -s $P/VirtualKeyBoard.py $S/VirtualKeyBoard.py
	echo "NewVirtualKeyBoard installed - the new keyboard is selected (as in the saved settings), restart enigma2"
else
	echo "NewVirtualKeyBoard installed - restart enigma2 and select the new keyboard in Menu > System > NewVirtualKeyBoard setup"
fi
exit 0
