class DotSet:
    def __init__(self, dots, flp=0, rot=0, loc=(0, 0), color='#FFFFFF'):
        for dot in dots:
            assert type(dot) is tuple and len(dot) == 2
        assert min(pos[0] for pos in dots) == 0
        assert min(pos[1] for pos in dots) == 0

        self.height = max(pos[0] for pos in dots) + 1
        self.width = max(pos[1] for pos in dots) + 1
        self.color = color

        self.initial_dot_set = set(dots)
        self.initial_config = (flp, rot, loc)
        self.reset()

    def flip(self):
        self.flp = (self.flp + 1) % 2
        self.rot = -self.rot

    def rotate(self, rot=1):
        self.rot = (self.rot + rot) % 4

    def move(self, displacement):
        self.loc = (self.loc[0] + displacement[0], self.loc[1] + displacement[1])

    def get_color(self):
        return self.color

    def set_config(self, flp, rot, loc):
        self.flp = flp
        self.rot = rot
        self.loc = loc

    def get_config(self):
        return self.flp, self.rot, self.loc

    def get(self):
        return self._get_at_config(*self.get_config())

    def is_on(self, loc):
        return loc in self.get()

    def reset(self):
        self.set_config(*self.initial_config)

    def _get_at_config(self, flp, rot, loc=(0, 0)):
        return self._moved(self._rotated(self._flipped(flp), rot), loc)

    def _get_dims_at_config(self, flp, rot, loc):
        return (self.width, self.height) if rot % 2 else (self.height, self.width)

    def _flipped(self, flp):
        if flp % 2 == 0:
            return self.initial_dot_set
        return {(self.height - 1 - dot[0], dot[1]) for dot in self.initial_dot_set}

    def _rotated(self, dot_set, rot):
        if rot % 4 == 0:
            return dot_set
        if rot % 4 == 1:
            return {(self.width - 1 - pos[1], pos[0]) for pos in dot_set}
        elif rot % 4 == 2:
            return {(self.height - 1 - pos[0], self.width - 1 - pos[1]) for pos in dot_set}
        elif rot % 4 == 3:
            return {(pos[1], self.height - 1 - pos[0]) for pos in dot_set}

    def _moved(self, dot_set, displacement):
        return {(dot[0] + displacement[0], dot[1] + displacement[1]) for dot in dot_set}

    def __str__(self):
        dot_set = self._get_at_config(self.flp, self.rot)
        height, width = self._get_dims_at_config(*self.get_config())
        out = ''
        for h in range(height):
            out += '\n'
            for w in range(width):
                if (h, w) in dot_set:
                    out += u'\u26AB' + ' '
                else:
                    out += u'\u26AA' + ' '
        return out


class DotShape(DotSet):
    def get_unique_orients(self):
        orients = []
        shapes = []
        for flp in [0, 1]:
            for rot in range(0, 4):
                config_shape = self._get_at_config(flp, rot)
                if all(shape != config_shape for shape in shapes):
                    orients.append((flp, rot))
                    shapes.append(config_shape)
        return dict(zip(orients, shapes))

    def _dot_set_to_config(self, dot_set):
        loc1 = min(pos[0] for pos in dot_set)
        loc2 = min(pos[1] for pos in dot_set)
        origin_dot_set = {(h-loc1, w-loc2) for (h, w) in dot_set}
        for orient, shape in self.get_unique_orients().items():
            if shape == origin_dot_set:
                return orient[0], orient[1], (loc1, loc2)
        return None


class DotGrid(DotSet):
    white_side_color = '#FFFFFF'
    black_side_color = '#373535'

    def __init__(self, invalid_black, invalid_white, flp=0, rot=0, loc=(0, 0), height=4, width=4):
        for dot in invalid_black | invalid_white:
            assert (type(dot) is tuple and len(dot) == 2)
            assert (dot[0] < height) and (dot[1] < width)

        self.height = height
        self.width = width

        self.initial_black_dots = set(invalid_black)
        self.initial_white_dots = set(invalid_white)

        self.initial_config = (flp, rot, loc)
        self.reset()

    def get_color(self):
        if self.flp:
            valid_color, invalid_color = self.black_side_color, self.white_side_color
        else:
            valid_color, invalid_color = self.white_side_color, self.black_side_color
        return valid_color, invalid_color

    def get(self):
        return self._get_all_at_config(*self.get_config())

    def get_invalid(self):
        return self._get_at_config(*self.get_config())

    def get_valid(self):
        return self._get_valid_at_config(*self.get_config())

    def is_on(self, loc):
        return (0 <= loc[0] - self.loc[0] < self.height) \
               and (0 <= loc[1] - self.loc[1] < self.width)

    def _flipped(self, flp):
        if flp % 2 == 0:
            return self.initial_black_dots.copy()
        return self.initial_white_dots.copy()

    def _get_all_at_config(self, flp, rot, loc=(0, 0)):
        height, width = self._get_dims_at_config(*self.get_config())
        return {(i, j) for i in range(loc[0], loc[0] + height)
                for j in range(loc[1], loc[1] + width)}

    def _get_valid_at_config(self, flp, rot, loc=(0, 0)):
        return self._get_all_at_config(flp, rot, loc) - self._get_at_config(flp, rot, loc)
