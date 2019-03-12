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


# first number is average, second is variance
# these characterize the normal distribution of distance at each square
left_cpt = []
right_cpt = []

# load up left_cpt from its CPT CSV
print "loading left sonar CPTs"
with open('left_sonar_straight_cpt.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    for row in csv_reader:
        # norm is for each individual normal distribution
        norm = map(lambda x: float(x), row[0].split(', '))
        left_cpt.append(norm)
        print norm


# load up right_cpt from its CPT CSV
print "loading right sonar CPTs"
with open('right_sonar_straight_cpt.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    for row in csv_reader:
        # norm is for each individual normal distribution
        norm = map(lambda x: float(x), row[0].split(', '))
        right_cpt.append(norm)
        print norm


# sensor input currently by command line - this should be changed when implemented on the NAO. 
print "type in left sonar distance from wall: "
left_distance = input()

print "type in right sonar distance from wall: "
right_distance = input()


# find the effective maximum probability and its associated distance coordinate (row in the convention of this program)
max_index = 0

for row in range(num_rows):
    print "Coordinate", row
    print "Left probability: ", gaussian(left_distance, np.average(left_cpt[row]), np.var(left_cpt[row]))
    print "Right probability: ", gaussian(right_distance, np.average(right_cpt[row]), np.var(right_cpt[row]))

    # no need for finding the complete probability (also factoring in normalization and probability of being in the distance coordinate), so only two multiplications are needed
    if gaussian(left_distance, np.average(left_cpt[row]), np.var(left_cpt[row]))*gaussian(right_distance, np.average(right_cpt[row]), np.var(right_cpt[row])) > gaussian(left_distance, np.average(left_cpt[max_index]), np.var(left_cpt[max_index]))*gaussian(right_distance, np.average(right_cpt[max_index]), np.var(right_cpt[max_index])):
        max_index = row


# print most likely distance coordinate (0 being the farthest at 20 inches away from the wall)
print "most likely distance coordinate: ", max_index
print "most likely distance coordinate left CPT: ", left_cpt[max_index]
print "most likely distance coordinate left probability: ", gaussian(left_distance, np.average(left_cpt[max_index]), np.var(left_cpt[max_index]))
print "most likely distance coordinate right CPT: ", right_cpt[max_index]
print "most likely distance coordinate right probability: ",gaussian(right_distance, np.average(right_cpt[max_index]), np.var(right_cpt[max_index]))