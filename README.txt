This document describes the process of collecting, processing and plotting ADS-B data
received from nearby aircraft. Contact reddit.com/u/aarkebauer with any questions.

------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------

Overview

I use a Raspberry Pi to collect and store the raw ADS-B data in a file. Data is collected
using an inexpensive USB SDR antenna and is stored in the data file at 5 second intervals.
A wide array of such antennas are available, and the one I use is the NooElec NESDR Mini
SDR & DVB-T USB Stick.
(http://www.nooelec.com/store/computer-peripherals/usb-ota-receivers/dvb-t-receivers/nesdr
- mini-rtl2832-r820t.html)

I then transfer this data file to my computer, where I have a bash script that deletes the
'data' folder in the current directory (explained below) and then runs a python program
(dump1090plot.py) that takes creates a new file containing all data collected for each
individual aircraft. The names of these files are the ICAO hex codes of the aircraft, and
they are stored in a folder labeled 'data'. The program then looks at each of these files,
makes lists of all position values (latitude, longitude, altitude) and filters out any
"bad points," which I define as any points at which either altitude, latitude, or
longitude data was NOT collected. The same python program then plots each of these lists
of positions using matplotlib.

There are several options that can be set in this program. They are described below, and
are contained (with descriptions) within the program itself around line 155.

Detailed descriptions of the setup and processes that occur are presented below.

------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------

Raspberry Pi

Several items must be installed on the Raspberry Pi prior to collecting data. First,
I installed dump1090, which will decode the ADS-B data obtained by the receiver (so named
because ADS-B is broadcast at 1090 MHz). The following is the process I used to install
this via command line on the Pi:

sudo apt-get update
sudo apt-get upgrade
sudo su				# to avoid writing sudo at the beginning of the following 6 commands
<The following is one line>
printf 'blacklist dvb_usb_rtl28xxu\nblacklist rtl2832\nblacklist rtl2830' > /etc/modprobe.d/nortl.conf
apt-get install git-core
apt-get install git
apt-get install cmake
apt-get install libusb-1.0-0-dev  
apt-get install build-essential 
git clone git://git.osmocom.org/rtl-sdr.git
cd rtl-sdr
mkdir build
cd build
cmake ../ -DINSTALL_UDEV_RULES=ON
make
make install										# must be run as root
ldconfig											# must be run as root
cd ~
cp ./rtl-sdr/rtl-sdr.rules /etc/udev/rules.d/		# must be run as root
reboot												# must be run as root
<It will reboot>
rtl_test -t
cd ~ 
git clone git://github.com/MalcolmRobb/dump1090.git
cd dump1090
make
apt-get install pkg-config							# must be run as root
make


After this is installed, I would suggest reading through the README.md file in the
dump1090 directory. This contains many useful commands and additional information.

To run dump1090 in the terminal window and collect ADS-B in real time from nearby
aircraft, run the following command while in the dump1090 directory:

./dump1090 --interactive

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

Next, I installed an Apache web server on the Pi. Although an internet connection is NOT
required for any part of this process, the data obtained from dump1090 is stored at
http://localhost:8080/data.json and to access it, you need to be able to navigate to this
page.

The following is the process I used to install this via command line on the Pi:

sudo apt-get install apache2 php5 libapache2-mod-php5

sudo service apache2 restart

