import csv
import os
import cpt_motion_calculator as prob_helper


# Generate probabilities for the sonar counts being within each range (currently range size of 1 inch) for a given state
def calculateProbForSingleState(sonarCptTable, sonarReadings, col, row, orientation):
    leftProbsForState = sonarCptTable[col][row][orientation]
    
    leftSonarValues = sonarReadings[col][row][orientation]
    numLeftValues = len(leftSonarValues)
    for sonarVal in leftSonarValues:
        sonarRangeKey = getSonarRangeKey(sonarVal)
        if sonarRangeKey in leftProbsForState:
            leftProbsForState[sonarRangeKey] = leftProbsForState[sonarRangeKey] + 1
        else:
            leftProbsForState[sonarRangeKey] = 1
    
    for sonarValKey, numReadings in leftProbsForState.iteritems():
        sonarCptTable[col][row][orientation][sonarValKey] = round((float(numReadings) / float(numLeftValues)), 5)
                    

# Gets the range key for a sonar value that is used for a map of sonar value range probabilities for a given state
def getSonarRangeKey(sonarValue):
    quotient, remainder = divmod(sonarValue, sonar_increment_size)
    return quotient
    
def runLandmarkCptGeneration(sensor_folder):
    # This method generates prob tables for the sonar values being within a range for each state (square/orientation)
    
    meter_to_inch_conversion = 39.37

    numRows, numCols = 8, 4;
    sonarReadingsLeft = [[[[] for z in range(prob_helper.NUM_ORIENTATIONS)] for y in range(numRows)] for x in range(numCols)]
    sonarReadingsRight = [[[[] for z in range(prob_helper.NUM_ORIENTATIONS)] for y in range(numRows)] for x in range(numCols)]
    sonarLeftCptTable = [[[{} for z in range(prob_helper.NUM_ORIENTATIONS)] for y in range(numRows)] for x in range(numCols)]
    sonarRightCptTable = [[[{} for z in range(prob_helper.NUM_ORIENTATIONS)] for y in range(numRows)] for x in range(numCols)]

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

                        # column 9 is left sonar, column 10 is right sonar
                        sonarReadingsLeft[mappedColNum][mappedRowNum][destOrientationInt].append(
                            float(row[9])*meter_to_inch_conversion)
                        sonarReadingsRight[mappedColNum][mappedRowNum][destOrientationInt].append(
                            float(row[10])*meter_to_inch_conversion)

    #print(sensorLandmarkCounts)
    #print("Values for 1,5,2: " + str(sensorLandmarkCounts[1][5][2]))
    #print("Length: " + str(len(sensorLandmarkCounts[1][5][2])))

    # Generate probabilities for the sonar counts within each range for each state
    for x in range(numCols):
        for y in range(numRows):
            for z in range(prob_helper.NUM_ORIENTATIONS):
                calculateProbForSingleState(sonarLeftCptTable, sonarReadingsLeft, x, y, z)
                calculateProbForSingleState(sonarRightCptTable, sonarReadingsRight, x, y, z)

    #print("Prob for 1,5,0: " + str(sonarRightCptTable[1][5][0]))

    # Generate the CSV with the probabilities
    with open('sonar_cpt_evidence.csv', 'w') as csvfile:
        fieldnames = ['column', 'row', 'orientation', 'sonar_name', 'sonar_range_begin_val', 'probability']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for x in range(numCols):
            for y in range(numRows):
                for z in range(prob_helper.NUM_ORIENTATIONS):
                    col = str(x)
                    row = str(y)
                    orientation = prob_helper.mapOrientationToStr(z)
                    
                    writeToCsv(writer, 'L', sonarLeftCptTable[x][y][z], col, row, orientation)
                    writeToCsv(writer, 'R', sonarRightCptTable[x][y][z], col, row, orientation)

# Write probabilities to a CSV for a single sonar sensor and for a single state
def writeToCsv(writer, sonarName, probsForSingleState, col, row, orientation):   
    for sonarRangeValKey, probVal in probsForSingleState.iteritems():
        writer.writerow({'column': col, 'row': row, 'orientation': orientation, 'sonar_name': sonarName, 'sonar_range_begin_val': str(sonarRangeValKey), 'probability': str(probVal)})
    
##############
#### MAIN ####
##############

sensor_folder = 'sensor_data'
sonar_increment_size = 1.0

if __name__ == '__main__':
    runLandmarkCptGeneration(sensor_folder)