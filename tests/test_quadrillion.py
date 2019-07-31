import pytest
from dots_set import DotsSet, DotsGrid, Config
from quadrillion_exception import *
from quadrillion import Quadrillion


@pytest.fixture()
def quadrillion_game():
    return Quadrillion()


@pytest.fixture()
def sorted_shapes(quadrillion_game):
    return sort_by_location(quadrillion_game.shapes)


@pytest.fixture()
def sorted_grids(quadrillion_game):
    return sort_by_location(quadrillion_game.grids)


def sort_by_location(items):
    return sorted(items, key=lambda item: item.config.location)


def test_get_at_shape_returns_shape(quadrillion_game):
    dot = (11, 6)
    shape = quadrillion_game.get_at(dot)
    assert dot in shape
    assert type(shape) == DotsSet


def test_get_at_grid_returns_grid(quadrillion_game):
    dot = (7, 6)
    grid = quadrillion_game.get_at(dot)
    assert dot in grid
    assert type(grid) == DotsGrid


def test_get_at_shape_over_grid_returns_shape(quadrillion_game):
    test_get_at_grid_returns_grid(quadrillion_game)

    dot = (11, 6)
    shape = quadrillion_game.get_at(dot)
    shape.move((-4, 0))

    dot = (7, 6)
    shape = quadrillion_game.get_at(dot)
    assert dot in shape
    assert type(shape) == DotsSet


def test_get_at_empty_dot_fails(quadrillion_game):
    with pytest.raises(NoItemException):
        quadrillion_game.get_at((1, 1))


def test_pick_shapes_and_grids_allowed(quadrillion_game, sorted_shapes, sorted_grids):
    shapes = set(sorted_shapes[1:2])
    grids = set(sorted_grids[1:2])

    assert shapes < quadrillion_game.released_shapes
    assert grids < quadrillion_game.released_grids

    quadrillion_game.pick(shapes | grids)
    assert not shapes & quadrillion_game.released_shapes
    assert not grids & quadrillion_game.released_grids


def test_pick_while_others_are_picked_fails(quadrillion_game, sorted_shapes):
    quadrillion_game.pick([sorted_shapes[4]])
    with pytest.raises(StateException):
        quadrillion_game.pick([sorted_shapes[7]])


def test_pick_shapes_over_grids_allowed(quadrillion_game, sorted_shapes, sorted_grids):
    shapes = {sorted_shapes[3], sorted_shapes[8]}
    for shape in shapes:
        shape.move((-5, 0))
    grids = {sorted_grids[2], sorted_grids[3]}

    assert shapes < quadrillion_game.released_shapes
    assert grids < quadrillion_game.released_grids

    quadrillion_game.pick(shapes | grids)
    assert not shapes & quadrillion_game.released_shapes
    assert not grids & quadrillion_game.released_grids


def test_pick_grids_under_shapes_fails(quadrillion_game, sorted_shapes, sorted_grids):
    shapes = [sorted_shapes[3], sorted_shapes[8]]
    for shape in shapes:
        shape.move((-5, 0))
    assert set(sorted_grids) == quadrillion_game.released_grids

    with pytest.raises(IllegalPickException):
        quadrillion_game.pick(sorted_grids + [sorted_shapes[1]])
    assert set(sorted_shapes) == quadrillion_game.released_shapes
    assert set(sorted_grids) == quadrillion_game.released_grids


def test_release_before_pick_fails(quadrillion_game):
    with pytest.raises(StateException):
        quadrillion_game.release()


def test_release_shapes_and_grids_works(quadrillion_game, sorted_shapes, sorted_grids):
    shape1 = sorted_shapes[2]
    shape2 = sorted_shapes[10]
    grid1 = sorted_grids[0]
    grid2 = sorted_grids[3]

    quadrillion_game.pick({shape1, shape2, grid1, grid2})
    grid1.config = Config(1, 0, (5, 8))
    grid2.config = Config(1, 0, (1, 4))
    shape1.move((-8, 3))
    shape2.move((-8, -3))

    quadrillion_game.release()
    assert set(sorted_shapes) == quadrillion_game.released_shapes
    assert set(sorted_grids) == quadrillion_game.released_grids
    assert not {shape1, shape2} & quadrillion_game.released_unplaced_shapes


