from dot_set import DotShape, DotGrid
from graphic_display_new import QuadrillionGraphicDisplay

SHAPES = {'s<': ({(0,0),(0,1),(1,0)},             (0, 1, (12, 14)), '#91D8F7'),
          's2': ({(0,0),(0,1),(1,1),(1,2)},       (0, 0, (12, 8)),  '#B93A3F'),
          'sb': ({(0,0),(0,1),(0,2),(1,0),(1,1)}, (1, 0, (12, 11)), '#80CCC0'),
          'sU': ({(0,0),(0,1),(0,2),(1,0),(1,2)}, (0, 3, (10, 1)),  '#90C74B'),
          'sT': ({(0,0),(0,1),(0,2),(1,1),(2,1)}, (0, 1, (10, 6)),  '#009D6F'),
          'sC': ({(0,0),(1,0),(2,0),(2,1),(2,2)}, (0, 2, (10, 13)), '#00AFEE'),
          's/': ({(0,0),(1,0),(1,1),(2,1),(2,2)}, (0, 2, (10, 8)),  '#853B93'),
          'sZ': ({(0,0),(0,1),(1,1),(2,1),(2,2)}, (1, 1, (10, 11)), '#2A57A4'),
          'sF': ({(0,0),(0,1),(1,1),(1,2),(2,1)}, (0, 1, (10, 3)),  '#F79734'),
          'sL': ({(0,0),(0,1),(0,2),(0,3),(1,0)}, (0, 1, (10, 0)),  '#ED3338'),
          's1': ({(0,0),(0,1),(0,2),(0,3),(1,1)}, (0, 2, (12, 5)),  '#FFDD23'),
          's9': ({(0,0),(0,1),(0,2),(1,2),(1,3)}, (1, 0, (12, 2)),  '#F078AD')}

GRIDS = {'g1': (({(0,1)}, {(3,1)}),             (0, 0, (1, 4))),
         'g2': (({(0,1),(0,2)}, {(0,3),(2,2)}), (0, 0, (1, 8))),
         'g3': (({(0,0),(0,3)}, {(0,0),(2,0)}), (0, 0, (5, 4))),
         'g4': (({(0,0),(3,2)}, {(1,2),(3,3)}), (0, 0, (5, 8)))}

DOT_SPACE_DIM = (14, 16)


class Quadrillion:
    def __init__(self, dot_space_dim=DOT_SPACE_DIM, initial_configs=None):
        self.dot_space_dim = dot_space_dim
        self.shapes = dict()
        self.grids = dict()
        self.views = []
        if initial_configs is None: initial_configs = dict()

        for grid in GRIDS:
            if grid in initial_configs:
                config = initial_configs[grid]
            else:
                config = GRIDS[grid][1]
            self.grids[grid] = DotGrid(*GRIDS[grid][0], *config)

        for shape in SHAPES:
            if shape in initial_configs:
                config = initial_configs[shape]
            else:
                config = SHAPES[shape][1]
            self.shapes[shape] = DotShape(SHAPES[shape][0], *config, SHAPES[shape][2])

        self.reset()

    def reset(self):
        self.picked = None
        self.is_shape_picked = False
        self.grids_locs = dict()
        self.shapes_locs = dict()

        for grid_id, grid in self.grids.items():
            grid.reset()
            released = self._release_grid(grid_id)
            assert released
        for shape_id, shape in self.shapes.items():
            shape.reset()
            released = self._release_shape(shape_id)
            assert released

    def pick(self, loc):
        if loc in self.shapes_locs:
            self._pick_shape(self.shapes_locs[loc])
        elif loc in self.grids_locs:
            self._pick_grid(self.grids_locs[loc])
        if self.picked:
            return self.picked[1]
        return None

    def release(self):
        if self.picked:
            if self.is_shape_picked:
                released = self._release_shape(self.picked[0])
            else:
                released = self._release_grid(self.picked[0])
            if not released:
                self.picked[1].set_config(*self.picked[2])
            self.picked = None
            return released
        return False

    def is_won(self):
        return self._valid_grid_locs() == set(self.shapes_locs.keys())

    def is_on_board(self, dot_set):
        return all(0 <= y < self.dot_space_dim[0] and 0 <= x < self.dot_space_dim[1] for (y, x) in dot_set)

    def attach_view(self, view):
        self.views.append(view)

    def _valid_grid_locs(self):
        valid = set()
        for grid in self.grids.values():
            valid |= grid.get_valid()
        return valid

    def _release_grid(self, grid_id):
        released = self.is_on_board(self.grids[grid_id].get()) \
                   and not any(dot in self.grids_locs.keys() or dot in self.shapes_locs.keys()
                               for dot in self.grids[grid_id].get())
        if released:
            for dot in self.grids[grid_id].get():
                self.grids_locs[dot] = grid_id
        return released

    def _release_shape(self, shape_id):
        valid = self._valid_grid_locs()
        released = self.is_on_board(self.shapes[shape_id].get()) \
                   and all(dot in valid and dot not in self.shapes_locs.keys() for dot in self.shapes[shape_id].get())
        if not self.picked:
            released = released or not any(dot in self.grids_locs.keys() or dot in self.shapes_locs.keys()
                                           for dot in self.shapes[shape_id].get())
        if released:
            for dot in self.shapes[shape_id].get():
                self.shapes_locs[dot] = shape_id
        return released

    def _pick_shape(self, shape_id):
        self.picked = (shape_id, self.shapes[shape_id], self.shapes[shape_id].get_config())
        self.is_shape_picked = True
        for dot in self.shapes[shape_id].get():
            del self.shapes_locs[dot]

    def _pick_grid(self, grid_id):
        if not any(dot in self.shapes_locs.keys() for dot in self.grids[grid_id].get()):
            self.picked = (grid_id, self.grids[grid_id], self.grids[grid_id].get_config())
            self.is_shape_picked = False
            for dot in self.grids[grid_id].get():
                del self.grids_locs[dot]


if __name__ == '__main__':
    quadrillion = Quadrillion()
    view = QuadrillionGraphicDisplay(quadrillion)
    quadrillion.attach_view(view)
