## 12/13/2025

Today, I began the robotics portion of this project. 

So far, I've been able to get motion control and vision capture working via control through my macbook. 

The end goal is to get the following 3 components working for a fully functional solver robot:

1. **Motion control modules that make cube manipulation really easy** We have a Python library Arm_Lib that lets us contrl each joint servo via angle in degrees. We need a wrapper on top of this to let our solver call pre-made turning functions. 
2. **Inspection via computer vision:** we need to not only be able to recognize the color of each tile on a cube face, but also make sure we are rotating and keeping track of the cube orientation while inspecting to ensure no state drift. 
3. **Optimal solving algorithm**: We could use a pre-existing algorithm, but fewest moves isn't the only metric we care about. For the robot to be as fast as possible, we should reduce the number of cube rotations as those will consume more time than turns.
4. **Optional: turning setup**: We need to make sure the cube turns as smoothly as possible. This is tough with just one pincher robot arm. Might need to set up an anchoring mechanism for the cube, but this means no turns if its fixed, so arm has to move around more to reach some sides. 

## 12/14/2025

### Phase 1 - Fully programmable solve sequences executable by robot

In order for our robot "brain" to easily manipulate the arm to do what it needs to do, we need to set up some easy to use python functions that will do things like "move face a 90°". 

Due to some physical limitations with the arm length and amount of servos, we have to elevate the arm itself. 

We also have to anchor the cube down since it can't be turned with a single gripper.

End goal here is that we can take a move sequence like:

` F U' L2 D2 F' `

, and the arm can automatically execute that sequence. 

We can assume that at the beginning of the solve, the top face (which the robot looks down at), is F, and the face furthest from the robot is U. 

We need to implement functions for each turn, as well as each cube rotation, since the arm is only capable of turning the bottom side. 

Cube rotation is officially working! At least along the Y-axis

