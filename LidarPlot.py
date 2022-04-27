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

    return GenerateDataPolarPlotByDataAdjusted(data)
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

    ax.scatter(a_adj, r_adj, s=1, label='Lidar Range [in.]')

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


def rolling_window(array, window_size, freq=1):
    shape = (array.shape[0] - window_size + 1, window_size)
    strides = (array.strides[0],) + array.strides
    rolled = np.lib.stride_tricks.as_strided(array, shape=shape, strides=strides)
    return rolled[np.arange(0,shape[0],freq)]

def hampel_filter_v(input_data, half_win_length, threshold):
    # based from https://stackoverflow.com/a/71732887
    padded_data = np.concatenate([[np.nan]*half_win_length, input_data, [np.nan]*half_win_length])
    # windows = np.ma.array(np.lib.stride_tricks.sliding_window_view(padded_data, 2*half_win_length+1))
    windows = np.ma.array(rolling_window(padded_data, half_win_length*2+1))
    windows[np.isnan(windows)] = np.ma.masked
    median = np.ma.median(windows, axis=1)
    mad = np.ma.median(np.abs(windows-np.atleast_2d(median).T), axis=1)
    k = 1.4826
    bad = np.abs(input_data-median) > (k*mad*threshold)
    return np.where(bad)[0]


def GenerateDataPolarPlotByDataAdjusted(data):
    #angle, dist pairs
    ldata = data['Lidar']
    x = []
    y = []
    offset = 90
    for pair in ldata:
        ang = np.deg2rad(pair[0])
        yt = pair[1] * np.sin(ang + np.deg2rad(offset))
        xt = -pair[1] * np.cos(ang + np.deg2rad(offset))
        x.append(xt)
        y.append(yt)
    coord = np.array(list(zip(x, y)))
    x = np.array(x)
    y = np.array(y)

    # Eclipse Fit
    reg = LsqEllipse().fit(coord)
    center, width, height, phi = reg.as_parameters()
    # lsq_data = {'center': center, 'width': width, 'height': height, 'phi': phi}

    MM_TO_INCH = 1/25.4
    x_adj = x - center[0]
    y_adj = y - center[1]

    r_adj = np.sqrt(np.square(x_adj) + np.square(y_adj)) * MM_TO_INCH
    a_adj = np.arctan2(y_adj, x_adj)

    # Remove outlier data
    sortData = np.column_stack([a_adj, r_adj])
    sortData = sortData[sortData[:, 0].argsort()]
    outlier_indices = hampel_filter_v(sortData[:, 1], int(r_adj.size*5/360/2), 3)
    rnew = np.delete(sortData[:, 1], outlier_indices)
    anew = np.delete(sortData[:, 0], outlier_indices)
    # print("Removed ", r_adj.size - rnew.size)
    # print("of", r_adj.size)

    # New Eclipse Fit
    xnew = rnew * np.cos(anew)*25.4
    ynew = rnew * np.sin(anew)*25.4
    coord = np.array(list(zip(xnew, ynew)))
    reg = LsqEllipse().fit(coord)
    center, width, height, phi = reg.as_parameters()
    lsq_data = {'center': center, 'width': width, 'height': height, 'phi': phi, "Lidar_Data_f": tuple(zip(np.rad2deg(anew), rnew*25.4))}

    # Eclipse Plot Arrays
    angles = np.linspace(0, 360, 300)
    x1 = width*np.cos(np.deg2rad(angles))
    y1 = height*np.sin(np.deg2rad(angles))
    fitR = np.sqrt(np.square(x1) + np.square(y1)) * MM_TO_INCH
    fitA = np.arctan2(y1, x1)


    fig = plt.figure(dpi=300)
    ax = fig.add_subplot(111, projection='polar')
    ax.scatter(anew, rnew, s=1, label='Lidar Range [in.]')
    #center point
    ax.scatter(0, 0, s=10, label='Center of Fit')
    #fit shape
    ax.plot(fitA, fitR, c='red', label='Ellipse Fit [in.]')
    ax.legend(loc='upper center', bbox_to_anchor=(1.45, 0.8), shadow=True, ncol=1)
    ax.set_rmin(0)
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
        # data = db.get_lidar_data_byID(13)
        data = db.get_lidar_data_byID(26)
    import time
    buf = GenerateDataPolarPlotByDataAdjusted(data)
    # buf = GenerateDataPolarPlotByData(data)
    im = Image.open(buf[0])
    im.show()
