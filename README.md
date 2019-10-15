# HowFancyAreMyNeighbours
Script to see the Wifi technologies in use around you


This is a Python Script to check on the Wifi technologies in use around you. I created it because I couldn't see this in another tool and it was a good learning exercise.

Requirements: 
A Wifi card that's able to be put into monitor mode
The Airmon suite installed
TShark installed
Python 3 installed


Usage:
First put your card into monitor mode
ifconfig wlan0 down
iwconfig wlan0 mode monitor
ifconfig wlan0 up

Now start airodump-ng to force the card to start channel hopping
airodump-ng wlan0 --band abg

While airodump is running, capture the card's output to a temporary file
tshark -i wlan0 -w /tmp/airodumpabgcapture.pcap

Wait for 5 mins while enough packets are captured. You're rotating channels a lot so this takes a while

Stop the capture with tshark and then stop airodump 

Now run the script to analyse the surrounding Wifi.
python3 ./HowFancyAreMyNeighbours.py


TODO: Import a check for 802.11ac and some of the other newer stuff.
