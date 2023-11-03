'''
Author: Mackenzie Carlson
Last Updated: 10/18/2023
****Need to update description****This code imports three csv files made by Server.py when collecting UDP packet data from the detectors (one for each of the three spectral orders: 0 and +/-1) on OAxFORTIS. Each event/photon corresponds to a row in a csv file that contains the packet number, packet time stamp, x coordinate, y coordinate, and pulse height. XY coordinate plots, pulse height histograms, and instantaneous count rate plots are output for each spectral order in addition to showing the average count rate.
INSTRUCTIONS: run below in command line, the modifier must be the same as what was used to run Server.py
                    python3 OAxFORTISplots.py <modifier>
              You will then be asked to input the date you collected the data in the form of YYYY-MM-DD
OUTPUT: Figure containing plots and calculations will pop up in new window. Once this window is closed, an image of the figure will be saved with filename "FORTISplots_<modifier>.png"
'''

import matplotlib.pyplot as plt
import csv
from astropy.io import fits
import sys
import numpy as np
from math import log10, floor
import matplotlib
from matplotlib import colors
from itertools import groupby
np.set_printoptions(threshold=sys.maxsize)
matplotlib.rcParams.update({'font.size': 7})
import time
start_time = time.time()
import os
class color:
    BOLD = '\033[1m'
    END = '\033[0m'


######### --- Inputs --- ############
if len(sys.argv) == 2:
    modifier = sys.argv[1]
else:
    print("Run like : python3 OAxFORTISplots.py <arg1:filename modifier used to run Server.py>")
    exit(1)
    
date = input(color.BOLD + "Enter Date of Data Collection as YYYY-MM-DD: " + color.END)
os.chdir('./{}'.format(date)) #enter correct data folder



############# --- Extract and Filter Data from all three files --- ########################################
'''
#### compare to just single channel
dataS = []
Single = np.loadtxt('Zero_May2623wsfc17.csv', delimiter='\t')
for row in Single:
    #if int(row[3]) == 0:
    dataS.append([int(row[2]),int(row[3]),int(row[4])])
dataS = np.asarray(dataS)
TimesS = Single.T[1]
TimeS = TimesS[np.insert(np.diff(TimesS).astype(bool), 0, True)]
TimeSb = np.insert(TimeS, 0, 0., axis=0)
TimeSb = np.delete(TimeSb,-1)
CountsS = Single.T[5]
CountsS = CountsS[np.insert(np.diff(TimesS).astype(bool), 0, True)]
packnumS = Single.T[0]
'''

data0 = []       # packet data (each row contain x coordinate, y coordinate, pulse height)
ZeroFile = './Zero_{}.csv'.format(modifier)
if os.path.getsize(ZeroFile) > 0:  #checks if file has any data
    Zero = np.loadtxt(ZeroFile, delimiter='\t')
    for row in Zero:
        if int(row[4]) != 0:    #pulse height restrictions
            data0.append([int(row[2]),int(row[3]),int(row[4])])
    data0 = np.asarray(data0)
    Times = Zero.T[1] # Packet Time Stamp
    Time0 = Times[np.insert(np.diff(Times).astype(bool), 0, True)] #skip repeats in each packet
    Time0b = np.insert(Time0, 0, 0., axis=0) #array of previous times, add zero to beginning to offset time stamp array
    Time0b = np.delete(Time0b,-1)
    Counts0 = Zero.T[5] # Num Photons in each Packet
    Counts0 = Counts0[np.insert(np.diff(Times).astype(bool), 0, True)]
    packnum0 = Zero.T[0]

datap1 = []
Pos1File = './Pos1_{}.csv'.format(modifier)
if os.path.getsize(Pos1File) > 0:
    Pos1 = np.loadtxt(Pos1File, delimiter='\t')
    for row in Pos1:
        if int(row[4]) != 0:
            datap1.append([int(row[2]),int(row[3]),int(row[4])])
    datap1 = np.asarray(datap1)
    Times = Pos1.T[1]
    Timep1 = Times[np.insert(np.diff(Times).astype(bool), 0, True)]
    Timep1b = np.insert(Timep1, 0, 0., axis=0)
    Timep1b = np.delete(Timep1b,-1)
    Countsp1 = Pos1.T[5]
    Countsp1 = Countsp1[np.insert(np.diff(Times).astype(bool), 0, True)]
    packnump1 = Pos1.T[0]

