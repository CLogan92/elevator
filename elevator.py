
from enum import Enum
import threading
import time
import sys

# Design an elevator:
# What do elevators do?  
#     They take people up and down in a building.
#     They typically take in the same "orders" depending on the direction they're traveling..
#         E.g: If an elevator is going up, and there are other people on other floors going up, it'll stop there, and pick the people up, and keep moving.
#              Once there are no more floors going up (or it's at the max floor) then it'll service people going down.  
#              This isn't a FIFO, rather it's more event driven... 
#              It's not a FIFO, because if Floor 5 presses up before Floor 3 does, the elevator will stop at 3 first, because it's traveling that direction!
# Things not to consider right now: 
#   -> Weight, or number of occupants.  This is a cattle car elevator. 

# So, what do we need?  
# We need to know how many floors there are
#   Floor 0 = Ground Floor
#   1st Floor = 1, etc.
NUM_OF_FLOORS = 3 

# A small value check to see if we can shutdown after so long in IDLE. 
ELEVATOR_WAIT_CNT = 3

# A small second count which indicates how long we want the thread to sleep for
ELEVATOR_SLEEP_SEC = 2

# Elevators can only go up and down...
class ElevatorDirection(Enum):
    UP   = 1
    DOWN = 2

# We need to know what our elevator is currently doing
class ElevatorState(Enum):
    IDLE    = 0 # No Requests, stays on the last floor it stopped at.
    MOVING  = 1 # Up or down
    STOPPED = 2 # Picking people up, or dropping people off

class ElevatorDoorState(Enum):
    OPEN = 0
    CLOSED = 1

# This is the panel that is outside the elevator doors that a new passenger would press to request the elevator
# We'll need to know which floor the request came in on, and which direction they would like to go
class ExtPanel(object):
    def __init__(self):
        self.floorNum = 0 # The floor that the up or down button was pressed on
        self.desiredDirection = ElevatorDirection.UP # The up or or down button which was pressed
        self.btnPressed = False

    # Take in which floor we received the request for, and what direction they want to go.
    def RequestElevator(self, floorNum, direction:ElevatorDirection):
        self.floorNum = floorNum
        self.desiredDirection = direction
        self.btnPressed = True

    def CleanupExternalPanel(self):
        self.btnPressed = False

# Next this is the internal panel in the elevator. 
# We'll need to know which floor they want to go to, 
class IntPanel(object):
    def __init__(self):
        self.numOfBtns = NUM_OF_FLOORS -1
        self.floorBtnPrsd = 0
        self.hasABtnBeenPrsd = False

    def FloorBtnPressed(self, floorBtnPrsd):
        self.floorBtnPressed = floorBtnPrsd
        self.hasABtnBeenPrsd = True

    def CleanupInternalPannel(self):
        self.floorBtnPressed = 0
        self.hasABtnBeenPrsd = False


