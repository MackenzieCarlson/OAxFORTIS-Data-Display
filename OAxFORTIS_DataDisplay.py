import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import csv
import sys
import matplotlib
from matplotlib import colors
import matplotlib.gridspec as gridspec
matplotlib.rcParams.update({'font.size': 8})

#### Inputs ####
if len(sys.argv) == 2:
    modifier = sys.argv[1]
else:
    print("Run like : python3 OAxFORTIS_DataDisplay.py <arg1:filename modifier used to run Server.py>")
    exit(1)


datap1 = []
data0 = []
datan1 = []
Np1, Tp1, Xp1, Yp1, Pp1 = [], [], [], [], []
N0, T0, X0, Y0, P0 = [], [], [], [], []
Nn1, Tn1, Xn1, Yn1, Pn1 = [], [], [], [], []
CntRt_p1 = []
CntRt_0 = []
CntRt_n1 = []


## Establish Figure
#fig = plt.figure(figsize=(16,8))
'''
XYp1 = plt.subplot2grid((8, 12), (0, 8), rowspan=4, colspan=4)
XY0 = plt.subplot2grid((8, 12), (0, 4), rowspan=4, colspan=4)
XYn1 = plt.subplot2grid((8, 12), (0, 0), rowspan=4, colspan=4)
plt.subplots_adjust(wspace=0.0)

txtp1 = plt.subplot2grid((8, 12), (4, 8), colspan=4) ###these are the count rate text and go directly under coordinates plots
txtp1.axis('off')
txt0 = plt.subplot2grid((8, 12), (4, 4), colspan=4)
txt0.axis('off')
txtn1 = plt.subplot2grid((8, 12), (4, 0), colspan=4)
txtn1.axis('off')
'''
#gs = fig.add_gridspec(ncols=3, nrows=1, hspace=0, wspace=0)
#(XYn1, XY0, XYp1) = gs.subplots(sharey='row')

#gs_kw = dict(width_ratios=[1.4767,1,1.4767], height_ratios=[1,1.1] )
gs_kw = dict(width_ratios=[1,1,1], height_ratios=[1.2,1] )
fig, ((XYn1, XY0, XYp1), (txtn1, txt0, txtp1)) = plt.subplots(nrows=2, ncols=3, sharey=True, gridspec_kw=gs_kw, figsize=(16,7))
fig.subplots_adjust(hspace=0,wspace=0)


## Set Figure and Plot Parameters
XYp1.set_title('+1 Order (270°)')
#XYp1.set_xlim(left=1000,right=14500)
#XYp1.set_ylim(top=14000)
XYp1.set_xticks([])
XYp1.set_yticks([])
#XYp1.set_aspect(0.677)
XY0.set_title('Zero Order')
#XY0.set_xlim(right=16383)
#XY0.set_ylim(top=16500)
#XY0.set_aspect('equal')
XY0.set_xticks([])
XY0.set_yticks([])
#XY0.set_xlabel('X')
XYn1.set_title('-1 Order (90°)')
#XYn1.set_xlim(left=1000, right=12000)
#XYn1.set_ylim(top=11500)
#XYn1.set_xticks([])
#XYn1.set_yticks([])
#XYp1.set_ylabel('Y')
XYn1.invert_xaxis()
#XYn1.set_aspect(0.677)

txtp1.axis('off')
txt0.axis('off')
txtn1.axis('off')


## Empty Plots
#plot1, = XYp1.plot(Xp1,Yp1,'.',ms=.5,color='darkolivegreen') #these three make spot plots
#plot2, = XY0.plot(X0,Y0,'.',ms=.5,color='darkslategrey')
#plot3, = XYn1.plot(Xn1,Yn1,'.',ms=.5,color='indigo')

#hist1,x,y = np.histogram2d(Xp1, Yp1, bins=[164,164], range=[[0,16383],[0,16383]])
#plot1 = XYp1.imshow(hist1.T, cmap='plasma_r', norm = colors.LogNorm())
#hist2,x,y = np.histogram2d(X0, Y0, bins=[164,164], range=[[0,16383],[0,16383]])
#plot2 = XY0.imshow(hist2.T, cmap='plasma_r', norm = colors.LogNorm())
#hist3,x,y = np.histogram2d(Xn1, Yn1, bins=[164,164], range=[[0,16383],[0,16383]])
#plot3 = XYn1.imshow(hist3.T, cmap='plasma_r', norm = colors.LogNorm())

#plot1 = XYp1.hist2d('', '', bins=[164,164], range=[[0,16383],[0,16383]], cmap='plasma_r', norm = colors.LogNorm())
#plot2 = XY0.hist2d('', '', bins=[164,164], range=[[0,16383],[0,16383]], cmap='plasma_r', norm = colors.LogNorm())
#plot3 = XYn1.hist2d('','', bins=[164,164], range=[[0,16383],[0,16383]], cmap='plasma_r', norm = colors.LogNorm())


