
from enum import Enum

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

# Elevators can only go up and down...
class ElevatorDirection(Enum):
    UP   = 1
    DOWN = 2

# We need to know what our elevator is currently doing
class ElevatorState(Enum):
    IDLE    = 0 # No Requests, stays on the last floor it stopped at.
    MOVING  = 1 # Up or down
    STOPPED = 2 # Picking people up, or dropping people off

# We'll need to know which floor the request came in on, and which direction they would like to go
# This would be the panel that is outside the elevator doors that a new passenger would press to request the elevator
class ExtPanel(object):
    def __init__(self):
        self.floorNum = 0 # The floor that the up or down button was pressed on
        self.direction = ElevatorDirection.UP # The up or or down button which was pressed

    def RequestElevator(self, floorNum, direction):
        self.floorNum = floorNum
        self.direction = direction

# Next we'll need to know which floor they want to go to, this is the internal panel in the elevator.
class IntPanel(object):
    def __init__(self):
        self.numOfBtns = NUM_OF_FLOORS -1
        self.floorBtnPrsd = 0

    def FloorBtnPressed(self, floorBtnPrsd):
        self.floorBtnPressed = floorBtnPrsd

# Now that we have a way to control the elevator, we can create the elevator.
class Elevator():
    def __init__(self):
        self.elevatorState    = ElevatorState.IDLE
        self.curElevatorFloor = 0
        self.desiredFloor     = 0 # TODO: Make this a list, so we can append floors.
        self.elevatorDir      = ElevatorDirection.UP

        # Setup our interfaces:
        self.ExtPanel.__init__(self)
        self.IntPanel.__init__(self)

        print("Done setting up elevator")

        print(self.ExtPanel.floorNum)

    def MoveElevator(self, elevatorDir, desiredFloor):
        if (self.curElevatorFloor != self.desiredFloor):
            self.elevatorState = ElevatorState.MOVING

            if (self.elevatorDir.UP):
                # TODO: Check if people want off on this floor.
                # TODO: Verify that elevator can't fly through the roof.
                self.curElevatorFloor += 1
            else:
                # TODO: Check if people want off on this floor.
                # TODO: Verify that elevator can't fly through the roof.
                self.curElevatorFloor -= 1
        else:
            print("Ding!  Reached desired floor %d :)" % self.desiredFloor)
            self.curElevatorFloor = self.desiredFloor
            self.elevatorState = ElevatorState.IDLE # Stop to let the people off.

            # TODO: Check if there's anymore floors to stop at, if not, go to IDLE.

    def ChangeElevatorDir(self):
        if (self.curElevatorFloor - self.desiredFloor < 0): # If our current floor is negative, we know we're below the desired floor, move up.
            self.elevatorDir = ElevatorDirection.UP
        else:
            self.elevatorDir = ElevatorDirection.DOWN

if __name__ == '__main__':

    # Create the elevator Class.
    bldgElevatr = Elevator()

    # I want to go to floor 3!



