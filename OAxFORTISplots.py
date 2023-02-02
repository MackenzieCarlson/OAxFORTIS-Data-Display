'''
Author: Mackenzie Carlson
Last Updated: 02/02/2023
This code imports three csv files made by Server.py when collecting UDP packet data from the detectors (one for each of the three spectral orders: 0 and +/-1) on OAxFORTIS. Each event/photon corresponds to a row in a csv file that contains the packet number, packet time stamp, x coordinate, y coordinate, and pulse height. XY coordinate plots, pulse height histograms, and instantaneous count rate plots are output for each spectral order in addition to showing the average count rate.
INSTRUCTIONS: run below in command line, the modifier must be the same as what was used to run Server.py
                    python3 OAxFORTISplots.py <modifier>
OUTPUT: Figure containing plots and calculations will pop up in new window. Once this window is closed, an image of the figure will be saved with filename "FORTISplots_<modifier>.png"
'''

import matplotlib.pyplot as plt
import csv
import sys
import numpy as np
import matplotlib
from matplotlib import colors
from itertools import groupby
np.set_printoptions(threshold=sys.maxsize)
matplotlib.rcParams.update({'font.size': 7})
import time
start_time = time.time()

#### Inputs ####
if len(sys.argv) == 2:
    modifier = sys.argv[1]
else:
    print("Run like : python3 OAxFORTISplots.py <arg1:filename modifier used to run Server.py>")
    exit(1)


#### --- Extract and Filter Data from all three csv files --- ########################################
data0 = []       # packet data (each row contain x coordinate, y coordinate, pulse height)
Zero = np.loadtxt('Zero_{}.csv'.format(modifier))
for row in Zero:
    #if int(row[4]) != 0:    #exclude non-event rows (pulse height is non-zero)
    data0.append([int(row[2]),int(row[3]),int(row[4])])
data0 = np.asarray(data0)
Times = Zero.T[1] # Packet Time Stamp
Time0 = Times[np.insert(np.diff(Times).astype(np.bool), 0, True)] #skip repeats in each packet
Time0b = np.insert(Time0, 0, 0., axis=0) #array of previous times, add zero to beginning to offset time stamp array
Time0b = np.delete(Time0b,-1)
Counts0 = Zero.T[5] # Num Photons in each Packet
Counts0 = Counts0[np.insert(np.diff(Times).astype(np.bool), 0, True)]

datap1 = []
Pos1 = np.loadtxt('Pos1_{}.csv'.format(modifier))
for row in Pos1:
    #if int(row[4]) != 0:
    datap1.append([int(row[2]),int(row[3]),int(row[4])])
datap1 = np.asarray(datap1)
Times = Pos1.T[1]
Timep1 = Times[np.insert(np.diff(Times).astype(np.bool), 0, True)]
Timep1b = np.insert(Timep1, 0, 0., axis=0)
Timep1b = np.delete(Timep1b,-1)
Countsp1 = Pos1.T[5]
Countsp1 = Countsp1[np.insert(np.diff(Times).astype(np.bool), 0, True)]

datan1 = []
Neg1 = np.loadtxt('Neg1_{}.csv'.format(modifier))
for row in Neg1:
    #if int(row[4]) != 0:
    datan1.append([int(row[2]),int(row[3]),int(row[4])])
datan1 = np.asarray(datan1)
Times = Neg1.T[1]
Timen1 = Times[np.insert(np.diff(Times).astype(np.bool), 0, True)]
Timen1b = np.insert(Timen1, 0, 0., axis=0)
Timen1b = np.delete(Timen1b,-1)
Countsn1 = Neg1.T[5]
Countsn1 = Countsn1[np.insert(np.diff(Times).astype(np.bool), 0, True)]





###################### SET UP FIGURE #############################################################
# all plots are going to be presented as subplots on one figure
fig = plt.figure(figsize=(15,8))
XYp1 = plt.subplot2grid((8, 12), (0, 8), rowspan=4, colspan=4)
XY0 = plt.subplot2grid((8, 12), (0, 4), rowspan=4, colspan=4)
XYn1 = plt.subplot2grid((8, 12), (0, 0), rowspan=4, colspan=4)

empty = plt.subplot2grid((8, 12), (4, 0), colspan=12) #python is stupid, subplot2grid is stupid, this creates an empty space between XY plots and everything below
empty.set_visible(False)

ICRp1 = plt.subplot2grid((8, 12), (5, 0), colspan=4)
ICR0 = plt.subplot2grid((8, 12), (6, 0), colspan=4)
ICRn1 = plt.subplot2grid((8, 12), (7, 0), colspan=4)

#empty2 = plt.subplot2grid((8, 12), (4, 4), colspan=1) #creates an empty space between rate & histogram plots and text
#empty2.set_visible(False)

PHp1 = plt.subplot2grid((8, 12), (5, 8), colspan=4)
PH0 = plt.subplot2grid((8, 12), (6, 8), colspan=4)
PHn1 = plt.subplot2grid((8, 12), (7, 8), colspan=4)



