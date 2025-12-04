# Rubik's Cube Solvers

![Rubik's Cube](https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Rubik%27s_cube.svg/288px-Rubik%27s_cube.svg.png "Scrambled Rubik's Cube")

This repo has a few approaches to solving the Rubik's Cube. 

## Phase 1 - Simple graph-based search

1. Breadth-First-Search: Simple BFS. This has a huge branching factor (18) so if the scramble is more than 3 moves we can't reliably solve within a minute. 

Naive optimizations: move pruning (e.g. don't turn the same side if we just turned it)

## Phase 2 - Heuristic-Based Approach

2. A\*: BFS w/ a Priority Queue, key = heuristic
3. Iterative Deepening DFS (ID-DFS): We use DFS but we limit depth to a certain number. We iterate through each depth from 1 to a limit n and then run DFS until we find a solution. 
4. Iterative Deepning A* (IDA*): combination of 2 and 3

Naive Heuristics:

- Number of unsolved tiles (not pieces)
- Total distance from each piece to its side
- Entropy of each side

None of these worked that well, so we can only solve scrambles up to 6 moves reliably here. 

## Phase 3 - Better Heuristics (WIP)

In actual cubing, it's useful to know how far each piece is from its correct spot, not just the individual tiles on each side. 

Additionally, pieces can be flipped (edges) or rotated (corners) so we should track that as well. 

A formula that could be used here is:

1. For edges:
    a) euclidean distance from edge to its correct spot
    b) if edge in correct spot, 1 if its flipped, else 0

2. For corners:
    a) euclidean distance from corner to its correct spot
    b) if corner in correct spot, 1 if its rotated, else 0