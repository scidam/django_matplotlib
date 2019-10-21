import matplotlib.pyplot as plt

def test_figure():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot([1,2,3,4], [4,5,2,1])
    return fig
