import csv
import sys
import os
import numpy as np

meter_to_inch_conversion = 39.37

sensor_folder = 'sensor_data'

num_rows, num_cols = 8, 4

# gaussian pdf (including normalization) definition
def gaussian(x, mu, var):
    return np.exp(-np.power(x - mu, 2.) / (2 * var))/np.sqrt(2*np.pi*var)

# Orientation can be 'S', 'L', or 'R'
def calculateSonarFusion(orientation, left_distance, right_distance):
    # first number is average, second is variance
    # these characterize the normal distribution of distance at each square
    left_cpt = []
    right_cpt = []
    fusion_cpt = []
    
    left_distance = left_distance * meter_to_inch_conversion
    right_distance = right_distance * meter_to_inch_conversion
    
    left_sonar_filename = 'left_sonar_straight_cpt.csv'
    right_sonar_filename = 'right_sonar_straight_cpt.csv'
    if orientation == 'L':
        left_sonar_filename = 'left_sonar_left_cpt.csv'
        right_sonar_filename = 'right_sonar_left_cpt.csv'
    elif orientation == 'R':
        left_sonar_filename = 'left_sonar_right_cpt.csv'
        right_sonar_filename = 'right_sonar_right_cpt.csv'
    
    # load up left_cpt from its CPT CSV
    print "loading left sonar CPTs"
    with open(left_sonar_filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            # norm is for each individual normal distribution
            norm = map(lambda x: float(x), row[0].split(', '))
            left_cpt.append(norm)
            print norm


    # load up right_cpt from its CPT CSV
    print "loading right sonar CPTs"
    with open(right_sonar_filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            # norm is for each individual normal distribution
            norm = map(lambda x: float(x), row[0].split(', '))
            right_cpt.append(norm)
            print norm


    # find the effective maximum probability and its associated distance coordinate (row in the convention of this program)
    max_index = 0

    if orientation == 'S':
        for row in range(num_rows):
            print "Coordinate", row
            leftProb = gaussian(left_distance, left_cpt[row][0], left_cpt[row][1])
            rightProb = gaussian(right_distance, right_cpt[row][0], right_cpt[row][1])
            fusionProb = leftProb * rightProb
            print "Left probability: ", leftProb
            print "Right probability: ", rightProb
            print "Fusion probability: ", fusionProb
            fusion_cpt.append(fusionProb)

            # no need for finding the complete probability (also factoring in normalization and probability of being in the distance coordinate), so only two multiplications are needed
            if fusionProb > fusion_cpt[max_index]:
                max_index = row
    else:
        for col in range(num_cols):
            print "Coordinate", col
            leftProb = gaussian(left_distance, left_cpt[col][0], left_cpt[col][1])
            rightProb = gaussian(right_distance, right_cpt[col][0], right_cpt[col][1])
            fusionProb = leftProb * rightProb
            print "Left probability: ", leftProb
            print "Right probability: ", rightProb
            print "Fusion probability: ", fusionProb
            fusion_cpt.append(fusionProb)

            # no need for finding the complete probability (also factoring in normalization and probability of being in the distance coordinate), so only two multiplications are needed
            if fusionProb > fusion_cpt[max_index]:
                max_index = col

    # print most likely distance coordinate (0 being the farthest at 20 inches away from the wall)
    print "most likely distance coordinate: ", max_index
    print "most likely distance coordinate left CPT: ", left_cpt[max_index]
    print "most likely distance coordinate left probability: ", gaussian(left_distance, np.average(left_cpt[max_index]), np.var(left_cpt[max_index]))
    print "most likely distance coordinate right CPT: ", right_cpt[max_index]
    print "most likely distance coordinate right probability: ",gaussian(right_distance, np.average(right_cpt[max_index]), np.var(right_cpt[max_index]))

    sumProbAlpha = sum(fusion_cpt)
    normalized_fusion_cpt = [p / sumProbAlpha for p in fusion_cpt]
    print "Sonar Fusion Probabilities normalized: ", normalized_fusion_cpt
    
    return fusion_cpt

# landmarkDetected can be 'T' or 'F'
# Orientation can be 'S', 'L', or 'R'
def calculateLandmarkColumnCpt(orientation, landmarkDetected):
    # For this the rows/columns are reversed from how the data was taking. This is indexed by column and then row
    # [0][0] is still the lower left of the grid with the robot facing straight
    landmark_cpt = []
    
    landmark_merged_cpt = []
    if orientation == 'S':
        landmark_merged_cpt = [0.0 for x in range(num_cols)]
    else:
        landmark_merged_cpt = [0.0 for x in range(num_rows)]
    
    cptFilename = 'landmark_cpt_false_' + orientation + '.csv'
    if landmarkDetected == 'T':
        cptFilename = 'landmark_cpt_true_' + orientation + '.csv'

    with open(cptFilename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            landmarkRowProbs = map(lambda x: float(x), row[0].split(','))
            landmark_cpt.append(landmarkRowProbs)
            print "landmark probs: ", landmarkRowProbs
            
    for y in range(num_rows):
        for x in range(num_cols):
            landmarkProb = landmark_cpt[y][x] # Indexing is reversed for landmark CPT based on how it was loaded
            
            if orientation == 'S':
                landmark_merged_cpt[x] = landmark_merged_cpt[x] + landmarkProb
            else:
                landmark_merged_cpt[y] = landmark_merged_cpt[y] + landmarkProb
    
    sumProbAlpha = sum(landmark_merged_cpt)
    normalized_landmark_cpt = [p / sumProbAlpha for p in landmark_merged_cpt]
    print "Landmark Column CPT sums normalized: ", normalized_landmark_cpt
    
    return landmark_merged_cpt

if __name__ == '__main__':
    print "type in left sonar distance from wall: "
    left_distance = input()

    print "type in right sonar distance from wall: "
    right_distance = input()
    
    print "type in 'T' if a landmark was detected, or 'F' if it was not: "
    landmarkDetected = raw_input()
    
    calculateSonarFusion(left_distance, right_distance)
    
    calculateLandmarkColumnCpt(landmarkDetected)