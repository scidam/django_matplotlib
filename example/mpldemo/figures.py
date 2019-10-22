import matplotlib.pyplot as plt
import numpy as np


def plot_line():
    """ Plots piecewise line """

    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [3, 2, 6])
    return fig


def plot_sine():
    """ Plots sine function """

    fig, ax = plt.subplots()
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)
    ax.plot(x, y)
    return fig


def image_plot():
    """ plt.imshow demonstration 
    
    Source:
    
        https://matplotlib.org/3.1.0/gallery/images_contours_and_fields/image_demo.html
    
    """

    delta = 0.025
    x = y = np.arange(-3.0, 3.0, delta)
    X, Y = np.meshgrid(x, y)
    Z1 = np.exp(-X**2 - Y**2)
    Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)
    Z = (Z1 - Z2) * 2
    fig, ax = plt.subplots()
    im = ax.imshow(Z, interpolation='bilinear', cmap='RdYlGn',
                origin='lower', extent=[-3, 3, -3, 3],
                vmax=abs(Z).max(), vmin=-abs(Z).max()
            )
    return fig


def plot_with_args(x, y):
    """ Pass arguments to plotting function """

    fig, ax = plt.subplots()
    plt.plot(x, y)
    return fig


def countour_plot(custom_title):
    """ Contour plot demo """

    delta = 0.025
    x = np.arange(-3.0, 3.0, delta)
    y = np.arange(-2.0, 2.0, delta)
    X, Y = np.meshgrid(x, y)
    Z1 = np.exp(-X**2 - Y**2)
    Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)
    Z = (Z1 - Z2) * 2
    fig, ax = plt.subplots()
    CS = ax.contour(X, Y, Z)
    ax.clabel(CS, inline=1, fontsize=10)
    ax.set_title(custom_title)
    return fig


    