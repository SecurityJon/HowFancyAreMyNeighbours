import subprocess
import string


#Pull in Data from TShark to process
runtshark = subprocess.run(["tshark", "-r", "/tmp/airodumpabgcapture.pcap", "-Y", "wlan.fc.type_subtype == 0x0008", "-T", "fields", "-e", "radiotap.channel.freq", "-e", "wlan.tag.number", "-e", "wlan.ta", "-e", "wlan.supported_rates", "-e", "wlan.ssid"], encoding='utf-8', stdout=subprocess.PIPE)


#Print the Headers
print ("Freq", "\t\t", end = '')
print ("Tech", "\t\t", end = '')
print ("BSSID", "\t\t\t\t", end = '')
print ("SSID", "\t\t", end = '')
print ("")


#Create a list to be used later
modifiedList = ['']

#Split the TShark output by new line
for line in runtshark.stdout.split('\n'):
    #Futher split the line output
    linetoprocess = line.split()

    #If the line contains some data
    if not (len(line) == 0): 
        if (linetoprocess[0].startswith('24')):
            linetoprocess[0] = "2.4GHz"
        if (linetoprocess[0].startswith('5')):
            linetoprocess[0] = "5.0GHz"

        #If the line does contain 802.11 tag headers
        if not (linetoprocess[1].find(',45,') == -1):
            linetoprocess[1] = "802.11n"
        else:
            if (linetoprocess[1].find(',45,') == -1):
                if (linetoprocess[0] == "5.0GHz"):
                    linetoprocess[1] = "802.11a"
                if (linetoprocess[0] == "2.4GHz"):
                    #If the line does not contain 802.11g speeds
                    if (linetoprocess[3].find('108') == -1):
                        linetoprocess[1] = "802.11b"
                    else:
                        linetoprocess[1] = "802.11g"

        tempString = "%s%s%s%s%s%s" % (linetoprocess[0], "\t\t" ,linetoprocess[1], "\t\t", linetoprocess[2], "\t\t")
        for x in range(4, len(linetoprocess)):
             tempString = tempString + "%s " % (linetoprocess[x]) 
        

        modifiedList.append(tempString)



thisIsNowAList = sorted(set(modifiedList))

for item in thisIsNowAList:
    print (item)
    #thisIsNowAListSplitUp = item.split()
    #for subitem in thisIsNowAListSplitUp:
    #    print (subitem, "\t\t", end = '')
    #print('')

