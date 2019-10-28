# SmartGames Quadrillion IQ-puzzle game and solver

[Quadrillion](https://www.smartgamesandpuzzles.com/quadrillion.html) is an IQ puzzle game designed by SmartGames, Belgium. The game consists of four magnetic grids and twelve shapes. The player creates a board by sticking the grids together (in one of many possible configuration) and then solves the game by fitting all twelve shapes on the grids.

This python package allows the user to play the game and to solve it. The solution is based on the Constraint Satisfaction Problem (CSP) formulation. The package is implemented in pure python 3 without depending on any external library (except for tests which use pytest).

## Game Play

You can open the game by running the `main.py` file in your IDE or typing the following command in the parent directory containing quadrillion folder.

```
python quadrillion
```

A GUI will appear as shown below

<p align="center">
  <img src="https://user-images.githubusercontent.com/37188590/153775428-b3e06214-17e7-41d6-88d0-d579ea455f0b.png">
</p>

### Control:

- Pick a shape or grid: left click on it.
- Move the selected item: move the mouse or use the WASD keys.
- Rotate the selected item: right or left arrow (← or →) keys
- Flip the selected item: upward or downward (↓ or ↑) keys
- Release the selected item (only happens if the item is in a valid location): left click or the `Enter` key
- Unpick the item (return it to its state before picking it): right click or the `Esc` key
- Restart game: press the `Reset` button on the GUI or the `R` key
- Solve the game (assign all shapes a place on the grids): press the `Find Solution!` button on the GUI or the `F` key
- Help (put one shape in its correct place on the grids): press the `Help me!` button on the GUI or the `H` key
- Save the current board: press the `Save` button on the GUI
- Load the last saved board: press the `Load` button on the GUI

## Software design

The package diagram below gives an overview of the main modules in the quadrillion package. Each module takes care of a specific responsibility:

- `dots_set.py`: models game’s physical objects (grids and shapes).
- `quadrillion.py`: games’ controller
- `graphic_display.py`: all GUI stuff (view)

  **Note**: with the classes available in the above three modules, the user can play the game with no solver.

- `csp.py`: a CSP solver and an abstract CSP class that needs to be implemented by a domain-specific CSP for the solver to solve it.
- `quadrillion_csp.py`: adapts quadrillion to the abstract CSP provided in csp.py and uses the solver to solve the game.

<p align="center">
  <img src="https://user-images.githubusercontent.com/37188590/153776815-61af1099-a041-4065-8461-0c81e87fe0c8.png">
</p>
