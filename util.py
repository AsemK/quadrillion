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


def unique_configs(pos_set):
    configs = [0]
    shapes = [pos_set]
    for config in range(1,8):
        config_shape = rotated(pos_set, config)
        if not sum([shape == config_shape for shape in shapes]):
            configs.append(config)
            shapes.append(config_shape)
    return zip(configs, shapes)


def list2array(pos_set, default=False):
    height = max(pos[0] for pos in pos_set) + 1
    width  = max(pos[1] for pos in pos_set) + 1
    shape  = [[int(default) for i in range(width)] for j in range(height)]
    for pos in pos_set:
        shape[pos[0]][pos[1]] = int(not default)
    return shape


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
