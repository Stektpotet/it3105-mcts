import importlib
import random

import numpy as np
import argparse
import os

import yaml

from game import Game
from games.games import Nim

def parse_args_and_config():
    """
    :return: arguments, configuration dictionary
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", default=False, nargs='?', const=True)
    parser.add_argument("-cfg", "--config", type=str, default=["config\\default.yml"], nargs=1)
    args = parser.parse_args()

    if not os.path.isfile(args.config[0]):
        print(f"unable to open config file: \"{args.config[0]}\"")
        args.config[0] = "config\\default.yml"
    with open(args.config[0]) as cfg_file:
        print("using config file: ", args.config[0])
        config = yaml.load(cfg_file, Loader=yaml.FullLoader)
    return args, config


if __name__ == '__main__':
    game: Game

    args, cfg = parse_args_and_config()

    game_class = Nim

    try:
        game_class = getattr(importlib.import_module("games.games"), cfg["game"]["type"])
    except AttributeError as e:
        print(f"Unable to make a game of type '{cfg['game']['type']}', did you spell it correctly?\n"
              f"Defaulting to 'Nim' as game!\n")

    print(f"Playing Game: {game_class.__name__}")

    game = Game.from_config(game_class, cfg["game"])

    if args.verbose:
        print(f"\n[ Initial state ]============\n{game}\n=============================\n")
    while not game.completed:
        moves = game.allowed_moves()
        move = random.choice(moves)  # TODO: AI
        game.apply_move(move)
        if args.verbose:
            game.print_move(move)

    print(f"Player {'1'if game.did_player1_win() else '2'} wins!")