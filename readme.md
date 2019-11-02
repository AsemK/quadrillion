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

# Software design

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

The classes on all class and sequence diagrams below are colored with the same color as their corresponding package.

## Model and controller

The diagram below shows the classes responsible for modelling and controlling the game. Quadrillion shapes and grids are represented by the `DotsSet` and `DotsGrid` classes respectively. These classes allow moving, flipping and rotating shapes and grids.

<p align="center">
  <img src="https://user-images.githubusercontent.com/37188590/153776813-0252fc08-1d20-49f0-a19d-6203da3658d6.png">
</p>

Shapes and grids (`DotsSet`s) are composed of _dots_. Each dot is represented by a `tuple` of two numbers (row, column) indicating its location on a matrix spanning the whole game board. So, the upper left dot is `(0, 0)` and the lower right is `(board_height – 1, board_width – 1)`. The position of a `DotsSet` is always the upper left dot in the matrix spanning it, even if this dot is not part of the `DotsSet` itself (see the figure below). This way, rotating and flipping a `DotsSet` preserves its position. A grid is different from a shape in the sense that it has _open_ dots over which shapes can be placed, and _closed_ dots which must remain empty. Each grid also has two sides, one black and one white. Closed dots have the opposite color of the side they are on and do not correspond to closed dots on the other side.

<p align="center">
  <img src="https://user-images.githubusercontent.com/37188590/154043793-a4cb1347-04df-46fa-8e3d-e143e3e24874.png">
</p>

The configuration (`config`) of a dots set is a `tuple` indicating its rotation, flip, and location. The current configuration of a `DotsSet` determines its state compared to the initial dots used during instantiation. Keeping the initial dots fixed, the configuration contains all needed information to get the current position of all dots in the set. This allow the configuration to act as a _momento_ that can be used to snapshot and retrieve the state of a dots set at any time.

`dots_set.py` also contains a factory class `DotsSetFactory` responsible for creating quadrillion shapes and grids as well as saving and loading them. In saving and loading, only configurations are involved.

While classes in `dots_set.py` model how quadrillion objects are manipulated, they know nothing about the rules of the game or its mechanics. This is the responsibility of the classes in `quadrillion.py`. The class `Quadrillion` allows the user to manipulate game’s items (grids and shapes) preventing violating game’s rules. This is achieved by a simple mechanism that has two key elements: `pick` and `release`. The user selects some items and calls the method `pick` with a list of these items. The `Quadrillion` class then checks if these items can be picked and raises an exception if it is not the case (for example if a grid is picked without picking also the shapes above it). If the call ended successfully, the user can manipulate these picked items by directly calling methods on their objects. After that, the user can call the `release` method in the `Quadrillion` class. This method will check that the current states of the picked items do not violate any of game’s rules (e.g. no two shapes can be over each other). If that is the case, the call will end successfully. Otherwise, an exception will be raised and the picked items will remain picked.

The user has also the choice to `unpick` the picked items. This will retrieve the state of the picked items using a snapshot of their configurations taken at the moment of picking (**momento design pattern**).

The Quadrillion class allows queries to get the visible item (if any) at any dot on the board. If a shape is over a board, then the shape is the visible item on all its dots. It also keeps a collection of different sets of items, like currently released shapes, currently released shapes outside grids (`released_unplaced_shapes`), released grids, … etc.

Almost all the functionality in the Quadrillion class is achieved by delegation to two strategy classes (**strategy pattern**), `ShapeQuadrillionStrategy` and `GridQuadrillionStrategy`. The common functionality of these strategy classes is kept in the base `QuadrillionStrategy` class. The sequence diagram below shows an example of how delegation is used in the pick and releases methods.

<p align="center">
  <img src="https://user-images.githubusercontent.com/37188590/153776817-6c352fd4-4753-4960-ad9c-82babdb68e0b.png">
</p>

The Quadrillion game can be thought as having three layers on top of each other’s, the ground layer, the grid layer and the shape layer. A grid can be on the ground but cannot be over any shape, and a shape can be either completely on ground or completely over open dots of grids. Because of this concept, when picking items, the `Quadrillion` class first tries to pick shapes in these items (by delegation to `ShapeQuadrillionStrategy`), and then tries to pick the grids, if there are unpicked shapes over the grids, the method will fail. Similarly, when releasing, the grids in the picked items are released first, then the shapes are released, if the shapes are not either completely over grids or on the ground, the release will fail.

## View

The relation between the quadrillion game controller and view follow the **observer pattern**.

<p align="center">
  <img src="https://user-images.githubusercontent.com/37188590/153776810-80653474-e0a7-4fbd-908d-5f5f12ab5078.png">
</p>

<p align="center">
  <img src="https://user-images.githubusercontent.com/37188590/153776816-300c3c9d-5154-470e-be16-942888bb3c3e.png">
</p>

## Solver

<p align="center">
  <img src="https://user-images.githubusercontent.com/37188590/153776809-e061b519-ca66-4e34-ad3c-9ad0923614ff.png">
</p>
