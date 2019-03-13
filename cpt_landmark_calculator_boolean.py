import os
import csv


def getTotalLandmarksSeen(sensor_folder):

    totalLandmarkCount = 0
    
    for dataFile in os.listdir(sensor_folder):
        #if dataFile == 'round 3.csv':
            with open(os.path.join(sensor_folder, dataFile)) as csvfile:
                dataReader = csv.reader(csvfile)
                sensorDataList = map(tuple, dataReader)
                for row in sensorDataList:
                    # ignore every other row which is all commas, and column 11 in a row is landmark data
                    if row[1] and float(row[22]) != 0.0:
                        totalLandmarkCount = totalLandmarkCount + 1
                            
    return totalLandmarkCount
    
def runLandmarkCptGeneration(sensor_folder, currentOrientation, totalLandmarkCountAllOrientations):
    ## This method does the full CPT calculation and output for a single orientation. 
    ## Call this multiple times, one for each orientation
    
    meter_to_inch_conversion = 39.37

    numRows, numCols = 8, 4;
    sensorLandmarkCounts = [[0 for x in range(numRows)] for y in range(numCols)]
    orientationLandmarkCount = 0
    sensorLandmarkCptTable = [[0.0 for x in range(numRows)] for y in range(numCols)]
    sensorTotalCounts = [[0 for x in range(numRows)] for y in range(numCols)] 

    # The (x,y) coordinates for right/left orientation is not the same as straight, need to map
    # Manually mapping this seems easier given the small number of squares
    # (Ignore this, this was just used to figure out the mapping algorithm)
    #rightSquareMapping[0][0] = (0,7)
    #rightSquareMapping[0][1] = (1,7)
    #rightSquareMapping[0][2] = (2,7)
    #rightSquareMapping[0][3] = (3,7)
    #rightSquareMapping[1][0] = (0,6)
    #rightSquareMapping[1][1] = (1,6)
    #rightSquareMapping[1][2] = (2,6)
    #rightSquareMapping[1][3] = (3,6)
    #rightSquareMapping[2][0] = (0,5)
    #rightSquareMapping[2][1] = (1,5)
    #rightSquareMapping[2][2] = (2,5)
    #rightSquareMapping[2][3] = (3,5)
    #leftSquareMapping[0][0] = (3,0)
    #leftSquareMapping[0][1] = (2,0)
    #leftSquareMapping[0][2] = (1,0)
    #leftSquareMapping[0][3] = (0,0)
    #leftSquareMapping[1][0] = (3,1)
    #leftSquareMapping[1][1] = (2,1)
    #leftSquareMapping[1][2] = (1,1)
    #leftSquareMapping[1][3] = (0,1)
    #leftSquareMapping[2][0] = (3,2)
    #leftSquareMapping[2][1] = (2,2)
    #leftSquareMapping[2][2] = (1,2)
    #leftSquareMapping[2][3] = (0,2)

    for dataFile in os.listdir(sensor_folder):
        #if dataFile == 'round 3.csv':
            with open(os.path.join(sensor_folder, dataFile)) as csvfile:
                dataReader = csv.reader(csvfile)
                sensorDataList = map(tuple, dataReader)
                for row in sensorDataList:
                    # Every other row is all commas so ignore those
                    if row[1] and row[3].strip() == currentOrientation:
                        colNum = int(row[1])
                        rowNum = int(row[2])
                        #print(colNum)
                        #print(rowNum)
                        
                        # 'Straight' orientation uses the standard row/column number ordering, starting from lower left as [0,0]
                        if row[3].strip() == 'S':
                            mappedColNum = colNum
                            mappedRowNum = rowNum
                        # 'Right' orientation starts from the lower left numbering also, need to convert to the 'Straight' orientation
                        elif row[3].strip() == 'R':
                            mappedColNum = rowNum
                            mappedRowNum = numRows - colNum - 1
                            #print('(' + str(colNum) + ',' + str(rowNum) + ') -> (' + str(mappedColNum) + ',' + str(mappedRowNum) + ')')
                        # 'Left' orientation starts from the lower left numbering also, need to convert to the 'Straight' orientation
                        elif row[3].strip() == 'L':
                            mappedColNum = numCols - rowNum - 1
                            mappedRowNum = colNum
                            #print('(' + str(colNum) + ',' + str(rowNum) + ') -> (' + str(mappedColNum) + ',' + str(mappedRowNum) + ')')                       

                        # column 11 in a row is landmark data
                        if float(row[22]) != 0.0:
                            sensorLandmarkCounts[mappedColNum][mappedRowNum] = sensorLandmarkCounts[mappedColNum][mappedRowNum] + 1
                            orientationLandmarkCount = orientationLandmarkCount + 1
                        
                        sensorTotalCounts[mappedColNum][mappedRowNum] = sensorTotalCounts[mappedColNum][mappedRowNum] + 1 

    print(sensorLandmarkCounts)
    print(orientationLandmarkCount)
    print(totalLandmarkCountAllOrientations)
    print(sensorTotalCounts[0])
    print(sensorTotalCounts)
    print(sensorTotalCounts)
    print(sensorTotalCounts[3])

    # Compute the probabilities for a given square given a landmark
    for x in range(numCols):
        for y in range(numRows):
            sensorLandmarkCptTable[x][y] = float(sensorLandmarkCounts[x][y]) / float(totalLandmarkCountAllOrientations)

    print(sensorLandmarkCptTable)

    # Write the landmark data to a CSV file in the same orientation as the robot facing forward 
    # (may want to change this for a script to read this in, but this is just to visualize it for now)
    with open('landmark_cpt_' + currentOrientation + '.csv', 'w') as csvfile:
        fieldnames = ['landmarkProb']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        for y in range(numRows - 1 , -1, -1):
            rowData = ""
            for x in range(numCols):
                rowData = rowData + str(sensorLandmarkCptTable[x][y])
                if x != (numCols - 1):
                    rowData = rowData + ","
            writer.writerow({'landmarkProb': rowData})

##############
#### MAIN ####
##############

sensor_folder = 'sensor_data'

totalLandmarkCountAllOrientations = getTotalLandmarksSeen(sensor_folder)

runLandmarkCptGeneration(sensor_folder, 'S', totalLandmarkCountAllOrientations)
runLandmarkCptGeneration(sensor_folder, 'L', totalLandmarkCountAllOrientations)
runLandmarkCptGeneration(sensor_folder, 'R', totalLandmarkCountAllOrientations)