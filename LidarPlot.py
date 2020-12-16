import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image

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


# im = Image.open(buf)
# im.show()
# buf.close()

# img = fig2img(plt.gcf())
# img.show()
