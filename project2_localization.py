import cpt_motion_calculator as prob_helper
import csv
from random import randint
import cpt_sonar_calculator_evidence as sonar_helper

# Random coin for particle filtering 
def coin(bias):
    n = randint(1, 100)
    if (n % 100 < (bias * 100)):
        return True
    return False

# Using the transition probs from recorded data, make 10% of transition probability spread across the remaining states that previously
# had 0 probability. Return the results in a 2D list indexed by result square and result orientation in integer form.
def createTransitionProbMatrixWithNoise(transitionProbs):
    endStateProbTable = [[0.0 for y in range(prob_helper.NUM_ORIENTATIONS)] for x in range(prob_helper.NUM_RESULT_SQUARES)]
    
    # Fill in the non-zero probabilities. Times by 0.9 to leave 10% of probability for the remaining states
    for transitionProb in transitionProbs:
        resultSquare = transitionProb[0]
        resultOrientation = prob_helper.mapOrientationToNumber(transitionProb[1])
        endStateProbTable[resultSquare][resultOrientation] = round(transitionProb[2] * 0.9, 10)
    
    noiseProb = 0.1 / ((prob_helper.NUM_ORIENTATIONS * prob_helper.NUM_RESULT_SQUARES) - len(transitionProbs))
    noiseProb = round(noiseProb, 10)
    
    endStateProbTableWithNoise = [[noiseProb if y == 0.0 else y for y in x ] for x in endStateProbTable]
    
    return endStateProbTableWithNoise

# Gets the Probability(Landmark = True | State) where State is the square and orientation combination
def getLandmarkEvidenceProbForState(landmarkEvidenceProbs, squareColumn, squareRow, orientation):
    orientationInt = prob_helper.mapOrientationToNumber(orientation)
    probOfLandmark = landmarkEvidenceProbs[squareColumn][squareRow][orientationInt]
    return probOfLandmark
    
# Gets the Probability(Sonar Value | State) where State is the square and orientation combination
# and the sonar value has to fall within a range (currently 1 inch range size)
def getSonarEvidenceProbForState(sonarEvidenceProbs, squareColumn, squareRow, orientation, sonarVal):
    orientationInt = prob_helper.mapOrientationToNumber(orientation)
    sonarKey = sonar_helper.getSonarRangeKey(sonarVal)
    
    sonarProbsForState = sonarEvidenceProbs[squareColumn][squareRow][orientationInt]
    
    probOfSonarVal = 0.0
    try:
        probOfSonarVal = sonarProbsForState[sonarKey]
    except KeyError:
        closestSonarKey = min(sonarProbsForState.keys(), key=lambda x:abs(x - sonarKey))
        print("No key was found for sonar value: " + str(sonarVal) + " and for square (" + str(squareColumn) + "," + str(squareRow) + "," + orientation + ")")
        print("Using the closest key instead: " + str(closestSonarKey))
        probOfSonarVal = sonarProbsForState[closestSonarKey]
        
    return probOfSonarVal

# Gets the non-zero transition probabilities for motion to a destination square and orientation
# The results returned are a list of tuples. Each tuple is of the form (ResultSquare, ResultOrientation, Probability)
# Directed/Result orientations are 'S', 'R', and 'L'
# Result square map (Start state is square 4, and 'S'. Directed destination squares are only 0-8 but the robot may end in any square):
# 16 15 14 13 12
# 17  0  1  2 11
# 18  3  4  5 10
# 19  6  7  8  9
# 20 21 22 23 24
def getTransitionProbability(endStateMotionProbs, destSquare, destOrientation):
    destOrientationInt = prob_helper.mapOrientationToNumber(destOrientation)
    probsForEndState = endStateMotionProbs[destSquare][destOrientationInt]
    #print("Probs when trying to move to square, orientation (" + str(destSquare) + "," + destOrientation + ") are: " + str(probsForEndState))
    return probsForEndState
    
