from RubiksCube import *
import copy
import time

cube = RubiksCube()

cube.scramble(9)

cube.print_cube()

visited = set()

def solve_cube(cube):    
    bfs_queue = [(cube, [])]

    while bfs_queue:

        cur_cube, moves_so_far = bfs_queue.pop(0)

        if cur_cube.state_tuple() in visited:
            continue

        visited.add(cur_cube.state_tuple())

        if cur_cube.is_solved():
            return True, moves_so_far

        if len(moves_so_far) > 100:
            return False, moves_so_far

        for color in cur_cube.color_map:
            for n in range(1, 4):
                new_cube = copy.deepcopy(cur_cube)
                new_cube.turn(color, n)

                new_moves_so_far = moves_so_far + [(color, n)]

                if new_cube.is_solved():
                    return True, new_moves_so_far
                if new_cube.state_tuple() in visited:
                    continue

                bfs_queue.append((new_cube, new_moves_so_far))
    
    return False, ["Coudn't Solve"]


start_time = time.time()

result, moves = solve_cube(cube)

print(result, moves)

end_time = time.time()

print(f"Time taken: {end_time - start_time} seconds")
