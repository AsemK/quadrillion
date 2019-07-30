import pytest
from dots_set import DotsSet, DotsGrid, DotsSetFactory, Config

"""
shapes:
 [0]         [1]         [2]         [3]
O O O        O O        . O O        O .
O O . rot -> O O rot -> O O O rot -> O O  clockwise rotation
. . .        . O        . . .        O O
 flip
  |
  v
 [4]         [5]         [6]         [7]
O O .        O O        O O O        . O
O O O rot -> O O rot -> . O O rot -> O O 
. . .        O .        . . .        O O
"""
SHAPES = [{(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)},
          {(0, 1), (0, 0), (2, 1), (1, 0), (1, 1)},
          {(0, 1), (1, 2), (0, 2), (1, 0), (1, 1)},
          {(0, 0), (2, 1), (2, 0), (1, 0), (1, 1)},
          {(1, 2), (0, 1), (0, 0), (1, 0), (1, 1)},
          {(0, 1), (0, 0), (2, 0), (1, 0), (1, 1)},
          {(0, 1), (1, 2), (0, 0), (1, 1), (0, 2)},
          {(0, 1), (2, 1), (2, 0), (1, 0), (1, 1)}]

"""
grids:
O . . O        O O O O        O O O O        O O O O
O O O O rot -> O O O . rot -> O O O O rot -> . O O O
O O O O        O O O .        O O O O        . O O O
O O O O        O O O O        O . . O        O O O O < open dot
 flip                           ^
  |                             closed dot
  v
O O O .        O O O O        O O O O        . O O O
O O O O rot -> O O O O rot -> O . O O rot -> O O . O
O O . O        O . O O        O O O O        O O O O
O O O O        O O O .        . O O O        O O O O
"""
GRIDS_HEIGHT, GRIDS_WIDTH = 4, 4
GRIDS_CLOSED_DOTS = [{(0, 1), (0, 2)}, {(1, 3), (2, 3)}, {(3, 2), (3, 1)}, {(2, 0), (1, 0)},
                     {(0, 3), (2, 2)}, {(3, 3), (2, 1)}, {(3, 0), (1, 1)}, {(1, 2), (0, 0)}]
GRIDS_OPEN_DOTS = [{(y, x) for y in range(GRIDS_HEIGHT) for x in range(GRIDS_WIDTH)} - closed
                   for closed in GRIDS_CLOSED_DOTS]


class TestDotsSetInstantiation:
    def test_instantiation_with_non_int_dots_fails(self):
        with pytest.raises(TypeError):
            DotsSet({(2, 3), (3, 1), (4, 5.5)})

    def test_instantiation_with_non_tuples_fails(self):
        with pytest.raises(TypeError):
            DotsSet({[2, 3], (3, 1), (4, 5)})

    def test_instantiation_with_negative_dots_fails(self):
        with pytest.raises(TypeError):
            DotsSet({(-2, 3), (3, 1), (4, 5)})

    def test_instantiation_with_dots_works(self):
        dots_set = DotsSet({(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)})
        color = dots_set.color
        assert all(dot in dots_set for dot in {(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)})



class TestTwoSidedDotsGridInstantiation:
    def test_instantiation_with_non_int_dots_fails(self):
        with pytest.raises(TypeError):
            DotsGrid({(2, 3), (3, 1.5)}, {(1, 2), (0, 0)}, 4, 4)

    def test_instantiation_with_non_tuples_fails(self):
        with pytest.raises(TypeError):
            DotsGrid({(2, 3), (3, 1)}, {[1, 2], (0, 0)}, 4, 4)

    def test_instantiation_with_negative_dots_fails(self):
        with pytest.raises(TypeError):
            DotsGrid({(-2, 3), (3, 1)}, {(1, 2), (0, 0)}, 4, 4)

    def test_instantiation_with_dots_outside_size_fails(self):
        with pytest.raises(TypeError):
            DotsGrid({(2, 3), (3, 1)}, {(1, 2), (0, 0)}, 3, 3)

    def test_instantiation_with_dots_works(self):
        dots_set = DotsGrid({(2, 3), (3, 1)}, {(1, 2), (0, 0)}, 4, 4)
        color1 = dots_set.color
        assert len(dots_set) == 4*4
        assert dots_set.closed_dots == {(2, 3), (3, 1)}
        dots_set.flip()
        color2 = dots_set.color
        assert dots_set.closed_dots == {(1, 2), (0, 0)}
        assert color1 != color2


