import csv
import numpy as np
import os
import matplotlib.pyplot as plt
from ellipse import LsqEllipse
import pickle
#laser mount was off by this much
#from scimath.units.api import UnitScalar
#from scimath.units.api import UnitArray
import scimath.units.api
from scimath.units.length import inch, mm, cm

def ReadFile(filename):
    csvfile = open(filename, newline='')

    reader = csv.reader(csvfile)

    alist_raw = []
    dlist_raw = []
    for index, row in enumerate(reader):
        #skip header
        if(index == 0):
            continue
        alist_raw.append(mountoffset+float(row[0]))
        dlist_raw.append(float(row[1]))
    csvfile.close()
    #convert to xy
    xraw = []
    yraw = []
    alist = []
    rlist = []
    for index, angle in enumerate(alist_raw):
        ang = np.deg2rad(angle)
        yt = dlist_raw[index] * np.sin(ang)
        xt = dlist_raw[index] * np.cos(ang)
        xraw.append(xt)
        yraw.append(yt)
        #alist.append(ang)
        #rlist.append(pair[1])
    coord = np.array(list(zip(xraw, yraw)))
    x = np.array(xraw)
    y = np.array(yraw)

    reg = LsqEllipse().fit(coord)
    center, width, height, phi = reg.as_parameters()
    print("Center " + str(center[0]) + ", " + str(center[0]) + " Height: " + str(height*2) + " Width: " + str(width*2))
    xadj = []
    yadj = []
    a_adj = []
    r_adj = []

    for pair in coord:
        xadjp = pair[0] - center[0]
        yadjp = pair[1] - center[1]
        xadj.append(xadjp)
        yadj.append(yadjp)

        rp = np.sqrt((xadjp) ** 2 + (yadjp) ** 2)
        r_adj.append(rp)

        ap = np.arctan2(yadjp, xadjp)
        a_adj.append(ap)

    coord = np.array(list(zip(xadj, yadj)))
    x = np.array(x)
    y = np.array(y)

    reg = LsqEllipse().fit(coord)
    center, width, height, phi = reg.as_parameters()
    print("Center " + str(center[0]) + ", " + str(center[0]) + " Height: " + str(height*2) + " Width: " + str(width*2))

    a_adj = np.asarray(a_adj)
    testp = np.round(a_adj, 2)

    w1 = np.where(testp == -0.0)[0].tolist()# 0.005045844763557249)
    w2 = np.where(a_adj >= np.deg2rad(179.5))[0].tolist()#np.deg2rad(180.000005008956))#3.140464327423381)
    #print(w1)
    #print("W1")
    r_w1 = []
    for i in range(len(w1)):
        index = w1[i]
        #print(r_adj[index])
        r_w1.append(r_adj[index])

    #print("W2")
    r_w2 = []
    for p in w2:
        #print(r_adj[p])
        r_w2.append(r_adj[p])
    r_w1 = np.asarray(r_w1)
    r_w2 = np.asarray(r_w2)
    wdith_avg = np.average(r_w1)+np.average(r_w2)
    print("Width")

    print(np.average(r_w1)+np.average(r_w2))

    h1 = np.where(testp == -1.58)[0]#np.deg2rad(-90.6231)
    #-1.581671473364073
    h2 = np.where(testp == 1.57)[0]#np.deg2rad(90.12518178)
    if(len(h2) == 0):
        h2 = np.where(testp == 1.58)[0]
        print("Cannot find 1.57")
    #1.5729811610194038
    # print(h1)
    # print(h2)

    r_h1 = []
    for i in range(len(h1)):
        index = h1[i]
        #print(r_adj[index])
        r_h1.append(r_adj[index])

    r_h2 = []
    for p in h2:
        #print(r_adj[p])
        r_h2.append(r_adj[p])
    r_h1 = np.asarray(r_h1)
    r_h2 = np.asarray(r_h2)
    height_avg = np.average(r_h1)+np.average(r_h2)
    print("Height")
    print(np.average(r_h1)+np.average(r_h2))

    fitX = []
    fitY = []
    fitA = []
    fitR = []
    angles = np.linspace(0, 360, 300)
    for a in angles:
        x1 = width * np.cos(np.deg2rad(a)) #+ xc
        y1 = height * np.sin(np.deg2rad(a)) #+ yc
        R = np.sqrt(x1 ** 2 + y1 ** 2)
        an = np.arctan2(y1, x1)
        fitX.append(x1)
        fitY.append(y1)
        fitA.append(an)
        fitR.append(R)

    fitdata = {'x': fitX, 'y': fitY, 'fitA': fitA, 'fitR': fitR}
    lsqdata = {'center': center, 'height': height, 'width':width, 'phi': phi}
    rawdata = {'x': xraw, 'y': yraw,'a': alist_raw, 'r': dlist_raw}
    measured = {'height': height_avg, 'width': wdith_avg}
    returndata = {"fit": fitdata, "lsq": lsqdata, "raw": rawdata, "measured": measured, "angleoffset": mountoffset}
    return returndata

