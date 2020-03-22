import random
from typing import List

import numpy as np

from game import Game

# rules: a player may
# a. pick up the coin currently sitting on the ledge
# b. move a coin from its current location to another location to the left

class Ledge(Game):

    def __init__(self, player_starting: int, initial_board=None):
        Game.__init__(self, player_starting)

        if type(initial_board) is list:
            self.board = np.array(initial_board)
            if len(np.where(self.board > 1)[0]) > 1:
                print(f"Bad initial configuration, too many gold! - Overriding board definition: [1, 0, 0, 2]")
                self.board = np.array([1, 0, 0, 2])
            elif len(np.where(self.board < 0)[0]) > 0:
                print(f"Bad initial configuration, bad coin values! - Overriding board definition: [1, 0, 0, 2]")
                self.board = np.array([1, 0, 0, 2])
        else:
            length = initial_board["length"]
            copper_coins = initial_board["copper_coins"]
            if copper_coins >= length:
                print(f"Too many copper coins, clamping to length-1: {length - 1}!")
                copper_coins = length - 1
            elif copper_coins < 0:
                print("Negative amount of copper coins, clamping to 0!")
                copper_coins = 0

            indices = np.arange(length)
            gold_index = random.randrange(length)
            indices = np.delete(indices, gold_index)
            copper_indices = np.random.choice(indices, copper_coins)
            board = np.zeros(length, dtype=np.int32)
            board[gold_index] = 2
            for i in np.nditer(copper_indices):
                board[i] = 1
            self.board = board

        self._completed = False

    # ================= PROPERTIES =================

    @property
    def state_key(self) -> bytes:
        return self.board.tobytes()
        pass

    @property
    def completed(self) -> bool:
        return self._completed

    # ================= METHODS =================

    def allowed_moves(self) -> List:
        movable_indices = [i for i in range(len(self.board)) if self.board[i] != 0]
        moves = []
        if self.board[0] != 0:  # if the ledge has content, add pop of ledge element as a move
            moves.append(0)

        for q in range(len(movable_indices) - 1, -1, -1):
            available_moves_from_q = movable_indices[q] - 1 - movable_indices[q - 1]
            if available_moves_from_q < 0:
                available_moves_from_q = movable_indices[q]
            for distance in range(1, available_moves_from_q + 1):
                p = movable_indices[q] - distance
                moves.append((movable_indices[q], p))
        return moves

    def _get_state_after_move(self, move) -> (np.ndarray, bool):
        board = np.copy(self.board)
        done = False
        if move == 0:
            if board[0] == 2:
                done = True
            board[0] = 0
        else:
            board[move[1]], board[move[0]] = board[move[0]], board[move[1]]

        return board, done

    def apply_move(self, move) -> None:
        self.board, self._completed = self._get_state_after_move(move)
        self._swap_player()


    def print_move(self, move) -> None:
        action = f"Popping ledge: {'gold' if self.board[0] == 2 else 'copper'} coin"
        if type(move) is tuple:
            action = f"Moving {'gold' if self.board[move[0]] == 2 else 'copper'} coin from {move[0]} to {move[1]}"

        print(f"Player {'1' if self._player1s_turn else '2'}:\n"
              f"{action}, resulting in board state:\n{self._get_state_after_move(move)[0]}\n")

    def __repr__(self):
        return f"{self.board}"
