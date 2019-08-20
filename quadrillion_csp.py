import time
from csp import CSP, CSPSolver
from dots_set import connected_dots_sets
from quadrillion_exception import *


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
               and self._is_small_empty_dots_in_domain(assignments, domains)

    def is_consistent_assignment(self, assignment):
        shape, dots = assignment
        return self._current_assignments_dots.isdisjoint(dots)

    def solve(self):
        """
        Applies a solution (if found) to quadrillion game
        """
        solution = self._get_solution()
        for shape in self._variables:
            shape.set_dots(solution[shape])
        self.quadrillion.release()

    def help(self):
        """
        If a solution is found, one shape is moved to its configuration according to the solution.
        """
        solution = self._get_solution()
        shape = set(solution.keys()).pop()
        shape.set_dots(solution[shape])
        self.quadrillion.release()

    def _get_solution(self):
        """
        Uses the csp_solver to get a new solution if needed, otherwise adapts the cashed solution
        :return: a solution dictionary containing shapes and their corresponding dots.
        """
        if self.quadrillion.is_won():
            raise StateException("The game is already solved!")
        try:
            self._variables = self.quadrillion.released_unplaced_shapes
            self._empty_grids_dots = self.quadrillion.released_empty_grids_dots
            self.quadrillion.pick(self._variables)
            if self._is_new_solution_needed():
                start_time = time.time()
                self._domains = self._extract_domains()
                solution = self._csp_solver(self)
                print("--- %s seconds ---" % (time.time() - start_time))
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
        """
        saves a snapshot of the dots of all shapes with the dots of shapes in solution.
        """
        self._solution = dict()
        for shape in self.quadrillion.shapes:
            self._solution[shape] = frozenset(shape)
        self._solution.update(solution)

    def _adapt_solution(self):
        """
        :returns: the subset of the cashed solution corresponding to the current variables
        """
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

    def _is_valid_empty_dots(self, empty_dots):
        """
        checks if the connected regions of the empty dots can be filled by shapes in the self._variables
        based on the number of dots in these connected components and in the shapes.
        Also, cashes the small connected components (5 or less dots) to check if they can be filled by a
        valid value in the domain of a variable.
        """
        self._connected_small_sets = []
        nr_empty_dots = len(empty_dots)
        for connected_dots_set in connected_dots_sets(empty_dots):
            if not QuadrillionCSPAdapter._is_valid_nr_empty_connected_dots(nr_empty_dots,
                                                                          len(connected_dots_set)):
                return False
            elif len(connected_dots_set) <= 5:
                self._connected_small_sets.append(connected_dots_set)
        return True

    def _is_small_empty_dots_in_domain(self, assignments, domains):
        """
        checks if small connected components of the empty dots in the domain of some variable.
        If so, the assignment of that variable is inferred to be the connected component of empty dots.
        otherwise, it is known that there is no valid solution.
        """
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

    def _is_on_empty_dots(self, dots):
        return dots <= self._empty_grids_dots

    @staticmethod
    def _get_smallest_square_over_dots(dots):
        """
        To guarantee that dots in the domain cover the complete empty dot in all possible configuration,
        the dots of the smallest square over empty dots is used.
        """
        y = min(h for h, w in dots)
        x = min(w for h, w in dots)
        height = max(h for h, w in dots) + 1
        width = max(w for h, w in dots) + 1
        return {(h, w) for h in range(y, height) for w in range(x, width)}

    @staticmethod
    def _is_valid_nr_empty_connected_dots(nr_empty_dots, nr_empty_connected_dots):
        """
        Determines if a connected component in the empty dots can be filled by a shape in the variables
        considering only the number of dots.
        """
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
