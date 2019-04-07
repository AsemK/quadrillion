from dot_set import DotShape, DotGrid
from graphic_display import QuadrillionGraphicDisplay
from quadrillion_data import GRIDS, SHAPES, DOT_SPACE_DIM


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
        self.is_picked = False
        self.grid_strategy = GridQuadrillionStrategy(self.dot_space_dim, self.grids)
        self.shape_strategy = ShapeQuadrillionStrategy(self.dot_space_dim, self.shapes)
        self.grid_strategy.reset(self.shape_strategy)
        self.shape_strategy.reset(self.grid_strategy)
        self.notify()

    def pick(self, items):
        if not self.is_picked:
            shapes, grids = self._separate_shapes_grids(items)
            if self.shape_strategy.pick(shapes) and self.grid_strategy.pick(grids):
                self.is_picked = True
            else:
                self.unpick()
        return self.is_picked

    def unpick(self):
        self.grid_strategy.unpick()
        self.shape_strategy.unpick()
        self.is_picked = False
        self.notify()

    def release(self):
        if self.is_picked:
            if self.grid_strategy.is_release_possible() and self.shape_strategy.is_release_possible():
                self.grid_strategy.release()
                self.shape_strategy.release()
                self.is_picked = False
                self.notify()
        return not self.is_picked

    def get_at(self, dot):
        for strategy in self.shape_strategy, self.grid_strategy:
            item = strategy.get_at(dot)
            if item:
                return item
        return None

    def attach_view(self, view):
        self.views.append(view)

    def notify(self, item=None):
        for view in self.views:
            view.update(item)

    def is_won(self):
        return len(self.get_released_empty_grid_dots()) == 0

    def get_released_grid_dots(self):
        return self.grid_strategy.get_released_dots()

    def get_released_empty_grid_dots(self):
        return self.grid_strategy.get_released_valid_dots() - self.shape_strategy.get_released_dots()

    def get_released_unplaced_shapes(self):
        return self.shape_strategy.get_released_unplaced_shapes()

    def _separate_shapes_grids(self, items):
        items = set(items)
        shapes = self.shapes & items
        grids = self.grids & items
        return shapes, grids


class QuadrillionStrategy:
    def __init__(self, dot_space_dim, colleagues):
        self._dot_space_dim = dot_space_dim
        self._colleagues = colleagues
        self._colleagues_dots = dict()
        self._other_strategy = None
        self._picked = set(colleagues)
        self._picked_momento = dict()

    def reset(self, other_strategy):
        self._other_strategy = other_strategy
        if self.is_release_possible():
            self.release()
        # TODO: Add InitialState exception here

    def release(self):
        for colleague in self._picked:
            for dot in colleague.get():
                self._colleagues_dots[dot] = colleague
        self._picked = set()
        self._picked_momento = dict()

    def pick(self, colleagues):
        picked = self.are_pickable(colleagues)
        if picked:
            self._picked = colleagues
            for colleague in colleagues:
                self._picked_momento[colleague] = colleague.get_config()
                for dot in colleague.get():
                    del self._colleagues_dots[dot]
        return picked

    def unpick(self):
        for colleague, momento in self._picked_momento.items():
            colleague.set_config(*momento)
        self.release()

    def get_at(self, dot):
        if dot in self._colleagues_dots:
            return self._colleagues_dots[dot]
        return None

    def get_released_dots(self):
        return set(self._colleagues_dots.keys())

    def is_release_possible(self):
        return all(self.is_on_board(colleague) and not self.is_overlapping_released_dots(colleague)
                   for colleague in self._picked) and self._are_separated(self._picked)

    def are_pickable(self, colleagues):
        return True

    def is_on_board(self, item):
        return all(0 <= y < self._dot_space_dim[0] and 0 <= x < self._dot_space_dim[1] for (y, x) in item.get())

    def is_overlapping_released_dots(self, item):
        return any(dot in self.get_released_dots() for dot in item.get())

    def _get_all_dots_list(self, items):
        dots_list = []
        for item in items:
            dots_list.extend(item.get())
        return dots_list

    def _are_separated(self, items):
        dots_list = self._get_all_dots_list(items)
        return len(dots_list) == len(set(dots_list))


class GridQuadrillionStrategy(QuadrillionStrategy):
    def is_release_possible(self):
        return QuadrillionStrategy.is_release_possible(self)\
               and not any(self._other_strategy.is_overlapping_released_dots(grid) for grid in self._picked)

    def are_pickable(self, grids):
        return QuadrillionStrategy.are_pickable(self, grids)\
               and not any(self._other_strategy.is_overlapping_released_dots(grid) for grid in grids)

    def is_on_all_valid(self, item):
        valid = self._get_valid_dots(self._colleagues)
        return all(dot in valid for dot in item.get())

    def is_overlapping_all_dots(self, item):
        all_dots = self._get_all_dots_list(self._colleagues)
        return any(dot in set(all_dots) for dot in item.get())

    def get_released_valid_dots(self):
        return self._get_valid_dots(self._colleagues - self._picked)

    def _get_valid_dots(self, grids):
        valid = set()
        for grid in grids:
            valid |= grid.get_valid()
        return valid


class ShapeQuadrillionStrategy(QuadrillionStrategy):
    def is_release_possible(self):
        return QuadrillionStrategy.is_release_possible(self)\
               and all(self._other_strategy.is_on_all_valid(shape)
                       or not self._other_strategy.is_overlapping_all_dots(shape) for shape in self._picked)

    def get_released_unplaced_shapes(self):
        unplaced = set(self._colleagues) - self._picked
        for shape in unplaced:
            if self._other_strategy.is_overlapping_released_dots(shape):
                unplaced.remove(shape)
        return unplaced


if __name__ == '__main__':
    quadrillion = Quadrillion()
    view = QuadrillionGraphicDisplay(quadrillion)
