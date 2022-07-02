#!/bin/sh
##setup command=wget http://tunisia-dreambox.info/TSplugins/NewVirtualKeyBoard/subsinstaller.sh -O - | /bin/sh

if [ ! -d /usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard ]; then
	echo
	echo
	echo "*** NewVirtualKeyBoard No found ... Will be install first ***"
	echo
	echo
	wget http://tunisia-dreambox.info/TSplugins/NewVirtualKeyBoard/installer.sh -O - | /bin/sh
fi

cd /tmp 
if [ -d /usr/lib/enigma2/python/Plugins/Extensions/SubsSupport ]; then
	wget "http://tunisia-dreambox.info/TSplugins/NewVirtualKeyBoard/subtitles.py"
	rm -f /usr/lib/enigma2/python/Plugins/Extensions/SubsSupport/subtitles.py > /dev/null 2>&1
	mv subtitles.py /usr/lib/enigma2/python/Plugins/Extensions/SubsSupport  > /dev/null 2>&1
fi
cd ..

sync
echo
echo "#########################################################"
echo "#             PLEASE RESTART YOUR STB                   #"
echo "##########################################################"

exit 0
