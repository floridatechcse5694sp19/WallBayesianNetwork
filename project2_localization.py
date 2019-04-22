from naoqi import ALProxy
import csv
import nao_movements
import cpt_motion_calculator as prob_helper
import random
from random import randint
import cpt_sonar_calculator_evidence as sonar_helper
import time

# Random coin for particle filtering 
def coin(bias):
    n = randint(1, 100)
    if (n % 100 < (bias * 100)):
        return True
    return False
    
def coinForTransition(transitionProbs):
    n = random.uniform(0, 0.999999999)
    runningBias = 0.0
    for i in range(prob_helper.NUM_RESULT_SQUARES):
        for j in range(prob_helper.NUM_ORIENTATIONS):
            runningBias = runningBias + transitionProbs[i][j]
            
            if (n < runningBias):
                return (i, j)

    return (prob_helper.NUM_RESULT_SQUARES-1, prob_helper.NUM_ORIENTATIONS-1)
    
def coinForWeightSampling(weightsForMazeStates):
    n = random.uniform(0, 0.999999999)
    runningBias = 0.0
    for i in range(MAZE_SIZE):
        for j in range(MAZE_SIZE):
            for orientation, weight in weightsForMazeStates[i][j].iteritems():
                runningBias = runningBias + weight
                
                if (n < runningBias):
                    return (i, j, orientation)

    return (MAZE_SIZE-2, MAZE_SIZE-2, 'R')
    
def createMazeMapping(mazeMapping):
    for x in range(NUM_COLS):
        for y in range(NUM_ROWS):
            mazeMapping[y+1][x+1]['U'] = (x, y, 'S')
            mazeMapping[y+1][x+1]['R'] = (x, y, 'R')
            mazeMapping[y+1][x+1]['L'] = (x, y, 'L')
            # We don't have data for down, so just use the further back row we have data for
            mazeMapping[y+1][x+1]['D'] = (x, NUM_ROWS-1, 'S')
            
    for x in range(NUM_COLS):
        for y in range(9, 11):
            mazeMapping[y][x+1]['U'] = (x, NUM_ROWS-1, 'S')
            mazeMapping[y][x+1]['R'] = (x, NUM_ROWS-1, 'S')
            mazeMapping[y][x+1]['L'] = (x, NUM_ROWS-1, 'L')
            mazeMapping[y][x+1]['D'] = (x, MAZE_SIZE-y-2, 'S')
            
    for x in range(NUM_COLS):
        for y in range(11, 15):
            mazeMapping[y][x+1]['U'] = (x, NUM_ROWS-1, 'S')
            mazeMapping[y][x+1]['R'] = (x, NUM_ROWS-1, 'S')
            mazeMapping[y][x+1]['L'] = (MAZE_SIZE-y-2, x, 'S')
            mazeMapping[y][x+1]['D'] = (x, MAZE_SIZE-y-2, 'S')
            
    for x in range(5, 7):
        for y in range(11, 15):
            mazeMapping[y][x]['U'] = (NUM_COLS-1, NUM_ROWS-1, 'S')
            mazeMapping[y][x]['R'] = (y-11, NUM_ROWS-1, 'S')
            mazeMapping[y][x]['L'] = (MAZE_SIZE-y-2, x-1, 'S')
            mazeMapping[y][x]['D'] = (0, MAZE_SIZE-y-2, 'S')
            
    for x in range(7, 15):
        for y in range(11, 15):
            mazeMapping[y][x]['U'] = (y-11, NUM_ROWS-1, 'S')
            mazeMapping[y][x]['R'] = (y-11, MAZE_SIZE-x-2, 'S')
            mazeMapping[y][x]['L'] = (y-11, NUM_ROWS-1, 'S')
            mazeMapping[y][x]['D'] = (y-11, MAZE_SIZE-x-2, 'R')

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