text1 = XYp1.text(0.15,-0.2,'', fontsize=10, weight="bold", transform=XYp1.transAxes) #0.38, 0.35 pos1
text2 = XY0.text(0.15,-0.2,'', fontsize=10, weight="bold", transform=XY0.transAxes) #0.38, 0.26 zero
text3 = XYn1.text(0.2,-0.2,'', fontsize=10, weight="bold", transform=XYn1.transAxes) #0.38, 0.17 neg1


#fake initial function to please funcanimation
def init_func():
    global Pos1, Zero, Neg1
    Pos1 = []
    Zero = []
    Neg1 = []
    #pass

## Update plots with new data, perform calculations as new data comes in
def update(frame):
    ### +1 Order
    Pos1 = np.loadtxt('Pos1_{}.csv'.format(modifier))
    for row in Pos1:
        datap1.append([int(row[2]),int(row[3]),int(row[4])])
    Xp1 = np.asarray(datap1).T[0]
    Yp1 = np.asarray(datap1).T[1]
    
    #hist1,x,y = np.histogram2d(Xp1, Yp1, bins=[164,164], range=[[0,16383],[0,16383]])
    XYp1.hist2d(Xp1, Yp1, bins=[355,355], range=[[0,16383],[0,16383]], density=True, cmap='plasma', norm = colors.LogNorm()) #range=[[0,13600],[2200,13000]]
    
    Times = Pos1.T[1] # Packet Time Stamp
    Timep1 = Times[np.insert(np.diff(Times).astype(np.bool), 0, True)] #skip repeats in each packet
    Timep1b = np.insert(Timep1, 0, 0., axis=0) #array of previous times, add zero to beginning to offset time stamp array
    Timep1b = np.delete(Timep1b,-1)
    Countsp1 = Pos1.T[5] # Num Photons in each Packet
    Countsp1 = Countsp1[np.insert(np.diff(Times).astype(np.bool), 0, True)]
    CntRt_p1 = int(Countsp1[-1]/(Timep1[-1]-Timep1b[-1])) #calculate count rate for each frame
    text1.set_text('+1 Order Inst Rate: %.0f counts/s'%(CntRt_p1))
    
    
    ### 0 Order
    Zero = np.loadtxt('Zero_{}.csv'.format(modifier))
    for row in Zero:
        data0.append([int(row[2]),int(row[3]),int(row[4])])
    X0 = np.asarray(data0).T[0]
    Y0 = np.asarray(data0).T[1]
    
    #hist2,x,y = np.histogram2d(X0, Y0, bins=[164,164], range=[[0,16383],[0,16383]])
    XY0.hist2d(X0, Y0, bins=[355,355], range=[[0,16383],[0,16383]], density=True, cmap='plasma', norm = colors.LogNorm()) #range=[[1500,11500],[2000,12000]]
    
    Times = Zero.T[1]
    Time0 = Times[np.insert(np.diff(Times).astype(np.bool), 0, True)]
    Time0b = np.insert(Time0, 0, 0., axis=0)
    Time0b = np.delete(Time0b,-1)
    Counts0 = Zero.T[5]
    Counts0 = Counts0[np.insert(np.diff(Times).astype(np.bool), 0, True)]
    CntRt_0 = int(Counts0[-1]/(Time0[-1]-Time0b[-1]))
    text2.set_text('Zero Order Inst Rate: %.0f counts/s'%(CntRt_0))


    ### -1 Order
    Neg1 = np.loadtxt('Neg1_{}.csv'.format(modifier))
    for row in Neg1:
        datan1.append([int(row[2]),int(row[3]),int(row[4])])
    Xn1 = np.asarray(datan1).T[0]
    Yn1 = np.asarray(datan1).T[1]
    
    #hist3,x,y = np.histogram2d(Xn1, Yn1, bins=[164,164], range=[[0,16383],[0,16383]])
    XYn1.hist2d(Xn1, Yn1, bins=[355,355], range=[[0,16383],[0,16383]], density=True, cmap='plasma', norm = colors.LogNorm()) #range=[[1900,11500],[1900,11000]]
    
    Times = Neg1.T[1]
    Timen1 = Times[np.insert(np.diff(Times).astype(np.bool), 0, True)]
    Timen1b = np.insert(Timen1, 0, 0., axis=0)
    Timen1b = np.delete(Timen1b,-1)
    Countsn1 = Neg1.T[5]
    Countsn1 = Countsn1[np.insert(np.diff(Times).astype(np.bool), 0, True)]
    CntRt_n1 = int(Countsn1[-1]/(Timen1[-1]-Timen1b[-1]))
    text3.set_text('-1 Order Inst Rate: %.0f counts/s'%(CntRt_n1))
    
    #return plot1,plot2,plot3,text1,text2,text3

animation = FuncAnimation(fig, update, init_func=init_func, frames=np.arange(0, 10000, 25), interval=100)#, blit=True) #frames=np.arange(0, 10000, 25) #init_func=lambda: None #frames=[0,100000]

plt.show()


