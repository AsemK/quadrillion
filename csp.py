from abc import ABC, abstractmethod


class CSP(ABC):
    """
    A simple abstract class for constraint satisfaction problems
    """
    @property
    @abstractmethod
    def variables(self):
        """
        :return: iterable of variables
        """
        pass

    @property
    @abstractmethod
    def domains(self):
        """
        :return: a dictionary containing all variables and the corresponding
        (node consistent) values that each variable can be assigned.
        """
        pass

    @abstractmethod
    def register_current_assignments(self, assignments, domains):
        """
        register the input assignments and infers (force arc consistency) on
        other unassigned variables in domains. As a results, new inferred assignments
        might be added to the input assignments.
        :param assignments: a dictionary containing variable(s) and the corresponding
        valid assignment(s).
        :param domains: a dictionary containing variables and their current possible values.
        :returns boolean that is False if inference found that no solution is possible
        with the input assignments
        """
        pass

    @abstractmethod
    def is_consistent_assignment(self, assignment):
        """
        This method is the way of checking the constraints of the problem. It determines if
        the input assignment is consistent with the previously registered assignments.
        :param assignment: a single tuple containing (variable, assignment)
        The input variable MUST NOT be one of the variables set when calling
        set_current_assignments.
        :returns: a boolean
        """
        pass


class CSPSolver:
    """
    An implementation of the backtracking search algorithm as described in
    the book "AI, a Modern Approach", ed. 3, ch. 6.
    """
    def __init__(self):
        self.select_unassigned_variable = self.get_unassigned_variable_with_minimum_remaining_values

    def __call__(self, csp):
        """
        :param csp: a constraint satisfaction problem object that provides the function
        indicated in CSP abstract class.
        :returns the first found solution or None if there is not any. The solution is
        returned as a dictionary containing variables and the corresponding values.
        """
        self.iterations = 0  # reset iterations counter
        self.csp = csp
        self.variables = csp.variables
        self.domains = csp.domains
        # ensure that each variable has a non-empty domain
        for shape in self.domains:
            if not self.domains[shape]:
                return None
        return self.back_tracking_search(dict(), self.domains)

    def back_tracking_search(self, assignments, domains):
        """
        The recursive back-tracking search method
        """
        if len(assignments) == len(self.variables):
            return assignments
        elif not domains:
            return None
        var = self.select_unassigned_variable(assignments, domains)
        self.iterations += 1  # search iterations counter
        old_vars = set(assignments.keys())
        for val in domains[var]:
            assignments[var] = val
            new_domains = self.forward_check(assignments, domains)
            solution = self.back_tracking_search(assignments, new_domains)
            if solution:
                return solution
            for new_var in set(assignments.keys()) - old_vars:
                del assignments[new_var]
        return None  # Failure

    def forward_check(self, assignments, domains):
        """
        A function that should be called at the begging of each search recursion to
        eliminate assignments inconsistent with the current assignment from the search space.
        :return: a new domains dictionary where all the assignments are consistent with
        the input assignments or None if no solution is possible given the input assignments and domains.
        """
        if self.csp.register_current_assignments(assignments, domains):
            new_domains = dict()
            for var in set(domains.keys()) - set(assignments.keys()):
                new_domains[var] = set()
                for val in domains[var]:
                    if self.csp.is_consistent_assignment((var, val)):
                        new_domains[var].add(val)
                if not new_domains[var]:
                    return None
            return new_domains
        return None

    @staticmethod
    def get_unassigned_variable_with_minimum_remaining_values(assignments, domains):
        """
        Selects the next variable to be assigned by the minimum remaining values heuristic
        :return: the variable with the minimum remaining values
        """
        return min(set(domains.keys()) - set(assignments.keys()), key=lambda var: len(domains[var]))

    def get_search_iterations(self):
        return self.iterations
