from dots_set import DotsSetFactory
from quadrillion_data import DOT_SPACE_DIM
from quadrillion_exception import *


class Quadrillion:
    def __init__(self, dot_space_dim=DOT_SPACE_DIM, dots_sets_factory=None):
        self.dot_space_dim = dot_space_dim
        self.dots_sets_factory = dots_sets_factory if dots_sets_factory else DotsSetFactory()
        self._views = []
        self.reset()

    def reset(self):
        """
        returns the game to its initial state.
        """
        self.grids = self.dots_sets_factory.grids
        self.shapes = self.dots_sets_factory.shapes
        self._grid_strategy = GridQuadrillionStrategy(self.dot_space_dim, self.grids)
        self._shape_strategy = ShapeQuadrillionStrategy(self.dot_space_dim, self.shapes)
        self._grid_strategy.reset(self._shape_strategy)
        self._shape_strategy.reset(self._grid_strategy)
        self._is_picked = False
        self._picked_items_momentos = []
        self._notify()

    def pick(self, items):
        """
        Must be called before any item can be moved to check if it is allowed to move it.
        :param items: an iterable of dots_sets
        """
        if not self._is_picked:
            try:
                shapes, grids = self._separate_shapes_grids(items)
                self._shape_strategy.pick(shapes)
                self._grid_strategy.pick(grids)
                self._capture_items_momentos(items)
                self._is_picked = True
            except IllegalPickException:
                self._shape_strategy.release()
                raise
        else:
            raise StateException('Cannot pick before releasing already picked items!')

    def release(self):
        """
        Must be called after picked items are moved to their desired position.
        """
        if self._is_picked:
            picked_grids = self._grid_strategy.picked_items
            try:
                self._grid_strategy.release()
                self._shape_strategy.release()
                self._is_picked = False
                self._notify()
            except IllegalReleaseException:
                self._grid_strategy.pick(picked_grids)
                raise
        else:
            raise StateException('Cannot release while no picked items!')

    def unpick(self):
        """
        Can be called after some items are picked to return them to their position before picking them.
        """
        if self._is_picked:
            try:
                self._restore_items_momentos()
                self.release()
            except IllegalReleaseException:
                raise QuadrillionException('Software Error: momentos were not'
                                           ' captured at legal configurations')
        else:
            raise StateException('Cannot unpick while no picked items!')

    def get_at(self, dot):
        """
        :returns the visible dots_set at the input dot in quadrillion board.
        """
        for strategy in self._shape_strategy, self._grid_strategy:
            item = strategy.get_at(dot)
            if item:
                return item
        raise NoItemException('There is no item at dot {}'.format(dot))

    def is_won(self):
        return not self._is_picked and len(self.released_empty_grids_dots) == 0

    def subscribe(self, view):
        self._views.append(view)

    def save_game(self, file_name='last_saved'):
        self.dots_sets_factory.save_configs(file_name)

    def load_game(self, file_name='last_saved'):
        try:
            self.dots_sets_factory.load_config(file_name)
            self.reset()
        except FileNotFoundError:
            raise QuadrillionException('Cannot find file %s' % file_name)

    @property
    def is_picked(self):  # are there picked items in the game
        return self._is_picked

    @property
    def released_grids(self):
        return self._grid_strategy.released_items

    @property
    def released_empty_grids_dots(self):
        return self._grid_strategy.released_open_dots - self._shape_strategy.released_dots

    @property
    def released_shapes(self):
        return self._shape_strategy.released_items

    @property
    def released_unplaced_shapes(self):
        return self._shape_strategy.released_unplaced_shapes  # released shapes outside grids

    def _notify(self):
        for view in self._views:
            view.update()

    def _separate_shapes_grids(self, items):
        items = set(items)
        shapes = self.shapes & items
        grids = self.grids & items
        return shapes, grids

    def _capture_items_momentos(self, items):
        self._picked_items_momentos = [(item, item.config) for item in items]

    def _restore_items_momentos(self):
        for item, config in self._picked_items_momentos:
            item.config = config


class QuadrillionStrategy:
    def __init__(self, dot_space_dim, items):
        self._dot_space_dim = dot_space_dim
        self._items = items
        self._other_strategy = None
        self._picked = set(self._items)

    def reset(self, other_strategy):
        self._other_strategy = other_strategy
        for item in self._items:
            item.reset()
        try:
            self.release()
        except IllegalReleaseException:
            raise InitialConfigurationsException('Initial configuration of items are not legal!')

    def release(self):
        if self.is_release_possible():
            self._picked = set()
        else:
            raise IllegalReleaseException('It is not possible to release the picked'
                                          ' items with their current configuration!')

    def pick(self, items):
        if self.are_pickable(items):
            self._picked = set(items)
        else:
            raise IllegalPickException('It is not possible to pick the selected items!')

    def get_at(self, dot):
        for item in self.released_items:
            if dot in item:
                return item
        return None

    def is_release_possible(self):
        return all(self.is_on_board(item) and not self.is_overlapping_released_items(item)
                   for item in self.picked_items) and self._are_separated(self.picked_items)

    def are_pickable(self, items):
        return True

    def is_on_board(self, item):
        return all(0 <= y < self._dot_space_dim[0] and 0 <= x < self._dot_space_dim[1] for (y, x) in item)

    def is_overlapping_released_items(self, item):
        return any(any(dot in other_item for other_item in self.released_items) for dot in item)

    def _get_all_dots_list(self, items):
        return [dot for item in items for dot in item]

    def _are_separated(self, items):
        dots_list = self._get_all_dots_list(items)
        return len(dots_list) == len(set(dots_list))

    @property
    def picked_items(self):
        return self._picked

    @property
    def released_items(self):
        return self._items - self._picked

    @property
    def released_dots(self):
        return set(self._get_all_dots_list(self.released_items))


class GridQuadrillionStrategy(QuadrillionStrategy):
    def is_release_possible(self):
        return QuadrillionStrategy.is_release_possible(self)\
               and not any(self._other_strategy.is_overlapping_released_items(grid) for grid in self.picked_items)

    def are_pickable(self, grids):
        return set(grids) <= self.picked_items\
               or not any(self._other_strategy.is_overlapping_released_items(grid) for grid in grids)

    def is_on_released_open_dots(self, item):
        return all(dot in self.released_open_dots for dot in item)

    @property
    def released_open_dots(self):
        return {dot for grid in self.released_items for dot in grid.open_dots}


class ShapeQuadrillionStrategy(QuadrillionStrategy):
    def is_release_possible(self):
        return QuadrillionStrategy.is_release_possible(self)\
               and all(self._other_strategy.is_on_released_open_dots(shape)
                       or not self._other_strategy.is_overlapping_released_items(shape)
                       for shape in self.picked_items)

    @property
    def released_unplaced_shapes(self):
        return {shape for shape in self.released_items
                if not self._other_strategy.is_overlapping_released_items(shape)}
