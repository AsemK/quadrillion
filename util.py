def transposed(pos_set):
    return {(pos[1], pos[0]) for pos in pos_set}


def rotated(pos_set, rotation, height=0, width=0):
    new_set = pos_set.copy()
    if rotation % 8 == 0:
        return new_set

    if not (height or width):
        offset_v = min(pos[0] for pos in pos_set)
        offset_h = min(pos[1] for pos in pos_set)
        new_set = {(pos[0] - offset_v, pos[1] - offset_h) for pos in new_set}
        height = max(pos[0] for pos in new_set) + 1
        width = max(pos[1] for pos in new_set) + 1
    else:
        offset_v = offset_h = 0

    if rotation % 8 > 3:
        new_set = {(height - 1 - pos[0], pos[1]) for pos in new_set}

    if rotation % 8 == 4:
        return {(pos[0]+offset_v, pos[1]+offset_h) for pos in new_set}

    if rotation % 4 == 1:
        new_set = transposed(new_set)
        new_set = {(width - 1 - pos[0], pos[1]) for pos in new_set}
    elif rotation % 4 == 2:
        new_set = {(height - 1 - pos[0], pos[1]) for pos in new_set}
        new_set = {(pos[0], width - 1 - pos[1]) for pos in new_set}
    elif rotation % 4 == 3:
        new_set = transposed(new_set)
        new_set = {(pos[0], height - 1 - pos[1]) for pos in new_set}

    return {(pos[0]+offset_v, pos[1]+offset_h) for pos in new_set}


def is_connected(pos_set):
    closed = set()
    set_len = len(pos_set)
    for pos in pos_set:
        if pos not in closed:
            connected = small_bfs(pos_set, closed, pos)
            if not valid_pos_set_component(set_len, connected):
                return False
    return True


def small_bfs(pos_set, closed, pos):
    fringe = []
    fringe.insert(0, pos)
    closed.add(pos)
    connected = 1
    while fringe:
        s = fringe.pop()
        successors = [(s[0]+1, s[1]), (s[0]-1, s[1]), (s[0], s[1]+1), (s[0], s[1]-1)]
        for suc in successors:
            if (suc in pos_set) and (suc not in closed):
                fringe.insert(0, suc)
                closed.add(suc)
                connected += 1
    return connected


def valid_pos_set_component(set_len, connected):
    if ((set_len % 5 == 0 and connected % 5 == 0)
    or ((set_len % 5) % 4 == 0 and (connected % 5) % 4 == 0)
    or ((set_len % 5) % 3 == 0 and (connected % 5) % 3 == 0)
    or ((57 - set_len) % 5 == 0 and (connected%5%4%3 == 0 or ((connected-7)>=0 and (connected-7)%5 == 0)))):
        return True
    else:
        return False


class DotSet:
    def __init__(self, dots):
        for dot in dots:
            assert(type(dot) is tuple and len(dot) == 2)

        self.dot_set = set(dots)
        self.height = max(pos[0] for pos in dots)
        self.width = max(pos[1] for pos in dots)

        self.loc = (0, 0)
        self.flp = 0
        self.rot = 0

    def flipped(self, flp):
        if flp % 2 == 0:
            return self.dot_set.copy()
        return {(self.height - dot[0], dot[1]) for dot in self.dot_set}

    def rotated(self, dot_set, rot):
        if rot % 4 == 0:
            return dot_set.copy()
        if rot % 4 == 1:
            new_set = {(pos[1], pos[0]) for pos in dot_set}
            return {(self.width - pos[0], pos[1]) for pos in new_set}
        elif rot % 4 == 2:
            new_set = {(self.height - pos[0], pos[1]) for pos in dot_set}
            return {(pos[0], self.width - pos[1]) for pos in new_set}
        elif rot % 4 == 3:
            new_set = {(pos[1], pos[0]) for pos in dot_set}
            return {(pos[0], self.height - pos[1]) for pos in new_set}

    def get_unique_orients(self):
        configs = []
        shapes = []
        for flp in [0, 1]:
            for rot in range(0, 4):
                config_shape = self.rotated(self.flipped(flp), rot)
                if not sum(shape == config_shape for shape in shapes):
                    configs.append((flp, rot))
                    shapes.append(config_shape)
        return dict(zip(configs, shapes))

    def set_config(self, loc, flp, rot):
        self.loc = loc
        self.flp = flp
        self.rot = rot

    def get_at_config(self, loc, flp, rot):
        return {(dot[0] + loc[0], dot[1] + loc[1]) for dot
                in self.rotated(self.flipped(flp), rot)}

    def get(self):
        return self.get_at_config(self.loc, self.flp, self.rot)

    def get_config(self):
        return self.loc, self.flp, self.rot

    def flip(self):
        self.flp = (self.flp + 1) % 2
        return self.get()

    def rotate(self, rot):
        self.rot = (self.rot + rot) % 4
        return self.get()

    def move(self, displacement):
        self.loc[0] += displacement[0]; self.loc[1] += displacement[1]
        return self.get()

    def is_on(self, loc):
        return loc in self.get()


class SquareDottedGrid(DotSet):
    def __init__(self, black_dots, wight_dots, height=4, width=4):
        self.black_dots = set(black_dots)
        self.wight_dots = set(wight_dots)
        self.height = height
        self.width = width

        self.loc = (0, 0)
        self.flp = 0
        self.rot = 0

    def flipped(self, flp):
        if flp % 2 == 0:
            return self.black_dots.copy()
        return self.wight_dots.copy()

    def is_on(self, loc):
        return (0 <= loc[0] - self.loc[0] < self.height) \
               and (0 <= loc[1] - self.loc[1] < self.width)

    def total_dots(self, config):
        return {(i, j) for i in range(c[0][0], self.loc[0] + self.height)
                for j in range(self.loc[1], self.loc[1] + self.width)}
