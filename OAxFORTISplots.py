'''
Author: Mackenzie Carlson
Created: 10/6/2022
Last Updated: 4/1/2024
Most Recent Update: new plot window structure, change aspect ratio and cropping of 2d histograms, plot colors

This code imports three csv files made by OAxFORTIS_datacollect.py when collecting UDP packet data from the detectors (one for each of the three spectral orders: 0 and +/-1). 
Each event/photon corresponds to a row in a csv file, with each row containing the packet number, packet time stamp, x coordinate, y coordinate, and pulse height. 
Calculations are done to produce the figures listed in OUTPUT.

INSTRUCTIONS: run below in command line, the modifier must be the same as what was used to run OAxFORTIS_datacollect.py
                    python3 OAxFORTISplots.py <modifier>
              You will then be asked to input the date (YYYY-MM-DD) you collected the data
              
OUTPUT: 3 Windows will pop up with the following figures:
        (1) XY 2D histograms for each order with y-axis count projections
        (2) Enlarged and scaled projections for each other
        (3) Instantaneous count rate plot and pulse height histogram
        Once these windows are closed, an image of the each window will be saved with filename "FORTISplots<1,2,3>_<modifier>.png"
'''

import matplotlib.pyplot as plt
import csv
import os
import sys
import numpy as np
import matplotlib
from matplotlib import colors
np.set_printoptions(threshold=sys.maxsize)
matplotlib.rcParams.update({'font.size': 7})
import time
start_time = time.time()
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
Single = np.loadtxt('Zero_May2623wff17.csv', delimiter='\t')
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
    Zero = np.loadtxt(ZeroFile, delimiter=',') #you'll need to change delimiter to /t (for all 3 channels) for any data collected before 11/16/23
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
    Pos1 = np.loadtxt(Pos1File, delimiter=',')
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
    Neg1 = np.loadtxt(Neg1File, delimiter=',')
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

####### WFF playbacks
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
## Window 3: Count rate plots & pulse height distributions
fig3, [CR,PH] = plt.subplots(2,figsize=(15,7.5))
fig3.suptitle("{}_{}".format(date,modifier))

## Window 2: Enlarged & scaled projections
fig2, prjs = plt.subplots(3,figsize=(15,7.5)) #prjs[0] is +1, prjs[1] is 0, prjs[2] is -1
fig2.suptitle("{}_{}".format(date,modifier) + ' Projections')

## Window 1: XY 2D histograms & projections
asp = 63.5/43
nasp = asp-1
gs_kw = dict(width_ratios=[asp,1,asp], height_ratios=[1,1])
fig1, ((XYn1, XY0, XYp1),(Projn1, Proj0, Projp1)) = plt.subplots(nrows=2, ncols=3, gridspec_kw=gs_kw, figsize=(15,7.5))
fig1.subplots_adjust(hspace=.075,wspace=0)



################# --- 2D Hist Plots of X,Y points --- ##################################################
fullrange = [[0,16383],[0,16383]]
fullextent = [0,16383,0,16383]
pltscl = 41.253
inlindis=20
dl=20*63.5
asp = 43/63.5

if len(data0)>0:
    ## Zero Order 2D Histogram
    init0,_,_ = np.histogram2d(data0.T[0], data0.T[1], bins=[355,355], range=[[2400,12600],[1850,12050]], density=True)
    XY0.imshow(init0.T, interpolation='nearest', origin='lower', aspect='auto', cmap='magma', norm = colors.LogNorm(), extent=[2400,12600,1850,12050])
    XY0.set_title('Zero Order')
    XY0.set_xlabel('X')
    
    ## Small Projection
    n, bins, _ = Proj0.hist(data0.T[0], 1000, range=[2400,12600], color='black', histtype='step')
    Proj0.set_xlim(2400,12600)
    
    ## Large Projection
    n, bins, _ = prjs[1].hist(data0.T[0], 1500, range=[2400,12600], color='darkorange', histtype='step',label='Zero Order')
    #prjs[1].set_yscale('log')
    #prjs[1].set_ylim(0,1000)
    prjs[1].set_xlim(2400,12600)
    prjs[1].legend()
    prjs[1].set_ylabel('Projected Counts')

    
if len(datap1)>0:
    ## +1 Order 2D Histogram
    initp1,_,_ = np.histogram2d(datap1.T[0], datap1.T[1], bins=[355,355], range=[[3200,13300],[2300,12200]], density=True)
    XYp1.imshow(initp1.T, interpolation='nearest', origin='lower', aspect='auto', cmap='magma', norm = colors.LogNorm(), extent=[3200,13300,2300,12200])
    XYp1.set_title('+1 Order (270°)')
    
    ## Small Projection
    n, bins, _ = Projp1.hist(datap1.T[0], 1000, range=[3200,13300], color='black', histtype='step')
    Projp1.set_xlim(3200,13300)
    
    ## Large Projection
    n, bins, _ = prjs[0].hist(datap1.T[0], 1500, range=[3200,13300], color='mediumblue', histtype='step',label='+1 Order')
    #prjs[0].set_yscale('log')
    #prjs[0].set_ylim(0,50)
    prjs[0].set_xlim(3200,13300)
    prjs[0].legend()
    
    
