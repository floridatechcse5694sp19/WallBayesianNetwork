import csv
import sys
import os
import numpy as np

fieldnames = ['runid', 'column', 'row', 'orientation', 'headOrientationYaw', 'actualYawU', 'actualPitchU', 'actualYawL', 'actualPitchL', 'leftSonar', 'rightSonar', 'alpha1U', 'beta1U',
              'dalU', 'db1U', 'nb1U', 'alpha2U', 'beta2U', 'da2U', 'db2U', 'nb2U', 'tU', 'NU', 'alpha1L', 'beta1L', 'dalL', 'db1L', 'nb1L', 'alpha2L', 'beta2L', 'da2L', 'db2L', 'nb2L', 'tL', 'NL']

meter_to_inch_conversion = 39.37

sensor_folder = 'sensor_data'

numRows, numCols = 8, 4

def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))

left_samples = [[np.array([]) for x in range(numCols)] for y in range(numRows)]
right_samples = [[np.array([]) for x in range(numCols)] for y in range(numRows)]
print(left_samples)

for dataFile in os.listdir('sensor_data'):

    with open(os.path.join(sensor_folder, dataFile)) as csvfile:
        dataReader = csv.reader(csvfile)
        sensorDataList = map(tuple, dataReader)
        left_samples_per_round = [[[] for x in range(numCols)] for y in range(numRows)]
        right_samples_per_round = [
            [[] for x in range(numCols)] for y in range(numRows)]
        for row in sensorDataList:
            # Every other row is all columns so ignore those
            if row[1]:
                colNum = int(row[1])
                rowNum = int(row[2])
                if row[3] == 'S':
                    # print(str(float(row[9])*meter_to_inch_conversion) +
                    #       ", "+str(float(row[10])*meter_to_inch_conversion))
                    left_samples_per_round[int(row[2])][int(row[1])].append(
                        float(row[9])*meter_to_inch_conversion)
                    right_samples_per_round[int(row[2])][int(row[1])].append(
                        float(row[10])*meter_to_inch_conversion)

        # print(np.array(left_samples_per_round)[:,:])
        for row in range(numRows):
            for col in range(numCols):
                left_samples[row][col] = np.append(
                    left_samples[row][col], left_samples_per_round[row][col])
        for row in range(numRows):
            for col in range(numCols):
                right_samples[row][col] = np.append(
                    right_samples[row][col], right_samples_per_round[row][col])

        left_samples_per_round = []
        right_samples_per_round = []
        # print("end of file")


print "left sonar"
for row in range(numRows):
    for col in range(numCols):
        print row, ",", col, "number of values: ",left_samples[row][col].shape,"average: ", np.average(left_samples[row][col]), "variance: ", np.var(left_samples[row][col])

with open('left_sonar_straight_cpt.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in range(numRows):
        norms = []
        for col in range(numCols):
            # "mean, variance"
            norms.append(str(np.average(left_samples[row][col]))+', '+str(np.var(left_samples[row][col])))
        writer.writerow(norms)

with open('right_sonar_straight_cpt.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in range(numRows):
        norms = []
        for col in range(numCols):
            # "mean, variance"
            norms.append(str(np.average(right_samples[row][col]))+', '+str(np.var(right_samples[row][col])))
        writer.writerow(norms)