def detectsLandmark():
    motionid = motionProxy.post.angleInterpolation(
        ["HeadYaw", "HeadPitch"],
        [[0.00001, 0.0, 0.000001],[0.0, 0.000001]], [[0.00001, 0.0, 0.000001],[0.0, 0.000001]],
        True  # angle, time, absolute (vs relative to current)
        )
    time.sleep(0.5)
    landmarkProxy.pause(False) # not tested
    time.sleep(0.250)
    landmarkProxy.pause(True) # not tested

    data = memoryProxy.getData("LandmarkDetected")
    print("Landmark Data: " + str(data))
    # if there is information in data (at least one mark)
    if (data):
        markInfoArray = data[1]
        N = len(markInfoArray)
    
    return N > 0

def findMostLikelyState(particleCounts):
    mostLikelyState = ()
    maxCount = 0
    for state, count in particleCounts.iteritems():
        if count > maxCount:
            mostLikelyState = state
            maxCount = count

    return mostLikelyState, maxCount
    
# Gets the Probability(Landmark = True | State) where State is the square and orientation combination
def getLandmarkEvidenceProbForState(landmarkEvidenceProbs, squareColumn, squareRow, orientation):
    orientationInt = prob_helper.mapOrientationToNumber(orientation)
    probOfLandmark = landmarkEvidenceProbs[squareColumn][squareRow][orientationInt]
    return probOfLandmark

def getSonarEvidenceAllProbsForState(sonarEvidenceProbs, squareColumn, squareRow, orientation):
    orientationInt = prob_helper.mapOrientationToNumber(orientation)
    sonarProbsForState = sonarEvidenceProbs[squareColumn][squareRow][orientationInt]
    
    return sonarProbsForState

# Gets the Probability(Sonar Value | State) where State is the square and orientation combination
# and the sonar value has to fall within a range (currently 1 inch range size)
def getSonarEvidenceProbForState(sonarEvidenceProbs, squareColumn, squareRow, orientation, sonarVal):
    orientationInt = prob_helper.mapOrientationToNumber(orientation)
    
    sonarProbsForState = sonarEvidenceProbs[squareColumn][squareRow][orientationInt]
    
    probOfSonarVal = getSonarProbForSingleReading(sonarProbsForState, sonarVal)
        
    return probOfSonarVal

def getSonarProbForSingleReading(sonarProbsForState, squareColumn, squareRow, orientation, sonarVal):
    sonarKey = sonar_helper.getSonarRangeKey(sonarVal)
    
    probOfSonarVal = 0.0
    try:
        probOfSonarVal = sonarProbsForState[sonarKey]
    except KeyError:
        closestSonarKey = min(sonarProbsForState.keys(), key=lambda x:abs(x - sonarKey))
        #print("No key was found for sonar value: " + str(sonarVal) + " and for square (" + str(squareColumn) + "," + str(squareRow) + "," + orientation + ")")
        #print("Using the closest key instead: " + str(closestSonarKey))
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
                # Reverse to make lookup uniform with the maze data indices
                squareRow = NUM_ROWS - int(row[1]) - 1
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
                # Reverse to make lookup uniform with the maze data indices
                squareRow = NUM_ROWS - int(row[1]) - 1
                orientation = prob_helper.mapOrientationToNumber(row[2])
                sonarRangeBeginVal = float(row[4])
                probVal = float(row[5])
    
                sonarEvidenceProbs[squareCol][squareRow][orientation][sonarRangeBeginVal] = probVal


def move(command, postureProxy):
    functionList = []
    
    # Make a list of functions to call based on the command
    if command in ("0", "1", "2"):
        functionList.append(nao_movements.moveUp)
    if command in ("0", "3", "6"):
        functionList.append(nao_movements.moveLeft)
    if command in ("6", "7", "8"):
        functionList.append(nao_movements.moveDown)
    if command in ("2", "5", "8"):
        functionList.append(nao_movements.moveRight)
    if command == "L":
        functionList.append(nao_movements.turnLeft)
    if command == "R":
        functionList.append(nao_movements.turnRight)

    for f in functionList:
        f(motionProxy, postureProxy)

