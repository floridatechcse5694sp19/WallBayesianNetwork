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


# used to sum up all at specific distances
left_samples = [np.array([]) for y in range(numRows)]
right_samples = [np.array([]) for y in range(numRows)]

for dataFile in os.listdir('sensor_data'):

    with open(os.path.join(sensor_folder, dataFile)) as csvfile:
        dataReader = csv.reader(csvfile)
        sensorDataList = map(tuple, dataReader)
        left_samples_per_round = [[] for y in range(numRows)]
        right_samples_per_round = [[] for y in range(numRows)]
        for row in sensorDataList:
            # Every other row is all columns so ignore those
            if row[1]:
                colNum = int(row[1])
                rowNum = int(row[2])
                if row[3] == 'S':
                    left_samples_per_round[int(row[2])].append(
                        float(row[9])*meter_to_inch_conversion)
                    right_samples_per_round[int(row[2])].append(
                        float(row[10])*meter_to_inch_conversion)

        # print(np.array(left_samples_per_round)[:,:])
        for row in range(numRows):
            left_samples[row] = np.append(
                left_samples[row], left_samples_per_round[row])
        for row in range(numRows):
            right_samples[row] = np.append(
                right_samples[row], right_samples_per_round[row])

        left_samples_per_round = []
        right_samples_per_round = []
        # print("end of file")


print "left sonar"
for row in range(numRows):
    print row, ",", "number of values: ", left_samples[row].shape, "average: ", np.average(
        left_samples[row]), "variance: ", np.var(left_samples[row])


print "right sonar"
for row in range(numRows):
    print row, ",", "number of values: ", right_samples[row].shape, "average: ", np.average(
        right_samples[row]), "variance: ", np.var(right_samples[row])

with open('left_sonar_straight_cpt.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in range(numRows):
        norms = []
        # "mean, variance"
        norms.append(
            str(np.average(left_samples[row]))+', '+str(np.var(left_samples[row])))
        writer.writerow(norms)

with open('right_sonar_straight_cpt.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in range(numRows):
        norms = []
        # "mean, variance"
        norms.append(
            str(np.average(right_samples[row]))+', '+str(np.var(right_samples[row])))
        writer.writerow(norms)