class TestMovement:
    displacement = (3, 4)

    @pytest.fixture(scope='class', autouse=True, params=['shape', 'grid'])
    def setup(self, request):
        if request.param == 'shape':
            request.cls.dots_set = DotsSet(SHAPES[0])
            request.cls.assert_equals_dots_set = request.cls.assert_equals_shape
        elif request.param == 'grid':
            request.cls.dots_set = DotsGrid(GRIDS_CLOSED_DOTS[0], GRIDS_CLOSED_DOTS[4],
                                            GRIDS_HEIGHT, GRIDS_WIDTH)
            request.cls.assert_equals_dots_set = request.cls.assert_equals_grid

    def teardown(self):
        self._test_reset()

    def assert_equals_shape(self, shape_index, displacement=(0, 0)):
        displaced_shape = {(y + displacement[0], x + displacement[1])
                           for y, x in SHAPES[shape_index]}
        assert self.dots_set == displaced_shape

    def assert_equals_grid(self, grid_index, displacement=(0, 0)):
        displaced_closed = {(y + displacement[0], x + displacement[1])
                             for y, x in GRIDS_CLOSED_DOTS[grid_index]}
        displaced_open = {(y + displacement[0], x + displacement[1])
                           for y, x in GRIDS_OPEN_DOTS[grid_index]}
        assert self.dots_set.closed_dots == displaced_closed
        assert self.dots_set.open_dots == displaced_open
        assert self.dots_set == self.dots_set.closed_dots | self.dots_set.open_dots

    def do_movements(self, *movements):
        for move in movements:
            if move == 'f':
                self.dots_set.flip()
            elif move == 'cwr':
                self.dots_set.rotate(clockwise=True)
            elif move == 'ccwr':
                self.dots_set.rotate(clockwise=False)
            elif move == 'm':
                self.dots_set.move(self.displacement)

    def test_four_rotations_clockwise(self):
        for dots_set_index in [1, 2, 3, 0]:
            self.do_movements('cwr')
            self.assert_equals_dots_set(dots_set_index)

    def test_four_rotations_counterclockwise(self):
        for dots_set_index in [3, 2, 1, 0]:
            self.do_movements('ccwr')
            self.assert_equals_dots_set(dots_set_index)

    def test_two_flips(self):
        for dots_set_index in [4, 0]:
            self.do_movements('f')
            self.assert_equals_dots_set(dots_set_index)

    def test_rotate_flip(self):
        self.do_movements('ccwr', 'f')
        self.assert_equals_dots_set(5)

    def test_flip_rotate(self):
        self.do_movements('f', 'ccwr')
        self.assert_equals_dots_set(7)

    def test_move(self):
        self.do_movements('m')
        self.assert_equals_dots_set(0, self.displacement)

    def test_flip_rotate_move(self):
        self.do_movements('f', 'cwr', 'm')
        self.assert_equals_dots_set(5, self.displacement)

    def test_move_flip_rotate(self):
        self.do_movements('m', 'f', 'cwr')
        self.assert_equals_dots_set(5, self.displacement)

    def test_move_flip_rotate_after_reset(self):
        self.test_move_flip_rotate()
        self._test_reset()
        self.test_move_flip_rotate()

    def _test_reset(self):
        self.dots_set.reset()
        self.assert_equals_dots_set(0)