Now you can view dump1090 as follows:
	On RasPi: navigate to localhost:8080
	On computer (if connected to internet): navigate to [pi's ip address]:8080
	To view the latest raw data: add /data.json to the end of the above addresses
	
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

With these two items now installed, I wrote the following small program in python and
saved it to the home directory (/home/pi) as adsb.py

This program is used to collect (only) the latest set of ADS-B data from the file
described above. It then writes this to a file called "data.dat" in the same directory.

I also wrote the myscript.sh script in order to delete the previous data.dat file (This is
VERY important, as the above program simply appends new data to the old file, so if it
is not deleted old data will be plotted in addition to the new) as well as run the above
program every 5 seconds.

Make sure it is executable (using this command): chmod +x myscript.sh

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

I then start the script (begin recording data) using the following command: ./myscript
(Make sure the antenna is plugged into a USB port!)

To kill stop collecting data, I simply kill the script with control+C (elegant, I know).

Note: The file 'data.dat' grows at ~1.5 MB per hour for light to moderate air traffic.

------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------

Computer (OS X, but it should work for anything)

Make sure to have python and matplotlib installed on your computer. Instructions for
installation of these can be found fairly easily on the internet, so they are not included
here.

First, I transferred the file 'data.dat' from the Raspberry Pi to my computer. There are
a few methods of doing this, but I ssh'd into my Pi from my computer (instructions for
doing so are also readily available by doing some googling.) and used FileZilla for the
transfer.

In the SAME directory as the file titled 'data.dat' (it is important that this file name
is maintained), I wrote a python program titled 'dump1090plot.py' and a bash script titled
'plot.sh'. (Again, important that these file names are maintained if you use the same
procedure as the one I describe here)

The program (~ 400 lines) and script (6 lines) are copied and pasted in this document, and
if this is on github, hopefully are able to be downloaded easily.



TO RUN THE PROGRAM AND MAKE THE PLOT: simply execute plot.sh from the command line (in
the same directory as the script, run this command: ./plot.sh) Remember first to make the
script executable by running this command: chmod +x plot.sh. Instructions for making
an OS X application are included below.

If any crazy flight paths appear, dump1090 may have decoded information incorrectly.
To remedy this, delete all lines in 'data.dat' that contain the hex code of that flight.
The hex code can often be determined by looking at the flight number on the plot, then
going to 'data.dat' and looking at the hex number that corresponds to this flight number.
Running the following in the command line will delete all lines containing the hex number:

grep -v [hex number] data.dat > data.dat



Note: If you don't use this script, make sure a folder titled 'data' is present in the
same directory.

There are several settings within the program, dump1090plot.py, that can be altered
to customize the plot and its rotation.


The first set of settings (~ line 153) contain the following:

*****IMPORTANT*****IMPORTANT*****IMPORTANT*****IMPORTANT*****IMPORTANT*****IMPORTANT******
The first settings are current latitude and longitude. These are used to center the plot
on your location. It is important that these are correct in order to obtain a reasonable
plot.

The rest of the settings in this set are described in the program, but are repeated here
for convenience:

	# SET THESE LINES TO CURRENT LATITUDE AND LONGITUDE TO CENTER GRAPH
	currentlatitude = xxxxxxx		# Home is xxxxxxx
	currentlongitude = xxxxxxx	# Home is xxxxxxx

	# If the following is set to True it will plot from z = 0
	# If set to False it will plot from z = [minimum altitude] - 1000 ft
	plot_from_ground_level = False

	# The following is used to only plot flights under a certain altitude
	# Set this to float('inf') in order to see all flights
	only_plot_flights_under_this_altitude = float('inf') # to plot all: float('inf')

	# Setting this to True prints out the flight numbers for each plotted line
	# Setting this to False does not display flight numbers
	display_flight_number_labels = True

	# Set the following to True to plot planes WITHOUT flight number data
	# Set it to False to plot ONLY those planes WITH flight number data
	plot_planes_without_flight_numbers = False

	# If set to True planes with flight numbers containing only numbers
	# (e.g. 1653) will be displayed. If set to False then ONLY flight
	# numbers beginning with letters (e.g. UAL1653) will be displayed
	plot_planes_with_number_only_flight_numbers = True

	# Values used to change plot animation parameters are defined below #

	# If set to True all flight numbers will be printed to a document
	# titled flight_numbers.dat. If false, it will not make this file
	print_flight_number_file = False