# Loads end state transition probabilities when moving between squares and turning orientation. The "cpt_motion_calculator.py" script must be run
# first to generate the "motion_cpt.csv" file 
def loadAllEndStateMotionProbs():
    # Table storing a list of tuples containing (square,orient,prob) for each end state
    motionProbs = [[[] for y in range(prob_helper.NUM_ORIENTATIONS)] for x in range(prob_helper.NUM_DIRECTED_SQUARES)]   
    
    with open("motion_cpt.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader) # Skip the header
        
        for row in csv_reader:
            directedSquare = int(row[0])
            directedOrientation = prob_helper.mapOrientationToNumber(row[1])
            
            # Each dest state uses 3 columns in the CSV (square,orient,prob), so iterate 3 at a time
            for i in range(2, len(row), 3):
                resultSquare = int(row[i])
                resultOrientation = row[i+1]
                resultProb = float(row[i+2])
                
                motionProbs[directedSquare][directedOrientation].append((resultSquare, resultOrientation, resultProb))

    #for x in range(prob_helper.NUM_DIRECTED_SQUARES):
    #    for y in range(prob_helper.NUM_ORIENTATIONS):
    #        print("x: " + str(x) + ", y: " + str(y) + ", probl: " + str(motionProbs[x][y]))
    
    return motionProbs

# Loads the landmark evidence probabilities for landmark being true in each square/orientation. The "landmark_cpt_evidence.py" script must be run
# first to generate the "landmark_cpt_evidence.csv" file 
def loadAllLandmarkEvidenceProbs():
    landmarkEvidenceProbs = [[[None for z in range(prob_helper.NUM_ORIENTATIONS)] for y in range(NUM_ROWS)] for x in range(NUM_COLS)]
    
    with open("landmark_cpt_evidence.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader) # Skip the header
        
        for row in csv_reader:
            if row[0]:
                squareCol = int(row[0])
                squareRow = int(row[1])
                orientation = prob_helper.mapOrientationToNumber(row[2])
                landmarkProb = float(row[3])
                
                landmarkEvidenceProbs[squareCol][squareRow][orientation] = landmarkProb
            
    return landmarkEvidenceProbs
    
# Loads the left sonar evidence probabilities for a sonar value falling within a range in each square/orientation. 
# The "cpt_sonar_calculator_evidence.py" script must be run first to generate the "sonar_cpt_evidence.csv" file 
def loadAllLeftSonarEvidenceProbs():
    leftSonarEvidenceProbs = [[[{} for z in range(prob_helper.NUM_ORIENTATIONS)] for y in range(NUM_ROWS)] for x in range(NUM_COLS)]
    
    loadSingleSonarEvidenceProb(leftSonarEvidenceProbs, 'L')
            
    return leftSonarEvidenceProbs

# Loads the right sonar evidence probabilities for a sonar value falling within a range in each square/orientation. 
# The "cpt_sonar_calculator_evidence.py" script must be run first to generate the "sonar_cpt_evidence.csv" file 
def loadAllRightSonarEvidenceProbs():
    rightSonarEvidenceProbs = [[[{} for z in range(prob_helper.NUM_ORIENTATIONS)] for y in range(NUM_ROWS)] for x in range(NUM_COLS)]
    
    loadSingleSonarEvidenceProb(rightSonarEvidenceProbs, 'R')
            
    return rightSonarEvidenceProbs

# Loads a single row from a CSV file into the sonar probability matrix
def loadSingleSonarEvidenceProb(sonarEvidenceProbs, sonarNameToLoad):
    with open("sonar_cpt_evidence.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader) # Skip the header
        
        for row in csv_reader:
            sonarName = row[3]
            if sonarName == sonarNameToLoad:
                squareCol = int(row[0])
                squareRow = int(row[1])
                orientation = prob_helper.mapOrientationToNumber(row[2])
                sonarRangeBeginVal = float(row[4])
                probVal = float(row[5])
    
                sonarEvidenceProbs[squareCol][squareRow][orientation][sonarRangeBeginVal] = probVal
                
####################################
########### MAIN SECTION ###########
####################################
NUM_COLS = 4
NUM_ROWS = 8

endStateMotionProbs = loadAllEndStateMotionProbs()
landmarkEvidenceProbs = loadAllLandmarkEvidenceProbs()
leftSonarEvidenceProbs = loadAllLeftSonarEvidenceProbs()
rightSonarEvidenceProbs = loadAllRightSonarEvidenceProbs()

# Sample calls to get transition probs. The result tuples can be used for particle filtering. This is just a test.
transitionProbs = getTransitionProbability(endStateMotionProbs, 1, 'S')
print("Probs when trying to move to square, orientation (1,S) are: " + str(transitionProbs))
transitionProbTable = createTransitionProbMatrixWithNoise(transitionProbs)
print("Probs after adding noise are: " + str(transitionProbTable))

transitionProbs = getTransitionProbability(endStateMotionProbs, 8, 'R')
print("Probs when trying to move to square, orientation (8,R) are: " + str(transitionProbs))
transitionProbTable = createTransitionProbMatrixWithNoise(transitionProbs)
print("Probs after adding noise are: " + str(transitionProbTable))

# Sample calls to get prob of landmarks for specific states
landmarkEvidenceProb = getLandmarkEvidenceProbForState(landmarkEvidenceProbs, 1, 3, 'S')
print("Probability of seeing landmark = True in column 1, row 3, orientation straight: " + str(landmarkEvidenceProb))
landmarkEvidenceProb = getLandmarkEvidenceProbForState(landmarkEvidenceProbs, 3, 5, 'L')
print("Probability of seeing landmark = True in column 3, row 5, orientation left: " + str(landmarkEvidenceProb))

# Sample calls to get prob of sonar evidence falling within a range for specific states
leftSonarEvidenceProb = getSonarEvidenceProbForState(leftSonarEvidenceProbs, 1, 3, 'S', 10.5)
print("Probability of seeing left sonar val = 10.5 inches in column 1, row 3, orientation straight: " + str(leftSonarEvidenceProb))
leftSonarEvidenceProb = getSonarEvidenceProbForState(leftSonarEvidenceProbs, 1, 3, 'S', 12.5)
print("Probability of seeing left sonar val = 12.5 inches in column 1, row 3, orientation straight: " + str(leftSonarEvidenceProb))
rightSonarEvidenceProb = getSonarEvidenceProbForState(rightSonarEvidenceProbs, 1, 3, 'L', 7.23)
print("Probability of seeing right sonar val = 7.23 inches in column 1, row 3, orientation left: " + str(rightSonarEvidenceProb))