import math
from naoqi import ALProxy


squareSizeInches = 0.0508

def moveDown(motionProxy, postureProxy):
    prepareForMove(motionProxy, postureProxy)
        
    print("Moving down")
    motionProxy.moveTo(squareSizeInches * -1.0, 0.0, 0.0)
        
    # Wait for movement
    time.sleep(2)
    print("Downward movement should now be complete")

def moveLeft(motionProxy, postureProxy):
    prepareForMove(motionProxy, postureProxy)
        
    print("Moving left")
    motionProxy.moveTo(0.0, squareSizeInches, 0.0)
        
    # Wait for movement
    time.sleep(2)
    print("Left movement should now be complete")
    
def moveRight(motionProxy, postureProxy):
    prepareForMove(motionProxy, postureProxy)
        
    print("Moving right")
    motionProxy.moveTo(0.0, (squareSizeInches * -1.0), 0.0)
        
    # Wait for movement
    time.sleep(2)
    print("Right movement should now be complete")
    
def moveUp(motionProxy, postureProxy):
    prepareForMove(motionProxy, postureProxy)
        
    print("Moving up")
    motionProxy.moveTo(squareSizeInches, 0.0, 0.0)
        
    # Wait for movement
    time.sleep(2)
    print("Upward movement should now be complete")

def prepareForMove(motionProxy, postureProxy):
    postureProxy.goToPosture("StandInit",0.5)
    motionProxy.moveInit()
    if (motionProxy.moveIsActive()):
        print("Active move")
        motionProxy.killMove()

def turnLeft(motionProxy, postureProxy):
    prepareForMove(motionProxy, postureProxy)
    
    print("Turning left")
    motionProxy.moveTo(0.0, 0.0, math.radians(-90))
        
    # Wait for movement
    time.sleep(2)
    print("Left turn movement should now be complete")
    
def turnRight(motionProxy, postureProxy):
    prepareForMove(motionProxy, postureProxy)
    
    print("Turning right")
    motionProxy.moveTo(0.0, 0.0, math.radians(90))
        
    # Wait for movement
    time.sleep(2)
    print("Right turn movement should now be complete")