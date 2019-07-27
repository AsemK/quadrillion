class QuadrillionException(Exception):
    pass


class StateException(QuadrillionException):
    pass


class NoItemException(QuadrillionException):
    pass


class IllegalReleaseException(QuadrillionException):
    pass


class IllegalPickException(QuadrillionException):
    pass


class InitialConfigurationsException(IllegalReleaseException):
    pass

class NoSolutionException(QuadrillionException):
    pass