## Peg Solitaire RL

Run by:
`python main.py`

Command-line options
```
-v,     --verbose      FLAG: activates verbose logging during training
    usage:
    > python main.py -v
    
-cfg    --config        ARG:  load a specified config file.
    usage:
    > python main.py -cfg=config/some_config.yml
```

#### Config file

The config yaml-file controls all the hyper-parameters, there are 2 groups:

`mcts` - controls the parameters of the mcts
​	Within you'll find:
​	`simulations: <integer>` - the number of simulations/rollouts the mcts will perform to find optimal solutions (_M_)
​	`games: <integer>` - number of games that will be played in the batch (_G_)

`game` - controls the game mcts will be applied on
​	Within you'll find:
​		`type: <"Nim"|"Ledge">` - the game to play - if badly specified, defaults to "Nim"
​		`player_start_mode: <1|2|3>` - the player that starts, 3 causes random selection for each game of the batch

​	If `type` is `"Nim"`:
​		`stones: <integer>` - the number of stones/pieces to be played with
​		`max_move: <integer>` - the maximum number of stones/pieces a player can take in one turn (given that
​						   `max_move` pieces still are available)

​	if `type` is `"Ledge"`:
​		`initial_board: <list of [0|1|2] | object>` - may either describe the initial configuration directly as a list, or
​											     specify an object consisting of:
​			`length: <integer>` - the board's length
​			`copper_coins: <integer in range(0, length-1)>` - number of slots in the board that are copper pieces
​													   (1 will always be gold)
​				With the latter option, when defining the initial board as an object, the configuration of coins on the
​				board will be random.