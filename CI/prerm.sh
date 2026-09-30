#!/bin/sh
# prerm of the ipk/deb (CI/build_packages.py); the .bb has the same script
# (tests/test_keyboard.py checks that). The plugin may have replaced
# Screens/VirtualKeyBoard.py by a symlink into its folder - put the image's
# keyboard back when the package is removed, or enigma2 fails to import
# Screens.VirtualKeyBoard. Not on an upgrade: the new version keeps the link.
case "$1" in
	upgrade|failed-upgrade) exit 0 ;;
esac
S=/usr/lib/enigma2/python/Screens
if [ -L $S/VirtualKeyBoard.py ]; then
	rm -f $S/VirtualKeyBoard.py
	for e in py pyo pyc; do
		if [ -e $S/VirtualKeyBoard_backup.$e ]; then
			mv $S/VirtualKeyBoard_backup.$e $S/VirtualKeyBoard.$e
			break
		fi
	done
fi
exit 0