datan1 = []
Neg1File = './Neg1_{}.csv'.format(modifier)
if os.path.getsize(Neg1File) > 0:
    Neg1 = np.loadtxt(Neg1File, delimiter='\t')
    for row in Neg1:
        if int(row[4]) != 0:
            datan1.append([int(row[2]),int(row[3]),int(row[4])])
    datan1 = np.asarray(datan1)
    Times = Neg1.T[1]
    Timen1 = Times[np.insert(np.diff(Times).astype(bool), 0, True)]
    Timen1b = np.insert(Timen1, 0, 0., axis=0)
    Timen1b = np.delete(Timen1b,-1)
    Countsn1 = Neg1.T[5]
    Countsn1 = Countsn1[np.insert(np.diff(Times).astype(bool), 0, True)]
    packnumn1 = Neg1.T[0]

#######playbacks
'''
data0PB = []       # packet data (each row contain x coordinate, y coordinate, pulse height)
ZeroPB = np.loadtxt('Zero_{}pb.csv'.format(modifier), delimiter='\t')
for row in ZeroPB:
    #if int(row[3]) == 0:    #exclude non-event rows (pulse height is non-zero)
    data0PB.append([int(row[2]),int(row[3]),int(row[4])])
data0PB = np.asarray(data0PB)
TimesPB = ZeroPB.T[1] # Packet Time Stamp
Time0PB = TimesPB[np.insert(np.diff(TimesPB).astype(bool), 0, True)] #skip repeats in each packet
Time0bPB = np.insert(Time0PB, 0, 0., axis=0) #array of previous times, add zero to beginning to offset time stamp array
Time0bPB = np.delete(Time0bPB,-1)
Counts0PB = ZeroPB.T[5] # Num Photons in each Packet
Counts0PB = Counts0PB[np.insert(np.diff(TimesPB).astype(bool), 0, True)]

datap1PB = []
Pos1PB = np.loadtxt('Pos1_{}pb.csv'.format(modifier), delimiter='\t')
for row in Pos1PB:
    #if int(row[3]) != 0:
    datap1PB.append([int(row[2]),int(row[3]),int(row[4])])
datap1PB = np.asarray(datap1PB)
TimesPB = Pos1PB.T[1]
Timep1PB = TimesPB[np.insert(np.diff(TimesPB).astype(bool), 0, True)]
Timep1bPB = np.insert(Timep1PB, 0, 0., axis=0)
Timep1bPB = np.delete(Timep1bPB,-1)
Countsp1PB = Pos1PB.T[5]
Countsp1PB = Countsp1PB[np.insert(np.diff(TimesPB).astype(bool), 0, True)]

datan1PB = []
Neg1PB = np.loadtxt('Neg1_{}pb.csv'.format(modifier), delimiter='\t')
for row in Neg1PB:
    #if int(row[3]) != 0:
    datan1PB.append([int(row[2]),int(row[3]),int(row[4])])
datan1PB = np.asarray(datan1PB)
TimesPB = Neg1PB.T[1]
Timen1PB = TimesPB[np.insert(np.diff(TimesPB).astype(bool), 0, True)]
Timen1bPB = np.insert(Timen1PB, 0, 0., axis=0)
Timen1bPB = np.delete(Timen1bPB,-1)
Countsn1PB = Neg1PB.T[5]
Countsn1PB = Countsn1PB[np.insert(np.diff(TimesPB).astype(bool), 0, True)]

#print(len(data0),len(data0PB))
'''


###################### --- SET UP FIGURE --- #############################################################
## Figure 2
fig3, [CR,PH] = plt.subplots(2,figsize=(15,8))
fig3.suptitle("{}_{}".format(date,modifier))

## Figure 2
fig2, prjs = plt.subplots(3,figsize=(15,8)) #prjs[0] is +1, prjs[1] is 0, prjs[2] is -1
fig2.suptitle("{}_{}".format(date,modifier) + ' Projections')

## Figure 1
fig1 = plt.figure(figsize=(15,8))
XYp1 = plt.subplot2grid((8, 12), (0, 8), rowspan=4, colspan=4)
XY0 = plt.subplot2grid((8, 12), (0, 4), rowspan=4, colspan=4)
XYn1 = plt.subplot2grid((8, 12), (0, 0), rowspan=4, colspan=4)


