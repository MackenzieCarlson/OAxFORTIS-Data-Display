'''
Author: Mackenzie Carlson
Last Updated: 4/18/23
This code collects data streaming in via ethernet from OAxFORTIS sounding rocket TDCs, writes data to CSV files, and presents a window
    of plots that update live. If you want further post-acquisition analysis, use the OAxFORTISplots.py code.

Creates a socket to listen to a specific port receiving UDP packets destined for a specific IP address.
For each UDP packet received it will decode the raw little endian data, extract data for each event (see format below) and assign a time
stamp to the packet; update three 2D histogram plots (one for each spectral order) presenting X and Y locations of photons on detectors,
as well as update the live count rate; and write this data in three csv files.

Anticipated UDP Packet format: (see TDC manual for byte structure of packets)
- 1458 total bytes in each packet
- 729 items in decoded data list - first 3 are num photons, packet num, 0
- next 726 items are X coordinate, Y coordinate, and pulse height repeating
---> this means each packet can contain a max of 242 events!
- each packet contains same number of items - even if it contains <242 events, the rest is "filler" data and is disregarded in this code
    (this means it will also send empty packets if no photons are detected)
- if packets aren't full (such as during dark acquisition), they send at a regular interval (~1sec)

****** HOW TO RUN ******
INITIATING INSTRUCTIONS: TDC boards must already be on and connection must already be made with computer, or else socket creation will fail.
    In correct directory, run command below in command line. The 2nd argument is usually date of run in the form of MonDyYr.
                python OAxFORTIS_datacollect.py <insert date/filename modifier>
                
WHILE RUNNING: Upon successful creation of a socket, "#### Server is listening ####" will print to command line and you'll be told to wait
    patiently for the next printout. Note: If you just recently powered the electronics, the CISCO switch will take ~15sec to boot up before
    sending packets to computer even if TDCs have started sending packets out. Once a packet has been received, "####### Server has begun
    receiving packets #######" will print to the command line. At this point if you turn on the high voltage for the spectral and/or imaging
    channels, a window will pop up with plots & count rates that should automatically update as data is read in.
    
TO ESCAPE: Find your way back to the terminal. ^C to stop everything.

OUTPUT: Three CSV files will be written as data is read in (located in same directory as this code). You can see the contents of an individual
    file as it's being written by using the "tail -f <filename>" command in terminal. Note: Mackenzie will eventually remember to change this
    so it's written to FITS files instead :/
'''

import socket
import sys
import numpy as np
import time
import csv
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import colors
import matplotlib.gridspec as gridspec
matplotlib.rcParams.update({'font.size': 8})

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

## ---- Set CSV Output Filename ---- ##
if len(sys.argv) == 2:
    modifier = sys.argv[1]
else:
    print(color.BOLD + "Run like : python3 server.py <arg1:unique filename modifier (ex: Oct0622)>" + color.END)
    exit(1)
    



######################################################################################
##################### ---- Initiate Socket and Plots ---- #####################
######################################################################################

## ---- Create A Socket ---- ##
#TDCs are set to send packets to this ip,port combo
ip = '192.168.1.100'
port = 60000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (ip, port)
s.bind(server_address)
print(color.BOLD + "Socket created for: ", s.getsockname()) 
print(color.BLUE + '####### Server is listening' + color.DARKCYAN + ' ... wait for next message #######' + color.END)

## ---- Initiate Empty Plots ---- ##
gs_kw = dict(width_ratios=[1,1,1], height_ratios=[1.4,1] )
fig, ((XYn1, XY0, XYp1), (txtn1, txt0, txtp1)) = plt.subplots(nrows=2, ncols=3, sharey=True, gridspec_kw=gs_kw, figsize=(16,7))
fig.subplots_adjust(hspace=0,wspace=0)

XYp1.set_title('+1 Order (270°)')
XY0.set_title('Zero Order')
XYn1.set_title('-1 Order (90°)')
txtp1.axis('off')
txt0.axis('off')
txtn1.axis('off')

vmin = 0
vmax = 10000
plot1 = XYp1.imshow(np.zeros((10, 10)), interpolation='nearest', cmap='magma', norm=colors.LogNorm(vmin=vmin,vmax=vmax), origin='lower', extent=[0,16383,0,16383], aspect='auto')
plot2 = XY0.imshow(np.zeros((10, 10)), interpolation='nearest', cmap='magma', norm=colors.LogNorm(vmin=vmin,vmax=vmax), origin='lower', extent=[0,16383,0,16383], aspect='auto')
plot3 = XYn1.imshow(np.zeros((10, 10)), interpolation='nearest', cmap='magma', norm=colors.LogNorm(vmin=vmin,vmax=vmax), origin='lower', extent=[0,16383,0,16383], aspect='auto')
XYn1.invert_xaxis()

text1 = XYp1.text(0.15,-0.2,'', fontsize=10, weight="bold", transform=XYp1.transAxes) 
text2 = XY0.text(0.15,-0.2,'', fontsize=10, weight="bold", transform=XY0.transAxes) 
text3 = XYn1.text(0.2,-0.2,'', fontsize=10, weight="bold", transform=XYn1.transAxes) 




