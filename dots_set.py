from collections import Set, namedtuple
Config = namedtuple('Config', ['flips', 'rotations', 'location'])


class DotsSet(Set):
    def __init__(self, dots,
                 initial_config=Config(flips=0, rotations=0, location=(0, 0))):
        if not self._are_valid_dots(dots):
            raise TypeError("dots must be of the form (int, int)")
        self._dots_set = frozenset(dots)
        self._initial_height=max(pos[0] for pos in self._dots_set) + 1
        self._initial_width=max(pos[1] for pos in self._dots_set) + 1

        self._config = Config(flips=0, rotations=0, location=(0, 0))
        self._initial_config = initial_config
        self.reset()

    def __iter__(self):
        return iter(self._dots_set)

    def __contains__(self, value):
        return value in self._dots_set

    def __len__(self):
        return len(self._dots_set)

    def __repr__(self):
        return type(self).__name__ + '({' + ", ".join({str(dot) for dot in self}) + '})'

    def flip(self):
        self.config = self.config._replace(flips=self.config.flips + 1)

    def rotate(self, clockwise):
        rotation_sign = self._get_current_clockwise_rotation_sign()
        clockwise_rotations = 1 if clockwise else -1
        self.config = self.config._replace(rotations=self.config.rotations + clockwise_rotations*rotation_sign)

    def move(self, displacement):
        dy, dx = displacement
        y, x = self.config.location
        self.config = self.config._replace(location=(y+dy, x+dx))

    def reset(self):
        self.config = self._initial_config

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, config):
        delta_flips = (config.flips - self.config.flips)
        delta_rotations = (config.rotations - self.config.rotations)
        displacement = (config.location[0] - self.config.location[0],
                        config.location[1] - self.config.location[1])

        self._flip(delta_flips)
        self._config = self._config._replace(flips=config.flips % 2)
        self._rotate(delta_rotations)
        self._config = self._config._replace(rotations=config.rotations % 4)
        self._move(displacement)
        self._config = self._config._replace(location=config.location)

    def _are_valid_dots(self, dots):
        return all(len(dot) == 2 and isinstance(dot, tuple)
                   and all(isinstance(axis, int) for axis in dot)
                   for dot in dots)

    def _flip(self, times):
        if times % 2:
            self._flip_vertically()

    def _rotate(self, times):
        # if clockwise_rotation is negative, the rotation will be counterclockwise because of the modulo
        clockwise_rotations = times * self._get_current_clockwise_rotation_sign()
        if clockwise_rotations % 4 == 1:
            self._rotate_90_degrees_clockwise()
        elif clockwise_rotations % 4 == 2:
            self._rotate_180_degrees()
        elif clockwise_rotations % 4 == 3:
            self._rotate_90_degrees_counterclockwise()

    def _move(self, displacement):
        dy, dx = displacement
        self._dots_set = frozenset({(y + dy, x + dx) for y, x in self._dots_set})

    def _flip_vertically(self):
        height, width = self._get_current_height_and_width()
        y0, x0 = self.config.location
        self._dots_set = frozenset({(y0 + height - 1 - (y - y0), x)
                                    for y, x in self._dots_set})

    def _rotate_90_degrees_clockwise(self):
        height, width = self._get_current_height_and_width()
        y0, x0 = self.config.location
        self._dots_set = frozenset({(y0 + x - x0, x0 + height - 1 - (y - y0))
                                    for y, x in self._dots_set})

    def _rotate_180_degrees(self):
        height, width = self._get_current_height_and_width()
        y0, x0 = self.config.location
        self._dots_set = frozenset({(y0 + height - 1 - (y - y0), x0 + width - 1 - (x - x0))
                                    for y, x in self._dots_set})

    def _rotate_90_degrees_counterclockwise(self):
        height, width = self._get_current_height_and_width()
        y0, x0 = self.config.location
        self._dots_set = frozenset({(y0 + width - 1 - (x - x0), x0 + y - y0)
                                    for y, x in self._dots_set})

    def _get_current_clockwise_rotation_sign(self):
        return 1 - 2*(self.config.flips % 2)  # 1 if shape is not flipped else -1

    def _get_current_height_and_width(self):
        if self.config.rotations % 2 == 1:
            return self._initial_width, self._initial_height
        else:
            return self._initial_height, self._initial_width