The next set of settings (~ line 378) deal with the animation of the plot (it rotates):

	# ANIMATION PARAMETERS:
	speed = 1.5 # This is the speed at which the plot rotates. *** Higher numbers = slower ***
	revolutions = 3 # This is the number of revolutions that the plot will complete

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

The python program 'dump1090plot.py' does several things. First (in the createfiles
function), it takes the 'data.dat' file and makes a file for each aircraft that was picked
up. The file is stored in the folder titled 'data' and the filename is the ICAO hex code
of the aircraft. In the file is stored the following information (on separate lines)

Hex code
Flight number
Latitude
Longitude
Altitude
Track (Heading)
Speed

for each time (remember, collected data was written to 'data.dat' every five seconds)
the dump1090 program collected a valid latitude, longitude, AND altitude. An empty
line separates each set of data.

The program then (in the the plot function) opens each of these files (one by one) and
puts the contained data into several dictionaries, called allalts, alllats, allflights, 
and alllons. The keys are just ascending integers (one for each plane), and the values
are lists of the altitudes, latitudes, flight numbers, and longitudes, respectively, for
each plane. Null elements (flights that produced NO valid latitudes, longitudes AND
altitudes) are removed from these dictionaries.

Each of the lists within these dictionaries are used as the x, y, and z coordinates to
plot lines representing the flight paths of each airplane. Latitudes are x values,
longitudes are y values, and altitudes are z values.

Each flight is thusly plotted. Circles representing 60 and 120 miles (roughly, as I know
there is no standard degree:latitude or longitude conversion) as well as a z axis (with
altitude value labels) and cardinal directions are drawn on the plot as well.

The plot is scaled via a makeshift method described in detail in the comments of the
program, around line 320.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

The bash script 'plot.sh' does a few simple things. It deletes the 'data' folder and its
contents so that the old flights are not plotted again, deletes the old flight_numbers.dat
file (if this setting is enabled in the program, as described above), creates a new empty
folder titled 'data' and then runs dump1090plot.py

If you don't use this script, these steps are still important to do before running
dump1090plot.py.

The script is copied here for convenience:


#!/bin/bash

rm -rf data &&
rm -rf flight_numbers.dat &&
mkdir data &&
python dump1090plot.py

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

Turning 'plot.sh' into a OS X application.

I created an application that executes a script, called 'plot2.sh'. This is identical
in function to 'plot.sh' but includes an additional step necessary for function as an
application. It is copied here for convenience, but make sure to edit the 7th line to
contain the path to the folder that data.dat, dump1090plot.py, etc. are stored in:


#!/bin/bash

# This script is run by the Dump1090Plotter app
# It includes an additional cd to the dump1090plot folder

cd &&
cd [FOLDER CONTAINING data.dat, dump1090plot.py, ETC.] &&
rm -rf data &&
rm -rf flight_numbers.dat &&
mkdir data &&
python dump1090plot.py


Thomas Aylott came up with a clever “appify” script that allows you to easily create Mac
apps from shell scripts. It is copied here for convenience:


#!/usr/bin/env bash

APPNAME=${2:-$(basename "$1" ".sh")}
DIR="$APPNAME.app/Contents/MacOS"

if [ -a "$APPNAME.app" ]; then
  echo "$PWD/$APPNAME.app already exists :("
  exit 1
fi

mkdir -p "$DIR"
cp "$1" "$DIR/$APPNAME"
chmod +x "$DIR/$APPNAME"

echo "$PWD/$APPNAME.app"


First, save the script to the /usr/local/bin directory and name it appify (no extension).

Then enter the following command in command line: sudo chmod +x /usr/local/bin/appify
to make appify executable without root privileges.

Then, the following command can be run to create the app (from the directory containing
'plot2.sh' (and all other necessary files, described above)):

appify plot2.sh "Your App Name"


You can create a custom icon by right clicking on the app and selecting Get Info. Copy an
image to your clipboard, click on the icon at the top left of the Get Info box, and paste
the image.