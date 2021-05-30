from __future__ import annotations

import itertools
import unittest

from rules_python.python.runfiles import runfiles

import sudoku_solver


class TestSudokuSolver(unittest.TestCase):

    def _assert_solved_instance(self) -> None:
        self.assert_solved_instance(
            "example_sudoku.txt",
            [
                [ 6, 4, 2, 7, 9, 1, 3, 8, 5 ],
                [ 1, 3, 7, 5, 8, 6, 2, 4, 9 ],
                [ 8, 9, 5, 4, 3, 2, 1, 7, 6 ],
                [ 4, 6, 1, 8, 7, 5, 9, 3, 2 ],
                [ 3, 5, 8, 2, 6, 9, 4, 1, 7 ],
                [ 7, 2, 9, 1, 4, 3, 6, 5, 8 ],
                [ 9, 1, 3, 6, 5, 7, 8, 2, 4 ],
                [ 5, 8, 6, 3, 2, 4, 7, 9, 1 ],
                [ 2, 7, 4, 9, 1, 8, 5, 6, 3 ],
            ],
        )

    def test_solve_killer_sudoku(self) -> None:
        self._assert_solved_instance(
            "example_killer_sudoku.txt",
            [
                [ 1, 6, 5, 8, 7, 2, 3, 9, 4, ],
                [ 4, 7, 2, 5, 3, 9, 6, 1, 8, ],
                [ 9, 3, 8, 1, 4, 6, 5, 7, 2, ],
                [ 5, 9, 1, 4, 2, 7, 8, 3, 6, ],
                [ 6, 8, 7, 3, 1, 5, 4, 2, 9, ],
                [ 2, 4, 3, 9, 6, 8, 1, 5, 7, ],
                [ 3, 5, 9, 2, 8, 4, 7, 6, 1, ],
                [ 8, 1, 6, 7, 9, 3, 2, 4, 5, ],
                [ 7, 2, 4, 6, 5, 1, 9, 8, 3, ],
            ],
        )

    def _assert_solved_instance(self, input: str, expected: list[list[int]]) -> None:
        with open(runfiles.Create().Rlocation(f"sudoku_solver/{input}"), "r") as f:
            problem = sudoku_solver.Problem.parse(f)
        solution = problem.solve()
        for row, col in itertools.product(*(2 * [range(1, 10)])):
            assert solution[(row, col)] == expected[row - 1][col - 1]


if __name__ == '__main__':
    unittest.main()
