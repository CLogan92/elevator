from enum import Enum
import threading
import time

# Design an elevator:
# What do elevators do?  
#     They take people up and down in a building.
#     They typically take in the same "orders" depending on the direction they're traveling..
#         E.g: If an elevator is going up, and there are other people on other floors going up, it'll stop there, and pick the people up, and keep moving.
#              Once there are no more floors going up (or it's at the max floor) then it'll service people going down.  
#              This isn't a FIFO, rather it's more event driven... 
#              It's not a FIFO, because if an elevator is traveling up, and Floor 5 presses up before Floor 3 does, the elevator will stop at 3 first, 
#              because it's before 5, and is traveling that up!  Vice versa if the elevator were traveling down.

# Things to be implemented later:
#   -> Multiple passengers.  
#       1.) At the moment we're only picking up and dropping off one passenger at a time.  Something that can definitely be expanded on later
#           by using lists.  
#       2.) Some logic improvements will need to be done to ensure that we pick up passengers going in the same direction e.g: Elevators that are 
#           going up, pick up other passengers who are also going up and ignore those who are wanting to go down until the elevator is done going up. 
#       3.) Likewise, multiple passengers boarding but going to multiple floors, like I said, adding lists and using '.remove' when we reached the first floor 
#           in that direction.
#   -> Multiple elevators.  
#       This shouldn't be overly difficult to expand upon, we can create X amount of threads which represent each elevator, some logic would need to be done to
#       handle which elevator is picking up which person, it's not a race to see who picks up the passenger first. 
#   -> Event Driven.
#       Since we're running in a thread, we can implement some kind of signal that can run instead of just some simple sleep, do mechanic...
#       Kinda like Pyqt Signal Emits

# Assumptions
#   -> We're not using the direction mechanism that all elevators use.  Instead we run through some math and check if which direction we want to go from there.
#   -> We're not restricting which elevators are going to which floors, some high rise elevators only service certain select floors, and they have multiple elevators.
#   -> This elevator is only going up and down.
#   -> Passengers are willing to wait for the elevators, and ride them, instead of taking the stairs. 

# A small value check to see if we can shutdown after so long in IDLE. 
ELEVATOR_WAIT_CNT = 4

# A small second count which indicates how long we want the thread to sleep for
ELEVATOR_SLEEP_SEC = 2

# Time for the passengers to wait before checking elevator state, also allows thread to sleep and not go crazy with sys resources. 
PASSENGER_WAIT_SEC = 1

# Elevators can only go up and down... I guess some could go sideways, but we're not doing that right now. 
class ElevatorDirection(Enum):
    UP   = 1
    DOWN = 2

# We need to know what our elevator is currently doing
class ElevatorState(Enum):
    IDLE    = 0 # No Requests, stays on the last floor it stopped at.
    MOVING  = 1 # Up or down
    STOPPED = 2 # Picking people up, or dropping people off

# We need to actually control the elevator doors, don't need people trying to jump out of the elevator because the doors are open!
class ElevatorDoorState(Enum):
    OPEN   = 0
    CLOSED = 1

# This is the panel that is outside the elevator doors that a new passenger would press to request the elevator
# We'll need to know which floor the request came in on, and which direction they would like to go
class ExtPanel(object):
    def __init__(self):
        self.floorNum         = 0 # Which floor was the elevator requested on? 
        self.desiredDirection = ElevatorDirection.UP # The up or or down button which was pressed
        self.btnPressed       = False # A smalls signal which tells the controller that someone requested the elevator

    # Take in which floor we received the request for, and what direction they want to go.
    def RequestElevator(self, floorNum, direction:ElevatorDirection):
        self.floorNum         = floorNum
        self.desiredDirection = direction
        self.btnPressed       = True

    def CleanupExternalPanel(self):
        self.btnPressed = False

# Next this is the internal panel in the elevator. 
# We'll need to know which floor they want to go to, 
class IntPanel(object):
    def __init__(self):
        self.floorBtnPressed = 0 # Which floor is the passenger trying to go to?
        self.hasABtnBeenPrsd = False # Another signal which tells the controller than the passenger has pressed a button to change floors.

    def FloorBtnPressed(self, floorBtnPrsd):
        self.floorBtnPressed = floorBtnPrsd
        self.hasABtnBeenPrsd = True

    def CleanupInternalPanel(self):
        self.floorBtnPressed = 0
        self.hasABtnBeenPrsd = False


