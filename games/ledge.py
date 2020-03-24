import random
from typing import List

import numpy as np

from game import Game


# rules: a player may
# a. pick up the coin currently sitting on the ledge
# b. move a coin from its current location to another location to the left

class Ledge(Game):

    def clone(self):
        clone = Ledge(self.player_start_mode, self.board)
        clone._player1_starts = self._player1_starts
        clone._player1s_turn = self._player1s_turn
        return clone

    def __init__(self, player_start_mode: int, initial_board=None):
        Game.__init__(self, player_start_mode)

        if type(initial_board) is np.ndarray:
            self.board = np.copy(initial_board)
        elif type(initial_board) is list:
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
        self._last_state = np.copy(self.board)

    # ================= PROPERTIES =================

    @property
    def completed(self) -> bool:
        return self._completed

    # ================= METHODS =================

    def get_state(self) -> (bool, bytes):
        return self.player1s_turn, self.board.tobytes()

    # NOTE: these could be cached till apply_move is called
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

    def apply_move(self, move) -> None:
        self._last_state = np.copy(self.board)
        # Apply the move
        if move == 0:
            if self.board[0] == 2:
                self._completed = True
            self.board[0] = 0
        else:
            self.board[move[1]], self.board[move[0]] = self.board[move[0]], self.board[move[1]]
        # End turn, next player's turn
        self._swap_player()

    def print_move(self, move) -> None:
        action = f"Popping ledge: {'gold' if self._last_state[0] == 2 else 'copper'} coin"
        if type(move) is tuple:
            action = f"Moving {'gold' if self._last_state[move[0]] == 2 else 'copper'} coin from {move[0]} to {move[1]}"

        # This is inverted because the player was just swapped
        print(f"Player {'2' if self._player1s_turn else '1'}:\n"
              f"{action}, resulting in board state:\n{self.board}\n")

    def __repr__(self):
        return f"{self.board}"
