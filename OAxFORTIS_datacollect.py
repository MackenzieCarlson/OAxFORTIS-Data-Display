'''
Author: Mackenzie Carlson
Created: 3/2/2023
Last Updated: 3/9/2024
Most Recent Update: edit aspect ratio and cropping of histograms

This code:
    (1) creates a subfolder within the directory it resides in titled with today's date in the form of YYYY-MM-DD
    (2) collects data streaming in via ethernet from OAxFORTIS sounding rocket TDCs
    (3) writes data to CSV files within new subfolder
    (4) presents a window of plots that update live
If you want post-acquisition analysis, use OAxFORTISplots.py


To capture data this code creates a socket to listen to a specific port receiving UDP packets destined for a specific IP address.For each UDP packet received it will decode the raw little endian data, extract data for each event (see format below), and assign a time stamp to the packets

Anticipated UDP Packet format: (see TDC manual for byte structure of packets)
- 1458 total bytes in each packet
- 729 items in decoded data list - first 3 are num photons, packet num, 0
- next 726 items are X coordinate, Y coordinate, and pulse height repeating
---> this means each packet can contain a max of 242 events!
- The packets are sent out at a minimum frequency (~1sec)
- each packet contains same number of items - even if it contains <242 events, the rest is "filler" data (usually zeros) and is filtered out in this code
    (this means it will also send empty packets if no photons are detected)

****** HOW TO RUN ******
INITIATING INSTRUCTIONS: TDC boards and/or switch must already be on and connection must already be made with computer, or else socket creation will fail.
    In correct directory, run command below in command line. The 2nd argument is a filename modifier of your choice, such as "test1" (you can just use a space if you want to be rebellious).
                python OAxFORTIS_datacollect.py <insert modifier>
                
WHILE RUNNING: Upon successful creation of a socket, "#### Server is listening ####" will print to command line and you'll be told to wait patiently for the next printout. Note: If you just recently powered the electronics, the switch will take ~15sec to boot up. Once a packet has been received, "####### Server has begun receiving packets #######" will print to the command line. At this point if you turn on the high voltage for the spectral and/or imaging channels, a window will pop up with XY 2D histogram plots & count rates that should automatically update as data is read in.
    
TO ESCAPE: Find your way back to the terminal. ^C to stop everything.

OUTPUT: Three CSV files will be written to the newly created subfolder as data is read in.
'''


import socket
import os
import sys
import numpy as np
import time
import datetime
import csv
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import colors
import matplotlib.gridspec as gridspec
matplotlib.rcParams.update({'font.size': 8})
today = datetime.date.today()
now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
UTCnow = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())

class color: #because why not
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

## ---- Set Output Folder & Filename ---- ##
if len(sys.argv) == 2:
    modifier = sys.argv[1]
    folder = "./{}".format(today)
    if not os.path.isdir(folder):
        os.makedirs(folder)
else:
    print(color.BOLD + "Run like : python3 server.py <arg1:unique filename modifier (ex: Oct0622)>" + color.END)
    exit(1)
    



######################################################################################
##################### ---- Initial Socket and Plot Settings ---- #####################
######################################################################################

## ---- Create A Socket ---- ##
#TDCs are set to send packets to this ip,port combo
ip = ''     #open to broadcast ip='' and adapter set to 192.168.1.2 -- for unicast set ip='192.168.1.100' and same for adapter
port = 60000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (ip, port)
s.bind(server_address)
print(color.BOLD + "Socket created for: ", s.getsockname()) #check ip and port being used
print(color.BLUE + '####### Server is listening' + color.DARKCYAN + ' ... wait for next message #######' + color.END)

## ---- Initiate Empty Plots ---- ##
asp = 63.5/43
gs_kw = dict(width_ratios=[asp,1,asp], height_ratios=[1,1] )
fig, ((XYn1, XY0, XYp1), (txtn1, txt0, txtp1)) = plt.subplots(nrows=2, ncols=3, sharey=True, gridspec_kw=gs_kw, figsize=(16,7))
fig.subplots_adjust(hspace=.075,wspace=0)

XYp1.set_title('+1 Order (270°)')
XY0.set_title('Zero Order')
XYn1.set_title('-1 Order (90°)')
txtp1.axis('off')
txt0.axis('off')
txtn1.axis('off')

vmin = 1000 #arbitrary so imshow doesn't yell at me :(
vmax = 10000
plot1 = XYp1.imshow(np.zeros((10, 10)), interpolation='nearest', cmap='magma', norm=colors.LogNorm(vmin=vmin,vmax=vmax), origin='lower', extent=[1700,13800,2100,13090], aspect='auto')
plot2 = XY0.imshow(np.zeros((10, 10)), interpolation='nearest', cmap='magma', norm=colors.LogNorm(vmin=vmin,vmax=vmax), origin='lower', extent=[1300,13500,1750,13090], aspect='auto')
plot3 = XYn1.imshow(np.zeros((10, 10)), interpolation='nearest', cmap='magma', norm=colors.LogNorm(vmin=vmin,vmax=vmax), origin='lower', extent=[1900,13400,2100,13090], aspect='auto')
XYn1.invert_xaxis()

