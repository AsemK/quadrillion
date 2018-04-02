from csp import CSP, CSPSolver
from graphic_display import QuadrillionGraphicDisplay
import util
import time

SHAPES = {'s<': {(0,0),(0,1),(1,0)},             's2': {(0,0),(0,1),(1,1),(1,2)},
          'sb': {(0,0),(0,1),(0,2),(1,0),(1,1)}, 'sU': {(0,0),(0,1),(0,2),(1,0),(1,2)},
          'sT': {(0,0),(0,1),(0,2),(1,1),(2,1)}, 'sC': {(0,0),(1,0),(2,0),(2,1),(2,2)},
          's/': {(0,0),(1,0),(1,1),(2,1),(2,2)}, 'sZ': {(0,0),(0,1),(1,1),(2,1),(2,2)},
          'sF': {(0,0),(0,1),(1,1),(1,2),(2,1)}, 'sL': {(0,0),(0,1),(0,2),(0,3),(1,0)},
          's1': {(0,0),(0,1),(0,2),(0,3),(1,1)}, 's9': {(0,0),(0,1),(0,2),(1,2),(1,3)}}
ALL_SHAPES = {shape: dict(util.unique_configs(pos_set)) for shape, pos_set in SHAPES.items()}

GRIDS = {'g1': [{(0,1)}, {(3,1)}],             'g2': [{(0,1),(0,2)}, {(0,3),(2,2)}],
         'g3': [{(0,0),(0,3)}, {(0,0),(2,0)}], 'g4': [{(0,0),(3,2)}, {(1,2),(3,3)}]}


class QuadrillionCSP(CSP):
    def __init__(self, possible_locs=[(i, j) for i in range(8) for j in range(8)],
                 board_dots={(0,7),(1,3),(1,5),(3,3),(5,0),(6,0),(7,6)},
                 shapes=list(SHAPES.keys())):
        self.board_dots = board_dots
        self.possible_locs = possible_locs
        self.shapes = shapes

    def get_variables(self):
        return self.shapes

    @staticmethod
    def get_possible_orients(shape):
        return list(ALL_SHAPES[shape].keys())

    @staticmethod
    def get_shape_at_config(shape, config):
        loc, orient = config
        return {(pos[0] + loc[0], pos[1] + loc[1]) for pos in ALL_SHAPES[shape][orient]}

    def is_valid_assignment(self, shape, config):
        return not config & self.board_dots and config <= set(self.possible_locs)\
               and util.is_connected(set(self.possible_locs) - self.board_dots - config)

    def get_domains(self):
        valid_configs = dict()
        for shape in self.get_variables():
            valid_configs[shape] = []
            for loc in self.possible_locs:
                for orient in self.get_possible_orients(shape):
                    config = self.get_shape_at_config(shape, (loc, orient))
                    if self.is_valid_assignment(shape, config):
                        valid_configs[shape].append(config)
        return valid_configs

    def set_current_assignments(self, assignments):
        self.current_board = self.board_dots.copy()
        for shape, config in assignments.items():
            self.current_board |= config

    def is_consistent_assignment(self, assignment):
        return not assignment[1] & self.current_board\
                and util.is_connected(set(self.possible_locs) - self.current_board - assignment[1])


class QuadrillionCompactCSP(QuadrillionCSP):
    def __init__(self, possible_locs=[(i, j) for i in range(8) for j in range(8)],
                 board_dots={(0, 7), (1, 3), (1, 5), (3, 3), (5, 0), (6, 0), (7, 6)},
                 shapes=list(SHAPES.keys())):
        QuadrillionCSP.__init__(self, possible_locs, board_dots, shapes)

    def is_valid_assignment(self, shape, config):
        return QuadrillionCSP.is_valid_assignment(self, shape, self.get_shape_at_config(shape, config))

    def get_domains(self):
        valid_configs = dict()
        for shape in self.get_variables():
            valid_configs[shape] = []
            for loc in self.possible_locs:
                for orient in self.get_possible_orients(shape):
                    if self.is_valid_assignment(shape, (loc, orient)):
                        valid_configs[shape].append((loc, orient))
        return valid_configs

    def set_current_assignments(self, assignments):
        QuadrillionCSP.set_current_assignments(self, self.convert_assignments(assignments))

    def is_consistent_assignment(self, assignment):
        return QuadrillionCSP.is_consistent_assignment(self, (assignment[0], self.get_shape_at_config(*assignment)))

    def convert_assignments(self, assignments):
        return dict([(shape, self.get_shape_at_config(shape, config))
                     for shape, config in assignments.items()])


