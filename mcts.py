import math
from typing import List
import random

from game import Game

class SearchTree:
    class Node:

        @property
        def action_keys(self) -> List:
            return list(self._actions.keys())

        def __init__(self, player1: bool, allowed_moves: List):
            self._visits = 1  # upon creation, the node is being visited
            self._player1s_turn = player1
            # action utility
            self._actions = {
                action: [0, 0]  # initialize action values
                for action in allowed_moves
            }
            self._previous_move = None

        def update_values(self, player1_won: int):
            self._visits += 1
            self._actions[self._previous_move][0] += 1
            n, q = self._actions[self._previous_move]
            self._actions[self._previous_move][1] += (player1_won - q) / n

        def set_last_action(self, action) -> None:
            self._previous_move = action

        def action_value(self, action, c: float) -> float:
            visits, q_value = self._actions[action]

            # UCT exploration bonus
            exploration_bonus = c * math.sqrt(math.log(self._visits) / (visits + 1))

            if self._player1s_turn:
                return q_value + exploration_bonus
            return q_value - exploration_bonus

    def __init__(self, c=1):
        self._state_lookup = {}
        self.c = c

    def clear(self) -> None:
        self._state_lookup.clear()

    def current_state_node(self, game: Game):
        state_key = game.get_state()
        if state_key in self._state_lookup:
            return self._state_lookup[state_key]

        self._state_lookup[state_key] = self.Node(state_key[0], game.allowed_moves())
        return None  # This was a leaf node, notify the traversal

    @staticmethod
    def rollout_policy(game: Game):
        return random.choice(game.allowed_moves())

    def tree_policy(self, game: Game, c: float):
        node = self.current_state_node(game)
        all_actions = node.action_keys

        index = 0
        if game.player1s_turn:  # argmax
            highest = -math.inf
            for i, action in enumerate(all_actions):
                a = node.action_value(action, c)
                if a > highest:
                    highest = a
                    index = i
        else:  # argmin
            index = 0
            lowest = math.inf
            for i, action in enumerate(all_actions):
                a = node.action_value(action, c)
                if a < lowest:
                    lowest = a
                    index = i

        return all_actions[index]

    @staticmethod
    def backprop(path: List, result: int) -> None:
        for node in path:
            node.update_values(result)


class MonteCarloTreeSearch:
    def __init__(self, c: float = 1):
        self.tree = SearchTree()
        # self.c_init = c
        self.c = c

    def clear(self) -> None:
        self.tree.clear()
        # self.c = self.c_init

    def search(self, game: Game, simulations: int):
        # Perform a series of simulations to find the best action to perform
        # (by updating the policy throughout all the simulations)
        sim_games = [game.clone() for _ in range(simulations)]
        for g in sim_games:
            self._simulate(g)
        # Apply the policy onto the game in a greedy/exploitive manner
        return self.tree.tree_policy(game, 0)

    def _simulate(self, game: Game) -> None:
        # game = base_game.clone()  # Make a copy of the game to perform simulations on

        # 1 From the root state (R) use the tree policy to choose the next pre-existing child node.
        traversed_nodes = self._traverse_tree(game)

        # Perform a rollout from a leaf node
        player1_won = self._rollout(game)  # rollout

        # 4 Propagate information about F (such as the winner), along
        # the entire path from F back to S and then back to R. That
        # info updates node statistics that influence the tree policy
        self.tree.backprop(traversed_nodes, player1_won)

    # Traverse tree

    def _traverse_tree(self, game: Game) -> List:
        path = []  # list of nodes traversed
        while not game.completed:
            current_node = self.tree.current_state_node(game)
            if current_node is None:  # Leaf node found
                return path
            path.append(current_node)
            action = self.tree.tree_policy(game, self.c)  # find next action
            current_node.set_last_action(action)
            game.apply_move(action)
        return path

    def _rollout(self, game: Game) -> int:
        while not game.completed:
            move = self.tree.rollout_policy(game)
            game.apply_move(move)
        return not game.player1s_turn  # player 1 performed the last move

# https://www.idi.ntnu.no/emner/it3105/lectures/neural/mcts.pdf
# 1 From the root state (R) use the tree policy to choose the
# next pre-existing child node.

# 2 When a leaf node (not necessarily a final state) is reached,
# apply domain-dependent operators to produce successor
# (child) states.

# 3 Pick one of the new successors (S) as a starting point and
# use the default policy to perform a single-track rollout
# simulation from S to a final state (F).

# 4 Propagate information about F (such as the winner), along
# the entire path from F back to S and then back to R. That
# info updates node statistics that influence the tree policy
