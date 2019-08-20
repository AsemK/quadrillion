import pytest
from unittest import mock
from quadrillion import Quadrillion
from quadrillion_csp import QuadrillionCSPAdapter
from quadrillion_data import SAVE_PATH
from dots_set import Config
from quadrillion_exception import *


@pytest.fixture()
def quadrillion_csp():
    return QuadrillionCSPAdapter(Quadrillion())


saved_games_files = [file.name.split('.')[0] for file in SAVE_PATH.iterdir() if file.name.startswith('game')]


@pytest.mark.parametrize('game_file', saved_games_files)
def test_adapter_solves_game(quadrillion_csp, game_file):
    quadrillion_csp.quadrillion.load_game(game_file)
    quadrillion_csp.solve()
    assert quadrillion_csp.quadrillion.is_won()


def test_help(quadrillion_csp):
    assert quadrillion_csp.quadrillion.shapes == quadrillion_csp.quadrillion.released_unplaced_shapes
    for i in range(len(quadrillion_csp.quadrillion.shapes)):
        quadrillion_csp.help()
        assert len(quadrillion_csp.quadrillion.released_unplaced_shapes)\
               == len(quadrillion_csp.quadrillion.shapes) - i - 1
    assert quadrillion_csp.quadrillion.is_won()


def test_solve_reuses_last_found_solution(quadrillion_csp):
    quadrillion_csp.solve()
    quadrillion_csp.quadrillion.reset()

    assert not quadrillion_csp.quadrillion.is_won()

    with mock.patch.object(quadrillion_csp, '_csp_solver') as solver_mock:
        quadrillion_csp.solve()
        assert solver_mock.call_count == 0

    assert quadrillion_csp.quadrillion.is_won()


def test_solve_already_solved_game_raises_exception(quadrillion_csp):
    quadrillion_csp.solve()

    with pytest.raises(StateException):
        quadrillion_csp.solve()


def test_solve_game_while_items_are_picked_raises_exception(quadrillion_csp):
    quadrillion_csp.quadrillion.pick(quadrillion_csp.quadrillion.shapes)

    with pytest.raises(StateException):
        quadrillion_csp.solve()


def test_solve_unsolvable_game_raises_exception(quadrillion_csp):
    grids = list(quadrillion_csp.quadrillion.grids)
    grids[0].config = Config(0, 0, (0, 3))
    grids[1].config = Config(0, 0, (0, 9))
    grids[2].config = Config(0, 0, (5, 3))
    grids[3].config = Config(0, 0, (5, 9))

    with pytest.raises(NoSolutionException):
        quadrillion_csp.solve()


if __name__ == '__main__':
    pytest.main()
