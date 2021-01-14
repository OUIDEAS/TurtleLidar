import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image
from TurtleLidarDB import TurtleLidarDB

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

def testfromDB(dataid):
    data = []
    with TurtleLidarDB() as db:
        data = db.get_lidar_data(dataid)

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
    x = np.array(x)
    y = np.array(y)
    alist = np.array(alist)
    rlist = np.array(rlist)

    fig, ax = plt.subplots()
    #plt.polar(alist,rlist)
    ax.scatter(x, y)
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