class TestConfig:
    config1 = Config(flips=1, rotations=3, location=(4, 2))
    config2 = Config(flips=0, rotations=2, location=(3, 7))

    @pytest.fixture(scope='class', autouse=True, params=['shape', 'grid'])
    def setup(self, request):
        def take_shape_snapshot(shape):
            return set(shape)

        def take_grid_snapshot(grid):
            return set(grid.open_dots), set(grid.closed_dots)

        def shape_equals_snapshot(shape, snapshot):
            return shape == snapshot

        def grid_equals_snapshot(grid, snapshot):
            return (grid.open_dots, grid.closed_dots) == snapshot

        if request.param == 'shape':
            request.cls.unconfigured_set = DotsSet(SHAPES[0])
            request.cls.configured_set1 = DotsSet(SHAPES[0], request.cls.config1)
            request.cls.configured_set2 = DotsSet(SHAPES[0], request.cls.config2)
            request.cls.take_dots_set_snapshot = staticmethod(take_shape_snapshot)
            request.cls.take_dots_equals_snapshot = staticmethod(shape_equals_snapshot)

        elif request.param == 'grid':
            request.cls.unconfigured_set = DotsGrid(GRIDS_CLOSED_DOTS[0],
                                                    GRIDS_CLOSED_DOTS[4],
                                                    GRIDS_HEIGHT, GRIDS_WIDTH)
            request.cls.configured_set1 = DotsGrid(GRIDS_CLOSED_DOTS[0],
                                                   GRIDS_CLOSED_DOTS[4],
                                                   GRIDS_HEIGHT, GRIDS_WIDTH,
                                                   request.cls.config1)
            request.cls.configured_set2 = DotsGrid(GRIDS_CLOSED_DOTS[0],
                                                   GRIDS_CLOSED_DOTS[4],
                                                   GRIDS_HEIGHT, GRIDS_WIDTH,
                                                   request.cls.config2)
            request.cls.take_dots_set_snapshot = staticmethod(take_grid_snapshot)
            request.cls.take_dots_equals_snapshot = staticmethod(grid_equals_snapshot)

    def teardown(self):
        self.unconfigured_set.reset()
        self.configured_set1.reset()
        self.configured_set2.reset()

    def test_congifured_and_unconfigured_are_not_equal(self):
        configured_snapshot = self.take_dots_set_snapshot(self.configured_set1)
        assert not self.take_dots_equals_snapshot(self.unconfigured_set, configured_snapshot)

    def test_differnt_configurations_not_equal(self):
        set1_snapshot = self.take_dots_set_snapshot(self.configured_set1)
        assert not self.take_dots_equals_snapshot(self.configured_set2, set1_snapshot)

    def test_configuration_equals_flip_rotate_move1(self):
        self.check_configuration_equals_flip_rotate_move(self.config1, self.configured_set1)

    def test_configuration_equals_flip_rotate_move2(self):
        self.check_configuration_equals_flip_rotate_move(self.config2, self.configured_set2)

    def check_configuration_equals_flip_rotate_move(self, config, configured_shape):
        for flips in range(config.flips):
            self.unconfigured_set.flip()
        for rotations in range(config.rotations):
            self.unconfigured_set.rotate(clockwise=True)
        self.unconfigured_set.move(config.location)

        configured_snapshot = self.take_dots_set_snapshot(configured_shape)
        assert self.take_dots_equals_snapshot(self.unconfigured_set, configured_snapshot)

    def test_set_config(self):
        self.configured_set1.config = self.configured_set2.config
        set2_snapshot = self.take_dots_set_snapshot(self.configured_set2)
        assert self.take_dots_equals_snapshot(self.configured_set1, set2_snapshot)

    def test_set_config_to_self_has_no_effect(self):
        configured_set_before = self.take_dots_set_snapshot(self.configured_set1)
        self.configured_set1.config = self.configured_set1.config
        assert self.take_dots_equals_snapshot(self.configured_set1, configured_set_before)

    def test_reset(self):
        configured_set_before = self.take_dots_set_snapshot(self.configured_set1)
        self.configured_set1.config = self.configured_set2.config
        self.configured_set1.reset()
        assert self.take_dots_equals_snapshot(self.configured_set1, configured_set_before)

    def test_configuration_as_momento(self):
        self.configured_set1.flip()
        self.configured_set1.move((3,5))
        self.configured_set1.rotate(clockwise=False)
        snapshot1 = self.take_dots_set_snapshot(self.configured_set1)
        config1 = self.configured_set1.config

        self.configured_set1.flip()
        self.configured_set1.rotate(clockwise=True)
        self.configured_set1.rotate(clockwise=True)
        snapshot2 = self.take_dots_set_snapshot(self.configured_set1)
        config2 = self.configured_set1.config

        self.configured_set1.reset()
        self.configured_set1.config = config2
        assert self.take_dots_equals_snapshot(self.configured_set1, snapshot2)

        self.configured_set1.config = config1
        assert self.take_dots_equals_snapshot(self.configured_set1, snapshot1)

    def test_dots_sets_hash_does_not_change(self):
        a = hash(self.unconfigured_set)
        self.unconfigured_set.config = self.configured_set1.config
        assert a == hash(self.unconfigured_set)


class TestDotsSetFactory:
    @pytest.fixture(scope='class')
    def dots_set_factory(self):
        return DotsSetFactory()

    def test_create_shapes(self, dots_set_factory):
        shapes = dots_set_factory.create_shapes()
        assert type(shapes) == frozenset
        for shape in shapes:
            assert type(shape) == DotsSet

    def test_create_grids(self, dots_set_factory):
        grids = dots_set_factory.create_grids()
        assert type(grids) == frozenset
        for grid in grids:
            assert type(grid) == DotsGrid


if __name__ == '__main__':
    pytest.main()
