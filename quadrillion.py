from csp import CSP, CSPSolver
from graphic_display import QuadrillionGraphicDisplay
import util
from util import DotSet
import time

SHAPES = {'s<': DotSet({(0,0),(0,1),(1,0)}),             's2': DotSet({(0,0),(0,1),(1,1),(1,2)}),
          'sb': DotSet({(0,0),(0,1),(0,2),(1,0),(1,1)}), 'sU': DotSet({(0,0),(0,1),(0,2),(1,0),(1,2)}),
          'sT': DotSet({(0,0),(0,1),(0,2),(1,1),(2,1)}), 'sC': DotSet({(0,0),(1,0),(2,0),(2,1),(2,2)}),
          's/': DotSet({(0,0),(1,0),(1,1),(2,1),(2,2)}), 'sZ': DotSet({(0,0),(0,1),(1,1),(2,1),(2,2)}),
          'sF': DotSet({(0,0),(0,1),(1,1),(1,2),(2,1)}), 'sL': DotSet({(0,0),(0,1),(0,2),(0,3),(1,0)}),
          's1': DotSet({(0,0),(0,1),(0,2),(0,3),(1,1)}), 's9': DotSet({(0,0),(0,1),(0,2),(1,2),(1,3)})}

GRIDS = {'g1': [{(0,1)}, {(3,1)}],             'g2': [{(0,1),(0,2)}, {(0,3),(2,2)}],
         'g3': [{(0,0),(0,3)}, {(0,0),(2,0)}], 'g4': [{(0,0),(3,2)}, {(1,2),(3,3)}]}


class QuadrillionCSP(CSP):
    def __init__(self, possible_locs=[(i, j) for i in range(8) for j in range(8)],
                 board_dots={(0,7),(1,3),(1,5),(3,3),(5,0),(6,0),(7,6)},
                 shapes=list(SHAPES.keys()), compact=False):
        self.board_dots = board_dots
        self.current_board = self.board_dots.copy()
        self.possible_locs = possible_locs
        self.shapes = shapes

        if compact:
            self.convert_assignment = lambda shape, config: SHAPES[shape].get_at_config(*config)
            self.get_assignment = lambda shape, config: config
        else:
            self.convert_assignment = lambda shape, config: config
            self.get_assignment = lambda shape, config: SHAPES[shape].get_at_config(*config)

    def get_variables(self):
        return self.shapes

    def is_valid_assignment(self, shape, assignment):
        return self.convert_assignment(shape, assignment) <= set(self.possible_locs) \
               and self.is_consistent_assignment((shape, assignment))

    def get_domains(self):
        domains = dict()
        for shape in self.get_variables():
            domains[shape] = []
            for loc in self.possible_locs:
                for flip, rot in list(SHAPES[shape].get_unique_orients().keys()):
                    assignment = self.get_assignment(shape, (loc, flip, rot))
                    if self.is_valid_assignment(shape, assignment):
                        domains[shape].append(assignment)
        return domains

    def set_current_assignments(self, assignments):
        assignments = self.convert_assignments(assignments)
        self.current_board = self.board_dots.copy()
        for shape, config in assignments.items():
            self.current_board |= config

    def is_consistent_assignment(self, assignment):
        assignment = (assignment[0], self.convert_assignment(*assignment))
        return not assignment[1] & self.current_board\
                and util.is_connected(set(self.possible_locs) - self.current_board - assignment[1])

    def convert_assignments(self, assignments):
        return dict([(shape, self.convert_assignment(shape, config))
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
                                         self.calc_board_dots(grids_configs, assignments),
                                         shapes)
        start_time = time.process_time()
        solver = CSPSolver(quadrillion_csp)
        solution = quadrillion_csp.convert_assignments(solver.get_solution())
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
