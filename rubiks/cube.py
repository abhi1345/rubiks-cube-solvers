from __future__ import annotations

import random
from typing import Iterable, List, Sequence, Tuple


Face = List[List[int]]
Move = Tuple[str, int]


def rotate_matrix(matrix: Face) -> Face:
    return [list(row) for row in zip(*matrix[::-1])]


SOLVED_STATE: List[Face] = [
    [[0, 0, 0], 
    [0, 0, 0], 
    [0, 0, 0]],

    [[1, 1, 1], 
    [1, 1, 1], 
    [1, 1, 1]],

    [[2, 2, 2], 
    [2, 2, 2], 
    [2, 2, 2]],

    [[3, 3, 3], 
    [3, 3, 3], 
    [3, 3, 3]],

    [[4, 4, 4], 
    [4, 4, 4], 
    [4, 4, 4]],
    
    [[5, 5, 5], 
    [5, 5, 5], 
    [5, 5, 5]],
]


def _copy_state(state: Sequence[Face]) -> List[Face]:
    return [ [row[:] for row in face] for face in state ]


class RubiksCube:

    def __init__(self, state: Sequence[Face] | None = None):
        self.color_map = ["white", "yellow", "red", "orange", "blue", "green"]
        self.state: List[Face] = _copy_state(state or SOLVED_STATE)
        self.turns = {
            "white": self.turn_white_side,
            "yellow": self.turn_yellow_side,
            "red": self.turn_red_side,
            "orange": self.turn_orange_side,
            "blue": self.turn_blue_side,
            "green": self.turn_green_side,
        }

    def state_tuple(self):
        return tuple(tuple(tuple(row) for row in side) for side in self.state)

    def print_cube(self):
        for i in range(len(self.color_map)):
            print(f"\n{self.color_map[i]} side:")
            for row in self.state[i]:
                print(row)

    def turn(self, color, n):
        self.turns[color](n)

    def turn_white_side(self, n):
        for _ in range(n):
            self.state[0] = rotate_matrix(self.state[0])

            colors_to_cycle = ["red", "green", "orange", "blue"]
            rows_to_cycle = ["top", "top", "top", "top"]

            self.cycle_rows(colors_to_cycle, rows_to_cycle)

    def turn_yellow_side(self, n):
        for _ in range(n):
            self.state[1] = rotate_matrix(self.state[1])

            colors_to_cycle = ["red", "blue", "orange", "green"]
            rows_to_cycle = ["bottom", "bottom", "bottom", "bottom"]

            self.cycle_rows(colors_to_cycle, rows_to_cycle)

    def turn_red_side(self, n):
        for _ in range(n):
            self.state[2] = rotate_matrix(self.state[2])

            colors_to_cycle = ["white", "blue", "yellow", "green"]
            rows_to_cycle = ["left", "left", "right", "right"]
            reverse_before_inserting = [1, 0, 1, 0]

            self.cycle_rows(colors_to_cycle, rows_to_cycle, reverse_before_inserting)

    def turn_orange_side(self, n):
        for _ in range(n):
            self.state[3] = rotate_matrix(self.state[3])

            colors_to_cycle = ["white", "green", "yellow", "blue"]
            rows_to_cycle = ["right", "left", "left", "right"]
            reverse_before_inserting = [0, 1, 0, 1]

            self.cycle_rows(colors_to_cycle, rows_to_cycle, reverse_before_inserting)

    def turn_blue_side(self, n):
        for _ in range(n):
            self.state[4] = rotate_matrix(self.state[4])

            colors_to_cycle = ["white", "orange", "yellow", "red"]
            rows_to_cycle = ["bottom", "left", "bottom", "right"]
            reverse_before_inserting = [1, 0, 0, 1]

            self.cycle_rows(colors_to_cycle, rows_to_cycle, reverse_before_inserting)

    def turn_green_side(self, n):
        for _ in range(n):
            self.state[5] = rotate_matrix(self.state[5])

            colors_to_cycle = ["white", "red", "yellow", "orange"]
            rows_to_cycle = ["top", "left", "top", "right"]
            reverse_before_inserting = [0, 1, 1, 0]

            self.cycle_rows(colors_to_cycle, rows_to_cycle, reverse_before_inserting)

    def get_row(self, side, row):
        if row == "top":
            return side[0]
        elif row == "left":
            return [x[0] for x in side]
        elif row == "bottom":
            return side[-1]
        elif row == "right":
            return [x[-1] for x in side]
        raise ValueError 
    
    def replace_row(self, matrix, row_label, new_row):
        if row_label == "top":
            matrix[0] = new_row
        elif row_label == "left":
            for i,x in enumerate(matrix):
                x[0] = new_row[i]
        elif row_label == "bottom":
            matrix[-1] = new_row
        elif row_label == "right":
            for i,x in enumerate(matrix):
                x[-1] = new_row[i]
        else:
            raise ValueError(f"Invalid inputs: {row_label, new_row}")
    
    def cycle_rows(self, colors_to_cycle, rows_to_cycle, reverse_before_inserting=None):
        color_indices_to_cycle = [self.color_map.index(color) for color in colors_to_cycle] 
        matrices_to_cycle = [self.state[i] for i in color_indices_to_cycle]
        extracted_rows = [self.get_row(matrices_to_cycle[i], rows_to_cycle[i]) for i in range(len(rows_to_cycle))]

        for i in range(len(colors_to_cycle)):
            get_from_index = i - 1
            row_to_insert = extracted_rows[get_from_index]

            if reverse_before_inserting and reverse_before_inserting[i] == 1:
                row_to_insert = list(reversed(row_to_insert))

            self.replace_row(self.state[color_indices_to_cycle[i]], 
                             rows_to_cycle[i], 
                             row_to_insert)
            
    def is_solved(self):
        return self.state == SOLVED_STATE

    def clone(self) -> "RubiksCube":
        return RubiksCube(state=_copy_state(self.state))

    def apply_moves(self, moves: Iterable[Move]) -> None:
        for color, n in moves:
            self.turn(color, n)

    def scramble(self, steps: int = 25) -> list[Move]:
        moves: list[Move] = []
        for _ in range(steps):
            color = random.choice(self.color_map)
            rotations = random.randint(1, 3)
            moves.append((color, rotations))
        self.apply_moves(moves)
        return moves

    def __lt__(self, other):
        if not isinstance(other, RubiksCube):
            return NotImplemented
        return True
