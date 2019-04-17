# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 15:02:49 2019

@author: kholud
"""

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%% Setup and initialization %%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

from math import *
import random
import matplotlib.pyplot as plt
 

class RobotClass:
    &quot;&quot;&quot; Class for the robot model used in this demo &quot;&quot;&quot;
 
    def __init__(self):
 
        self.x = random.random() * world_size           # robot's x coordinate
        self.y = random.random() * world_size           # robot's y coordinate
        self.orientation = random.random() * 2.0 * pi   # robot's orientation
 
        self.forward_noise = 0.0   # noise of the forward movement
        self.turn_noise = 0.0      # noise of the turn
        self.sense_noise = 0.0     # noise of the sensing
        
        #Robot’s initial position in the world can be set by:
def set(self, new_x, new_y, new_orientation):
    &quot;&quot;&quot; Set robot's initial position and orientation
    :param new_x: new x coordinate
    :param new_y: new y coordinate
    :param new_orientation: new orientation
    &quot;&quot;&quot;
 
    if new_x &lt; 0 or new_x &gt;= world_size:
        raise ValueError('X coordinate out of bound')
    if new_y &lt; 0 or new_y &gt;= world_size:
        raise ValueError('Y coordinate out of bound')
    if new_orientation &lt; 0 or new_orientation &gt;= 2 * pi:
        raise ValueError('Orientation must be in [0..2pi]')
 
    self.x = float(new_x)
    self.y = float(new_y)
    self.orientation = float(new_orientation)
    
    #Noise parameters can be set by:

    def set_noise(self, new_forward_noise, new_turn_noise, new_sense_noise):
    &quot;&quot;&quot; Set the noise parameters, changing them is often useful in particle filters
    :param new_forward_noise: new noise value for the forward movement
    :param new_turn_noise:    new noise value for the turn
    :param new_sense_noise:  new noise value for the sensing
    &quot;&quot;&quot;
 
    self.forward_noise = float(new_forward_noise)
    self.turn_noise = float(new_turn_noise)
    self.sense_noise = float(new_sense_noise)
    
    #The robot senses its environment receiving distance to eight landmarks. Obviously there is always some measurement noise which is modelled here as an added Gaussian with zero mean (which means there is a certain chance to be too short or too long and this probability is covered by Gaussian)

def sense(self):
    &quot;&quot;&quot; Sense the environment: calculate distances to landmarks
    :return measured distances to the known landmarks
    &quot;&quot;&quot;
 
    z = []
 
    for i in range(len(landmarks)):
        dist = sqrt((self.x - landmarks[i][0]) ** 2 + (self.y - landmarks[i][1]) ** 2)
        dist += random.gauss(0.0, self.sense_noise)
        z.append(dist)
 
    return z


def move(self, turn, forward):
    &quot;&quot;&quot; Perform robot's turn and move
    :param turn:    turn command
    :param forward: forward command
    :return robot's state after the move
    &quot;&quot;&quot;
 
    if forward &lt; 0:
        raise ValueError('Robot cannot move backwards')
 
    # turn, and add randomness to the turning command
    orientation = self.orientation + float(turn) + random.gauss(0.0, self.turn_noise)
    orientation %= 2 * pi
 
    # move, and add randomness to the motion command
    dist = float(forward) + random.gauss(0.0, self.forward_noise)
    x = self.x + (cos(orientation) * dist)
    y = self.y + (sin(orientation) * dist)
 
    # cyclic truncate
    x %= world_size
    y %= world_size
 
    # set particle
    res = RobotClass()
    res.set(x, y, orientation)
    res.set_noise(self.forward_noise, self.turn_noise, self.sense_noise)
 
    return res
#Our particle filter will maintain a set of 1000 random guesses (particles) where the robot might be. Each guess (or particle) is a vector containing (x,y) coordinates and a heading direction which is an angle relative to the x axis. Now we create a list of 1000 particles:

# create a set of particles
n = 1000  # number of particles
p = []    # list of particles
 
for i in range(n):
    x = RobotClass()
    x.set_noise(0.05, 0.05, 5.0)
    p.append(x)
    
    #For each particle we simulate robot motion. Each of our particles will first turn by 0.1 and move 5 meters. A current measurement vector is applied to every particle from the list.
    steps = 18  # particle filter steps
 
for t in range(steps):
 
    # move the robot and sense the environment after that
    myrobot = myrobot.move(0.1, 5.)
    z = myrobot.sense()
 
    # now we simulate a robot motion for each of
    # these particles
    p2 = []
 
    for i in range(n):
        p2.append( p[i].move(0.1, 5.) )
 
    p = p2
    
    # generate particle weights depending on robot's measurement
w = []
 
for i in range(n):
    w.append(p[i].measurement_prob(z))
    
    # resampling with a sample probability proportional
# to the importance weight
p3 = []
 
index = int(random.random() * n)
beta = 0.0
mw = max(w)
 
for i in range(n):
    beta += random.random() * 2.0 * mw
 
    while beta &gt; w[index]:
        beta -= w[index]
        index = (index + 1) % n
 
    p3.append(p[index])
 
# here we get a set of co-located particles
p = p3

