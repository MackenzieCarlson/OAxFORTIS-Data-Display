'''
Author: Mackenzie Carlson
Last Updated: 02/01/23
This code creates a socket to listen to a specific port receiving data packets destined for a specific IP address. It is currently configured to decode raw little endian data, extract data for each event (packet number, packet time stamp, X coordinate, Y coordinate, and pulse height), and write this data in three csv files (one for each spectral order) as the data comes in.
INSTRUCTIONS: TDC boards must already be on and connection must already be made with computer, or else socket creation might fail. In correct directory, run command below in command line. The 2nd argument is usually date of run in the form of MonDyYr (Ex: Mar3122).
                python3 OAxFORTIS_Server.py <insert date/filename modifier>
OUTPUT: Address of each incoming UDP packet will print in terminal window after the #### Server is listening #### comment. Three csv files will be written as data is read in (located in same directory as this code). You can see the contents of an individual file as it's being written by using the "tail -f <filename>" command in terminal.
'''

import socket
import sys
import numpy as np
import time
import csv


#### Inputs ####
if len(sys.argv) == 2:
    modifier = sys.argv[1]
else:
    print("Run like : python3 server.py <arg1:unique filename modifier (ex: Oct0622)>")
    exit(1)
#these are hardcoded in TDCs that are outputting UDP packets
ip = '192.168.1.100'
port = 60000


#### Create a Socket ####
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to the port
server_address = (ip, port)
s.bind(server_address)
print("Socket created for: ", s.getsockname()) #check ip and port being used
print("####### Server is listening #######")


#### Receive Data In A 'Forever Loop' And Write To Files ####
base_t = time.time()

with open("Zero_{}.csv".format(modifier),"a") as f0, open("Neg1_{}.csv".format(modifier),"a") as fn1, open("Pos1_{}.csv".format(modifier),"a") as fp1:
    while True:
        data, address = s.recvfrom(4096)
        print(address)
        decdata = list(ord(i) for i in data.decode('utf-16-le',errors='replace')) #decoded data
        
        #1458 total bytes in each packet; 729 items in decoded data list - first 3 are num photons, packet num, 0
        n = decdata[0] # number of events/photons in each packet
        num_photons = np.repeat(decdata[0],n)
        packetnum = np.repeat(decdata[1],n)
        ts = time.time()
        times = np.repeat(ts-base_t,n)
        X = np.asarray(decdata[3::3])
        Y = np.asarray(decdata[4::3])
        P = np.asarray(decdata[5::3])
        # only want real events (non-zero pulse height) and no duplicate events
        X = X[:n]
        Y = Y[:n]
        P = P[:n]
        
        if n!=0:
            ## Zero Order File
            if address == ('192.168.1.10', 62510):
                writer = csv.writer(f0, delimiter='\t')
                writer.writerows(zip(packetnum,times,X,Y,P,num_photons))
                f0.flush() #clear input buffer so file can be written as data comes in
            ## +1 Order File (270 deg)
            elif address == ('192.168.1.11', 62510):
                writer = csv.writer(fp1, delimiter='\t')
                writer.writerows(zip(packetnum,times,X,Y,P,num_photons))
                fp1.flush()
            ## -1 Order File (90 deg)
            elif address == ('192.168.1.12', 62510):
                writer = csv.writer(fn1, delimiter='\t')
                writer.writerows(zip(packetnum,times,X,Y,P,num_photons))
                fn1.flush()
        else: pass
