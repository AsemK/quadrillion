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
                self.picked = None
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


class QuadrillionStrategy:
    def __init__(self, dot_space_dim, colleagues):
        self._dot_space_dim = dot_space_dim
        self._colleagues = colleagues
        self._colleagues_dots = dict()

    def reset(self, other_strategy):
        self.other_strategy = other_strategy
        for colleague in self._colleagues:
            colleague.reset()
            released = self.release(colleague)
            assert released

    def release(self, colleague):
        released = self.is_releasable(colleague)
        if released:
            for dot in colleague.get():
                self._colleagues_dots[dot] = colleague
        return released

    def pick(self, colleague):
        picked = self.is_pickable(colleague)
        if picked:
            for dot in colleague.get():
                del self._colleagues_dots[dot]
        return picked

    def get_at(self, dot):
        if dot in self._colleagues_dots:
            return self._colleagues_dots[dot]
        return None

    def get_released_dots(self):
        return set(self._colleagues_dots.keys())

    def is_releasable(self, colleague):
        return self.is_on_board(colleague) and not self.is_overlapping_released_dots(colleague)

    def is_pickable(self, colleague):
        return True

    def is_on_board(self, item):
        return all(0 <= y < self._dot_space_dim[0] and 0 <= x < self._dot_space_dim[1] for (y, x) in item.get())

    def is_overlapping_released_dots(self, item):
        return any(dot in self.get_released_dots() for dot in item.get())


class GridQuadrillionStrategy(QuadrillionStrategy):
    def is_releasable(self, colleague):
        return QuadrillionStrategy.is_releasable(self, colleague)\
               and not self.other_strategy.is_overlapping_released_dots(colleague)

    def is_pickable(self, colleague):
        return not self.other_strategy.is_overlapping_released_dots(colleague)

    def is_on_valid(self, item):
        valid = self.get_released_valid_dots()
        return all(dot in valid for dot in item.get())

    def get_released_valid_dots(self):
        # TODO: make it for released dots only
        valid = self.get_released_dots()
        for grid in self._colleagues:
            valid -= grid.get_invalid()
        return valid


class ShapeQuadrillionStrategy(QuadrillionStrategy):
    def is_releasable(self, colleague):
        return QuadrillionStrategy.is_releasable(self, colleague)\
               and (self.other_strategy.is_on_valid(colleague)
                    or not self.other_strategy.is_overlapping_released_dots(colleague))

    def get_released_unplaced_shapes(self):
        # TODO: make it for released dots only
        unplaced = set(self._colleagues)
        for shape in unplaced:
            if self.other_strategy.is_overlapping_released_dots(shape):
                unplaced.remove(shape)
        return unplaced


if __name__ == '__main__':
    quadrillion = Quadrillion()
    view = QuadrillionGraphicDisplay(quadrillion)
