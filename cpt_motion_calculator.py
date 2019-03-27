import csv
import os


# Converts an orientation string into a number for easy indexing in data structures
def mapOrientationToNumber(orientationStr):
    orientationInt = 0
    try:
        orientationInt = ORIENTATIONS.index(orientationStr)
    except ValueError:
        print("Invalid orientation value in the data: " + orientationStr)
    return orientationInt
    
# Converts an orientation number back into a string
def mapOrientationToStr(orientationInt):
    return ORIENTATIONS[orientationInt]

####################################
########### MAIN SECTION ###########
####################################

dataFolder = 'motion_data'
ORIENTATIONS = ('S', 'R', 'L')
NUM_DIRECTED_SQUARES = 9
NUM_RESULT_SQUARES = 25
NUM_ORIENTATIONS = len(ORIENTATIONS)

# This will hold a list of result state tuples in a 2D array indexed by the directed square/orientation
motionCounts = [[[] for y in range(NUM_ORIENTATIONS)] for x in range(NUM_DIRECTED_SQUARES)]

# Write result tuple state data to motionCounts
for dataFile in os.listdir('motion_data'):
    with open(os.path.join(dataFolder, dataFile)) as csvfile:
        dataReader = csv.reader(csvfile)
        motionDataList = map(tuple, dataReader)
        
        for row in motionDataList:
            # Every other row is all commas so ignore those
            if row[0] and row[1]:
                directedSquare = row[0]
                directedOrientation = row[1]
                endSquare = row[2]
                endOrientation = row[3]
                
                motionCounts[int(directedSquare)][mapOrientationToNumber(directedOrientation)].append((endSquare, endOrientation))
                
#print(motionCounts)

# Write probabilities to CSV file
with open('motion_cpt.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["DIRECTED_SQUARE", "DIRECTED_ORIENTATION", "RESULT_SQUARE_1", "RESULT_ORIENTATION_1", "RESULT_PROBABILITY_1",
        "RESULT_SQUARE_2", "RESULT_ORIENTATION_2", "RESULT_PROBABILITY_2", "etc..."])

    for directedSquare in range(NUM_DIRECTED_SQUARES):
        for directedOrientation in range(NUM_ORIENTATIONS):
            #print("DIRECTED: " + str(directedSquare) + "," + str(directedOrientation))
        
            # Table indexed by result square and orientation that stores how many times the robot ended up in that state (for a given
            # directed state since we are in two nested for loops)
            endStateTable = [[0.0 for y in range(NUM_ORIENTATIONS)] for x in range(NUM_RESULT_SQUARES)]
            
            for endStateTuple in motionCounts[directedSquare][directedOrientation]:
                #print(endStateTuple)
                endSquare = int(endStateTuple[0])
                endOrientation = mapOrientationToNumber(endStateTuple[1])
                
                endStateTable[endSquare][endOrientation] = endStateTable[endSquare][endOrientation] + 1.0
            
            # Compute the probabilities that the robot will end up in each state
            totalEndStateCount = len(motionCounts[directedSquare][directedOrientation])
            endStateCpt = [[p / float(totalEndStateCount) for p in subl] for subl in endStateTable]
            #print(endStateCpt)
            
            # For a directed square/orientation, write a row containing all end square/orientation states the robot ended up in that 
            # have a non-zero probability
            csvRow = []
            csvRow.append(str(directedSquare))
            csvRow.append(mapOrientationToStr(directedOrientation))
            for resultSquare in range(NUM_RESULT_SQUARES):
                for resultOrientation in range(NUM_ORIENTATIONS):
                    probValue = endStateCpt[resultSquare][resultOrientation]
                    if probValue > 0.0:
                        csvRow.append(str(resultSquare))
                        csvRow.append(mapOrientationToStr(resultOrientation))
                        csvRow.append(str(probValue))
            writer.writerow(csvRow)       