empty = plt.subplot2grid((8, 12), (4, 0), colspan=12) #python is stupid, subplot2grid is stupid, this creates an empty space between XY plots and everything below
empty.set_visible(False)

Proj0 =plt.subplot2grid((8, 12), (5, 4), colspan=4)
Projp1 =plt.subplot2grid((8, 12), (5, 8), colspan=4)
Projn1 =plt.subplot2grid((8, 12), (5, 0), colspan=4)



################# --- Plots of X,Y points --- ##################################################
if len(data0)>0:
    ## 2D Histogram
    '''
    #sums,x,y = np.histogram2d(data0.T[0],data0.T[1], bins=[355,355],weights=data0.T[2], range=[[0,16383],[0,16383]])
    #counts,_,_ = np.histogram2d(data0.T[0],data0.T[1], bins=[355,355], range=[[0,16383],[0,16383]])
    #with np.errstate(divide='ignore', invalid='ignore'): # suppress possible divide-by-zero warnings
        #XY0.pcolormesh(x, y, sums/counts, cmap='magma')
    '''
    init0,_,_ = np.histogram2d(data0.T[0], data0.T[1], bins=[355,355], range=[[1750,13250],[1500,13000]], density=True)
    ##init0,_,_ = np.histogram2d(data0.T[0], data0.T[1], bins=[355,355], range=[[3606.3,11393.7],[3356.3,11143.7]], density=True)
    #comp0,_,_ = np.histogram2d(data0PB.T[0], data0PB.T[1], bins=[355,355], range=[[0,16383],[0,16383]], density=True)
    #with np.errstate(divide='ignore', invalid='ignore'):  # suppress division by zero warnings
        #hist *= norm / hist.sum(axis=0, keepdims=True)
        #diff0 = np.absolute(init0 - comp0)/init0
    #print(max(max(x) for x in diff0))
    #print(np.nanargmax(np.ma.where(diff0 != 0, diff0, np.nan)))
    XY0.imshow(init0.T, interpolation='nearest', origin='lower', aspect='auto', cmap='magma', norm = colors.LogNorm(), extent=[-100,17000,-100,17000])
    #XY0.hist2d(data0.T[0], data0.T[1], bins=[355,355], range=[[0,16383],[0,16383]], density=True, cmap='magma', norm = colors.LogNorm()) #range=[[1500,11500],[2000,12000]] #weights=data0.T[2]
    XY0.set_title('Zero Order')
    #XY0.set_xlim(left=1000,right=14500)
    #XY0.set_ylim(top=14000)
    XY0.set_xlabel('X')
    
    ## Small Projection
    n, bins, _ = Proj0.hist(data0.T[0], 1000, range=[1750,13250], color='black', histtype='step')
    
    ## Large Projection
    n, bins, _ = prjs[1].hist(data0.T[0], 1500, range=[1750,13250], color='darkorange', histtype='step',label='Zero Order')
    prjs[1].set_ylim(0,30)
    prjs[1].legend()

    