# Now that we have a way to control the elevator, we can create the elevator.
class Elevator():
    def __init__(self):
        self.elevatorState    = ElevatorState.IDLE
        self.curElevatorFloor = 0
        self.desiredFloor     = 0 # TODO: Make this a list, so we can append floors.
        self.elevatorDir      = ElevatorDirection.UP
        self.elevatorDoor     = ElevatorDoorState.CLOSED

        # Setup our interfaces:
        self.externalPanel = ExtPanel()
        self.internalPanel = IntPanel()

        print("Done setting up elevator")

    def MoveElevator(self, elevatorDir, desiredFloor):
        if (self.curElevatorFloor != desiredFloor):
            print ("Elevator moving to floor %d" % desiredFloor)

            if (self.elevatorDir.UP):
                # TODO: Check if people want off on this floor.
                # TODO: Verify that elevator can't fly through the roof.
                self.curElevatorFloor += 1
            else:
                # TODO: Check if people want off on this floor.
                # TODO: Verify that elevator can't crash into the ground
                self.curElevatorFloor -= 1

            print ("Elevator going %s and is currently on floor %d" % (self.elevatorDir.UP.name, self.curElevatorFloor))
        else:
            print("Ding!  Reached desired floor: %d" % self.desiredFloor)
            self.curElevatorFloor = self.desiredFloor
            self.elevatorState = ElevatorState.STOPPED # Stop to let the people off.

            # TODO: Check if there's anymore floors to stop at, if not, go to IDLE.

    def ChangeElevatorDir(self):
        # If our current floor is negative, we know we're below the desired floor, move up.
        # TODO: There are posibilities where there are basements, so need to check that this still works in that case.
        if (self.curElevatorFloor - self.desiredFloor < 0):
            self.elevatorDir = ElevatorDirection.UP
        elif (self.curElevatorFloor - self.desiredFloor > 0):
            self.elevatorDir = ElevatorDirection.DOWN

    def CheckExtPannels(self):
        # If the req elevator button has been pressed, gather which floor it was on, and the direction
        # that they want to go.
        if (self.externalPanel.btnPressed):
            return (self.externalPanel.btnPressed, self.externalPanel.desiredDirection, self.externalPanel.floorNum)
        return (False, 0, 0)
    
    def ChangeElevatorDoorState(self, doorState : ElevatorDoorState):
        self.elevatorDoor = doorState
        print ("Elevator doors are now %s" % doorState.name)
    
    # A thread which handles the work that the elevator needs to do! 
    def ElevatorController(self):
        elevReq = False
        elevatorShutdownCnt = 0
        elevatorIdleCnt = 0
        newDir = 0
        newFloor = 0
        # TODO make this interruptable so we can actually quit when we want.
        while (True):
            # Append Desired Floor
            (elevReq, newDir, newFloor) = self.CheckExtPannels()

            if (elevReq == False and self.elevatorState == ElevatorState.IDLE):
                print ("Nothing to do")
                elevatorShutdownCnt += 1

                if (elevatorShutdownCnt >= ELEVATOR_WAIT_CNT):
                    # We've been idle for 5 counts now, shut down thread.
                    break
            else:
                # We've gotten here because the elevator needs to do something...
                if (self.elevatorState == ElevatorState.IDLE):
                    self.elevatorState = ElevatorState.MOVING
                    self.MoveElevator(newDir, newFloor)

                    if (self.curElevatorFloor == newFloor):
                        self.desiredFloor = newFloor
                        self.ChangeElevatorDoorState(ElevatorDoorState.OPEN)
                        self.externalPanel.CleanupExternalPanel()
                        elevReq = False
                # We've been stopped for one sleep cycle, passenger should've gotten on by now, I realize that 
                # it can take longer than 2 seconds, but this is in an ideal world...
                elif (self.elevatorState == ElevatorState.STOPPED):
                    if (self.internalPanel.hasABtnBeenPrsd == True):
                        elevatorIdleCnt = 0
                        self.ChangeElevatorDir()
                        self.ChangeElevatorDoorState(ElevatorDoorState.CLOSED)
                        self.desiredFloor = self.internalPanel.floorBtnPressed
                        self.MoveElevator(self.elevatorDir, self.desiredFloor)
                        self.elevatorState = ElevatorState.MOVING
                        self.internalPanel.CleanupInternalPannel()
                    else:
                        if (self.elevatorDoor == ElevatorDoorState.CLOSED):
                            self.ChangeElevatorDoorState(ElevatorDoorState.OPEN)

                        print ("Waiting for riders to get on or off and waiting for someone to press internal floor button")
                        elevatorIdleCnt += 1

                        if elevatorIdleCnt >= ELEVATOR_WAIT_CNT:
                            print ("Elevator has been stopped for some time, going to idle state.")
                            self.elevatorState = ElevatorState.IDLE

                elif (self.elevatorState == ElevatorState.MOVING):
                    self.MoveElevator(self.elevatorDir, self.desiredFloor)

            # Sleep for some seconds so thread doesn't go wild with sys resources. 
            print ("Sleeping for %d seconds" % ELEVATOR_SLEEP_SEC)
            time.sleep(ELEVATOR_SLEEP_SEC)


if __name__ == '__main__':

    # Create an elevator for the building.
    bldgElevatr = Elevator()
    elevThread = threading.Thread(target=bldgElevatr.ElevatorController)
    elevThread.start()
    NotOnDesiredFloor = True
    currentFloor = [0, 5, 7]
    desiredFloor = [3, 0, 2]
    elevatorDir  = [ElevatorDirection.UP, ElevatorDirection.DOWN, ElevatorDirection.DOWN]
    j = 0

    for i in range(3):

        print ("I wanna go %s!" % elevatorDir[i].name)
        bldgElevatr.externalPanel.RequestElevator(currentFloor[i], elevatorDir[i])

        # Wait for the elevator to land on floor AND have the doors open.
        while (bldgElevatr.curElevatorFloor != currentFloor[i] or bldgElevatr.elevatorDoor != ElevatorDoorState.OPEN):
            print ("Waiting on Elevator...")
            time.sleep(2)
            j += 1

            if (j >= ELEVATOR_WAIT_CNT*5):
                print ("Screw this, I'm taking the stairs!")
                exit()
        j = 0
        print ("Oh the elevator is here!")
        bldgElevatr.internalPanel.FloorBtnPressed(desiredFloor[i])
        print ("Pressing button to go to floor %d" % desiredFloor[i])

        while (NotOnDesiredFloor == True):
            if (desiredFloor[i] != bldgElevatr.curElevatorFloor):
                print ("Waiting to get to my floor")
                time.sleep(2)
            else:
                if (bldgElevatr.elevatorDoor == ElevatorDoorState.OPEN):
                    print ("I'm on my floor!")
                    NotOnDesiredFloor = False
                else:
                    print ("Waiting on the doors to open")
                time.sleep(1)

        NotOnDesiredFloor = True



