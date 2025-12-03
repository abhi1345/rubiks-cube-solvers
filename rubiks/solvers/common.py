from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from rubiks.constants import color_map, colors, opposite_color_map
from rubiks.cube import Move

@dataclass
class SolveResult:
    success: bool
    moves: list[Move]
    explored: int
    duration: float


def should_prune_move(history: Sequence[Move], candidate: Move) -> bool:
    if not history:
        return False

    last_color, last_turns = history[-1]
    color, turns = candidate

    if color != last_color:
        return False

    return turns == last_turns or turns == 4 - last_turns


__all__ = ["SolveResult", "should_prune_move", "colors", "color_map", "opposite_color_map"]
