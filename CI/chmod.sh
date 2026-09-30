#!/bin/sh

echo ""
echo "chmod safe cleanup by Persian Prince"
# Script by Persian Prince for https://github.com/OpenVisionE2
# You're not allowed to remove my copyright or reuse this script without putting this header.
echo ""
echo "Changing py files, please wait ..." 
begin=$(date +"%s")

echo ""
echo "chmod files"
find . -path ./.git -prune -o -type d -print0 | xargs -0 chmod 0755
find . -path ./.git -prune -o -type f -print0 | xargs -0 chmod 0644
find . -path ./.git -prune -o -type f -name "*.sh" -exec chmod +x {} \;
git add -u
git add *
git commit -m "chmod files"

echo ""
finish=$(date +"%s")
timediff=$(($finish-$begin))
printf 'Change time was %d minutes and %d seconds.\n' $((timediff / 60)) $((timediff % 60))
printf 'Fast changing would be less than 1 minute.\n'
echo ""
echo "chmod Done!"
echo ""
