#!/bin/bash
##setup command=wget https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/installer.sh -O - | /bin/sh
###########
version=13.0
# remove old version
cp -r /usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard/skins/kle /tmp/ >/dev/null 2>&1
rm -rf /usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyboard >/dev/null 2>&1
#rm -f /usr/lib/enigma2/python/Screens/NewVirtualKeyBoard.py > /dev/null 2>&1
#rm -f /usr/lib/enigma2/python/Screens/NewVirtualKeyBoard.pyo > /dev/null 2>&1
#rm -f /usr/lib/enigma2/python/Screens/NewVirtualKeyBoard.pyc > /dev/null 2>&1
# Download and install plugin
echo " ** Download and install NewVirtualKeyBoard ** "
cd /tmp
set -e
rm -rf *main* >/dev/null 2>&1
rm -rf *NewVirtualKeyBoard* >/dev/null 2>&1
wget "https://github.com/fairbird/NewVirtualKeyBoard/archive/refs/heads/main.tar.gz"
tar -xzf main.tar.gz
cp -r NewVirtualKeyBoard-main/usr /
if [ -f '/tmp/kle' ]; then
	cp -f /tmp/kle/* /usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard/skins/kle
fi
rm -rf /tmp/kle >/dev/null 2>&1
rm -rf *NewVirtualKeyBoard* >/dev/null 2>&1
rm -rf *main* >/dev/null 2>&1
echo
echo
set +e
cd ..

### Check if plugin installed correctly
if [ ! -d '/usr/lib/enigma2/python/Plugins/SystemPlugins/NewVirtualKeyBoard' ]; then
	echo "Some thing wrong .. Plugin not installed"
	exit 1
fi

if [ -d /usr/lib/enigma2/python/Plugins/Extensions/SubsSupport ]; then
	wget "https://raw.githubusercontent.com/fairbird/NewVirtualKeyBoard/main/subtitles.py"
	rm -f /usr/lib/enigma2/python/Plugins/Extensions/SubsSupport/subtitles.py >/dev/null 2>&1
	mv subtitles.py /usr/lib/enigma2/python/Plugins/Extensions/SubsSupport >/dev/null 2>&1
fi

sync
echo
echo
echo "###########################################################################"
echo "#                 NewVirtualKeyBoard INSTALLED SUCCESSFULLY               #"
echo "#                       mfaraj57 & RAED (fairbird)                        #"
echo "#                               support                                   #"
echo "#                         ttps://www.tunisia-sat.com                      #"
echo "#  restart enigma2 and select New virtual keyboard setup from menu-system #"
echo "###########################################################################"
echo
killall enigma2
exit 0