if len(datap1)>0:
    ## 2D Histogram
    '''
    #sums,x,y = np.histogram2d(datap1.T[0],datap1.T[1], bins=[355,355],weights=datap1.T[2], range=[[0,16383],[0,16383]])
    #counts,_,_ = np.histogram2d(datap1.T[0],datap1.T[1], bins=[355,355], range=[[0,16383],[0,16383]])
    #with np.errstate(divide='ignore', invalid='ignore'): # suppress possible divide-by-zero warnings
        #XYp1.pcolormesh(x, y, sums/counts, cmap='magma')
    '''
    initp1,_,_ = np.histogram2d(datap1.T[0], datap1.T[1], bins=[355,355], range=[[1750,13250],[1500,13000]], density=True)
    ##initp1,_,_ = np.histogram2d(datap1.T[0], datap1.T[1], bins=[355,355], range=[[3606.3,11393.7],[1500,13000]], density=True)
    #compp1,_,_ = np.histogram2d(datap1PB.T[0], datap1PB.T[1], bins=[355,355], range=[[0,16383],[0,16383]], density=True)
    #with np.errstate(divide='ignore', invalid='ignore'):  # suppress division by zero warnings
        #hist *= norm / hist.sum(axis=0, keepdims=True)
     #   diffp1 = np.absolute(initp1 - compp1)/initp1
    #print(max(max(x) for x in diffp1))
    #print(np.nanargmax(np.ma.where(diffp1 != 0, diffp1, np.nan)))
    XYp1.imshow(initp1.T, interpolation='nearest', origin='lower', aspect='auto', cmap='magma', norm = colors.LogNorm(), extent=[-100,17000,-100,17000])
    #XYp1.hist2d(datap1.T[0], datap1.T[1], bins=[355,355], range=[[0,16383],[0,16383]], density=True, cmap='magma', norm = colors.LogNorm()) #range=[[1700,13600],[2200,13000]]
    XYp1.set_title('+1 Order (270°)')
    #XYp1.set_xlim(left=1000,right=14500)
    #XYp1.set_ylim(top=14000)
    
    ## Small Projection
    n, bins, _ = Projp1.hist(datap1.T[0], 1000, range=[1750,13250], color='black', histtype='step')
    
    ## Large Projection
    n, bins, _ = prjs[0].hist(datap1.T[0], 1500, range=[1750,13250], color='mediumblue', histtype='step',label='+1 Order')
    prjs[0].set_ylim(0,20)
    prjs[0].legend()
    
    
if len(datan1)>0:
    ## 2D Histogram
    '''
    #sums,x,y = np.histogram2d(datan1.T[0],datan1.T[1], bins=[355,355],weights=datan1.T[2], range=[[0,16383],[0,16383]])
    #counts,_,_ = np.histogram2d(datan1.T[0],datan1.T[1], bins=[355,355], range=[[0,16383],[0,16383]])
    #with np.errstate(divide='ignore', invalid='ignore'): # suppress possible divide-by-zero warnings
        #XYn1.pcolormesh(x, y, sums/counts, cmap='magma')
    '''
    initn1,_,_ = np.histogram2d(datan1.T[0], datan1.T[1], bins=[355,355], range=[[1700,13250],[1500,13000]], density=True)
    ##initn1,_,_ = np.histogram2d(datan1.T[0], datan1.T[1], bins=[355,355], range=[[3606.3,11393.7],[1500,13000]], density=True)
    #compn1,_,_ = np.histogram2d(datan1PB.T[0], datan1PB.T[1], bins=[355,355], range=[[0,16383],[0,16383]], density=True)
    #with np.errstate(divide='ignore', invalid='ignore'):  # suppress division by zero warnings
        #hist *= norm / hist.sum(axis=0, keepdims=True)
     #   diffn1 = np.absolute(initn1 - compn1)/initn1
    #print(max(max(x) for x in diffn1))
    #print(np.nanargmax(np.ma.where(diffn1 != 0, diffn1, np.nan)))
    XYn1.imshow(initn1.T, interpolation='nearest', origin='lower',aspect='auto', cmap='magma', norm = colors.LogNorm(), extent=[-100,17000,-100,17000])
    #XYn1.hist2d(datan1.T[0], datan1.T[1], bins=[355,355], range=[[0,16383],[0,16383]], density=True, cmap='magma', norm = colors.LogNorm()) #range=[[1900,11500],[1900,11000]]
    XYn1.set_title('-1 Order (90°)')
    #XYn1.set_xlim(left=1000, right=11700)
    #XYn1.set_ylim(top=11500)
    XYn1.set_ylabel('Y')
    XYn1.invert_xaxis()
    
    ## Small Projection
    n, bins, _ = Projn1.hist(datan1.T[0], 1000, range=[1750,13250], color='black', histtype='step')
    Projn1.invert_xaxis()
    
    ## Large Projection
    n, bins, _ = prjs[2].hist(datan1.T[0], 1500, range=[1750,13250], color='darkmagenta', histtype='step',label='-1 Order')
    prjs[2].set_ylim(0,20)
    prjs[2].legend()
    prjs[2].invert_xaxis()



############# --- Pulse Height Histograms --- ##############################################
if len(data0)>0:
    n, bins, _ = PH.hist(data0.T[2], bins = np.arange(10,260,10), color = 'darkorange', histtype='step', label='Zero Order') #max pulse height is 255