if len(datan1)>0:
    ## -1 Order 2D Histogram
    initn1,_,_ = np.histogram2d(datan1.T[0], datan1.T[1], bins=[355,355], range=[[3450,13350],[2000,11700]], density=True) #Steve's: [[1900,13400],[2100,12890]] #mine old: [[2000,13500],[2100,12700]]
    XYn1.imshow(initn1.T, interpolation='nearest', origin='lower',aspect='auto', cmap='magma', norm = colors.LogNorm(), extent=[3450,13350,2000,11700])
    XYn1.set_title('-1 Order (90°)')
    XYn1.set_ylabel('Y')
    XYn1.invert_xaxis()
    
    ## Small Projection
    n, bins, _ = Projn1.hist(datan1.T[0], 1000, range=[3450,13350], color='black', histtype='step')
    Projn1.set_xlim(3450,13350)
    Projn1.set_ylabel('Projected Counts')
    Projn1.invert_xaxis()
    
    ## Large Projection
    n, bins, _ = prjs[2].hist(datan1.T[0], 1500, range=[3450,13350], color='mediumvioletred', histtype='step',label='-1 Order')
    #prjs[2].set_yscale('log')
    #prjs[2].set_ylim(0,1000)
    prjs[2].set_xlim(3450,13350)
    prjs[2].legend()
    prjs[2].invert_xaxis()
    prjs[2].set_xlabel('X-Pixel')



############# --- Pulse Height Histograms --- ##############################################
if len(data0)>0:
    n, bins, _ = PH.hist(data0.T[2], bins = np.arange(10,260,10), color = 'darkorange', lw=2, histtype='step', label='Zero Order') #max pulse height is 255
if len(datap1)>0:
    n, bins, _ = PH.hist(datap1.T[2], bins = np.arange(10,260,10), color = 'mediumblue', lw=2, histtype='step', label='+1 Order')
if len(datan1)>0:
    n, bins, _ = PH.hist(datan1.T[2], bins = np.arange(10,260,10), color = 'mediumvioletred', lw=2, histtype='step', label='-1 Order')
PH.legend()
PH.set_title('Pulse Height Histograms')
PH.set_xlabel('Pulse Height')
PH.set_ylabel('# of Events')



############## --- Count Rate Calculations --- ####################################################
# Average Count Rates = num of events / total time data taken
if len(data0)>0:
    AvgCntRt_0 = len(data0.T[0])/(Time0[-1]-Time0[0]) #used to use sum(Counts0) instead of len(data0.T[0])
    text_0 = '%.3f counts/s'%(AvgCntRt_0)
    #print('Zero Avg Rate: ',text_0)
    #plt.gcf().text(0.48, 0.26, text_0, fontsize=10, weight="bold") 
if len(datap1)>0:
    AvgCntRt_p1 = len(datap1.T[0])/(Timep1[-1]-Timep1[0])
    text_p1 = '%.0f counts/s'%(AvgCntRt_p1) 
    #plt.gcf().text(0.48, 0.35, text_p1, fontsize=10, weight="bold") 
if len(datan1)>0:
    AvgCntRt_n1 = len(datan1.T[0])/(Timen1[-1]-Timen1[0])
    text_n1 = '%.0f counts/s'%(AvgCntRt_n1) 
    #plt.gcf().text(0.48, 0.17, text_n1, fontsize=10, weight="bold") 


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
    CR.plot(T0, InstRt0, lw=2, color='darkorange', label='Zero Order')
if len(datap1)>0:
    CR.plot(Tp1, InstRtp1, lw=2, color='mediumblue', label='+1 Order')
if len(datan1)>0:
    CR.plot(Tn1, InstRtn1, lw=2, color='mediumvioletred', label='-1 Order')
CR.legend()
CR.set_ylabel('Instantaneous Rate of Events (counts/s)')
CR.set_xlabel('Packet Time Stamp (s)')
CR.set_title('Instantaneous Count Rate Plots')




plt.show()
fig1.savefig('FORTISplots1_{}.png'.format(sys.argv[1]), bbox_inches='tight',dpi=1200)
fig2.savefig('FORTISplots2_{}.png'.format(sys.argv[1]), bbox_inches='tight',dpi=1200)
fig3.savefig('FORTISplots3_{}.png'.format(sys.argv[1]), bbox_inches='tight',dpi=1200)
#saveas(gcf,'FORTISplots_{}.pdf'.format(sys.argv[1]))
print("--- %s seconds ---" % (time.time() - start_time))