######################################################################################
#### ---- Receive Data In A 'Forever Loop', Update Plots, And Write To Files ---- ####
######################################################################################
base_t = time.time()
last_calculation_time = base_t
prev_tp1 = None
prev_t0 = None
prev_tn1 = None
hist1 = np.empty((355,355))
hist2 = np.empty((355,355))
hist3 = np.empty((355,355))
hasprinted = False

with open("Zero_{}.csv".format(modifier),"a") as f0, open("Neg1_{}.csv".format(modifier),"a") as fn1, open("Pos1_{}.csv".format(modifier),"a") as fp1:
    while True:
        data, address = s.recvfrom(1458)
        if data and not hasprinted:
            print(color.PURPLE + '####### Server has begun receiving packets #######' + color.END)
            hasprinted = True
                
        decdata = list(ord(i) for i in data.decode('utf-16-le',errors='replace'))
        
        n = decdata[0] # Number of events/photons in each packet
        num_photons = np.repeat(decdata[0],n)
        packetnum = np.repeat(decdata[1],n)
        t = time.time() - base_t # Packet Time Stamp
        times = np.repeat(t,n)
        X = np.asarray(decdata[3::3])
        Y = np.asarray(decdata[4::3])
        P = np.asarray(decdata[5::3])
        # only want real events (non-zero pulse height) and no duplicate events
        X = X[:n]
        Y = Y[:n]
        P = P[:n]
        
        if n!=0:
            ## +1 Order (270°)
            if address == ('192.168.1.11', 62510):
                if prev_tp1 is not None:
                    del_tp1 = t - prev_tp1
                else:
                    del_tp1 = t
                prev_tp1 = t
                CntRt_p1 = n/del_tp1
                newhist1,x,y = np.histogram2d(X,Y, bins=[355,355], range=[[0,16383],[0,16383]])
                hist1 = np.add(hist1,newhist1)
                if n<50:
                    text1.set_text('+1 Order Inst Rate: %.0f counts/s'%(CntRt_p1))
                    vmin = hist1.min()
                    vmax = hist1.max()
                    plot1.set_data(hist1.T)
                    plot1.autoscale()
                    plt.pause(.00001)
                elif time.time() - last_calculation_time >= .75:
                    text1.set_text('+1 Order Inst Rate: %.0f counts/s'%(CntRt_p1))
                    vmin = hist1.min()
                    vmax = hist1.max()
                    plot1.set_data(hist1.T)
                    plot1.autoscale()
                    plt.pause(.00001)
                    last_calculation_time = time.time()
                # Write to file
                writer = csv.writer(fp1, delimiter='\t')
                writer.writerows(zip(packetnum,times,X,Y,P,num_photons))
                fp1.flush() # clear input buffer so file can be written as data comes in
                
            ## Zero Order
            elif address == ('192.168.1.10', 62510):
                if prev_t0 is not None:
                    del_t0 = t - prev_t0
                else:
                    del_t0 = t
                prev_t0 = t
                CntRt_0 = n/del_t0
                newhist2,x,y = np.histogram2d(X,Y, bins=[355,355], range=[[0,16383],[0,16383]])
                hist2 = np.add(hist2,newhist2)
                if n<50:
                    text2.set_text('Zero Order Inst Rate: %.0f counts/s'%(CntRt_0))
                    vmin = hist2.min()
                    vmax = hist2.max()
                    plot2.set_data(hist2.T)
                    plot2.autoscale()
                    plt.pause(0.00001)
                elif time.time() - last_calculation_time >= 0.75:
                    text2.set_text('Zero Order Inst Rate: %.0f counts/s'%(CntRt_0))
                    vmin = hist2.min()
                    vmax = hist2.max()
                    plot2.set_data(hist2.T)
                    plot2.autoscale()
                    plt.pause(0.00001)
                    last_calculation_time = time.time()
                # Write to file
                writer = csv.writer(f0, delimiter='\t')
                writer.writerows(zip(packetnum,times,X,Y,P,num_photons))
                f0.flush()

                
            ## -1 Order (90°)
            elif address == ('192.168.1.12', 62510):
                if prev_tn1 is not None:
                    del_tn1 = t - prev_tn1
                else:
                    del_tn1 = t
                prev_tn1 = t
                CntRt_n1 = n/del_tn1
                newhist3,x,y = np.histogram2d(X,Y, bins=[355,355], range=[[0,16383],[0,16383]])
                hist3 = np.add(hist3,newhist3)
                if n<50:
                    text3.set_text('-1 Order Inst Rate: %.0f counts/s'%(CntRt_n1))
                    vmin = hist3.min()
                    vmax = hist3.max()
                    plot3.set_data(hist3.T)
                    plot3.autoscale()
                    plt.pause(0.00001)
                elif time.time() - last_calculation_time >= 0.75:
                    text3.set_text('-1 Order Inst Rate: %.0f counts/s'%(CntRt_n1))
                    vmin = hist3.min()
                    vmax = hist3.max()
                    plot3.set_data(hist3.T)
                    plot3.autoscale()
                    plt.pause(0.00001)
                    last_calculation_time = time.time()
                # Write to file
                writer = csv.writer(fn1, delimiter='\t')
                writer.writerows(zip(packetnum,times,X,Y,P,num_photons))
                fn1.flush()
            else: pass
