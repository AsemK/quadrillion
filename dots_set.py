from collections import Set, namedtuple
from quadrillion_data import GRIDS, SHAPES
Config = namedtuple('Config', ['flips', 'rotations', 'location'])


class DotsSet(Set):
    def __init__(self, dots, initial_config=Config(flips=0, rotations=0, location=(0, 0)), color='#FFFFFF'):
        if not self._are_valid_dots(dots):
            raise TypeError("dots must be of the form (int y, int x) where y >= 0 and x >= 0")
        self._dots_set = self._initial_dots_set = frozenset(dots)
        self._height = max(pos[0] for pos in self._dots_set) + 1
        self._width = max(pos[1] for pos in self._dots_set) + 1
        self._color = color

        self._config = Config(flips=0, rotations=0, location=(0, 0))
        self._initial_config = initial_config
        self.reset()

    @classmethod
    def _from_iterable(cls, iterable):
        """new sets created as a result of Set operations (like __and__) are just simple sets"""
        return frozenset(iterable)

    def __iter__(self):
        return iter(self._dots_set)

    def __contains__(self, value):
        return value in self._dots_set

    def __len__(self):
        return len(self._dots_set)

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return type(self).__name__ + '({' + ", ".join({str(dot) for dot in self}) + '})'

    @property
    def color(self):
        return self._color

    def reset(self):
        self.config = self._initial_config

    def flip(self):
        self.config = self.config._replace(flips=self.config.flips + 1, rotations=-self.config.rotations)

    def rotate(self, clockwise):
        clockwise_rotations = 1 if clockwise else -1
        self.config = self.config._replace(rotations=self.config.rotations + clockwise_rotations)

    def move(self, displacement):
        dy, dx = displacement
        y, x = self.config.location
        self.config = self.config._replace(location=(y+dy, x+dx))

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        self._config = config._replace(flips=config.flips % 2, rotations=config.rotations % 4)
        self._dots_set = frozenset(self._initial_dots_configured(self.config))

    def _are_valid_dots(self, dots):
        return all(len(dot) == 2 and isinstance(dot, tuple)
                   and all(isinstance(axis, int) and axis >= 0 for axis in dot)
                   for dot in dots)

    def _initial_dots_configured(self, config):
        flipped_dots = self._initial_dots_flipped(config.flips)
        rotated_dots = self._rotated_clockwise(flipped_dots, config.rotations)
        moved_dots = self._moved(rotated_dots, config.location)
        return moved_dots

    def _initial_dots_flipped(self, times):
        if times % 2:
            return self._flipped_vertically(self._initial_dots_set)
        else:
            return self._initial_dots_set

    def _rotated_clockwise(self, dots, times):
        if times % 4 == 0:
            return dots
        elif times % 4 == 1:
            return self._rotated_90_degrees_clockwise(dots)
        elif times % 4 == 2:
            return self._rotated_180_degrees(dots)
        elif times % 4 == 3:
            return self._rotated_90_degrees_counterclockwise(dots)

    def _moved(self, dots, displacement):
        dy, dx = displacement
        return {(y + dy, x + dx) for y, x in dots}

    def _flipped_vertically(self, dots):
        return {(self._height - 1 - y, x) for y, x in dots}

    def _rotated_90_degrees_clockwise(self, dots):
        return {(x, self._height - 1 - y) for y, x in dots}

    def _rotated_180_degrees(self, dots):
        return {(self._height - 1 - y, self._width - 1 - x) for y, x in dots}

    def _rotated_90_degrees_counterclockwise(self, dots):
        return {(self._width - 1 - x, y) for y, x in dots}


class TwoSidedDotsGrid(DotsSet):
    _white_side_color = '#FFFFFF'
    _black_side_color = '#373535'

    def __init__(self, invalid_black, invalid_white, height=4, width=4,
                 initial_config=Config(flips=0, rotations=0, location=(0, 0))):
        if not self._are_valid_dots(set(invalid_black) | set(invalid_white), height, width):
            raise TypeError("dots must be of the form (int y, int x) " 
                            "where 0 <= y < height and 0 <= x < width")

        self._height = height
        self._width = width

        self._initial_black_dots = frozenset(invalid_black)
        self._initial_white_dots = frozenset(invalid_white)

        self._config = Config(flips=0, rotations=0, location=(0, 0))
        self._initial_config = initial_config
        self.reset()

    @property
    def color(self):
        if self.config.flips:
            valid_color, invalid_color = self._black_side_color, self._white_side_color
        else:
            valid_color, invalid_color = self._white_side_color, self._black_side_color
        return valid_color, invalid_color

    @property
    def invalid_dots(self):
        return self._get_invalid_dots_at(self.config)

    def _are_valid_dots(self, dots, height, width):
        return super()._are_valid_dots(dots) and all(y < height and x < width for y, x in dots)

    def _initial_dots_configured(self, config):
        return self._get_valid_dots_at(config)

    def _get_valid_dots_at(self, config):
        return self._get_all_dots_at(config) - self._get_invalid_dots_at(config)

    def _get_all_dots_at(self, config):
        y0, x0 = config.location
        return {(y, x) for y in range(y0, y0 + self._height) for x in range(x0, x0 + self._width)}

    def _get_invalid_dots_at(self, config):
        return super()._initial_dots_configured(config)

    def _initial_dots_flipped(self, times):
        return self._initial_white_dots if times % 2 else self._initial_black_dots


class DotsSetFactory:
    def create_shapes(self):
        return frozenset(DotsSet(dots, Config(*config), color)
                         for dots, config, color in SHAPES.values())

    def create_grids(self):
        return frozenset(TwoSidedDotsGrid(invalid_black, invalid_wight, initial_config=Config(*config))
                         for (invalid_black, invalid_wight), config in GRIDS.values())
