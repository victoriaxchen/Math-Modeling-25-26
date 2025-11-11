# Need to develop a model to optimize sweeping strategies in multi-floor buildings during emergency evacuations. The goal is to ensure all rooms are cleared in the shortest possible time, while prioritizing occupant safety and responder efficiency. Buildings vary in layout, number of floors, stairwell placement, location of exits, and occupancy patterns while responders face pressure to act quickly with sometimes limited information. 

## This package
* use `uv add` and `uv run` to handle python interface

## Code requirement
* represent the given floor plan of the room and hallways
* The room should have multiple attributes, such as area, type of occupant, type of room 
* the hallway has distance information between rooms
* The responder may allow different sweeping stretegies and may have different expertise 

## Task 1
* Create Your Building Sweep Model. Consider using a basic scenario of two fire fighters that will sweep a one-story office building with two exits on opposite sides of the building. There are three similar sized rooms on each side of the hallway connected to the central hallway. Develop a model to simulate how the responders can sweep this building
efficiently during a fire alarm. How long will it take for the two fire fighters to complete this sweep?  When building the model, you should consider the key elements identified above such as floor plan layout, number of responders, rules of movement and sweep verification, possible
presence of smoke, etc.
