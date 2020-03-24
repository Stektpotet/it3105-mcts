from abc import ABC, abstractmethod
import random
from typing import List

class State:
    """
    A functor wrapper of a state including its ability to convert itself to a key
    """
    @property
    def key(self) -> (bool, bytes):
        b = b'\x00'
        try:
            b = self._bytes_conversion(self._state)
        except AttributeError:
            print("AttrErr", self._state, type(self._state), self._player1)
        return self._player1, b

    @property
    def value(self):
        return self._state

    def __init__(self, state, player1: bool, bytes_conversion):
        self._state = state
        self._player1 = player1
        self._bytes_conversion = bytes_conversion


class Game(ABC):

    _player1s_turn: bool
    _player1_starts: bool

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
    def player1s_turn(self):
        return self._player1s_turn

    @property
    def player1_starts(self):
        return self._player1_starts

    @property
    @abstractmethod
    def completed(self) -> bool:
        pass

    # ================= METHODS =================

    def start(self):
        if 1 <= self.player_start_mode <= 2:
            self._player1s_turn = (self.player_start_mode == 1)
        else:
            self._player1s_turn = bool(random.getrandbits(1))
        self._player1_starts = self._player1s_turn

    @abstractmethod
    def get_state(self) -> (bool, bytes):
        pass

    @abstractmethod
    def clone(self):
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

    def __init__(self, player_start_mode: int):
        self.player_start_mode = player_start_mode

    def starting_player_won(self):
        if not self.completed:
            print("Winning player-evaluation was done even though game wasn't done yet!")
        # The starting player has won if they performed the last move.
        # Hence (p1_starts && !p1s_turn) || (!p1_starts && p1s_turn)
        # XOR for short: (p1_starts ^ p1s_turn)
        return self._player1_starts ^ self.player1s_turn