# Now that we have a way to control the elevator, we can create the elevator.
class Elevator():
    def __init__(self):
        self.elevatorState    = ElevatorState.IDLE
        self.curElevatorFloor = 0
        self.desiredFloor     = 0
        self.elevatorDir      = ElevatorDirection.UP
        self.elevatorDoor     = ElevatorDoorState.CLOSED
        self.elevatorRunning  = True

        # Setup our interfaces:
        self.externalPanel = ExtPanel()
        self.internalPanel = IntPanel()

        print("Done setting up elevator")


    def MoveElevator(self, elevatorDir, desiredFloor):
        if (self.curElevatorFloor != desiredFloor):
            # Update the current floor the elevator is according to the direction of travel.
            if (elevatorDir == ElevatorDirection.UP):
                self.curElevatorFloor += 1
            else:
                self.curElevatorFloor -= 1

            print ("\t\tElevator going %s, is currently on floor %d, and is heading to %d" % (elevatorDir.name, self.curElevatorFloor, desiredFloor))
        else:
            # Note:  That despite stopping on the desired floor, there will still be a small delay before the doors open... 
            # I think this is kinda realistic, so I'll keep it that way. :) 
            # Otherwise if this is not desirable, we can always do a check in the main loop, and continue so that we open the doors immediately. 
            print("\t\tDing!  Reached desired floor: %d" % self.desiredFloor)
            self.curElevatorFloor = self.desiredFloor
            self.elevatorState = ElevatorState.STOPPED # Stop to let the people off.


    def ChangeElevatorDir(self):
        # If our current floor is negative, we know we're below the desired floor, move up.
        if (self.desiredFloor - self.curElevatorFloor > 0):
            self.elevatorDir = ElevatorDirection.UP
        else:
            self.elevatorDir = ElevatorDirection.DOWN


    def CheckExtPannels(self):
        # If the req elevator button has been pressed, gather which floor it was on, and the direction
        # that they want to go.
        if (self.externalPanel.btnPressed):
            return (self.externalPanel.btnPressed, self.externalPanel.desiredDirection, self.externalPanel.floorNum)
        return (False, 0, 0)
    

    def ChangeElevatorDoorState(self, doorState : ElevatorDoorState):
        self.elevatorDoor = doorState
        print ("\t\tElevator doors are now %s" % doorState.name)
    

    def DeterminePassengerLocation(self, passengerFloor):
        if (self.curElevatorFloor == passengerFloor):
            # Passenger is on the same floor that the elevator is currently on!
            # Let the controller open the doors for us.
            # Cleanup the external panel as we are already on the same floor as the passenger. 
            print ("\t\tElevator is on same floor as new passenger.")
            self.elevatorState = ElevatorState.STOPPED
            self.externalPanel.CleanupExternalPanel()
        else:
            print ("\t\tElevator detects new passenger on another floor.")
            self.desiredFloor = passengerFloor
            self.ChangeElevatorDir()
            self.elevatorState = ElevatorState.MOVING


    def EmergencyStop(self):
        self.elevatorState = ElevatorState.STOPPED
        self.ChangeElevatorDoorState(ElevatorDoorState.OPEN)
        print ("\t\tElevator is stopping on floor %d" % self.curElevatorFloor)
        self.elevatorRunning = False


    # A thread which handles the work that the elevator needs to do! 
    def ElevatorController(self):
        elevReq = False
        elevatorShutdownCnt = 0
        elevatorIdleCnt = 0
        newDir = 0
        newFloor = 0

        while (self.elevatorRunning == True):
            # Get Desired Floor
            (elevReq, newDir, newFloor) = self.CheckExtPannels()

            if (elevReq == False and self.elevatorState == ElevatorState.IDLE):
                print ("\t\tElevator has nothing to do")
                elevatorShutdownCnt += 1

                if (elevatorShutdownCnt >= ELEVATOR_WAIT_CNT):
                    # We've been idle for 5 counts now, shut down thread.
                    print ("\t\tElevator Shutting Down")
                    break
            else:
                # We've gotten here because the elevator needs to do something...
                if (self.elevatorState == ElevatorState.IDLE):
                    self.DeterminePassengerLocation(newFloor)
                    continue

                elif (self.elevatorState == ElevatorState.STOPPED):
                    # First check if any passenger has pressed any of the internal floor buttons.  
                    if (self.internalPanel.hasABtnBeenPrsd == True):
                        print ("\t\tElevator's internal button pressed, blast the elevator music and let's go.")
                        # Update Elevator's state, we are now able to move, because passenger pressed internal button
                        self.elevatorState = ElevatorState.MOVING

                        # Close the doors so the elevator can actually move. 
                        self.ChangeElevatorDoorState(ElevatorDoorState.CLOSED)
                        
                        # Read in which floor button the passenger selected. 
                        self.desiredFloor = self.internalPanel.floorBtnPressed

                        # Determine which way (Up or Down) we need to go based off what floor we're on already.
                        # TODO actually use the "Direction" that the passenger chose. 
                        self.ChangeElevatorDir()

                        # Actually move the elevator
                        self.MoveElevator(self.elevatorDir, self.desiredFloor)

                        # Cleanup both the internal/external panels 
                        self.internalPanel.CleanupInternalPanel()
                        self.externalPanel.CleanupExternalPanel()
                        elevatorIdleCnt = 0
                    # Else, the passenger has likely got to their floor
                    else:
                        # Open the doors, since we're stopped
                        if (self.elevatorDoor == ElevatorDoorState.CLOSED):
                            self.ChangeElevatorDoorState(ElevatorDoorState.OPEN)

                        if (elevReq == True):
                            self.DeterminePassengerLocation(newFloor)
                            # Continue so that we can reach the passenger as quick as we can without sleeping.
                            continue

                        print ("\t\tElevator waiting for riders to get on or off and waiting for someone to press internal floor button")
                        elevatorIdleCnt += 1

                        if elevatorIdleCnt >= ELEVATOR_WAIT_CNT:
                            print ("\t\tElevator has been stopped for some time, going to idle state.")
                            self.elevatorState = ElevatorState.IDLE

                elif (self.elevatorState == ElevatorState.MOVING):
                    # Close the doors, since we're getting ready to move
                    if (self.elevatorDoor == ElevatorDoorState.OPEN):
                        self.ChangeElevatorDoorState(ElevatorDoorState.CLOSED)
                    self.MoveElevator(self.elevatorDir, self.desiredFloor)

            # Sleep for some seconds so thread doesn't go wild with sys resources. 
            print ("\t\tElevator thread sleeping for %d seconds" % ELEVATOR_SLEEP_SEC)
            time.sleep(ELEVATOR_SLEEP_SEC)


