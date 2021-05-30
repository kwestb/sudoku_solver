from __future__ import annotations

import dataclasses
import itertools
import re
import sys
import typing

import ortools.linear_solver.pywraplp


@dataclasses.dataclass
class Problem:
    """
    A class representing a problem instance.

    You load a problem instance from a file stream using the 'parse'
    method, and you solve the instance using the 'solve' method.
    """

    problem: dict[frozenset[(int, int)], int]

    @staticmethod
    def parse(input: typing.TextIO) -> "Problem":
        """
        Parse the input format.

        The input format consists of lines in a text file. Each line is a comma-separated
        list of cells followed by a colon, followed by the sum of the values of the cells
        in the solution. Each cell is a pair of integers enclosed in parentheses, separated
        by a comma, just like a tuple in python.
        """

        return Problem({
            cells: int(right_side)
            # read the lines
            for line in input.readlines()
            # strip out comments
            for line in [re.sub("#.*$", "", line)]
            # strip out whitespace
            for line in [re.sub("\\s*", "", line)]
            # filter out empty lines
            if line
            # split the line on the colon; the left side is a comma-separated
            # list of cells and the right side is their sum
            for left_side, right_side in [re.split(":", line)]
            for cells in [
                frozenset(
                    # parse the list of cells into tuples
                    tuple(map(int, map(match.group, range(1, 3))))
                    for match in map(
                        re.compile("\\(([1-9]),([1-9])\\)").match,
                        re.findall("(\\([1-9],[1-9]\\)),?", left_side),
                    )
                )
            ]
        })

    def __str__(self) -> str:
        """
        Produce a string representation of the problem in the input format.
        """

        return "\n".join(
            sorted(
                "%s:%d" % (",".join(map("(%d,%d)".__mod__, sorted(cells))), group_sum)
                for cells, group_sum in self.problem.items()
            ),
        )

    def solve(self, backend: str = "SCIP") -> Solution:
        """
        Solve a Sudoku instance.

        The problem is given as a 9-element list of 9-element lists of "cells". Each cell is
        either an integer from 1 though 9 inclusive (if the cell has a preassigned value in
        the problem) or None (if the cell should be solved for in the solution). The return
        value is a 9-element list of 9-element lists of integers that fully solve the Sudoku.
        """

        # Create "sets" representing the rows, columns and values for the Sudoku problem.
        rows, columns, values = 3 * [range(1, 10)]

        # Instantiate the solver. By default, it uses the SCIP backend. https://www.scipopt.org/
        solver = ortools.linear_solver.pywraplp.Solver.CreateSolver(backend)

        # For every combination of cell and value, create a binary decision variable
        # that determines if the value belongs at that cell in the solution. We store
        # these variables in a 3-dimensional array indexed by the rows, columns, and values.
        decision_vars = {
            row: {
                col: {val: solver.IntVar(0, 1, f"d{row}{col}{val}") for val in values}
                for col in columns
            }
            for row in rows
        }

        # For every cell, create an integer variable taking values over the range [1, 9]
        # that will hold the value assignment for that cell. We store these variables in
        # a 2-dimensional array indexed by the rows and columns.
        solution_vars = {
            row: {col: solver.IntVar(1, 9, f"s{row}{col}") for col in columns}
            for row in rows
        }

        # The objective is to minimize the sum of the solution variables.
        objective = solver.Objective()
        objective.SetMinimization()
        for row, col in itertools.product(rows, columns):
            objective.SetCoefficient(solution_vars[row][col], 1)

        # Initialize from the data in the problem instance.
        #
        # For each set of cells in the problem instance, the sum of their
        # solution variables must be equal to the sum in the problem instance.
        for group, group_sum in self.problem.items():
            constraint = solver.Constraint(group_sum, group_sum)
            for row, col in group:
                constraint.SetCoefficient(solution_vars[row][col], 1)

        # Every cell must take a value assignment in the solution.
        #
        # For each cell, the sum of the decision variables over values
        # must be exactly equal to 1.
        for row, col in itertools.product(rows, columns):
            constraint = solver.Constraint(1, 1)
            for val in values:
                constraint.SetCoefficient(decision_vars[row][col][val], 1)

        # Every value appears exactly once on each row in the solution.
        #
        # For each row and value, the sum of the decision variables over
        # columns must be exactly equal to 1.
        for row, val in itertools.product(rows, values):
            constraint = solver.Constraint(1, 1)
            for col in columns:
                constraint.SetCoefficient(decision_vars[row][col][val], 1)

        # Every value appears exactly once on each column in the solution.
        #
        # For each column and value, the sum of the decision variables
        # over rows must be exactly equal to 1.
        for col, val in itertools.product(columns, values):
            constraint = solver.Constraint(1, 1)
            for row in rows:
                constraint.SetCoefficient(decision_vars[row][col][val], 1)


        # Every value appears exactly once in each of the non-overlapping 3x3 subgrids.
        #
        # For each subgrid and value, the sum of the decision variables
        # over the subgrid must be exactly equal to 1.
        for i, j, val in itertools.product(range(3), range(3), values):
            constraint = solver.Constraint(1, 1)
            for row, col in itertools.product(*map(lambda x: range(3 * x + 1, 3 * x + 4), (i, j))):
                constraint.SetCoefficient(decision_vars[row][col][val], 1)

        # Connect the decision variables to the solution variables.
        #
        # For every (row, column), the value-weighted sum of the decision
        # variables is equal to the solution variable.
        for row, col in itertools.product(rows, columns):
            constraint = solver.Constraint(0, 0)
            constraint.SetCoefficient(solution_vars[row][col], -1)
            for val in values:
                constraint.SetCoefficient(decision_vars[row][col][val], val)

        # Solve the instance.
        solver.Solve()

        # Extract and return the solution.
        return Solution({
            (row, col): int(solution_vars[row][col].solution_value())
            for row, col in itertools.product(rows, columns)
        })


@dataclasses.dataclass
class Solution:
    """
    A wrapper for a solution to a problem.

    You can interrogate this object by retrieving the solution
    value for a cell with '__getitem__'. The '__str__' allows
    the solution to be pretty-printed to a stream if you like.
    """

    solution: dict[(int, int), int]

    def __getitem__(self, cell: tuple[int, int]) -> int:
        """
        Return the solution value for the given cell.
        """

        return self.solution[cell]

    def __str__(self) -> str:
        """
        Return a pretty represention of the solution suitable for output to a terminal.
        """

        def row(i: int) -> str:
            """
            Return the string representation of a given row in the solution.
            """

            return " ".join([
                "|",
                " | ".join(
                    " ".join(str(self[(i, 3 * k + j - 3)]) for j in range(1, 4))
                    for k in range(1, 4)
                ),
                "|",
            ])

        return "\n".join(
            itertools.chain(
                ["+-------+-------+-------+"],
                map(row, range(1, 4)),
                ["+-------+-------+-------+"],
                map(row, range(4, 7)),
                ["+-------+-------+-------+"],
                map(row, range(7, 10)),
                ["+-------+-------+-------+"],
            ),
        )

    def print(self, out: typing.TextIO) -> None:
        """
        Print the solution to the given output stream.
        """

        print(self, file=out)


if __name__ == "__main__":
    # Solve the problem on stdin and write the solution to stdout
    Problem.parse(sys.stdin).solve().print(sys.stdout)
