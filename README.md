# Objective:

  1. Provide code that simulates an elevator.  You may use any language (recommend using java or Python).
  2. Please upload your code Git Hub
  3. Additionally, document all assumptions and any features that weren't implemented.

# Dependencies:

Python 3.11.3, other versions are untested, but should work.   

# Usage:

1. Clone this repository, and place it into a local file somewhere on the PC.
2. Open a command prompt in that location.
    - In the file explorer's Address bar, type "CMD", and that will open a command prompt in that location. 
    - Also, holding shift and right clicking in the white space of the folder, and selecting "Open PowerShell window here" will also work.
4. In the command prompt, type `python elevator.py`
5. The code will execute with the default passenger characteristics. 
6. If it is desired to interrupt the execution, then in the same command prompt window that is running the program press `ctrl+c`.  This will interrupt execution.  This will also open the elevator doors so that no one is trapped :) 
7. The number of passengers can be edited, by adding more entries to the vars `currentFloor`, `desiredFloor`, and `elevatorDir`.  There is logic to ensure that the `currentFloor` and `desireFloor` lengths are the same so that no potential issues arise from that. 
    - Note:  The `elevatorDir` mechanism is not being used right now, this is mentioned in the assumptions and things to implement later.

# Assumptions made along the way:
1. Only one passenger at a time at the moment.  Yes, elevators are more than capable to handle more than one person, but I wanted to get it working with one person for the time being.  I realize this is a pretty large assumption, but the bulk of the working mechanics are there, and I wanted to get this submitted quickly for evalulation.  If it's desired, I can start working on it right away. 
2. We're not using the direction mechanism that all elevators use.  Instead we run through some math and check if which direction we want to go from there.  This would need to change for mulitple requests on multiple floors as well.  This direction mechanism should help facilitate that. 
3. We're not restricting which elevators are going to which floors, some high rise elevators only service certain select floors, and they have multiple elevators.
4. This elevator is only going up and down.
5. Passengers are willing to wait for the elevators, and ride them, instead of taking the stairs. 

# Potential things to be implemented later:
## Multiple passengers.  
1. At the moment we're only picking up and dropping off one passenger at a time.  Something that can definitely be expanded on later by using lists.  
2. Some logic improvements will need to be done to ensure that we pick up passengers going in the same direction e.g: Elevators that are going up, pick up other passengers who are also going up and ignore those who are wanting to go down until the elevator is done going up. 
3. Likewise, multiple passengers boarding but going to multiple floors, like I said, adding lists and using '.remove' when we reached the first floor in that direction.
## Multiple elevators.  
This shouldn't be overly difficult to expand upon, we can create X amount of threads which represent each elevator, some logic would need to be done to handle which elevator is picking up which person, it's not a race to see who picks up the passenger first. 
## Event Driven.
Since we're running in a thread, we can implement some kind of signal that can run instead of just some simple sleep, do mechanic... Kinda like Pyqt Signal Emits
