
import game
import sys
import numpy as np
import heuristicai as h


# Author:      chrn (original by nneonneo)
# Date:        11.11.2016
# Copyright:   Algorithm from https://github.com/nneonneo/2048-ai
# Description: The logic to beat the game. Based on expectimax algorithm.


def find_best_move(board):
    """
    find the best move for the next turn.
    It will split the workload in 4 process for each move.
    """
    bestmove = -1
    UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3
    move_args = [UP, DOWN, LEFT, RIGHT]

    result = [score_toplevel_move(i, board) for i in range(len(move_args))]
    bestmove = result.index(max(result))
    for m in move_args:
        print("move: %d score: %.4f" % (m, result[m]))
    return bestmove


def score_toplevel_move(move, board, depth=0):
    """
    Entry Point to score the first move.
    """
    newboard = execute_move(move, board)
    length = len(newboard)

    if board_equals(board, newboard):
        return depth
    # TODO:
    # Implement the Expectimax Algorithm.
    # 1.) Start the recursion until it reach a certain depth
    if count_zeros_in_board(newboard) < 4:
        dyn_depth = 2
    else:
        dyn_depth = 1

    if depth < dyn_depth:
        depth += 1
        score = 0
        # 2.) When you don't reach the last depth, get all possible board states and
        #		calculate their scores dependence of the probability this will occur. (recursively)

        for row in range(length):
            for col in range(length):
                if newboard[row][col] == 0:
                    score += get_score_wight(newboard, row, col, depth, 2)
                    score += get_score_wight(newboard, row, col, depth, 4)
                    newboard[row][col] = 0
        return score / count_zeros_in_board(newboard)
    # 3.) When you reach the leaf calculate the board score with your heuristic.
    else:
        if count_zeros_in_board(newboard) > 0:
            return count_zeros_in_board(newboard) * (score_monotonicity(newboard) * first_row_bonus(newboard))
        else:
            return corner_shockwave(board) + (score_monotonicity(newboard) * first_row_bonus(newboard))


def get_score_wight(newboard, row, col, depth, num):
    directions = [x for x in range(4)]
    newboard[row][col] = num
    weight = 0.9 if num == 2 else 0.1
    moves_score = [0 for x in range(4)]
    for m in range(len(directions)):
        moves_score[m] = score_toplevel_move(m, newboard, depth)
    return weight * np.max(moves_score)


def execute_move(move, board):
    """
    move and return the grid without a new random tile
	It won't affect the state of the game in the browser.
    """

    UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3

    if move == UP:
        return game.merge_up(board)
    elif move == DOWN:
        return game.merge_down(board)
    elif move == LEFT:
        return game.merge_left(board)
    elif move == RIGHT:
        return game.merge_right(board)
    else:
        sys.exit("No valid move")


def board_equals(board, newboard):
    """
    Check if two boards are equal
    """
    return (newboard == board).all()


def first_row_bonus(board):
    factor = 1
    first = board[0][0]
    second = board[0][1]
    third = board[0][2]
    fourth = board[0][3]
    if first >= 8:
        factor += 10 * first
    if second >= 8:
        factor += 10 * first + 3 * second
    if third >= 8:
        factor += 10 * first + 3 * second + 2 * third
    if fourth >= 8:
        factor += 10 * first + 3 * second + 2 * third + fourth

    return factor


# check if values of the tiles are all either increasing or
# decreasing along both the left/right and up/down directions
def score_monotonicity(board):
    factor = 1
    new_board = np.copy(board)
    length = len(new_board)

    # sort right highest to left lowest
    for i in range(length):
        new_board[i][::-1].sort()

    for i in range(length):
        if row_equals(new_board[i], board[i]):
            factor += 1

    # sort left lowest to right highest
    for i in range(length):
        new_board[i].sort()

    for i in range(length):
        if row_equals(new_board[i], board[i]):
            factor += 1

    for i in range(length):
        new_board.T[i].sort()

    # sort down highest to up lowest
    for i in range(length):
        if row_equals(new_board.T[i], board.T[i]):
            factor += 1

    for i in range(length):
        new_board.T[i][::-1].sort()

    # sort up highest to down lowest
    for i in range(length):
        if row_equals(new_board.T[i], board.T[i]):
            factor += 1

    return factor


def corner_shockwave(board):
    board = np.copy(board)
    weight = [1000, 900, 700, 500
            , 800, 700, 500, 200
            , 700, 500, 200, 30
            , 500, 200, 30, 0]
    board = board.ravel()
    return np.sum(np.array(board) * np.array(weight))


def row_equals(row, new_row):
    return all(np.equal(new_row, row))


def count_zeros_in_board(board):
    zeros = 0
    for i in range(len(board)):
        zeros += 4 - np.count_nonzero(board[i])
    return zeros
