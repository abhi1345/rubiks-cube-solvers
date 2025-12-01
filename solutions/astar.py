import copy
import time
from heapq import heappush, heappop
import math

try:
    from RubiksCube import RubiksCube
except ImportError:
    import os
    import sys

    # Allow running as a script without relying on package-relative imports.
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from RubiksCube import RubiksCube

def compute_number_of_misplaced_tiles_heuristic(cube):
    
    output = 0

    for expected, side in enumerate(cube.state):
        for row in side:
            for tile in row:
                if tile != expected:
                    output += 1

    return output

def entropy_of_list(l):
    return -sum([(l.count(x)/len(l)) * math.log2(l.count(x)/len(l)) for x in l])

def entropy_of_matrix(m):
    return sum([entropy_of_list(row) for row in m])

def compute_entropy_heuristic(cube):
    return sum([entropy_of_matrix(side) for side in cube.state])

def combined_heuristic(cube):
    return compute_number_of_misplaced_tiles_heuristic(cube) + compute_entropy_heuristic(cube)

def validate(heuristic_fn):
    print(f"Validating heuristic: {heuristic_fn.__name__}")

    cube = RubiksCube()

    solved_heuristic = heuristic_fn(cube)

    print(f"Solved heuristic: {solved_heuristic}")

    for i in range(10):
        cube.scramble(2)
        print(f"Heuristic after 2 scrambles: {heuristic_fn(cube)}")

# validate(compute_entropy_heuristic)
# validate(compute_number_of_misplaced_tiles_heuristic)

def solve_cube_astar(cube):

    cases_explored = 0

    visited = set()

    heuristic_fn = combined_heuristic

    starting_heuristic = heuristic_fn(cube)

    bfs_queue = [(starting_heuristic, cube, [])]

    while bfs_queue:

        cur_heuristic, cur_cube, moves_so_far = heappop(bfs_queue)

        if cur_cube.state_tuple() in visited:
            continue

        visited.add(cur_cube.state_tuple())

        if cur_cube.is_solved():
            return True, moves_so_far

        if len(moves_so_far) > 100:
            return False, moves_so_far

        for color in cur_cube.color_map:
            for n in range(1, 4):

                if len(moves_so_far) > 0:
                    if (color, n) == moves_so_far[-1]:
                        continue
                    elif (color, 4-n) == moves_so_far[-1]:
                        continue

                new_cube = copy.deepcopy(cur_cube)
                new_cube.turn(color, n)

                new_moves_so_far = moves_so_far + [(color, n)]

                if new_cube.is_solved():
                    print(f"Cases Explored: {cases_explored}")
                    return True, new_moves_so_far
                if new_cube.state_tuple() in visited:
                    continue

                new_heuristic = len(new_moves_so_far) + heuristic_fn(new_cube)

                heappush(bfs_queue, (new_heuristic, new_cube, new_moves_so_far))

                cases_explored += 1
    
    return False, ["Coudn't Solve"]
