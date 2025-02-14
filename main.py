import copy
import importlib
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
    _args = parser.parse_args()

    if not os.path.isfile(_args.config[0]):
        print(f"unable to open config file: \"{_args.config[0]}\"")
        _args.config[0] = "config\\default.yml"
    with open(_args.config[0]) as cfg_file:
        print("using config file: ", _args.config[0])
        config = yaml.load(cfg_file, Loader=yaml.FullLoader)
    return _args, config


def start_game(game_cfg) -> Game:
    game_class = Nim  # default to Nim as game
    try:
        game_class = getattr(importlib.import_module("games.games"), game_cfg["type"])
    except AttributeError:
        print(f"Unable to make a game of type '{game_cfg['type']}', did you spell it correctly?\n"
              f"Defaulting to 'Nim' as game!\n")
    return Game.from_config(game_class, game_cfg)


def run_game_batched(initial_game: Game, games: int, simulations: int, verbose=False):
    mcts = MonteCarloTreeSearch()
    # Various stats for the batch
    p1_starts = 0
    p2_starts = 0
    p1_wins = 0
    p2_wins = 0
    win_count = 0

    for i in tqdm(range(games)):
        if verbose:
            print("Starting game:", i)
        game = copy.deepcopy(initial_game)
        mcts.clear()
        game.start()  # Select starting player
        if game.player1_starts:
            p1_starts += 1
        else:
            p2_starts += 1

        while not game.completed:
            # NOTE: simulations can decay over time to speed up, that's why they're not part of constructor
            move = mcts.search(game, simulations)
            game.apply_move(move)
            if verbose:
                game.print_move(move)

        if game.starting_player_won():
            win_count += 1

        if game.player1s_turn:
            p2_wins += 1
        else:
            p1_wins += 1

    print(f"Player 1 started {p1_starts} out of {games} games - {p1_starts * 100 / games}%)")
    print(f"Player 2 started {p2_starts} out of {games} games - {p2_starts * 100 / games}%)")
    print(f"Starting player won {win_count} out of {games} games - {win_count * 100 / games}%)")
    print(f"Player 1 won {p1_wins} out of {games} games - {p1_wins * 100 / games}%)")
    print(f"Player 2 won {p2_wins} out of {games} games - {p2_wins * 100 / games}%)")


if __name__ == '__main__':
    args, cfg = parse_args_and_config()
    game_to_play = start_game(cfg["game"])
    run_game_batched(game_to_play, **cfg["mcts"], verbose=args.verbose)
