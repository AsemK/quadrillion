from csp import CSP, CSPSolver
from quadrillion import Quadrillion
from graphic_display import QuadrillionGraphicDisplay


class QuadrillionCSPAdapter(CSP):
    def __init__(self, quadrillion):
        self._quadrillion = quadrillion

        self._variables = self._quadrillion.released_unplaced_shapes
        self._empty_grids_dots = self._quadrillion.released_empty_grids_dots
        self._domains = self._extract_domains()

        self._quadrillion.pick(self._variables)

    def get_variables(self):
        return self._variables

    def get_domains(self):
        return self._domains

    def set_current_assignments(self, assignments):
        self._empty_grids_dots = self._quadrillion.released_empty_grids_dots
        for shape, config in assignments.items():
            shape.config = config
            self._empty_grids_dots -= shape

    def is_consistent_assignment(self, assignment):
        shape, config = assignment
        shape.config = config
        return shape <= self._empty_grids_dots and is_connected(self._empty_grids_dots - shape)

    def _extract_domains(self):
        domains = dict()
        square_dots = self._get_smallest_square_over_dots(self._empty_grids_dots)
        for variable in self._variables:
            domain = []
            for loc in square_dots:
                for config in variable.get_unique_configs_at(loc):
                    if self.is_consistent_assignment((variable, config)):
                        domain.append(config)
            domains[variable] = domain
        return domains

    def _get_smallest_square_over_dots(self, dots):
        y = min(h for h, w in dots)
        x = min(w for h, w in dots)
        height = max(h for h, w in dots) + 1
        width = max(w for h, w in dots) + 1
        return {(h, w) for h in range(y, height) for w in range(x, width)}

    def get_solution(self):
        csp_solver = CSPSolver(self)
        solution = csp_solver.get_solution()
        self.iterations = csp_solver.iterations
        for shape in self._variables:
            shape.config = solution[shape]
        self._quadrillion.release()


def is_connected(dot_set):
    closed = set()
    set_len = len(dot_set)
    for dot in dot_set:
        if dot not in closed:
            connected = small_bfs(dot_set, closed, dot)
            if not valid_pos_set_component(set_len, connected):
                return False
    return True


def small_bfs(dot_set, closed, dot):
    fringe = []
    fringe.insert(0, dot)
    closed.add(dot)
    connected = 1
    while fringe:
        s = fringe.pop()
        successors = [(s[0]+1, s[1]), (s[0]-1, s[1]), (s[0], s[1]+1), (s[0], s[1]-1)]
        for suc in successors:
            if (suc in dot_set) and (suc not in closed):
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


if __name__ == '__main__':
    import time
    start_time = time.time()

    quadrillion = Quadrillion()
    quadrillion_csp = QuadrillionCSPAdapter(quadrillion)
    quadrillion_csp.get_solution()

    print("--- %s seconds ---" % (time.time() - start_time))
    print('--- %s iterations ---' % quadrillion_csp.iterations)

    view = QuadrillionGraphicDisplay(quadrillion)
