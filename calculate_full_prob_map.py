import csv
import sys
import os
import numpy as np
import sensor_fusion
import localization_visualization

meter_to_inch_conversion = 39.37

sensor_folder = 'sensor_data'

num_rows, num_cols = 8, 4

def calculateFullCptMap(left_distance, right_distance, landmarkDetected):
    # Sonar fusion has probabilities for each row given input values
    sonar_fusion_cpt = sensor_fusion.calculateSonarFusion(left_distance, right_distance)
    # Landmark has probabilities for each column given landmark detection
    landmark_cpt = sensor_fusion.calculateLandmarkColumnCpt(landmarkDetected)
    
    full_cpt = [[0 for y in range(num_rows)] for x in range(num_cols)]
    

    probAlphaSum = 0
    for x in range(num_cols):
        landmarkProb = landmark_cpt[x]
        for y in range(num_rows):
            sonarRowProb = sonar_fusion_cpt[y]
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
    
    probMap = calculateFullCptMap(left_distance, right_distance, landmarkDetected)
    
    localization_visualization.showProbMap(probMap)