from csp import CSP, CSPSolver
from dots_set import connected_dots_sets
from quadrillion_exception import *
import time


class QuadrillionCSPAdapter(CSP):
    def __init__(self, quadrillion):
        self.quadrillion = quadrillion
        self._solution = dict()
        self._csp_solver = CSPSolver()

    @property
    def variables(self):
        return self._variables

    @property
    def domains(self):
        return self._domains

    def register_current_assignments(self, assignments, domains):
        self._current_assignments_dots = set()
        for dots in assignments.values():
            self._current_assignments_dots |= dots
        return self._is_valid_empty_dots(self._empty_grids_dots-self._current_assignments_dots)\
               and self._is_small_dots_in_domain(assignments, domains)

    def is_consistent_assignment(self, assignment):
        shape, dots = assignment
        return self._current_assignments_dots.isdisjoint(dots)

    def solve(self):
        solution = self._get_solution()
        for shape in self._variables:
            shape.set_dots(solution[shape])
        self.quadrillion.release()

    def help(self):
        solution = self._get_solution()
        shape = set(solution.keys()).pop()
        shape.set_dots(solution[shape])
        self.quadrillion.release()

    def _get_solution(self):
        try:
            self._variables = self.quadrillion.released_unplaced_shapes
            self._empty_grids_dots = self.quadrillion.released_empty_grids_dots
            self.quadrillion.pick(self._variables)
            if self._is_new_solution_needed():
                start_time = time.time()
                self._domains = self._extract_domains()
                solution = self._csp_solver(self)
                print("--- %s seconds ---" % (time.time() - start_time))
                print("--- %s iterations ---" % self._csp_solver.iterations)
                if solution:
                    self._cash_solution(solution)
                    return solution
                else:
                    self.quadrillion.unpick()
                    raise NoSolutionException('The current state of the game has no solution.')
            else:
                return self._adapt_solution()
        except StateException:
            raise StateException('Cannot solve while items are picked.')

    def _is_new_solution_needed(self):
        if self._solution:
            for shape in self._variables:
                if not self._is_on_empty_dots(self._solution[shape]):
                    return True
            return False
        return True

    def _cash_solution(self, solution):
        self._solution = dict()
        for shape in self.quadrillion.shapes:
            self._solution[shape] = frozenset(shape)
        self._solution.update(solution)

    def _adapt_solution(self):
        solution = dict()
        for shape in self._variables:
            solution[shape] = self._solution[shape]
        return solution

    def _extract_domains(self):
        domains = dict()
        if self._is_valid_empty_dots(self._empty_grids_dots):
            square_dots = self._get_smallest_square_over_dots(self._empty_grids_dots)
            for variable in self._variables:
                domain = set()
                for loc in square_dots:
                    for config in variable.get_unique_configs_at(loc):
                        dots = frozenset(variable.configured(config))
                        if self._is_on_empty_dots(dots):
                            domain.add(dots)
                domains[variable] = domain
        return domains

    def _is_small_dots_in_domain(self, assignments, domains):
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

    def _is_on_empty_dots(self, dots):
        return dots <= self._empty_grids_dots

    @staticmethod
    def _get_smallest_square_over_dots(dots):
        y = min(h for h, w in dots)
        x = min(w for h, w in dots)
        height = max(h for h, w in dots) + 1
        width = max(w for h, w in dots) + 1
        return {(h, w) for h in range(y, height) for w in range(x, width)}

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
