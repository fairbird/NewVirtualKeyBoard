#!/bin/sh
##setup command=wget https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/subsinstaller.sh -O - | /bin/sh

if [ ! -d /usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard ]; then
	echo
	echo
	echo "*** NewVirtualKeyBoard No found ... Will be install first ***"
	echo
	echo
	wget https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/installer.sh -O - | /bin/sh
fi

cd /tmp 
if [ -d /usr/lib/enigma2/python/Plugins/Extensions/SubsSupport ]; then
	wget "https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/subtitles.py"
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
