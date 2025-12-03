from __future__ import annotations

from typing import Callable, Dict, List

from rubiks import RubiksCube
from rubiks.cube import Move
from rubiks.heuristics import DEFAULT_HEURISTIC, Heuristic
from rubiks.solvers import SolveResult, solve_cube_astar, solve_cube_bfs, solve_cube_iddfs

SolverFn = Callable[..., SolveResult]

SOLVER_REGISTRY: Dict[str, SolverFn] = {
    "astar": solve_cube_astar,
    "bfs": solve_cube_bfs,
    "iddfs": solve_cube_iddfs,
}


def run(
    method: str = "iddfs",
    *,
    scramble_moves: int = 5,
    heuristic: Heuristic = DEFAULT_HEURISTIC,
    max_depth: int = 5,
) -> tuple[SolveResult, List[Move]]:
    cube = RubiksCube()
    scramble_sequence = cube.scramble(scramble_moves)

    solver = SOLVER_REGISTRY.get(method)
    if solver is None:
        raise ValueError(f"Unknown solver '{method}'. Available: {sorted(SOLVER_REGISTRY)}")

    kwargs = {"max_depth": max_depth}
    if method == "astar":
        kwargs["heuristic"] = heuristic

    result = solver(cube, **kwargs)
    return result, scramble_sequence


if __name__ == "__main__":
    solve_result, scramble_sequence = run()

    print(f"Scramble ({len(scramble_sequence)} moves): {scramble_sequence}")
    print(f"Solved: {solve_result.success}")
    print(f"Moves found ({len(solve_result.moves)}): {solve_result.moves}")
    print(f"States explored: {solve_result.explored}")
    print(f"Duration: {solve_result.duration:.4f}s")
