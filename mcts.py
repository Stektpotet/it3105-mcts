import copy
from typing import Dict, List

import numpy as np
import random

from game import Game

class Node:
    def __init__(self, player1: bool, allowed_moves: List):
        self._visits = 1  # upon creation, the node is being visited
        self._player1s_turn = player1
        # action utility
        self.actions = {
            a: [0, 0]  # initialize action values
            for a in allowed_moves
        }
        self.previous_move = None

    def update_values(self, player1_won):
        self._visits += 1
        self.actions[self.previous_move][0] += 1
        n, q = self.actions[self.previous_move]
        self.actions[self.previous_move][1] += (int(player1_won) - q) / n

    def set_last_action(self, action):
        self.previous_move = action

    def action_value(self, move, c):
        visits, q_value = self.actions[move]
        # UCT exploration bonus
        exploration_bonus = c * np.sqrt(np.log(self._visits) / (visits + 1))

        if self._player1s_turn:
            return q_value + exploration_bonus
        return q_value - exploration_bonus

    def __repr__(self):
        return f"Player {'1' if self._player1s_turn else '2'}:\n" \
               f"Visits: {self._visits},\n" \
               f"Visits: {self.actions},\n" \
               f"Previous: {self.previous_move}"

class SearchTree:
    # _state_lookup: Dict[(bool, bytes), Node]

    def __init__(self, c=1):
        self._state_lookup = {}
        self.c = c

    def clear(self) -> None:
        self._state_lookup.clear()

    def current_state_node(self, game: Game):
        state_key = game.get_state()
        node = self._state_lookup.get(state_key)
        if node is not None:
            return node

        self._state_lookup[state_key] = Node(state_key[0], game.allowed_moves())
        return None  # This was a leaf node, notify the traversal

    @staticmethod
    def rollout_policy(game: Game):
        return random.choice(game.allowed_moves())

    def tree_policy(self, game: Game, c):
        node = self.current_state_node(game)
        all_actions = list(node.actions.keys())
        action_values = np.array([node.action_value(a, c) for a in all_actions])

        if game.player1s_turn:
            action_index = np.argmax(action_values)
        else:
            action_index = np.argmin(action_values)

        return all_actions[action_index]

    #TODO: def greedy: i.e. tree_policy where c = 0

    def backup(self, nodes, result):
        for node in nodes:
            node.update_values(result)


class MonteCarloTreeSearch:
    def __init__(self, c=1):
        self.tree = SearchTree()
        self.c = c

    def init_tree(self):
        self.tree.clear()

    def search(self, game: Game, simulations: int):
        for i in range(simulations):
            self.simulate(game)
        return self.tree.tree_policy(game, 0)  # find greedy best action

    def simulate(self, base_game: Game):
        game = copy.deepcopy(base_game)
        traversed_nodes = self.sim_tree(game)
        player1_won = self.rollout(game)  # rollout
        self.tree.backup(traversed_nodes, player1_won)

    # Traverse tree
    def sim_tree(self, game: Game):
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

    def rollout(self, game: Game):
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