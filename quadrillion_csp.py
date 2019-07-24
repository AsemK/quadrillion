from csp import CSP, CSPSolver
from quadrillion import Quadrillion
from graphic_display import QuadrillionGraphicDisplay


class QuadrillionCSPAdapter(CSP):
    def __init__(self, quadrillion):
        self._quadrillion = quadrillion

        self._variables = self._quadrillion.released_unplaced_shapes
        self._empty_grids_dots = self._quadrillion.released_empty_grids_dots
        self._domains = self._extract_domains()
        self._solution = []

        self._quadrillion.pick(self._variables)

    def get_variables(self):
        return self._variables

    def get_domains(self):
        return self._domains

    def set_current_assignments(self, assignments, domains):
        self._current_assignments_dots = set()
        for dots in assignments.values():
            self._current_assignments_dots |= dots
        return self._is_valid_empty_dots(self._empty_grids_dots-self._current_assignments_dots)\
               and self.is_small_dots_in_domain(assignments, domains)

    def is_consistent_assignment(self, assignment):
        shape, dots = assignment
        return self._current_assignments_dots.isdisjoint(dots)

    def _extract_domains(self):
        domains = dict()
        if self._is_valid_empty_dots(self._empty_grids_dots):
            square_dots = self._get_smallest_square_over_dots(self._empty_grids_dots)
            for variable in self._variables:
                domain = set()
                for loc in square_dots:
                    for config in variable.get_unique_configs_at(loc):
                        dots = frozenset(variable.configured(config))
                        if self._is_node_consistent(dots):
                            domain.add(dots)
                domains[variable] = domain
        return domains

    def _is_node_consistent(self, dots):
        return self._is_on_empty_dots(dots, self._empty_grids_dots)\
               and self._is_valid_empty_dots(self._empty_grids_dots - dots)

    @staticmethod
    def _get_smallest_square_over_dots(dots):
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
            shape.set_dots(solution[shape])
        self._quadrillion.release()

    @staticmethod
    def _is_on_empty_dots(dots, empty_dots):
        return dots <= empty_dots

    def is_small_dots_in_domain(self, assignments, domains):
        if not self._connected_small_sets:
            return True
        else:
            found_assignments = dict()
            for connected_set in self._connected_small_sets:
                target = frozenset(connected_set)
                for var in set(domains.keys()) - set(assignments.keys()) - set(found_assignments.keys()):
                    if target in domains[var]:
                        found_assignments[var] = target
                        break
            if len(found_assignments) == len(self._connected_small_sets):
                assignments.update(found_assignments)
                for dots in found_assignments.values():
                    self._current_assignments_dots |= dots
                return True
            else:
                return False

    def _is_valid_empty_dots(self, empty_dots):
        self._connected_small_sets = []
        nr_empty_dots = len(empty_dots)
        for connected_dots_set in connected_dots_sets(empty_dots):
            if not QuadrillionCSPAdapter._is_valid_nr_empty_connected_dots(nr_empty_dots,
                                                                          len(connected_dots_set)):
                return False
            elif len(connected_dots_set) <= 5:
                self._connected_small_sets.append(connected_dots_set)
        return True

    @staticmethod
    def _is_valid_nr_empty_connected_dots(nr_empty_dots, nr_empty_connected_dots):
               # empty_connected_dots should have 5 dots
        return ((nr_empty_dots % 5 == 0 and nr_empty_connected_dots % 5 == 0)
               # empty_connected_dots should have 5 or 4 dots
            or ((nr_empty_dots - 4) % 5 == 0 and nr_empty_connected_dots % 5 % 4 == 0)
               # empty_connected_dots should have 5 or 3 dots
            or ((nr_empty_dots - 3) % 5 == 0 and nr_empty_connected_dots % 5 % 3 == 0)
               # empty_connected_dots should have 5, 4 or 3 dots
            or ((nr_empty_dots - 7) % 5 == 0 and (nr_empty_connected_dots % 5 % 4 % 3 == 0
                                                  or ((nr_empty_connected_dots - 7) >= 0
                                                      and (nr_empty_connected_dots - 7) % 5 == 0))))


def connected_dots_sets(dots_set):
    def connected_dots_set_at(dot):
        connected_dots = {dot}
        dots_queue =[dot]
        while dots_queue:
            y, x = dots_queue.pop()
            successors = dots_set & ({(y+1, x), (y-1, x), (y, x+1), (y, x-1)} - connected_dots)
            for dot in successors:
                connected_dots.add(dot)
                dots_queue.insert(0, dot)
        return connected_dots
    seen_dots = set()
    for dot in dots_set:
        if dot in seen_dots: continue
        connected_dots = connected_dots_set_at(dot)
        yield connected_dots
        seen_dots |= connected_dots


if __name__ == '__main__':
    import time
    start_time = time.time()

    quadrillion = Quadrillion()
    quadrillion_csp = QuadrillionCSPAdapter(quadrillion)
    quadrillion_csp.get_solution()

    print("--- %s seconds ---" % (time.time() - start_time))
    print('--- %s iterations ---' % quadrillion_csp.iterations)

    view = QuadrillionGraphicDisplay(quadrillion)