if __name__ == '__main__':

    # Here's the list of passengers, what floor they're on, and which floor they want to go to, and which direction they want to travel
    currentFloor = [0, 5, 7, 0, 3, -2]
    desiredFloor = [3, 0, 2, 3, -1, 0]
    elevatorDir  = [ElevatorDirection.UP, ElevatorDirection.DOWN, ElevatorDirection.DOWN, ElevatorDirection.UP, ElevatorDirection.DOWN, ElevatorDirection.UP] # TODO this isn't actually being used right now

    if (len(currentFloor) != len(desiredFloor)):
        raise Exception ("Current Floors and Desired Floors are not the same length!")
    
    # Create an elevator for the building.
    bldgElevatr = Elevator()

    # Create a thread which controls the elevator
    elevThread = threading.Thread(target=bldgElevatr.ElevatorController)
    elevThread.start()
    NotOnDesiredFloor = True
    timethen = 0

    try:
        for i in range(len(currentFloor)):
            timethen = time.time()
            print ("Passenger %d wants to go %s!" % (i + 1, elevatorDir[i].name))
            bldgElevatr.externalPanel.RequestElevator(currentFloor[i], elevatorDir[i])

            print ("Passenger is waiting for Elevator.")
            # We have to wait for both the elevator to be on the same floor, as well as the doors to be open before we can stop waiting.
            while (bldgElevatr.curElevatorFloor != currentFloor[i] or bldgElevatr.elevatorDoor != ElevatorDoorState.OPEN):
                time.sleep(PASSENGER_WAIT_SEC)
            else:
                print ("Passenger sees that elevator has arrived, and doors are open!")

            print ("Passenger is getting on elevator")
            bldgElevatr.internalPanel.FloorBtnPressed(desiredFloor[i])
            print ("Passenger pressed button to go to floor %d" % desiredFloor[i])

            while (NotOnDesiredFloor == True):
                if (desiredFloor[i] != bldgElevatr.curElevatorFloor):
                    print ("Passenger riding elevator to their floor")
                else:
                    if (bldgElevatr.elevatorDoor == ElevatorDoorState.OPEN):
                        NotOnDesiredFloor = False
                    else:
                        print ("Passenger waiting for elevator doors to open")

                time.sleep(PASSENGER_WAIT_SEC)
            else:
                print ("Passenger left elevator.")

                # Reset local var for next passenger
                NotOnDesiredFloor = True

                print ("It took %d seconds to take the passenger from floor %d to floor %d." % ((time.time() - timethen), currentFloor[i], desiredFloor[i]))
                print("\n\n")
    except KeyboardInterrupt:
        print ("Ctrl+C Pressed! Need to cleanup the threads and exit.")
        bldgElevatr.EmergencyStop()

        print ("Exiting...")
        exit()
