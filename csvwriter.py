import csv
import sys
import os
import time
import math
# Python Image Library
import Image

from naoqi import ALProxy


def getHeadPitch():
    ## return value based on sensors
    hc = motionProxy.getAngles("HeadPitch", False) # requested value
    hs = motionProxy.getAngles("HeadPitch", True)
    #print ("hc=",hc[0], "hs=",hs[0])
    return hs;

def getHeadYaw():
    ## return value based on sensors
    hc = motionProxy.getAngles("HeadYaw", False) # requested value
    hs = motionProxy.getAngles("HeadYaw", True)
    #print ("hc=",hc[0], "hs=",hs[0])
    return hs;

def getLandmarkAngles(i):
    ###
    # Read landmark data if available (at most 2 landmarks at once)
    # By default it reads the closest two, parsed as
    # (alpha1, beta1, da1, db1, mid, alpha2, beta2, da2, db2, mid2, time, N)
    #  mid="mark ID, da="width/delta alpha", db="height/delta beta"
    # When no landmark, returns N=0
    # if i<N returns mark i instead of mark 2
    ###
    data = getLandmarkPosition()
    print("Landmark Data: " + str(data))
    # if there is information in data (at least one mark)
    if (data):
        time = data[0]
        markInfoArray = data[1]
        N = len(markInfoArray)
        markInfo0 = markInfoArray[0]
        # get the angle from the data
        markShapeInfo = markInfo0[0]
        markExtraInfo = markInfo0[1]
        alpha1 = markShapeInfo[1]
        beta1 = markShapeInfo[2]
        da1 = markShapeInfo[3]
        db1 = markShapeInfo[4]
        mid = markExtraInfo[0]
        if (N == 1):
            print("N="+str(N) + " id="+str(mid))
            return (alpha1, beta1, da1, db1, mid, 0, 0, 0, 0, 0, time, N)
        if (N > 1):
            # if index i exists, return it. Otherwise returns index 1
            if (N > i and i > 0): 
                markInfo1 = markInfoArray[i]
            else: 
                markInfo1 = markInfoArray[1]
                markShapeInfo = markInfo1[0]
                markExtraInfo = markInfo1[1]
                alpha2 = markShapeInfo[1]
                beta2 = markShapeInfo[2]
                da2 = markShapeInfo[3]
                db2 = markShapeInfo[4]
                mid2 = markExtraInfo[0]
                print("N="+str(N) + " id="+str(mid)+" "+str(mid2))
            return (alpha1, beta1, da1, db1, mid, alpha2, beta2, da2, db2, mid2, time, N)
    else:
        return (10,0,0,0,0,0,0,0,0,0,0,0)

def getLandmarkPosition():
    ###
    # Looking in memory for the "LandmarkDetected" event
    ###
    return memoryProxy.getData("LandmarkDetected")

def saveNaoImage(IP, PORT, centerWall, rightWall, leftWall, orientation, headOrientation):
    """
    First get an image from Nao, then save it to the images folder. The name is based on the passed in orientation data
    """

    camProxy = ALProxy("ALVideoDevice", IP, PORT)
    resolution = 2    # VGA
    colorSpace = 11   # RGB

    videoClient = camProxy.subscribe("python_client", resolution, colorSpace, 5)

    t0 = time.time()

    # Get a camera image.
    # image[6] contains the image data passed as an array of ASCII chars.
    naoImage = camProxy.getImageRemote(videoClient)

    t1 = time.time()

    # Time the image transfer.
    print "acquisition delay ", t1 - t0

    camProxy.unsubscribe(videoClient)


    # Now we work with the image returned and save it as a PNG  using ImageDraw
    # package.

    # Get the image size and pixel array.
    imageWidth = naoImage[0]
    imageHeight = naoImage[1]
    array = naoImage[6]

    # Create a PIL Image from our pixel array.
    im = Image.fromstring("RGB", (imageWidth, imageHeight), array)

    # Save the image.
    imageName = str(centerWall) + "_" + str(rightWall) + "_" + str(leftWall) + "_" + str(orientation) + "_" + str(headOrientation) + ".png"
    imageRelativePath = os.path.join("images", imageName)
    im.save(imageRelativePath, "PNG")

