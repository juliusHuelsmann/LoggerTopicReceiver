
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import subprocess
import sys
from scipy import interpolate

from backend import *




backend = Backend(*sys.argv[1:])

def tryParse(s):
    try:
        return int(s)
    except:
        return 1



i=0
factor=1
mv = 10
#matplotlib.rcParams['patch.edgecolor'] = 'FFFFFF'
matplotlib.rcParams['axes.facecolor'] = '000000'
matplotlib.rcParams['axes.edgecolor'] = 'AAAAAA'
#matplotlib.rcParams['font.sans-serif'] = ['Source Han Sans TW', 'sans-serif']
matplotlib.rcParams['text.color'] = 'AAAAAA'
#matplotlib.rcParams['xtick.alignment'] = 'top'
#matplotlib.rcParams['ytick.alignment'] = 'center_baseline'
#matplotlib.rcParams['xtick.direction'] = 'in'
#matplotlib.rcParams['ytick.direction'] = 'in'
matplotlib.rcParams['ytick.color'] = 'AAAAAA'
matplotlib.rcParams['xtick.color'] = 'AAAAAA'
#matplotlib.rcParams['xtick.color'] = 'FFFFFF'
#matplotlib.rcParams['ytick.labelright'] = True
matplotlib.rcParams['xtick.labelbottom'] = True
#matplotlib.rcParams['xtick.labeltop'] = True
matplotlib.rcParams['text.latex.preview'] = True

matplotlib.rcParams['toolbar'] = 'None'


szpp = 3
fig = plt.figure(figsize=(szpp, szpp), facecolor=[0,0,0,1])
#print(matplotlib.rcParams.keys())


subplots = []




#XXX block vis thread when receiving incoming message.

def visualize(plotsInCol=3):
    global subplots
    global fig

    bk = backend.Z
    amountPlots = len(bk)
    if amountPlots == 0: return
    
    rows = int(np.ceil(amountPlots / plotsInCol))
    cols = int(min(amountPlots, plotsInCol))
    
    if rows != len(subplots) or len(subplots) == 0 or cols != len(subplots[0]):
        plt.close("all")
        fig = plt.figure(figsize=(szpp*cols,szpp*rows), facecolor=[0,0,0,1])
        plt.subplots_adjust(0.14 / cols, 0.10 / rows, 1 - .02 / cols, 1-.10 / rows)
        #plt.subplots_adjust(0.04, 0.06, 0.97, 0.94)
        subplots = [[plt.subplot(rows, cols, r*cols + c+1) for c in range(cols)] for r in range(rows)]

    for plti, i in enumerate(bk):
        assert(type(bk) is dict)
       
        #sp = plt.subplot(rows, cols, plti+1)
        sp = subplots[int(np.floor(plti / cols))][plti % cols]
        sp.clear()

        for j in bk[i]:
            lkz = bk[i][j][1]
            tkz = bk[i][j][0]
            name = j if j else i
            
            if lkz.shape[0]:
           
                #
                # Should work with arbritrary awmount of parameters
                if tkz == "scatter" or tkz == "points" or tkz == "histogram":
                    x = lkz[:,0] if lkz.shape[1] > 1 else np.arange(lkz.shape[0])
                    yy = lkz[:,1:] if lkz.shape[1] > 1 else lkz[:,0:1]
                    yy = yy.T

                    for en,y in enumerate(yy):
                        if tkz == "points":
                            sp.plot(x, y, 
                                    label= name + ("[" + str(en) + "]" if yy.shape[0] > 1 else ""))
                        elif tkz == "histogram":
                            #sp.hist(x  if tkz != "histogram" else y, y if tkz != "histogram" else x, 
                            #        label= name + ("[" + str(en) + "]" if yy.shape[0] > 1 else ""))
                            sp.hist(y, label=name + ("[" + str(en) + "]" if yy.shape[0] > 1 else ""))
                        else:
                            sp.plot(x, y,  
                                    label= name + ("[" + str(en) + "]" if yy.shape[0] > 1 else ""))


                
                elif tkz == "interval" :
                    assert(lkz.shape[1] == 2 or lkz.shape[1] == 3)
                    x = np.hstack((lkz[:,0:2], np.ones(lkz.shape[0])[:,np.newaxis] * np.nan)).flatten()
                    y = np.ones(x.shape[0])  * (lkz[0,2] if lkz.shape[1] == 3 else tryParse(j))

                    sp.plot(x, y, label= name)
                
        sp.legend()
        sp.set_title(name)




def walk(multithreaded=True):
    if multithreaded: backend.start()
    while True:
        if not multithreaded: backend.receiveVal()
        visualize()
        plt.pause(.1)


walk()
while False:

    
    # read core temperature
    #process = subprocess.Popen(['less /sys/devices/platform/coretemp.0/hwmon/hwmon1/temp?_input | xargs'], stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE)
    #output, error = process.communicate()

    #ii=i*factor
    #v[ii] = np.fromstring(output, dtype=int, sep=" ") / 1000
    #mv = max(np.max(v[ii]) + 5, mv)
    #if i > 2 and factor > 1:
    #    tck = [interpolate.splrep(ara[:ii:factor], v[:ii:factor,j],k=2) for j in range(3)]
    #    v[:ii] = np.array([interpolate.splev(ara[:ii], tck[j]) for j in range(3)]).T


    #ax2.clear()
    colors = [(.6, .5, .5), (.5, .6, .5), (.5, .5, .6)]
    steigung = not True
    abrt = ii if steigung else ii-3
    if abrt > 0:
        for k in range(3): 
            ax.plot(ara[:abrt], v[:abrt, k], color=colors[k], label=str(k))
        ax2.hist(v[:abrt:factor], color=colors, label=["1", "2", "3"])

        ax.grid(color=(.08, .11, .11), linestyle=':', linewidth=1)
        ax2.grid(color=(.08, .11, .11), linestyle=':', linewidth=1)
    ax.set_ylim([20, mv])

    plt.pause(1)
    i+=1
    if abrt == 1: 
        ax.legend()
        ax2.legend()
        ax2.set_title("ax2")
        ax.set_title("ax1")
        #plt.suptitle("supertitle")








