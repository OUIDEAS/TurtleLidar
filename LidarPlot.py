import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image
from ellipse import LsqEllipse
#from TurtleLidarDB import TurtleLidarDB, printLidarStatus, DebugPrint, create_csv_zip_bytes, clear_db_by_items

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
    range = 300*np.ones(rad.size)
    arm = 2
    y = arm*np.sin(rad)
    x = arm*np.cos(rad)
    xyarray = np.array(list(zip(x, y)))


    #trarray = np.array(list(zip(rad, range)))
    trarray = list(zip(rad, range))
    data = {'Lidar': trarray}
    #data = {}
    #data['lidar']= trarray

    return GenerateDataPolarPlotByData(data)
    # fig, ax = plt.subplots()
    # ax.scatter(x,y)
    # ax.grid(True)
    # ax.set_aspect('equal', 'box')
    # #plt.show()
    # buf = io.BytesIO()
    # plt.savefig(buf, format='png')
    # buf.seek(0)
    # return buf
def GenerateDataPolarPlotByData_Uncentered(data):
    # angle, dist pairs
    ldata = data['Lidar']
    x = []
    y = []
    alist = []
    rlist = []
    offset = 90
    for pair in ldata:
        ang = np.deg2rad(pair[0])
        yt = pair[1] * np.sin(ang + np.deg2rad(offset))
        xt = -pair[1] * np.cos(ang + np.deg2rad(offset))
        R1 = np.sqrt(xt ** 2 + yt ** 2)
        ang1 = np.arctan2(yt, xt)
        x.append(xt)
        y.append(yt)
        alist.append(ang1)
        rlist.append(R1)
    coord = np.array(list(zip(x, y)))
    x = np.array(x)
    y = np.array(y)
    alist = np.array(alist)
    rlist = np.array(rlist)

    # Eclipse Fit
    reg = LsqEllipse().fit(coord)
    center, width, height, phi = reg.as_parameters()
    lsq_data = {'center': center, 'width': width, 'height': height, 'phi': phi}
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
    # plt.polar(alist,rlist)
    # ax.scatter(x, y)

    ax.scatter(alist, rlist, s=1)
    ax.scatter(Ca, Cr, s=10)
    ax.plot(fitA, fitR, c='red')
    ax.legend(['Ellipse Fit', 'Lidar Data', 'Center of Fit'], loc='upper right')
    ax.set_rmin(0)
    ax.grid(True)
    ax.set_aspect('equal', 'box')
    # plt.show()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf, lsq_data

def GenerateDataPolarPlotByData(data):

    #angle, dist pairs
    ldata = data['Lidar']
    x = []
    y = []
    alist = []
    rlist = []
    offset = 90
    for pair in ldata:
        ang = np.deg2rad(pair[0])
        yt = pair[1] * np.sin(ang + np.deg2rad(offset))
        xt = -pair[1] * np.cos(ang + np.deg2rad(offset))
        R1 = np.sqrt(xt ** 2 + yt ** 2)
        ang1 = np.arctan2(yt, xt)
        x.append(xt)
        y.append(yt)
        alist.append(ang1)
        rlist.append(R1)
    coord = np.array(list(zip(x, y)))
    x = np.array(x)
    y = np.array(y)
    alist = np.array(alist)
    rlist = np.array(rlist)

    # Eclipse Fit
    reg = LsqEllipse().fit(coord)
    center, width, height, phi = reg.as_parameters()
    lsq_data = {'center': center, 'width': width, 'height': height, 'phi': phi}
    xyadjcoord = []
    xadj = []
    yadj = []
    a_adj = []
    r_adj = []
    MM_TO_INCH = 0.03937007874

    for pair in coord:
        xadjp = pair[0] - center[0]
        yadjp = pair[1] - center[1]
        xadj.append(xadjp)
        yadj.append(yadjp)

        rp = np.sqrt((xadjp) ** 2 + (yadjp ) ** 2)*MM_TO_INCH
        r_adj.append(rp)

        ap = np.arctan2(yadjp, xadjp)
        a_adj.append(ap)

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
        x1 = width * np.cos(np.deg2rad(a)) #+ xc
        y1 = height * np.sin(np.deg2rad(a)) #+ yc
        R = np.sqrt(x1 ** 2 + y1 ** 2)*MM_TO_INCH
        an = np.arctan2(y1, x1)
        fitA.append(an)
        fitR.append(R)

    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(111, projection='polar')
    #####ax = fig.add_subplot(111)
    #####fig, ax = plt.subplots()
    #####plt.polar(alist,rlist)
    #####ax.scatter(x, y)
    #####ax.scatter(xadj, yadj)

    ax.scatter(a_adj, r_adj, label='Lidar Range [in.]')

    #raw points
    #ax.scatter(alist, rlist, s=1)

    #center point
    # ax.scatter(Ca, Cr, s=10)
    ax.scatter(0, 0, s=10, label='Center of Fit')

    #fit shape
    ax.plot(fitA, fitR, c='red', label='Ellipse Fit [in.]')

    ax.legend(loc='upper center', bbox_to_anchor=(1.45, 0.8), shadow=True, ncol=1)
    ax.set_rmin(0)
    #ax.legend([, , ], loc='upper right')
    ax.grid(True)
    ax.set_aspect('equal', 'box')
    # plt.show()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf, lsq_data

#testfromDB()
# im = Image.open(buf)
# im.show()
# buf.close()

# img = fig2img(plt.gcf())
# img.show()
# if __name__ == '__main__':
#     print("lidar plot test")
#     with TurtleLidarDB() as db:
#          data = db.get_lidar_data_byID(1)
#     # #if (not data):
#     # #    return "error getting data"
#     pimage, lsq_data = GenerateDataPolarPlotByData(data)


if __name__ == '__main__':
    from TurtleLidarDB import TurtleLidarDB

    with TurtleLidarDB() as db:
        data = db.get_lidar_data_byID(19)

    buf = GenerateDataPolarPlotByData(data)
    im = Image.open(buf[0])
    im.show()