text1 = XYp1.text(0.15,-0.2,'', fontsize=10, weight="bold", transform=XYp1.transAxes) 
text2 = XY0.text(0.1,-0.2,'', fontsize=10, weight="bold", transform=XY0.transAxes) 
text3 = XYn1.text(0.2,-0.2,'', fontsize=10, weight="bold", transform=XYn1.transAxes) 




######################################################################################
#### ---- Receive Data In A 'Forever Loop', Update Plots, And Write To Files ---- ####
######################################################################################
base_t = time.time()
last_calculation_time = base_t
prev_tp1 = None
prev_t0 = None
prev_tn1 = None
newhist1 = []
newhist2 = []
newhist3 = []
hist1 = np.empty((355,355))
hist2 = np.empty((355,355))
hist3 = np.empty((355,355))
hasprinted = False


with open("./{}/Zero_{}.csv".format(today,modifier),"a") as f0, open("./{}/Neg1_{}.csv".format(today,modifier),"a") as fn1, open("./{}/Pos1_{}.csv".format(today,modifier),"a") as fp1:           
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
        
        if n>1:
            # only want real events (non-zero pulse height) and no duplicate events
            X = X[:n]
            #X = X[P!=0]
            Y = Y[:n]
            #Y = Y[P!=0]
            P = P[:n]
            #P = P[P!=0]
            
            ###############################################
            ################ +1 Order (270°) ##############
            ###############################################
            if address == ('192.168.1.11', 62510):
                if prev_tp1 is not None:
                    del_tp1 = t - prev_tp1
                else:
                    del_tp1 = t
                prev_tp1 = t
                CntRt_p1 = n/del_tp1
                text1.set_text('+1 Order Inst Rate: %.0f counts/s'%(CntRt_p1))
                newhist1,x,y = np.histogram2d(X,Y, bins=[355,355], range=[[1700,13800],[2100,13090]])
                hist1 = np.add(hist1,newhist1)
                ''' uncommenting this chunk of code (and those in other 2 orders) allows each spectral channel to update individually
                if  n<50:
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
                '''
                # Write to file
                writer = csv.writer(fp1, delimiter=',')
                writer.writerows(zip(packetnum,times,X,Y,P,num_photons))
                fp1.flush() # clear input buffer so file can be written & saved live
                
            ###############################################
            ################## Zero Order #################
            ###############################################
            elif address == ('192.168.1.10', 62510):
                if prev_t0 is not None:
                    del_t0 = t - prev_t0
                else:
                    del_t0 = t
                prev_t0 = t
                CntRt_0 = n/del_t0
                text2.set_text('Zero Order Inst Rate: %.0f counts/s'%(CntRt_0))
                newhist2,x,y = np.histogram2d(X,Y, bins=[355,355], range=[[1300,13500],[1750,13090]])
                hist2 = np.add(hist2,newhist2)
                '''
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
                '''
                # Write to file
                writer = csv.writer(f0, delimiter=',')
                writer.writerows(zip(packetnum,times,X,Y,P,num_photons))
                f0.flush()
                
            ##############################################
            ################ -1 Order (90°) ##############
            ##############################################
            elif address == ('192.168.1.12', 62510):
                if prev_tn1 is not None:
                    del_tn1 = t - prev_tn1
                else:
                    del_tn1 = t
                prev_tn1 = t
                CntRt_n1 = n/del_tn1
                text3.set_text('-1 Order Inst Rate: %.0f counts/s'%(CntRt_n1))
                newhist3,x,y = np.histogram2d(X,Y, bins=[355,355], range=[[1900,13400],[2100,13090]])
                hist3 = np.add(hist3,newhist3)
                '''
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
                '''
                # Write to file
                writer = csv.writer(fn1, delimiter=',')
                writer.writerows(zip(packetnum,times,X,Y,P,num_photons))
                fn1.flush()
            else:
                print(address)
                pass
            
            #######################################################################
            ########### Update plotting for each channel simultaneously ###########
            #######################################################################
            t_int = 0.75
            if  time.time() - last_calculation_time >= t_int:
                if len(newhist1) > 1:
                    vmin = hist1.min()
                    vmax = hist1.max()
                    plot1.set_data(hist1.T)
                    plot1.autoscale()
                
                if len(newhist2) > 1:
                    vmin = hist2.min()
                    vmax = hist2.max()
                    plot2.set_data(hist2.T)
                    plot2.autoscale()
                
                if len(newhist3) > 1:
                    vmin = hist3.min()
                    vmax = hist3.max()
                    plot3.set_data(hist3.T)
                    plot3.autoscale()
                
                last_calculation_time = time.time()
                plt.pause(.000001)