def test_release_shape_over_shapes_fails(quadrillion_game, sorted_shapes):
    quadrillion_game.pick([sorted_shapes[1]])
    sorted_shapes[1].rotate(clockwise=True)
    with pytest.raises(IllegalReleaseException):
        quadrillion_game.release()


def test_release_shape_over_closed_grids_dots_fails(quadrillion_game, sorted_shapes):
    quadrillion_game.pick([sorted_shapes[4]])
    sorted_shapes[4].move((4, 0))
    with pytest.raises(IllegalReleaseException):
        quadrillion_game.release()


def test_release_shape_over_part_of_grid_fails(quadrillion_game, sorted_shapes):
    quadrillion_game.pick([sorted_shapes[3]])
    sorted_shapes[3].move((2, 0))
    with pytest.raises(IllegalReleaseException):
        quadrillion_game.release()


def test_release_grid_over_grid_fails(quadrillion_game, sorted_grids):
    quadrillion_game.pick([sorted_grids[1]])
    sorted_grids[1].move((-1, -2))
    with pytest.raises(IllegalReleaseException):
        quadrillion_game.release()


def test_release_grid_over_shapes_fails(quadrillion_game, sorted_grids):
    quadrillion_game.pick([sorted_grids[0]])
    sorted_grids[0].move((8, -2))
    with pytest.raises(IllegalReleaseException):
        quadrillion_game.release()


def test_if_release_failed_all_items_still_picked(quadrillion_game, sorted_shapes, sorted_grids):
    shape = sorted_shapes[6]
    grid = sorted_grids[0]
    quadrillion_game.pick([shape, grid])
    shape.move((0,1))

    with pytest.raises(IllegalReleaseException):
        quadrillion_game.release()
    assert shape not in quadrillion_game.released_shapes
    assert grid not in quadrillion_game.released_grids


def test_unpick_before_pick_fails(quadrillion_game):
    with pytest.raises(StateException):
        quadrillion_game.unpick()


def test_unpick_undoes_moves_aftr_pick(quadrillion_game, sorted_shapes, sorted_grids):
    shape1 = sorted_shapes[2]
    shape2 = sorted_shapes[10]
    grid1 = sorted_grids[0]
    grid2 = sorted_grids[3]
    items = [shape1, shape2, grid1, grid2]
    configs_before = [item.config for item in items]

    quadrillion_game.pick({shape1, shape2, grid1, grid2})
    grid1.config = Config(1, 0, (5, 8))
    grid2.config = Config(1, 0, (1, 4))
    shape1.move((-8, 3))
    shape2.move((-8, -3))

    assert all(item.config != config for item, config in zip(items, configs_before))
    quadrillion_game.unpick()
    assert set(sorted_shapes) == quadrillion_game.released_shapes
    assert set(sorted_grids) == quadrillion_game.released_grids
    assert all(item.config == config for item, config in zip(items, configs_before))


def test_unpick_fails_if_momentos_are_not_captured_correctly(quadrillion_game, sorted_shapes):
    quadrillion_game.pick([sorted_shapes[11]])
    quadrillion_game._picked_items_momentos = [(sorted_shapes[11], Config(0, 3, (12, 13)))]
    with pytest.raises(QuadrillionException):
        quadrillion_game.unpick()


def test_reset_fails_if_initial_configs_are_inconsistent(quadrillion_game, sorted_shapes):
    sorted_shapes[0]._initial_config = Config(0, 3, (10, 1))
    with pytest.raises(InitialConfigurationsException):
        quadrillion_game.reset()


def test_is_won(quadrillion_game, sorted_shapes):
    assert not quadrillion_game.is_won()

    sorted_solution_configs = [(1, 0, (5, 5)), (0, 2, (1, 4)), (1, 2, (3, 5)), (0, 3, (6, 4)),
                               (0, 3, (3, 9)), (1, 0, (6, 8)), (0, 3, (2, 7)), (1, 0, (7, 5)),
                               (1, 3, (5, 10)), (0, 1, (1, 10)), (0, 1, (1, 7)), (0, 0, (3, 4))]

    for shape, config in zip(sorted_shapes, sorted_solution_configs):
        shape.config = Config(*config)

    assert quadrillion_game.is_won()

if __name__ == '__main__':
    pytest.main()
