import csv
import os
import cpt_motion_calculator as prob_helper


def runLandmarkCptGeneration(sensor_folder):
    ## This method does the full CPT calculation and output for a single orientation. 
    ## Call this multiple times, one for each orientation
    
    meter_to_inch_conversion = 39.37

    numRows, numCols = 8, 4;
    sensorLandmarkCounts = [[[[] for z in range(prob_helper.NUM_ORIENTATIONS)] for y in range(numRows)] for x in range(numCols)]
    sensorLandmarkCptTable = [[[0.0 for z in range(prob_helper.NUM_ORIENTATIONS)] for y in range(numRows)] for x in range(numCols)]

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
                    if row[1]:
                        colNum = int(row[1])
                        rowNum = int(row[2])
                        destOrientation = row[3].strip()
                        destOrientationInt = prob_helper.mapOrientationToNumber(destOrientation)
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
                        landmarkValue = False
                        if float(row[22]) != 0.0:
                            landmarkValue = True
                        
                        sensorLandmarkCounts[mappedColNum][mappedRowNum][destOrientationInt].append(landmarkValue)

    #print(sensorLandmarkCounts)
    #print("Values for 1,5,2: " + str(sensorLandmarkCounts[1][5][2]))
    #print("Length: " + str(len(sensorLandmarkCounts[1][5][2])))

    for x in range(numCols):
        for y in range(numRows):
            for z in range(prob_helper.NUM_ORIENTATIONS):
                # Compute the probabilities for a given square/orientation given landmark true/false data for that state
                landmarkValues = sensorLandmarkCounts[x][y][z]
                numTrueValues = 0
                numValues = 0
                for landmarkVal in landmarkValues:
                    if landmarkVal:
                        numTrueValues = numTrueValues + 1
                    numValues = numValues + 1
                    
                sensorLandmarkCptTable[x][y][z] = float(numTrueValues) / float(numValues)

    #print("Prob for 1,4,1: " + str(sensorLandmarkCptTable[1][4][1]))

    with open('landmark_cpt_evidence.csv', 'w') as csvfile:
        fieldnames = ['column', 'row', 'orientation', 'landmark_prob']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # This commented out part writes it in reverse so it's like you're the robot facing straight when reading the data
        #for y in range(numRows - 1 , -1, -1):
        for x in range(numCols):
            for y in range(numRows):
                for z in range(prob_helper.NUM_ORIENTATIONS):
                    col = str(x)
                    row = str(y)
                    orientation = prob_helper.mapOrientationToStr(z)
                    landmarkProb = str(sensorLandmarkCptTable[x][y][z])
                    
                    writer.writerow({'column': col, 'row': row, 'orientation': orientation, 'landmark_prob': landmarkProb})

##############
#### MAIN ####
##############

sensor_folder = 'sensor_data'

runLandmarkCptGeneration(sensor_folder)