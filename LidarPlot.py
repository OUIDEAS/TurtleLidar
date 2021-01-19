import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image
from ellipse import LsqEllipse

def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img

def GiveTestImg():
    rad = np.deg2rad(np.arange(0, 360, 1))

    arm = 2
    y = arm*np.sin(rad)
    x = arm*np.cos(rad)

    fig, ax = plt.subplots()
    ax.scatter(x,y)
    ax.grid(True)
    ax.set_aspect('equal', 'box')
    #plt.show()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

def GenerateDataPolarPlotByData(data):


    #angle, dist pairs
    ldata = data['Lidar']
    x = []
    y = []
    alist = []
    rlist = []
    for pair in ldata:
        ang = np.deg2rad(pair[0])
        yt = pair[1]*np.sin(ang)
        xt = pair[1]*np.cos(ang)
        x.append(xt)
        y.append(yt)
        alist.append(ang)
        rlist.append(pair[1])
    coord = np.array(list(zip(x, y)))
    x = np.array(x)
    y = np.array(y)
    alist = np.array(alist)
    rlist = np.array(rlist)

    # Eclipse Fit
    reg = LsqEllipse().fit(coord)
    center, width, height, phi = reg.as_parameters()

    # Center of Fit
    xc = center[0]
    yc = center[1]
    Cr = np.sqrt(xc ** 2 + yc ** 2)
    Ca = np.arctan2(yc, xc)

    # Eclipse Plot Arrays
    fitA = []
    fitR = []
    angles = np.linspace(0, 360, 300)
    for a in angles:
        x1 = width * np.cos(np.deg2rad(a)) + xc
        y1 = height * np.sin(np.deg2rad(a)) + yc
        R = np.sqrt(x1 ** 2 + y1 ** 2)
        an = np.arctan2(y1, x1)
        fitA.append(an)
        fitR.append(R)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='polar')

    # fig, ax = plt.subplots()
    #plt.polar(alist,rlist)
    # ax.scatter(x, y)

    ax.scatter(alist, rlist, s=1)
    ax.scatter(Ca, Cr, s=10)
    ax.plot(fitA, fitR, c='red')
    ax.legend(['Ellipse Fit', 'Lidar Data', 'Center of Fit'], loc='upper right')
    ax.grid(True)
    ax.set_aspect('equal', 'box')
    # plt.show()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

#testfromDB()
# im = Image.open(buf)
# im.show()
# buf.close()

# img = fig2img(plt.gcf())
# img.show()
