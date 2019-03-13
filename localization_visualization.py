import matplotlib as mpl
from matplotlib import pyplot
import numpy as np

num_rows, num_cols = 8, 4

# probMap is a 2D array with (0,0) starting in the lower left
def showProbMap(probMapStraight, probMapLeft, probMapRight):
    # Convert to pvals for display by map
    pvalsStraight = np.zeros((8,4))
    pvalsLeft = np.zeros((8,4))
    pvalsRight = np.zeros((8,4))
    #pvals[3,0] = 0.5
    #pvals[3,1] = 0.3
    #pvals[3,2] = 0.7
    #pvals[3,3] = 5.8
    for x in range(num_cols):
        for y in range (num_rows):
            pvalsStraight[y,x] = probMapStraight[x][y]
            pvalsLeft[y,x] = probMapLeft[x][y]
            pvalsRight[y,x] = probMapRight[x][y]

    cmap = mpl.colors.LinearSegmentedColormap.from_list('my_colormap',['white','blue'],256)

    fig, (ax1, ax2, ax3) = pyplot.subplots(1,3, figsize=(12, 5))
    
    fig.suptitle('Probabilities of Nao robot location')
    
    imgL = ax1.imshow(pvalsLeft, interpolation='nearest', origin='lower', aspect='auto', cmap=cmap, vmin=0, vmax=1)
    ax1.set_title('Left Orientation')
    imgS = ax2.imshow(pvalsStraight, interpolation='nearest', origin='lower', aspect='auto', cmap=cmap, vmin=0, vmax=1)
    ax2.set_title('Straight Orientation')
    imgR = ax3.imshow(pvalsRight, interpolation='nearest', origin='lower', aspect='auto', cmap=cmap, vmin=0, vmax=1)  
    ax3.set_title('Right Orientation')    

    for x in range(num_cols):
        for y in range (num_rows):
            ax1.text(x, y, str(pvalsLeft[y,x]), horizontalalignment='center', verticalalignment='center')
            ax2.text(x, y, str(pvalsStraight[y,x]), horizontalalignment='center', verticalalignment='center')
            ax3.text(x, y, str(pvalsRight[y,x]), horizontalalignment='center', verticalalignment='center')
 
    pyplot.colorbar(imgS, cmap=cmap)
    pyplot.show()
    