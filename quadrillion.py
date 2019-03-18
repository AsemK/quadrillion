from dot_set import DotShape, DotGrid
from graphic_display import QuadrillionGraphicDisplay

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


class QuadrillionStrategy:
    def __init__(self, dot_space_dim, colleagues):
        self._dot_space_dim = dot_space_dim
        self._colleagues = colleagues
        self._colleagues_dots = dict()

    def pick(self, colleague):
        picked = self.is_pickable(colleague)
        if picked:
            for dot in colleague.get():
                del self._colleagues_dots[dot]
        return picked

    def release(self, colleague):
        released = self.is_releasable(colleague)
        if released:
            for dot in colleague.get():
                self._colleagues_dots[dot] = colleague
        return released

    def reset(self, other_strategy):
        self.other_strategy = other_strategy
        for colleague in self._colleagues:
            colleague.reset()
            released = self.release(colleague)
            assert released

    def get_at(self, dot):
        if dot in self._colleagues_dots:
            return self._colleagues_dots[dot]
        return None

    def get_dots(self):
        return set(self._colleagues_dots.keys())

    def is_on_board(self, dot_set):
        return all(0 <= y < self._dot_space_dim[0] and 0 <= x < self._dot_space_dim[1] for (y, x) in dot_set.get())

    def is_overlapping(self, dot_set):
        return any(dot in self._colleagues_dots for dot in dot_set.get())

    def is_releasable(self, colleague):
        return False

    def is_pickable(self, colleague):
        return False


class GridQuadrillionStrategy(QuadrillionStrategy):
    def is_releasable(self, colleague):
        return self.is_on_board(colleague)\
               and not self.is_overlapping(colleague) and not self.other_strategy.is_overlapping(colleague)

    def is_pickable(self, colleague):
        return not self.other_strategy.is_overlapping(colleague)

    def is_on_valid(self, dot_set):
        valid = self.get_valid_dots()
        return all(dot in valid for dot in dot_set.get())

    def get_valid_dots(self):
        valid = self.get_dots()
        for grid in self._colleagues:
            valid -= grid.get_invalid()
        return valid


class ShapeQuadrillionStrategy(QuadrillionStrategy):
    def is_releasable(self, colleague):
        return self.is_on_board(colleague) and not self.is_overlapping(colleague)\
               and (self.other_strategy.is_on_valid(colleague) or not self.other_strategy.is_overlapping(colleague))

    def is_pickable(self, colleague):
        return True

    def get_unplaced(self):
        unplaced = set(self._colleagues)
        for shape in unplaced:
            if self.other_strategy.is_overlapping(shape):
                unplaced.remove(shape)
        return unplaced


class Quadrillion:
    def __init__(self, dot_space_dim=DOT_SPACE_DIM, initial_configs=None):
        self.dot_space_dim = dot_space_dim
        self.grids = set()
        self.shapes = set()
        self.views = []
        if initial_configs is None: initial_configs = dict()

        for grid in GRIDS:
            config = initial_configs[grid] if grid in initial_configs else GRIDS[grid][1]
            self.grids.add(DotGrid(*GRIDS[grid][0], *config))

        for shape in SHAPES:
            config = initial_configs[shape] if shape in initial_configs else SHAPES[shape][1]
            self.shapes.add(DotShape(SHAPES[shape][0], *config, SHAPES[shape][2]))

        self.grids = frozenset(self.grids)
        self.shapes = frozenset(self.shapes)
        self.reset()

    def reset(self):
        self.picked = None
        self.grid_strategy = GridQuadrillionStrategy(self.dot_space_dim, self.grids)
        self.shape_strategy = ShapeQuadrillionStrategy(self.dot_space_dim, self.shapes)
        self.grid_strategy.reset(self.shape_strategy)
        self.shape_strategy.reset(self.grid_strategy)
        self.notify()

    def pick_at(self, dot):
        if self.picked: return None
        for strategy in self.shape_strategy, self.grid_strategy:
            self.picked = strategy.get_at(dot)
            if self.picked:
                picked = strategy.pick(self.picked)
                if picked:
                    self.current_strategy = strategy
                    self.picked_momento = self.picked.get_config()
                    return self.picked
                break
        return None

    def unpick(self):
        if self.picked:
            self.picked.set_config(*self.picked_momento)
            self.current_strategy.release(self.picked)
            self.notify(self.picked)
            self.picked = None

    def release(self):
        if self.picked:
            released = self.current_strategy.release(self.picked)
            if not released:
                self.unpick()
            self.picked = None
            return released
        return False

    def attach_view(self, view):
        self.views.append(view)

    def notify(self, item=None):
        for view in self.views:
            view.update(item)

    def is_won(self):
        return len(self.get_empty_grid_dots()) == 0

    def get_grid_dots(self):
        return self.grid_strategy.get_dots()

    def get_empty_grid_dots(self):
        return self.grid_strategy.get_valid_dots() - self.shape_strategy.get_dots()

    def get_unplaced_shapes(self):
        return self.shape_strategy.get_unplaced()


if __name__ == '__main__':
    quadrillion = Quadrillion()
    view = QuadrillionGraphicDisplay(quadrillion)
