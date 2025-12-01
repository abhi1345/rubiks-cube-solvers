from RubiksCube import *
from solutions.bfs import solve_cube_bfs
from solutions.astar import solve_cube_astar
import copy
import time

cube = RubiksCube()

cube.scramble(4)

cube.print_cube()

start_time = time.time()

result, moves = solve_cube_astar(cube)

print(result, moves)

end_time = time.time()

print(f"Time taken: {end_time - start_time} seconds")
