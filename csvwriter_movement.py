import csv
import nao_movements as Movement
from naoqi import ALProxy

ip = "192.168.1.3"
port = 9559

# Proxies for walking around/movement/posture
motionProxy = ALProxy("ALMotion", ip, port)
postureProxy = ALProxy("ALRobotPosture", ip, port)

with open('motion_data.csv', 'a') as csvfile:
    fieldnames = ['directedSquareNumber', 'directedEndOrientation','actualSquareNumber', 'actualEndOrientation']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    print("Square numbers (4 is the starting square)")
    print("0  1  2")
    print("3  4  5")
    print("6  7  8");
    directedSquareNumber = raw_input('What square number to go to? (0-8): ').strip()
    directedEndOrientation = raw_input('What should the ending orientation be? (L, S, or R): ').strip().upper()
    
    functionList = []
    
    # Make a list of functions to call based on directed square/orientation
    if directedSquareNumber in ("0", "1", "2"):
        functionList.append(Movement.moveUp)
    if directedSquareNumber in ("0", "3", "6"):
        functionList.append(Movement.moveLeft)
    if directedSquareNumber in ("6", "7", "8"):
        functionList.append(Movement.moveDown)
    if directedSquareNumber in ("2", "5", "8"):
        functionList.append(Movement.moveRight)
    if directedEndOrientation == "L":
        functionList.append(Movement.turnLeft)
    if directedEndOrientation == "R":
        functionList.append(Movement.turnRight)

    for f in functionList:
        f(motionProxy, postureProxy)

    actualSquareNumber = raw_input('What square number did the robot end up in? (0-8): ').strip()
    actualEndOrientation = raw_input('What ending orientation did the robot end up in? (L, S, or R): ').strip().upper()
    
    writer.writerow({'directedSquareNumber': directedSquareNumber, 'directedEndOrientation': directedEndOrientation, 'actualSquareNumber': actualSquareNumber, 'actualEndOrientation':actualEndOrientation})