if len(datap1)>0:
    n, bins, _ = PH.hist(datap1.T[2], bins = np.arange(10,260,10), color = 'mediumblue', histtype='step', label='+1 Order')
if len(datan1)>0:
    n, bins, _ = PH.hist(datan1.T[2], bins = np.arange(10,260,10), color = 'darkmagenta', histtype='step', label='-1 Order')
PH.legend()
PH.set_title('Pulse Height Histograms')
PH.set_xlabel('Pulse Height')
PH.set_ylabel('# of Events')



############## --- Count Rate Calculations --- ####################################################
# Average Count Rates = num of events / total time data taken
if len(data0)>0:
    AvgCntRt_0 = int(sum(Counts0)/Time0[-1]-Time0[0])
    text_0 = '%.0f counts/s'%(AvgCntRt_0) #Zero Avg Rate:
    #plt.gcf().text(0.48, 0.26, text_0, fontsize=10, weight="bold") #0.38, 0.26 ##0.42
if len(datap1)>0:
    AvgCntRt_p1 = int(sum(Countsp1)/Timep1[-1]-Timep1[0])
    text_p1 = '%.0f counts/s'%(AvgCntRt_p1) #+1 Avg Rate:
    #plt.gcf().text(0.48, 0.35, text_p1, fontsize=10, weight="bold") #0.38, 0.35
if len(datan1)>0:
    AvgCntRt_n1 = int(sum(Countsn1)/Timen1[-1]-Timen1[0])
    text_n1 = '%.0f counts/s'%(AvgCntRt_n1) #-1 Avg Rate:
    #plt.gcf().text(0.48, 0.17, text_n1, fontsize=10, weight="bold") #0.38, 0.17


# Instantaneous Rate Plots
#only calculate rate at every 1.5sec timestamp interval
if len(data0)>0:
    last_calculation_time = 0
    InstRt0 = []
    T0 = []
    for o in range(len(Time0)-1):
        if Time0[o] - last_calculation_time >= 1.5:
            InstRt0.append(Counts0[o]/(Time0[o]-Time0b[o]))
            T0.append(Time0[o])
            last_calculation_time = Time0[o]
if len(datap1)>0:
    InstRtp1 = []
    Tp1 = []
    last_calculation_time = 0
    for p in range(len(Timep1)-1):
        if Timep1[p] - last_calculation_time >= 1.5:
            InstRtp1.append(Countsp1[p]/(Timep1[p]-Timep1b[p]))
            Tp1.append(Timep1[p])
            last_calculation_time = Timep1[p]
if len(datan1)>0:
    InstRtn1 = []
    Tn1 = []
    last_calculation_time = 0
    for n in range(len(Timen1)-1):
        if Timen1[n] - last_calculation_time >= 1.5:
            InstRtn1.append(Countsn1[n]/(Timen1[n]-Timen1b[n]))
            Tn1.append(Timen1[n])
            last_calculation_time = Timen1[n]

if len(data0)>0:
    CR.plot(T0,InstRt0,lw=1, color='darkorange', label='Zero Order')
if len(datap1)>0:
    CR.plot(Tp1,InstRtp1,lw=1, color='mediumblue', label='+1 Order')
if len(datan1)>0:
    CR.plot(Tn1,InstRtn1,lw=1, color='darkmagenta', label='-1 Order')
CR.legend()
CR.set_ylabel('Instantaneous Rate of Events (counts/s)')
CR.set_xlabel('Packet Time Stamp (s)')
CR.set_title('Instantaneous Count Rate Plots')



plt.subplots_adjust(wspace=0.0,hspace=0.0)
plt.show()
#Zero.close()
#Pos1.close()
#Neg1.close()
fig1.savefig('FORTISplots1_{}.png'.format(sys.argv[1]), bbox_inches='tight',dpi=1200)
fig2.savefig('FORTISplots2_{}.png'.format(sys.argv[1]), bbox_inches='tight',dpi=1200)
fig3.savefig('FORTISplots3_{}.png'.format(sys.argv[1]), bbox_inches='tight',dpi=1200)
#saveas(gcf,'FORTISplots_{}.pdf'.format(sys.argv[1]))
print("--- %s seconds ---" % (time.time() - start_time))
