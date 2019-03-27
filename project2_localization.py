from random import randint

def coin(bias):
    n = randint(1, 100)
    if (n % 100 < (bias * 100)):
        return True
    return False
    
    
####################################
########### MAIN SECTION ###########
####################################

#print coin(0.1)