import subprocess
import string
import sys
from os import system, name 
import os
import random

#Display info to the user
print("")
print("##########################################################################")
print("#\t\tHowFancyAreMyNeighbours.py")
print("#\t\tJon Aubrey - 2019")
print("#\t\tv0.2")
print("#\t\tDetection is based on reverse engineering and guesswork")
print("#\t\tCorrections welcome!")
print("##########################################################################")
print("")

#Check that we have a parameter to use
if len(sys.argv) <2:
    print ("Usage: HowFancyAreMyNeighours.py [wireless adaptor]")
    exit(1)

#Check for root access
if os.geteuid() != 0:
    print("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
    exit(1)


#Define the timeout we're going to use for scanning in seconds
targetTimeout = 180


#Generate a random filename for us to write to
randomFilename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
randomFilePath = "/tmp/" + randomFilename

#Put the card into monitor mode
print("-Setting Up Wifi Card into Monitor mode")
subprocess.run(["ifconfig", sys.argv[1], "down"], encoding='utf-8', stdout=subprocess.PIPE)
subprocess.run(["iwconfig", sys.argv[1], "mode", "monitor"], encoding='utf-8', stdout=subprocess.PIPE)
subprocess.run(["ifconfig", sys.argv[1], "up"], encoding='utf-8', stdout=subprocess.PIPE)

#Start airodump
print("-Forcing Channel Hopping")
runairodump = subprocess.Popen(["airodump-ng", sys.argv[1], "--band", "abg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

#Start capturing packets over the air, on a 3 min timer
print("-Capturing Packets. Please wait, this will take %s seconds to finish" % (targetTimeout))
try:
    runtsharkcapturing = subprocess.run(["tshark", "-i", sys.argv[1], "-w", randomFilePath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=targetTimeout)
except subprocess.TimeoutExpired:
    pass

#Kill airodump
runairodump.kill()


#Pull in Data from TShark to process
print("-Capture finished. Processing data, please wait")
runtshark = subprocess.run(["tshark", "-r", randomFilePath, "-Y", "wlan.fc.type_subtype == 0x0008", "-T", "fields", "-e", "radiotap.channel.freq", "-e", "wlan.tag.number", "-e", "wlan.ta", "-e", "wlan.supported_rates", "-e", "wlan.ssid"], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)


#Create a list to use later
fullList = []
modifiedList = ['']

#Create Headers
headerList = []
headerList.append("Freq")
headerList.append("Tech")
headerList.append("BSSID")
headerList.append("SSID")
headerList.append("Extra")

headerList2 = []
headerList2.append("------")
headerList2.append("------")
headerList2.append("------")
headerList2.append("------")
headerList2.append("------")


#Split the TShark output by new line
for line in runtshark.stdout.split('\n'):
    #Futher split the line output
    linetoprocess = line.split()

    debugString = ""
    freqFlag = ""
    TechFlag = ""

    #If the line contains some data
    if not (len(line) == 0): 
        if (linetoprocess[0].startswith('24')):
            #print ("2.4Ghz identified")								#debug
            freqFlag = "2.4GHz"
        if (linetoprocess[0].startswith('5')):
            freqFlag = "5.0GHz"

        #Check if we're missing n and ac headers on the 5GHz band, it must be A then.
        if (linetoprocess[1].find(',191,') == -1):
            if (linetoprocess[1].find(',45,') == -1):
                if not (freqFlag.find('5.0GHz') == -1):
                    TechFlag = TechFlag + "%s" % ("/a")

        #If the line does contain 802.11b speeds
        if not (linetoprocess[3].find('130') == -1):
            TechFlag = TechFlag + "%s" % ("/b")

        #If the line does contain 802.11g tag headers
        if not (linetoprocess[1].find('50') == -1):
            if not (freqFlag.find('2.4GHz') == -1):
                TechFlag = TechFlag + "%s" % ("/g")

        #If the line does contain 802.11 tag headers
        if not (linetoprocess[1].find(',45,') == -1):
            TechFlag = TechFlag + "%s" % ("/n")

        #If the line does contain 802.11ac tag headers
        if not (linetoprocess[1].find(',191,') == -1):
            TechFlag = TechFlag + "%s" % ("/ac")
            #Test for AC on the 2.4GHz channel
            if not (freqFlag.find('2.4GHz') == -1):
                debugString = debugString + "%s" % ("802.11ac on 2.4GHz. Weird")

        #Check if we're missing n and ac headers, it must be A then.
        if (linetoprocess[1].find(',191,') == -1):
            if (linetoprocess[1].find(',45,') == -1):
                if not (freqFlag.find('5.0GHz') == -1):
                    TechFlag = TechFlag + "%s" % ("/a")

        ssidString = ""

        for x in range(4, len(linetoprocess)):
             ssidString = ssidString + "%s " % (linetoprocess[x]) 

        #Add in the BSSID
        bssid = linetoprocess[2]
        

        #Put all of the data into a list
        thisList = []
        thisList.append(freqFlag)
        thisList.append(TechFlag)
        thisList.append(bssid)
        thisList.append(ssidString)
        thisList.append(debugString)

        #Append the list to the final list
        fullList.append(thisList)


#Sort the list and remove duplicates
fullList = [list(y) for y in set([tuple(x) for x in fullList])]

#Append the headers at the start
fullList.insert(0, headerList)
fullList.insert(1, headerList2)

#Print out the final results in a pretty way
print("")
for item in fullList:
    print("{: <20} {: <20} {: <20} {: <20} {: <20}".format(*item))


#Delete our temporary files
os.remove(randomFilePath)

#Remind the user to reset their terminal

print("")
print("Your terminal is now wrecked, issue 'reset' to fix this")





#TO FIX
#	It's advertising /g/ on the 5.0GHz band, so that aint right
#	I can only find a few that claim they do 'b', that aint right surely?
