import copy
import importlib
import random
from typing import Dict

import numpy as np
import argparse
import os

from tqdm import tqdm
import yaml

from game import Game
from games.games import Nim
from mcts import MonteCarloTreeSearch


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


def get_game_class(game_cfg):
    game_class = Nim  # default to Nim as game
    try:
        game_class = getattr(importlib.import_module("games.games"), cfg["game"]["type"])
    except AttributeError as e:
        print(f"Unable to make a game of type '{cfg['game']['type']}', did you spell it correctly?\n"
              f"Defaulting to 'Nim' as game!\n")
    return game_class


def start_game(game_cfg) -> Game:
    game_class = get_game_class(game_cfg)
    return Game.from_config(game_class, cfg["game"])


def run_game_batched(initial_game: Game, games: int, simulations: int, verbose=False):
    mcts = MonteCarloTreeSearch()

    win_count = 0

    for i in tqdm(range(games)):
        game = copy.deepcopy(initial_game)
        mcts.init_tree()  # NOTE: may be replaceable by creating a new instance of mcts

        while not game.completed:
            # NOTE: simulations can decay over time to speed up, that's why they're not part of constructor
            move = mcts.search(game, simulations)
            game.apply_move(move)
            if verbose:
                game.print_move(move)

        if game.starting_player_won():
            win_count += 1

    # TODO: Essential win statistics (for at least one of the two players) for a batch of games.
    #       When randomly assigned, this value is no good :P
    print(f"Starting player won {win_count} out of {games} games - {win_count * 100 / games}%)")

if __name__ == '__main__':

    args, cfg = parse_args_and_config()

    game = start_game(cfg["game"])
    run_game_batched(game, **cfg["mcts"], verbose=args.verbose)

    #
    # if args.verbose:
    #     print(f"\n[ Initial state ]============\n{game}\n=============================\n")
    # while not game.completed:
    #     moves = game.allowed_moves()
    #     move = random.choice(moves)  # TODO: AI
    #     game.apply_move(move)
    #     if args.verbose:
    #         game.print_move(move)
    #
    # print(f"Player {'1'if game.did_player1_win() else '2'} wins!")