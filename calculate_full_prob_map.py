import csv
import sys
import os
import numpy as np
import sensor_fusion
import localization_visualization

meter_to_inch_conversion = 39.37

sensor_folder = 'sensor_data'

num_rows, num_cols = 8, 4

def calculateFullCptMap(orientation, left_distance, right_distance, landmarkDetected):
    # Sonar fusion has probabilities for each row given input values
    sonar_fusion_cpt_straight = sensor_fusion.calculateSonarFusion(orientation, left_distance, right_distance)
    # Landmark has probabilities for each column given landmark detection
    landmark_cpt_straight = sensor_fusion.calculateLandmarkColumnCpt(orientation, landmarkDetected)
    
    full_cpt = [[0 for y in range(num_rows)] for x in range(num_cols)]
    

    probAlphaSum = 0
    if orientation == 'S':
        for x in range(num_cols):
            landmarkProb = landmark_cpt_straight[x]
            for y in range(num_rows):
                sonarRowProb = sonar_fusion_cpt_straight[y]
                tileProb = sonarRowProb * landmarkProb
                
                probAlphaSum = probAlphaSum + tileProb
                full_cpt[x][y] = tileProb
    elif orientation == 'R':
        for x in range(num_cols):
            sonarRowProb = sonar_fusion_cpt_straight[x]
            for y in range(num_rows):
                landmarkProb = landmark_cpt_straight[y]
                tileProb = sonarRowProb * landmarkProb
                
                probAlphaSum = probAlphaSum + tileProb
                full_cpt[x][y] = tileProb
    elif orientation == 'L':
        for x in range(num_cols):
            # Traverse the sonar CPT table backwards for Left since when taking data for the left orientation the numbering
            # Starting in the bottom right of the grid, as seen when looking Straight
            sonarRowProb = sonar_fusion_cpt_straight[num_cols - x - 1]
            for y in range(num_rows):
                landmarkProb = landmark_cpt_straight[y]
                tileProb = sonarRowProb * landmarkProb
                
                probAlphaSum = probAlphaSum + tileProb
                full_cpt[x][y] = tileProb
            
    # Normalize the results
    for x in range(num_cols):
        for y in range(num_rows):
            # Divide the counts by the sum to normalize the data to sum to 1
            full_cpt[x][y] = round(full_cpt[x][y] / probAlphaSum, 5)
            
    print "Full CPT after normalization: ", full_cpt

    return full_cpt

if __name__ == '__main__':
    print "type in left sonar distance from wall: "
    left_distance = input()

    print "type in right sonar distance from wall: "
    right_distance = input()
    
    print "type in 'T' if a landmark was detected, or 'F' if it was not: "
    landmarkDetected = raw_input()
    
    probMapStraight = calculateFullCptMap('S', left_distance, right_distance, landmarkDetected)
    probMapLeft = calculateFullCptMap('L', left_distance, right_distance, landmarkDetected)
    probMapRight = calculateFullCptMap('R', left_distance, right_distance, landmarkDetected)
    
    localization_visualization.showProbMap(probMapStraight, probMapLeft, probMapRight)