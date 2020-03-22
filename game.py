from abc import ABC, abstractmethod
from random import random
from typing import List

import numpy as np

class State:
    """
    A functor wrapper of a state including its ability to convert itself to a key
    """
    @property
    def key(self):
        return self._bytes_conversion(self._state)

    @property
    def value(self):
        return self._state

    def __init__(self, state, bytes_conversion):
        self._state = state
        self._bytes_conversion = bytes_conversion


class Game(ABC):

    @staticmethod
    def from_config(game_class, config):
        arg_count = game_class.__init__.__code__.co_argcount
        ctor_arg_names = game_class.__init__.__code__.co_varnames[1:arg_count]
        required_arg_count = arg_count - 1
        if game_class.__init__.__defaults__:
            required_arg_count = arg_count - len(game_class.__init__.__defaults__) - 1
        try:
            expected_keys = {key: config[key] for key in ctor_arg_names[:required_arg_count]}
            optional_keys = {}
            for key, value in config.items():
                if key in expected_keys:
                    continue
                if key in ctor_arg_names:
                    optional_keys[key] = value

            return game_class(**optional_keys, **expected_keys)
        except KeyError as e:
            exit(f"Missing key: {e} in config - unable to construct a valid {game_class.__name__} game!")
            return None

    # ================= PROPERTIES =================

    @property
    @abstractmethod
    def completed(self) -> bool:
        pass

    # ================= METHODS =================

    @abstractmethod
    def get_state(self) -> State:
        pass

    @abstractmethod
    def allowed_moves(self) -> List:
        pass

    @abstractmethod
    def apply_move(self, move) -> None:
        pass

    @abstractmethod
    def print_move(self, move) -> None:
        """
        Print a move right after it's been applied to
        show it's effect on the game
        :param move: the move that was made
        :return: None
        """
        pass

    def _swap_player(self) -> None:
        self._player1s_turn = not self._player1s_turn

    def __init__(self, player_starting: int):
        if player_starting < 1 or player_starting > 2:
            self._player1s_turn = bool(random.getrandbits(1))
        else:
            self._player1s_turn = (player_starting == 1)

    def did_player1_win(self):
        # player 1 wins if it's no longer his turn when the game completed,
        # i.e. if player 1 was the last player to perform an action!
        return self.completed and not self._player1s_turn
