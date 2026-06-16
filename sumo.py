from hub import light_matrix
from hub import port
from motor import BRAKE
import motor
import motor_pair
import color_sensor
import distance_sensor
import color
import random

import runloop

# List of Constants
# Sumo ring diameter = 150 cm
RING_DIAMETER = 200

# Maximum time for finind opponent
MAX_FINDING = 3

# List of Pors
LEFT_IR  = port.D
RIGHT_IR= port.C
DISTANCE_SENSOR = port.E

# Global variables
finding_counter = 0
leftDetected = False
rightDetected = False
opponent_found = False

def isOpponentFound():
    # Found opponent when the distance to opponent < ring size/2 and not detect edge
    global opponent_found
    opponent_found = not isAtEdge() and distance_sensor.distance(port.E) > 0 and distance_sensor.distance(port.E) < RING_DIAMETER/2
    return opponent_found

def isAtEdge():

    global leftDetected, rightDetected

    left = color_sensor.color(LEFT_IR)
    right = color_sensor.color(RIGHT_IR)

    leftDetected = left is not color.BLACK
    rightDetected = right is not color.BLACK

    return (leftDetected or rightDetected)


def setup():
    print("-----------")
    # Using port A and B for motor
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)

async def waitingAfterStart():
    # Waiting 5200 ms. Just for safe start time.
    print ("Sleep....zzzz")
    await runloop.sleep_ms(5200)
    print ("Wakeup")

async def runToEdge():
    # Move forward until IR can read white
    motor_pair.move_tank(motor_pair.PAIR_1, 400, 400)
    await runloop.until(isAtEdge)   
    motor_pair.stop(motor_pair.PAIR_1, stop=motor.BRAKE)

    # Then revsere for a short time
    moveBackDuration = 1000
    await motor_pair.move_tank_for_time(motor_pair.PAIR_1, -400, -400, moveBackDuration)

    # Turn robot to random direction
    await turnRobot()

async def turnRobot(isRandom = True, _leftvelocity=400, _rightvelocity=400, _minDuration=500, _maxDuration=1000):
    turnDuration = random.randint(_minDuration,_maxDuration)
    leftVelocity = _leftvelocity
    rightVelocity = _rightvelocity

    if (isRandom):
        if (random.randint(0,1) == 1):
            leftVelocity *=-1
        else:
            rightVelocity *=-1

    print("Turn duration:" + str(turnDuration))
    print("- left: " + str(leftVelocity))
    print("- right: " + str(rightVelocity))
    await motor_pair.move_tank_for_time(motor_pair.PAIR_1, leftVelocity, rightVelocity, turnDuration)

async def thisIsSpattaaaaaa():
    # Opponent is in the front .... Kill it with fullspeed.
    # If opponent disappear, stop the robot
    print ("This is SPARTAAAAA !!!!")
    motor_pair.move_tank(motor_pair.PAIR_1, 1000, 1000)
    await runloop.until(lambda: not isOpponentFound())
    motor_pair.stop(motor_pair.PAIR_1, stop=motor.BRAKE)


async def strolling():
    print("I'm walking in Lavender field.")
    # Reset finding counter. So that, the robot can finding opponent in the next round
    global finding_counter
    finding_counter = 0

    # Running straigth until reach edge or found opponent
    motor_pair.move_tank(motor_pair.PAIR_1, 400, 400)
    await runloop.until(lambda : isAtEdge() or isOpponentFound())
    motor_pair.stop(motor_pair.PAIR_1, stop=motor.BRAKE)

    if (opponent_found):
        # Kill them
        await thisIsSpattaaaaaa()
    else:
        # Then revsere for a short time
        moveBackDuration = random.randint(1000,1500)
        await motor_pair.move_tank_for_time(motor_pair.PAIR_1, -400, -400, moveBackDuration)

        # Turn robot as per detected side
        if (leftDetected and rightDetected):
            # Both IR detect edge, random turn
            await turnRobot()

        elif (leftDetected and not rightDetected):
            # Only left IR detects edge, turn right
            await turnRobot(False, 400, -400)

        elif (not leftDetected and rightDetected):
            # Only right IR detects edge, turn left
            await turnRobot(False, -400, 400)
        else:
            print("....Do nothing....")

async def findingOpponent():
    # If number of finding is exceed maximum, do nothing
    global finding_counter
    if (finding_counter >= MAX_FINDING):
        return;
    # Count finding up
    finding_counter += 1

    print("FBI open up!!!")

    # Turn around until found opponent or timeout
    turnVelocity = 400
    leftVelocity = turnVelocity
    rightVelocity = turnVelocity

    if (random.randint(0,1) == 1):
        leftVelocity *=-1
    else:
        rightVelocity *=-1
    motor_pair.move_tank(motor_pair.PAIR_1, leftVelocity, rightVelocity)
    await runloop.until((lambda : isAtEdge() or isOpponentFound()), timeout=1500)

    # If opponent found, kill them
    if (opponent_found):
        # Kill them
        await thisIsSpattaaaaaa()

async def battle():
    print("Battle start")

    modeList = (findingOpponent, strolling)
    
    while (True):
        # Selecting a mode by using random
        mode = random.choice(modeList)
        await mode()
        await runloop.sleep_ms(1000)


# Initialize the robot
setup()

# Sleep 5200 ms
runloop.run(waitingAfterStart())

# Run to edge (ignore sonar, just run straigth to edge)
runloop.run(runToEdge())

# start battle
runloop.run(battle())
