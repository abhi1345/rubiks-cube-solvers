## 12/13/2025

Today, I began the robotics portion of this project. 

So far, I've been able to get motion control and vision capture working via control through my macbook. 

The end goal is to get the following 3 components working for a fully functional solver robot:

1. **Motion control modules that make cube manipulation really easy** We have a Python library Arm_Lib that lets us contrl each joint servo via angle in degrees. We need a wrapper on top of this to let our solver call pre-made turning functions. 
2. **Inspection via computer vision:** we need to not only be able to recognize the color of each tile on a cube face, but also make sure we are rotating and keeping track of the cube orientation while inspecting to ensure no state drift. 