class Quadrillion:
    def __init__(self,
                 initial_grids_configs={'g1': ((1, 4), 0, 0), 'g2': ((1, 8), 0, 0),
                                        'g3': ((5, 4), 0, 0), 'g4': ((5, 8), 0, 0)},
                 initial_assignment=dict()):
        # grid config is a tuple (loc, side, rotation)
        self.grids_configs = initial_grids_configs
        self.initial_assignments = initial_assignment

    @staticmethod
    def set_grid_loc(config, loc):
        return loc, config[1], config[2]

    @staticmethod
    def set_grid_side(config, side):
        return config[0], side%2, config[2]

    @staticmethod
    def set_grid_rotation(config, rotation):
        return config[0], config[1], rotation%4

    @staticmethod
    def calc_onboard_locs(grids_configs):
        onboard_locs = []
        for grid, config in grids_configs.items():
            onboard_locs += [(i, j) for i in range(config[0][0], config[0][0] + 4)
                              for j in range(config[0][1], config[0][1] + 4)]
        return onboard_locs

    @staticmethod
    def calc_possible_locs(grids_configs):
        height = max(config[0][0] for config in grids_configs.values()) + 4
        width = max(config[0][1] for config in grids_configs.values()) + 4
        return [(i, j) for i in range(height) for j in range(width)]

    def calc_board_dots(self, grids_configs, assignments):
        board_dots = set()
        for grid, config in grids_configs.items():
            board_dots |= self.get_grid_dots(grid, config)
        for shape, pos_set in assignments.items():
            board_dots |= pos_set
        board_dots |= set(self.calc_possible_locs(grids_configs))-set(self.calc_onboard_locs(grids_configs))
        return board_dots

    @staticmethod
    def get_grid_dots(grid, config):
        return {(pos[0] + config[0][0], pos[1] + config[0][1])
                for pos in util.rotated(GRIDS[grid][config[1]], config[2], 4, 4)}

    def move_grid(self, config, displacement):
        return self.set_grid_loc(config, (config[0][0]+displacement[0], config[0][1]+displacement[1]))

    def rotate_grid(self, config, rotation):
        return self.set_grid_rotation(config, config[2]+rotation)

    def flip_grid(self, config):
        return self.set_grid_side(config, config[1]+1)

    @staticmethod
    def rotate_shape(pos_set, rotation):
        return util.rotated(pos_set, rotation%4)

    @staticmethod
    def flip_shape(pos_set):
        return util.rotated(pos_set, 4)

    def get_initial_assignments(self):
        return self.initial_assignments

    def get_grids_configs(self):
        return self.grids_configs

    def get_search_time(self):
        return self.search_time

    def get_search_iterations(self):
        return self.search_iterations

    def get_solution(self, grids_configs, assignments):
        shapes = list(set(SHAPES.keys()) - set(assignments.keys()))
        quadrillion_csp = QuadrillionCSP(self.calc_possible_locs(grids_configs),
                                         self.calc_board_dots(grids_configs, assignments), shapes)
        start_time = time.process_time()
        solver = CSPSolver(quadrillion_csp)
        solution = solver.get_solution()
        self.search_time = time.process_time() - start_time
        self.search_iterations = solver.get_search_iterations()
        return solution

    @staticmethod
    def is_on_grid(cell, grids_configs):
        for grid, config in grids_configs.items():
            if (0 <= cell[0] - config[0][0] < 4) and (0 <= cell[1] - config[0][1] < 4):
                return grid
        return None

    @staticmethod
    def is_on_shape(cell, assignments):
        for shape, pos_set in assignments.items():
            if cell in pos_set:
                return shape
        return None

    @staticmethod
    def is_valid_grid_loc(grid, loc, grids_configs):
        for grid2, config in grids_configs.items():
            if grid2 == grid: continue
            if config[0][0] - 4 < loc[0] < config[0][0] + 4\
               and config[0][1] - 4 < loc[1] < config[0][1] + 4:
                return False
        return True

    def is_valid_shape_loc(self, shape, shape_dots, grids_configs, assignments):
        if shape in assignments:
            temp_assignment = assignments.copy()
            del temp_assignment[shape]
        else:
            temp_assignment = assignments
        if shape_dots <= set(self.calc_possible_locs(grids_configs)):
            if len(shape_dots & self.calc_board_dots(grids_configs, temp_assignment)) == 0:
                return True
        return False


if __name__ == '__main__':
    game = Quadrillion()
    display = QuadrillionGraphicDisplay(game)
