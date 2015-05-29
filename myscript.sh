#! /bin/sh
cd dump1090 &&
./dump1090 --net &
sleep 2 &&
cd &&
rm -rf data.dat &&
while true
do
	sudo python adsb.py &&
	sleep 5
done

exit