mountoffset = -90
datapath = "..\\LiDARData\\"

#csvfile = open(datapath+"12-18-2020_20.35.37.csv", newline='')
# print(datapath+"PipeInField\\11-03-2020_13.49.32.csv")
# print(datapath+"PipeInField\\11-03-2020_13.38.48.csv")
# csvfile = datapath+"02-19-2021_14.05.34.csv"
# ret = ReadFile(csvfile)
# folder = datapath+"\\PipeInField\\"
# folder = datapath
# dataret = []
# for filename in os.listdir(folder):
#     if(not filename.endswith(".csv")):
#         continue
#     readfile = folder + filename
#     print(readfile)
#     ret = ReadFile(readfile)
#     dataret.append(ret)
#
# pickle.dump(dataret, open('save.dat', "wb"))

dataret = pickle.load(open('save.dat', "rb"))

height = []
width = []
heightm = []
widthm = []
for datai in dataret:
    hinch = scimath.units.api.UnitScalar(datai['lsq']['height'], units='mm').as_units(inch)
    hinchm = scimath.units.api.UnitScalar(datai['measured']['height'], units='mm').as_units(inch)
    winch = scimath.units.api.UnitScalar(datai['lsq']['width'], units='mm').as_units(inch)
    winchm = scimath.units.api.UnitScalar(datai['measured']['width'], units='mm').as_units(inch)

    # print(hinch)
    # print(datai['lsq']['height'])
    # print(datai['lsq']['width'])
    #print(hinch)
    #print(winch)
    height.append(float(2*hinch))
    width.append(float(2*winch))
    heightm.append(float(hinchm))
    widthm.append(float(winchm))
wavg = np.average(widthm)
havg = np.average(heightm)
print("Measured average width/height [inches]")
print(wavg)
print(havg) #real is 23.75
print("Measured piped diameter is 23.75 inches")
print("Calibration offset is: ")
offset = np.average([wavg,havg])-23.75
print(str(offset)+" inches")
fig, ax = plt.subplots()
x = np.linspace(1, len(height), len(height))
# ax.scatter(x, height)
# ax.scatter(x, width)
ax.scatter(x, heightm)
ax.scatter(x, widthm)
#csvfile = open(datapath+"PipeInField\\11-03-2020_13.49.32.csv", newline='')
#ret = ReadFile(csvfile)
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='polar')
# fig, ax = plt.subplots()
# # ax.scatter(x, y)
# ax.scatter(xadj, yadj)
# # ax.scatter(alist, rlist, s=1)
# # ax.scatter(Ca, Cr, s=10)
# # ax.plot(fitA, fitR, c='red')
# ax.plot(fitX, fitY, c='red')
# # ax.legend(['Ellipse Fit', 'Lidar Data', 'Center of Fit'], loc='upper right')
ax.grid(True)
# ax.set_aspect('equal', 'box')
ax.set_ylabel('Distance [inch]')
ax.set_xlabel('Samples [-]')
plt.ylim([24, 26])
# ax.legend(['Fit-Width', 'Fit-Height', 'Exact-Width','Exact-Height'])
ax.legend(['Exact-Width','Exact-Height'])

plt.show()
#alist = np.array(alist)
#rlist = np.array(rlist)