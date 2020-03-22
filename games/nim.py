from typing import List

import numpy as np
from abc import abstractmethod
from game import Game, State


# https://en.wikipedia.org/wiki/Nim
# Nim parameters
# collections/heaps of stones
# Min & Max stones removed

# Simple version of Nim:
# N: number of stones on the board
# K: max number of stones a player can take of the board
# MIN: 1 :: the minimum number of stones that can be removed in a turn
# Rules:
# The 2 players take turns removing n stones (MIN <= n <= K && n <= N)
# the player who takes the last stone wins.

# THE SYSTEM SHOULD BE ABLE TO PLAY WITH ANY VALUE FOR N & K, WHERE 1 < K < N < 100



class Nim(Game):

    def __init__(self, player_starting: int, stones: int, max_move: int, min_move: int = 1):
        Game.__init__(self, player_starting)
        self._initial_stone_count = stones
        if stones < 1:
            print(f"Too few, or negative amount of stones, clamping to 1!")
            stones = 1
        self._stones = stones
        self._max = max_move
        self._min = min_move
        self._starting_allowed_moves = list(np.arange(1, self._max_move + 1))
        self._last_state = self._stones

    # ================= PROPERTIES =================

    @property
    def completed(self) -> bool:
        """
        :return: game completion state:
            true = done, false = not done
        """
        return self._stones == 0

    # @property
    # def initial_stone_count(self) -> int:
    #     return self._initial_stone_count
    #
    # @property
    # def stones_left(self) -> int:
    #     return self._stones

    @property
    def _max_move(self):
        """
        :return: the maximum number of stones that can currently
        be taken given the number of remaining stones
        """
        return min(self._stones, self._max)

    # ================= METHODS =================

    def get_state(self) -> State:
        return State(self._stones, lambda s: s.to_bytes(4, byteorder="big"))

    def allowed_moves(self) -> List:
        """
        Get all the allowed moves at this point
        :return: (MIN <= n <= K && n <= N)
        """
        # minor optimization to avoid reallocation of new arrays every turn
        if self._stones < self._max:
            return list(np.arange(1, self._max_move + 1))
        return self._starting_allowed_moves

    def apply_move(self, move: int) -> None:
        self._last_state = self._stones
        # Apply the move
        if move < self._min or move > self._max_move:
            exit(f"Illegal move performed! tried to remove {move}, "
                 f"when the constraints were ({self._min} <= {move} <= {self._max_move})!")
        self._stones -= move
        # End turn, next player's turn
        self._swap_player()

    def print_move(self, move) -> None:
        print(f"{'Player 1' if self._player1s_turn else 'Player 2'}:\n"
              f"taking {move} of {self._last_state} stones, {self._stones} stones remain...\n")

    def __repr__(self):
        return f"Stones left: {self._stones}\nselection range: {self._min} - {self._max_move}"
