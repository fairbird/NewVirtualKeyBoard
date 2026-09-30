SUMMARY = "NewVirtualKeyBoard - replacement virtual keyboard for enigma2"
DESCRIPTION = "NewVirtualKeyBoard plugin by mfaraj57 & RAED"
MAINTAINER = "RAED - fairbird"
LICENSE = "GPL-3.0-only"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/GPL-3.0-only;md5=c79ff39f19dfec6d293b95dea7b07891"

SRC_URI = "git://github.com/fairbird/NewVirtualKeyBoard;protocol=https;branch=main"
SRCREV = "${AUTOREV}"
S = "${WORKDIR}/git"

# pure Python + images, nothing to build (no distutils/setup.py any more)
inherit gitpkgv allarch

PV = "13.10+git"
PKGV = "13.10+git${GITPKGV}"

PLUGINDIR = "${libdir}/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard"

do_configure[noexec] = "1"
do_compile[noexec] = "1"

do_install() {
	install -d ${D}${libdir}/enigma2/python/Plugins/SystemPlugins
	cp -r ${S}/usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard ${D}${libdir}/enigma2/python/Plugins/SystemPlugins/
	# translation sources stay in the repo, the box needs the .mo files only
	rm -f ${D}${PLUGINDIR}/locale/*.pot ${D}${PLUGINDIR}/locale/updateallpo.sh ${D}${PLUGINDIR}/locale/*/LC_MESSAGES/*.po
}

FILES:${PN} = "${PLUGINDIR}"

# the new keyboard selected in the saved settings (a restore after a new
# image): replace the image keyboard again (same script as CI/postinst.sh)
pkg_postinst:${PN}() {
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
}

# the plugin can replace Screens/VirtualKeyBoard.py by a symlink into its
# folder - put the image's keyboard back before the folder is removed, or
# enigma2 fails to import Screens.VirtualKeyBoard (same script as
# CI/prerm.sh, only an upgrade keeps the keyboard replacement)
pkg_prerm:${PN}() {
#!/bin/sh
case "$1" in
	upgrade|failed-upgrade) exit 0 ;;
esac
S=$D/usr/lib/enigma2/python/Screens
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
}
