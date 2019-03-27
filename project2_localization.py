import cpt_motion_calculator as prob_helper
import csv
from random import randint

# Random coin for particle filtering 
def coin(bias):
    n = randint(1, 100)
    if (n % 100 < (bias * 100)):
        return True
    return False

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
def loadEndStateProbs():
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

####################################
########### MAIN SECTION ###########
####################################

endStateMotionProbs = loadEndStateProbs()

# Sample calls to get transition probs. The result tuples can be used for particle filtering. This is just a test.
transitionProbs = getTransitionProbability(endStateMotionProbs, 1, 'S')
print("Probs when trying to move to square, orientation (1,S) are: " + str(transitionProbs))
transitionProbs = getTransitionProbability(endStateMotionProbs, 8, 'R')
print("Probs when trying to move to square, orientation (8,R) are: " + str(transitionProbs))