def performParticleFiltering(maze_data, particles, endStateMotionProbs, landmarkMazeProbs, leftSonarMazeProbs, rightSonarMazeProbs, command):
    
    destSquare = 4
    destOrientation = 'S'
    if command == 'L' or command == 'R':
        destOrientation = command
    else:
        destSquare = int(command)
        
    transitionProbs = getTransitionProbability(endStateMotionProbs, destSquare, destOrientation)
    print("Probs when trying to move to square, orientation (1,S) are: " + str(transitionProbs))
    transitionProbTable = createTransitionProbMatrixWithNoise(transitionProbs)
    print("Probs after adding noise are: " + str(transitionProbTable))
    print("Prob for (1,0,S): " + str(transitionProbTable[1][prob_helper.mapOrientationToNumber('S')]))
    
    landmarkReading = detectsLandmark()
    
    # Get sonar left first echo (distance in meters to the first obstacle).
    leftSonarReading = memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
    leftSonarReading = leftSonarReading * 0.0254 # Convert to inches
    #print("left sonar: " + str(leftSonar))

    # Same thing for right.
    rightSonarReading = memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
    rightSonarReading = rightSonarReading * 0.0254 # Convert to inches
    #print("right sonar: " + str(rightSonar))
    
    #leftSonarReading = 10.5
    #rightSonarReading = 10.5
    
    for particle in particles:
        particle.transition(maze_data, transitionProbTable, command)
        
        particleX, particleY, particleH = particle.xyh
        
        landmarkProb = landmarkMazeProbs[particleY][particleX][particleH]
        if not landmarkReading:
            landmarkProb = 1 - landmarkProb
        
        #print("Landmark prob: " + str(landmarkProb))
        
        
        leftSonarStateProbs = leftSonarMazeProbs[particleY][particleX][particleH]
        leftSonarReadingProb = getSonarProbForSingleReading(leftSonarStateProbs, particleX, particleY, particleH, leftSonarReading)
        rightSonarStateProbs = rightSonarMazeProbs[particleY][particleX][particleH]
        rightSonarReadingProb = getSonarProbForSingleReading(rightSonarStateProbs, particleX, particleY, particleH, rightSonarReading)
        
        #print("Left sonar prob: " + str(leftSonarReadingProb))
        #print("Right sonar prob: " + str(rightSonarReadingProb))
        
        particleWeight = landmarkProb * leftSonarReadingProb * rightSonarReadingProb
        particle.w = particleWeight
    
    weightsForMazeStates = [[{} for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
    totalWeight = 0.0
    
    for particle in particles:
        particleX, particleY, particleH = particle.xyh
        
        weightForSquare = weightsForMazeStates[particleY][particleX]
        if weightForSquare is None:
            weightsForMazeStates[particleY][particleX][particleH] = particle.w
        else:
            weightForState = weightForSquare.get(particleH, 0.0)
            weightForState = weightForState + particle.w
            weightForSquare[particleH] = weightForState
        
        totalWeight = totalWeight + particle.w
        
    for x in range(MAZE_SIZE):
        for y in range(MAZE_SIZE):
            for orientation, weight in weightsForMazeStates[particleY][particleX].iteritems():
                weightsForMazeStates[particleY][particleX][orientation] = weight / totalWeight
    
    #print("weightsForMazeStates: " + str(weightsForMazeStates))
    
    for particle in particles:
        (newX, newY, newH) = coinForWeightSampling(weightsForMazeStates)
        particle.X = newX
        particle.Y = newY
        particle.H = newH
    
def reloadParticleCounts(particles):
    particleCounts = {}
    for particle in particles:
        particleCounts[particle.xyh] = particleCounts.get(particle.xyh, 0) + 1
    
    return particleCounts
    

def speakState(particleCounts, totalParticleCount):
    mostLikelyState, mostLikelyStateCount = findMostLikelyState(particleCounts)
    x = str(mostLikelyState[0])
    y = str(mostLikelyState[1])
    h = mostLikelyState[2]
    
    prob = (float(mostLikelyStateCount) / float(totalParticleCount)) * 100
    percentProbStr = str(int(prob))
    
    speakText = "The most likely state I'm in is " + x + ", " + y + ", " + h + " with a probability of " + percentProbStr + " percent"
    print(speakText)
    ttsProxy.say(speakText) 

# ------------------------------------------------------------------------
class Particle(object):
    def __init__(self, x, y, heading, w=1):

        self.x = x
        self.y = y
        self.h = heading
        self.w = w

    def __repr__(self):
        return "(%f, %f, w=%f)" % (self.x, self.y, self.w)

    @property
    def xy(self):
        return (self.x, self.y)

    @property
    def xyh(self):
        return (self.x, self.y, self.h)
        
    def transition(self, maze_data, transitionProbTable, command):
        deltaX = 0
        deltaY = 0
        
        (transitionEndSquare, transitionEndOrientation) = coinForTransition(transitionProbTable)
        transitionEndOrientationStr = prob_helper.mapOrientationToStr(transitionEndOrientation)
        #print(str(transitionEndSquare) + ", " + str(transitionEndOrientationStr))
        
        if transitionEndOrientationStr == 'L':
            if self.h == 'U':
                self.h = 'L'
            elif self.h == 'L':
                self.h = 'D'
            elif self.h == 'D':
                self.h = 'R'
            elif self.h == 'R':
                self.h = 'U'
        elif transitionEndOrientationStr == 'R':
            if self.h == 'U':
                self.h = 'R'
            elif self.h == 'R':
                self.h = 'D'
            elif self.h == 'D':
                self.h = 'L'
            elif self.h == 'L':
                self.h = 'U'
        
        if transitionEndSquare in (16, 15, 14, 13, 12):
            deltaY = 2
        if transitionEndSquare in (17, 0, 1, 2, 11):
            deltaY = 1
        if transitionEndSquare in (19, 6, 7, 8, 9):
            deltaY = -1
        if transitionEndSquare in (20, 21, 22, 23, 24):
            deltaY = -2
        if transitionEndSquare in (16, 17, 18, 19, 20):
            deltaX = 2
        if transitionEndSquare in (15, 0, 3, 6, 21):
            deltaX = 1
        if transitionEndSquare in (13, 2, 5, 8, 23):
            deltaX = -1
        if transitionEndSquare in (12, 11, 10, 9, 24):
            deltaX = -2
        
        if self.h == 'U':
            deltaY = deltaY * -1
        elif self.h == 'R':
            temp = deltaY
            deltaY = deltaX * -1
            deltaX = temp 
        elif self.h == 'L':
            temp = deltaX
            deltaX = deltaY * -1
            deltaY = temp

        tempX = self.x + deltaX
        tempY = self.y + deltaY
        
        if tempY >= len(maze_data) or tempX >= len(maze_data[0]) or maze_data[tempY][tempX] > 0:
            for i in range(5):
                if deltaX > 0:
                    deltaX = deltaX - 1
                elif deltaX < 0:
                    deltaX = deltaX + 1
                if deltaY > 0:
                    deltaY = deltaY - 1
                elif deltaY < 0:
                    deltaY = deltaY + 1
                
                tempX = self.x + deltaX
                tempY = self.y + deltaY
                
                if (tempY < len(maze_data) and tempX < len(maze_data[0])) and maze_data[tempY][tempX] == 0:
                    break
        
        self.x = tempX
        self.y = tempY
        

####################################
########### MAIN SECTION ###########
####################################

maze_data = ( ( 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ),
              ( 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ),
              ( 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ),
              ( 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ),
              ( 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ),
              ( 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ),
              ( 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ),
              ( 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ),
              ( 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ),
              ( 2, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ),
              ( 2, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2 ),
              ( 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2 ),
              ( 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2 ),
              ( 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2 ),
              ( 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2 ),
              ( 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2 ) )

MAZE_SIZE = 16
#print(maze_data[3][1])
              
NUM_COLS = 4
NUM_ROWS = 8

NUM_PARTICLES = 10000

IP = "192.168.1.2"
ttsProxy = ALProxy("ALTextToSpeech", IP, 9559)
motionProxy = ALProxy("ALMotion", IP, 9559)
postureProxy = ALProxy("ALRobotPosture", IP, 9559)
landmarkProxy = ALProxy("ALLandMarkDetection", IP, 9559)
landmarkProxy.subscribe("Wall_Mark", 100, 0.0)
sonarProxy = ALProxy("ALSonar", IP, 9559)
sonarProxy.subscribe("myApplication")

endStateMotionProbs = loadAllEndStateMotionProbs()

landmarkEvidenceProbs = loadAllLandmarkEvidenceProbs()
leftSonarEvidenceProbs = loadAllLeftSonarEvidenceProbs()
rightSonarEvidenceProbs = loadAllRightSonarEvidenceProbs()

landmarkMazeProbs = [[{} for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
leftSonarMazeProbs = [[{} for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
rightSonarMazeProbs = [[{} for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]

# x,y coordinates and orientation of the corresponding data in the original evidence probability table that was
# derived from the 4 by 8 rectangle we took data for
mazeMapping = [[{} for y in range(MAZE_SIZE)] for x in range(MAZE_SIZE)]
createMazeMapping(mazeMapping)
#print(mazeMapping)       

for x in range(MAZE_SIZE):
    for y in range(MAZE_SIZE):
        if maze_data[x][y] == 0:
            for orientation, mapping in mazeMapping[x][y].iteritems():
                origX = mapping[0]
                origY = mapping[1]
                origH = mapping[2]
                
                origProb = getLandmarkEvidenceProbForState(landmarkEvidenceProbs, origX, origY, origH)
                
                landmarkMazeProbs[x][y][orientation] = origProb
                
#print(landmarkMazeProbs)

for x in range(MAZE_SIZE):
    for y in range(MAZE_SIZE):
        if maze_data[x][y] == 0:
            for orientation, mapping in mazeMapping[x][y].iteritems():
                origX = mapping[0]
                origY = mapping[1]
                origH = mapping[2]
                
                leftSonarMazeProbs[x][y][orientation] = getSonarEvidenceAllProbsForState(leftSonarEvidenceProbs, origX, origY, origH)

#print(leftSonarMazeProbs)

for x in range(MAZE_SIZE):
    for y in range(MAZE_SIZE):
        if maze_data[x][y] == 0:
            for orientation, mapping in mazeMapping[x][y].iteritems():
                origX = mapping[0]
                origY = mapping[1]
                origH = mapping[2]
                
                rightSonarMazeProbs[x][y][orientation] = getSonarEvidenceAllProbsForState(rightSonarEvidenceProbs, origX, origY, origH)
            
'''
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
'''

startState = (3, 2, 'D')
#movePlan = ['1', '1']
movePlan = ['1', '1', '1', '1', '1', '1', '1', '1', '0', '0', '0', 'L', '1', '1', '1', '1', '1', '1', '1']

particleCounts = {}
particles = []

for i in range(NUM_PARTICLES):
    particles.append(Particle(startState[0], startState[1], startState[2]))

particleCounts = reloadParticleCounts(particles)
speakState(particleCounts, NUM_PARTICLES)

for command in movePlan:
    move(command, postureProxy)
    
    performParticleFiltering(maze_data, particles, endStateMotionProbs, landmarkMazeProbs, leftSonarMazeProbs, rightSonarMazeProbs, command)
    
    particleCounts = reloadParticleCounts(particles)
    #print(particleCounts)
    speakState(particleCounts, NUM_PARTICLES)