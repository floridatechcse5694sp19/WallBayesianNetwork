import matplotlib as mpl
from matplotlib import pyplot
import numpy as np

num_rows, num_cols = 8, 4

# probMap is a 2D array with (0,0) starting in the lower left
def showProbMap(probMap):
    # Convert to pvals for display by map
    pvals = np.zeros((8,4))
    #pvals[3,0] = 0.5
    #pvals[3,1] = 0.3
    #pvals[3,2] = 0.7
    #pvals[3,3] = 5.8
    for x in range(num_cols):
        for y in range (num_rows):
            pvals[y,x] = probMap[x][y]

    cmap = mpl.colors.LinearSegmentedColormap.from_list('my_colormap',['white','blue'],256)

    img = pyplot.imshow(pvals, interpolation='nearest', origin='lower', aspect='auto', cmap=cmap, vmin=0, vmax=1)

    pyplot.suptitle('Straight Orientation')

    for x in range(num_cols):
        for y in range (num_rows):
            pyplot.text(x, y, str(pvals[y,x]), horizontalalignment='center', verticalalignment='center')
 
    pyplot.colorbar(img, cmap=cmap)
    pyplot.show()
    