def subscribeToLandmarks():
    ###
    # subscribe to landmark detection with period 200ms and precision 0.0
    # the precision of 1 is maximim, and 0 is minimum.
    # The period of 30 is default (but we select 200, which is more than enough)
    ###
    landmarkProxy.subscribe("Wall_Mark", 200, 0.0)

ip = "192.168.1.3"
port = 9559
# Connect to ALSonar module.
sonarProxy = ALProxy("ALSonar", ip, port)

# Subscribe to sonars, this will launch sonars (at hardware level) and start data acquisition.
sonarProxy.subscribe("myApplication")

# Now you can retrieve sonar data from ALMemory.
memoryProxy = ALProxy("ALMemory", ip, port)

# Vision/landmark detection  proxy
landmarkProxy = ALProxy("ALLandMarkDetection", ip, port)

# Proxies for walking around/movement/posture
motionProxy = ALProxy("ALMotion", ip, port)
postureProxy = ALProxy("ALRobotPosture", ip, port)

with open('data.csv', 'a') as csvfile:
    fieldnames = ['centerWall','rightWall','leftWall','orientation','headOrientation','leftSonar', 'rightSonar']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    centerWall = input('How many inches away is NAO from the center wall?')
    rightWall = input('How many inches away is NAO from the right wall?')
    leftWall = input('How many inches away is NAO from the left wall?')
    orientation = input('what is the orientation of the body?')
    headOrientation = "Init"

    # TODO MODIFY THIS TO ROTATE AND DO NECESSARY ANGLES FOR EACH SQUARE/POSITION    
    for loopCount in range(1,2):
        postureProxy.goToPosture("StandInit",0.5)
        motionProxy.moveInit()
        motionProxy.setStiffnesses("Head", 1.0)
        if (motionProxy.moveIsActive()):
            print("active move")
            motionProxy.killMove()
        yaw = 0.0  # yaw desired for head (when body turning not desired)
        headOrientation = str(yaw)
        print("init head yaw")
        motionProxy.angleInterpolationWithSpeed("Head", [yaw, 0.0], 1.0)
        print("subscribe landmarks")
        subscribeToLandmarks();
        landmarkProxy.pause(True) # not tested
        
        print("Looking")
        motionid = motionProxy.post.angleInterpolation(
            ["HeadYaw", "HeadPitch"],
            [[0.00001+yaw, 0.0+yaw, 0.000001+yaw],[0.0, 0.000001]], [[1.0, 1.5, 2.0],[1.0, 3.0]],
            True  # angle, time, absolute (vs relative to current)
            )
        time.sleep(1.0)
        landmarkProxy.pause(False) # not tested
        time.sleep(0.5)
        landmarkProxy.pause(True) # not tested
        hps = getHeadPitch()
        if (abs(math.degrees(hps[0]) > 10.0)):
            print("unacceptable pitch:",math.degrees(hps[0]))
            break;
        headYaw = getHeadYaw();
        
        (alpha1, beta1, da1, db1, nb1, alpha2, beta2, da2, db2, nb2, t, N) = getLandmarkAngles(2);
        print("acceptable head yaw/pitch:",math.degrees(headYaw[0]),math.degrees(hps[0]))
        print("status, N="+str(N),"alpha="+str(math.degrees(alpha1))+"/"+str(math.degrees(alpha2)),"db="+str(math.degrees(db1))+"/"+str(math.degrees(db2)))

        # Get sonar left first echo (distance in meters to the first obstacle).
        leftSonar = memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
        print("left sonar: " + str(leftSonar))

        # Same thing for right.
        rightSonar = memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
        print("right sonar: " + str(rightSonar))
        
        # Save imagine from video output
        saveNaoImage(ip, port, centerWall, rightWall, leftWall, orientation, headOrientation)

        writer.writerow({'centerWall': centerWall, 'rightWall': rightWall, 'leftWall': leftWall, 'orientation':orientation, 'headOrientation':headOrientation, 'leftSonar':leftSonar,'rightSonar':rightSonar})
