class CSP:
    def get_variables(self):
        pass

    def get_domains(self):
        pass

    def set_current_assignments(self, assignments):
        pass

    def is_consistent_assignment(self, assignment):
        pass


class CSPSolver:
    def __init__(self, csp, convert_solution=lambda x: x):
        self.csp = csp
        self.vars = csp.get_variables()
        self.domains = csp.get_domains()
        self.select_unassigned_variable = self.get_unassigned_mrv
        self.convert_solution = convert_solution

    def forward_check(self, assignments, domains):
        new_domains = dict()
        self.csp.set_current_assignments(assignments)
        for var in set(domains.keys()) - set(assignments.keys()):
            new_domains[var] = []
            for val in domains[var]:
                if self.csp.is_consistent_assignment((var, val)):
                    new_domains[var].append(val)
            if not new_domains[var]:
                return None
        return new_domains

    @staticmethod
    def get_unassigned_mrv(assignments, domains):
        return min([(len(domains[var]), var) for var in set(domains.keys()) - set(assignments.keys())])[1]

    def back_tracking_search(self, assignments, domains):
        var = self.select_unassigned_variable(assignments, domains)
        if len(assignments) == len(self.vars)-1:
            assignments[var] = domains[var][0]
            return assignments
        self.iterations += 1
        for val in domains[var]:
            assignments[var] = val
            new_domains = self.forward_check(assignments, domains)
            if new_domains:
                result = self.back_tracking_search(assignments, new_domains)
                if result: return result
            del assignments[var]
        return None

    def get_solution(self):
        self.iterations = 0
        for shape in self.domains:
            if not self.domains[shape]:
                return None
        solution = self.back_tracking_search(dict(), self.domains)
        if solution:
            return self.convert_solution(solution)
        else:
            return None

    def get_search_iterations(self):
        return self.iterations
