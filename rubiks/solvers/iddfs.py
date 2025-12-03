from __future__ import annotations

from collections import deque
import time

from rubiks.cube import RubiksCube

from .common import SolveResult, should_prune_move

def solve_cube_iddfs(cube: RubiksCube, *, max_depth: int = 100) -> SolveResult:
    for depth in range(1, max_depth + 1):
        result = solve_cube_iddfs_helper(cube, max_depth=depth)
        if result.success:
            return result
    return result

def solve_cube_iddfs_helper(cube: RubiksCube, *, max_depth: int = 100) -> SolveResult:
    start = time.perf_counter()
    visited = set()
    queue = deque([(cube.clone(), [])])
    explored = 0

    while queue:
        cur_cube, moves_so_far = queue.pop()
        state_key = cur_cube.state_tuple()
        if state_key in visited:
            continue
        visited.add(state_key)

        if cur_cube.is_solved():
            return SolveResult(True, moves_so_far, explored, time.perf_counter() - start)

        if len(moves_so_far) >= max_depth:
            continue

        for color in cur_cube.color_map:
            for turns in range(1, 4):
                move = (color, turns)
                if should_prune_move(moves_so_far, move):
                    continue

                new_cube = cur_cube.clone()
                new_cube.turn(color, turns)

                new_moves = moves_so_far + [move]

                if new_cube.state_tuple() in visited:
                    continue

                queue.append((new_cube, new_moves))
                explored += 1

    return SolveResult(False, [], explored, time.perf_counter() - start)