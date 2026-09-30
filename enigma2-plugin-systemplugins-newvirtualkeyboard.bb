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

PV = "13.9+git"
PKGV = "13.9+git${GITPKGV}"

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