#### --- Spatial plot of X,Y points --- ##################################################
#colors = np.arange(0,len(X))
#XY0.scatter(data0.T[0], data0.T[1],s=.5,color='darkslategrey')#c=colors, cmap="cool")
XY0.hist2d(data0.T[0], data0.T[1], bins=[355,355], range=[[0,16383],[0,16383]], density=True, cmap='plasma', norm = colors.LogNorm()) #range=[[1500,11500],[2000,12000]]
XY0.set_title('Zero Order')
#XY0.set_xlim(left=1000,right=14500)
#XY0.set_ylim(top=14000)
#XY0.set_xticks([])
#XY0.set_yticks([])
XY0.set_xlabel('X')

#colorsp1 = np.arange(0,len(Xp1))
#XYp1.scatter(datap1.T[0], datap1.T[1],s=.5,color='darkolivegreen')#c=colorsp1, cmap="cool")
XYp1.hist2d(datap1.T[0], datap1.T[1], bins=[355,355], range=[[0,16383],[0,16383]], density=True, cmap='plasma', norm = colors.LogNorm()) #range=[[1700,13600],[2200,13000]]
XYp1.set_title('+1 Order (270°)')
#XYp1.set_xticks([])
#XYp1.set_yticks([])
#XYp1.set_xlim(left=1000,right=14500)
#XYp1.set_ylim(top=14000)
#XYp1.set_ylabel('Y')

#colorsn1 = np.arange(0,len(Xn1))
#XYn1.scatter(datan1.T[0], datan1.T[1],s=.5,color='indigo')#c=colorsn1, cmap="cool")
XYn1.hist2d(datan1.T[0], datan1.T[1], bins=[355,355], range=[[0,16383],[0,16383]], density=True, cmap='plasma', norm = colors.LogNorm()) #range=[[1900,11500],[1900,11000]]
XYn1.set_title('-1 Order (90°)')
#XYn1.set_xticks([])
#XYn1.set_yticks([])
#XYn1.set_xlim(left=1000, right=11700)
#XYn1.set_ylim(top=11500)
XYn1.set_ylabel('Y')
XYn1.invert_xaxis()


#### --- Pulse Height Histograms --- ##############################################
PH0.hist(data0.T[2], bins = np.arange(10,260,10), color = 'darkorange', rwidth=0.9, label='Zero Order') #max pulse height is 255
PH0.set_ylabel('# of Events')
PH0.legend()

PHp1.hist(datap1.T[2], bins = np.arange(10,260,10), color = 'mediumblue', rwidth=0.9, label='+1 Order')
PHp1.set_title('Pulse Height Histograms')
PHp1.legend()

PHn1.hist(datan1.T[2], bins = np.arange(10,260,10), color = 'darkmagenta', rwidth=0.9, label='-1 Order')
PHn1.set_xlabel('Pulse Height')
PHn1.legend()



#### --- Count Rate Calculations --- ####################################################
# Average Count Rates = num of events / total time data taken
AvgCntRt_0 = int(sum(Counts0)/Time0[-1]) #each data point in any masked array is for one events, so length of any masked array is the # of events
text_0 = 'Zero Avg Rate: %.0f counts/s'%(AvgCntRt_0)
plt.gcf().text(0.42, 0.26, text_0, fontsize=10, weight="bold") #0.38, 0.26
AvgCntRt_p1 = int(sum(Countsp1)/Timep1[-1])
text_p1 = '+1 Avg Rate: %.0f counts/s'%(AvgCntRt_p1)
plt.gcf().text(0.42, 0.35, text_p1, fontsize=10, weight="bold") #0.38, 0.35
AvgCntRt_n1 = int(sum(Countsn1)/Timen1[-1])
text_n1 = '-1 Avg Rate: %.0f counts/s'%(AvgCntRt_n1)
plt.gcf().text(0.42, 0.17, text_n1, fontsize=10, weight="bold") #0.38, 0.17


# Instantaneous Rate Plots
InstRt0 = Counts0/(Time0-Time0b)
InstRtp1 = Countsp1/(Timep1-Timep1b)
InstRtn1 = Countsn1/(Timen1-Timen1b)

ICR0.plot(Time0,InstRt0,lw=1, color='darkorange', label='Zero Order')
ICR0.set_ylabel('Rate of Events (counts/s)')
ICR0.legend()

ICRp1.plot(Timep1,InstRtp1,lw=1, color='mediumblue', label='+1 Order')
ICRp1.legend()
ICRp1.set_title('Instantaneous Count Rate Plots')

ICRn1.plot(Timen1,InstRtn1,lw=1, color='darkmagenta', label='-1 Order')
ICRn1.set_xlabel('Packet Time Stamp (s)')
ICRn1.legend()


print("--- %s seconds ---" % (time.time() - start_time))

plt.subplots_adjust(wspace=0.0,hspace=0.0)
plt.show()
fig.savefig('FORTISplots_{}.png'.format(sys.argv[1]), bbox_inches='tight')
#saveas(gcf,'FORTISplots_{}.pdf'.format(sys.argv[1]))
