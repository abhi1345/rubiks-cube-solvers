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

https://github.com/user-attachments/assets/abd3d752-8b16-4eca-8952-4d69445cb350

## 12/15/2025

### 5 PM

I'm realizing I can't work on the robot motion control portion of this project until I figure out a good anchoring position for the arm. It can't rotate the cube along its X-axis (move front face to bottom) in its current position (see video above). 

So, I'm taking a break from motion control and working on the vision module. I want this to be as made-from-scratch as possible but I also want to get it working. I'm considering starting with a vision API, likely a Gemini model since those are the current vision understanding leaders. I would later move to my own trained lightweight nn. The ultimate goal is for this to be a fully standalone edge device, so we will need efficient algorithms for CV and solving. But we can plug those in later, let's focus on e2e working solution first. 

At a high level, the CV requirements are this:
* Input: Pictures of each cube (6 pics, 1 of each face). Needs to include orientation of each face, so the color of the face center as well as the color of the face above it. These can be determined by the robot during inspection, but for v1 let's just label those face colors ourself. 
* Output: Cube state as a python data structure. 

Later, we'll want to pair this with an inspection motion control sequence so we can automatically look at the entire cube and identify the state. 

### 11 PM
Just finished collecting a ton of training data. I took pics of different scrambled faces of the cube. I want to set up an automated training pipeline where each time I take a picture, it gets labeled automatically. Label for a face would just be 9 numbers in [0,5], representing the colors from top to bottom, left to right. 

## 12/16/2025

Today, I cleaned up the data labeling pipeline. This is more of a concept prototype than something I'd use in production. The basic flow is:

`Python Code Controlling Robot`
1. Image gets taken of cube face on robot arm
2. Image gets sent to AWS S3 bucket

`AWS Lambda Function`
1. Function is triggered by new object created in bucket's `captures/` directory
2. Function runs: calls Gemini API to label the image
3. Image label gets added as a `.json` file to `labels/` directory

`EventBridge Schedule`
1. Every hour, we run the labeling lambda function
2. The function checks for unlabeled images and labels them using Gemini

Some next steps I want to do:
* Automate the data collection portion of this
    * Set up each turn/rotation via robot arm
    * Make the arm snap and send image on its own

## 12/17/2025

I have been able to get the arm and cube anchored! And the images in S3 are all labeled. 

I am only at 81 images though, so next step is definitely collecting more training images and running them through the Gemini labeling pipeline. 