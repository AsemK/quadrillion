import unittest
from dots_set import DotsSet, TwoSidedDotsGrid, Config

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
shapes = [{(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)},
          {(0, 1), (0, 0), (2, 1), (1, 0), (1, 1)},
          {(0, 1), (1, 2), (0, 2), (1, 0), (1, 1)},
          {(0, 0), (2, 1), (2, 0), (1, 0), (1, 1)},
          {(1, 2), (0, 1), (0, 0), (1, 0), (1, 1)},
          {(0, 1), (0, 0), (2, 0), (1, 0), (1, 1)},
          {(0, 1), (1, 2), (0, 0), (1, 1), (0, 2)},
          {(0, 1), (2, 1), (2, 0), (1, 0), (1, 1)}]


def shape_factory(config=None):
    if config is None:
        return DotsSet(shapes[0])
    else:
        return DotsSet(shapes[0], config)


"""
grids:
O . . O        O O O O        O O O O        O O O O
O O O O rot -> O O O . rot -> O O O O rot -> . O O O
O O O O        O O O .        O O O O        . O O O
O O O O        O O O O        O . . O        O O O O
 flip
  |
  v
O O O .        O O O O        O O O O        . O O O
O O O O rot -> O O O O rot -> O . O O rot -> O O . O
O O . O        O . O O        O O O O        O O O O
O O O O        O O O .        . O O O        O O O O
"""
grids_invalid_dots = [{(0, 1), (0, 2)}, {(1, 3), (2, 3)}, {(3, 2), (3, 1)}, {(2, 0), (1, 0)},
                      {(0, 3), (2, 2)}, {(3, 3), (2, 1)}, {(3, 0), (1, 1)}, {(1, 2), (0, 0)}]
grids_height, grids_width = 4, 4
grids = [{(y, x) for y in range(grids_height) for x in range(grids_width)} - invalid
         for invalid in grids_invalid_dots]

def grid_factory(config=None):
    if config is None:
        return TwoSidedDotsGrid(grids_invalid_dots[0], grids_invalid_dots[4],
                                grids_height, grids_width)
    else:
        return TwoSidedDotsGrid(grids_invalid_dots[0], grids_invalid_dots[4],
                                grids_height, grids_width, config)


class DotsSetInstantiationTest(unittest.TestCase):
    def test_instantiation_with_non_dots_fails(self):
        with self.assertRaises(TypeError):
            DotsSet({(2, 3), (3, 1), (4, 5.5)})

    def test_instantiation_with_non_tuples_fails(self):
        with self.assertRaises(TypeError):
            DotsSet({[2, 3], (3, 1), (4, 5)})

    def test_instantiation_with_dots_works(self):
        dots_set = DotsSet(shapes[0])
        self.assertEqual(len(dots_set), len(shapes[0]))
        self.assertTrue(all(dot in dots_set for dot in shapes[0]))
        self.assertTrue(all(dot in shapes[0] for dot in dots_set))


class MovementTest:
    displacement = (3, 4)

    def setUp(self):
        self.dots_set = self.shape_factory()

    def tearDown(self):
        self._test_reset()

    def do_movements_and_check_result(self, *movements, result_shape):
        for move in movements:
            if move == 'f':
                self.dots_set.flip()
            elif move == 'cwr':
                self.dots_set.rotate(clockwise=True)
            elif move == 'ccwr':
                self.dots_set.rotate(clockwise=False)
            elif move == 'm':
                self.dots_set.move(self.displacement)
        self.assertSequenceEqual(self.dots_set, result_shape)

    def test_four_rotations_clockwise(self):
        for shape in self.shapes[1:4] + [self.shapes[0]]:
            self.do_movements_and_check_result('cwr', result_shape=shape)

    def test_four_rotations_counterclockwise(self):
        for shape in self.shapes[3::-1]:
            self.do_movements_and_check_result('ccwr', result_shape=shape)

    def test_two_flips(self):
        for shape in self.shapes[4], self.shapes[0]:
            self.do_movements_and_check_result('f', result_shape=shape)

    def test_rotate_flip(self):
        self.do_movements_and_check_result('ccwr', 'f', result_shape=self.shapes[5])

    def test_flip_rotate(self):
        self.do_movements_and_check_result('f', 'ccwr', result_shape=self.shapes[7])

    def test_move(self):
        displaced_shape = {(y + self.displacement[0], x + self.displacement[1])
                           for y, x in self.shapes[0]}
        self.do_movements_and_check_result('m', result_shape=displaced_shape)

    def test_flip_rotate_move(self):
        displaced_shape = {(y + self.displacement[0], x + self.displacement[1])
                           for y, x in self.shapes[5]}
        self.do_movements_and_check_result('f', 'cwr', 'm', result_shape=displaced_shape)

    def test_move_flip_rotate(self):
        displaced_shape = {(y + self.displacement[0], x + self.displacement[1])
                           for y, x in self.shapes[5]}
        self.do_movements_and_check_result('m', 'f', 'cwr', result_shape=displaced_shape)

    def test_move_flip_rotate_after_reset(self):
        self.test_move_flip_rotate()
        self._test_reset()
        self.test_move_flip_rotate()

    def _test_reset(self):
        self.dots_set.reset()
        self.assertSequenceEqual(self.dots_set, self.shapes[0])
        self.assertEqual(self.dots_set.config, Config(flips=0, rotations=0, location=(0, 0)))


class ConfigTest:
    config1 = Config(flips=1, rotations=3, location=(4, 2))
    config2 = Config(flips=0, rotations=2, location=(3, 7))

    def setUp(self):
        self.configured_set1 = self.shape_factory(self.config1)
        self.configured_set2 = self.shape_factory(self.config2)
        self.unconfigured_set = self.shape_factory()

    def test_congifured_and_unconfigured_are_not_equal(self):
        self.assertNotEqual(self.configured_set1, self.unconfigured_set)

    def test_differnt_configurations_not_equal(self):
        self.assertNotEqual(self.configured_set1, self.configured_set2)

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

        self.assertEqual(self.unconfigured_set, configured_shape)

    def test_set_config(self):
        self.configured_set1.config = self.configured_set2.config
        self.assertEqual(self.configured_set1, self.configured_set2)

    def test_set_config_to_self_has_no_effect(self):
        configured_set_before = set(self.configured_set1)
        self.configured_set1.config = self.configured_set1.config
        self.assertEqual(self.configured_set1, configured_set_before)

    def test_reset(self):
        configured_set_before = set(self.configured_set1)
        self.configured_set1.config = self.configured_set2.config
        self.configured_set1.reset()
        self.assertEqual(self.configured_set1, configured_set_before)

    def test_configurations_as_momentos(self):
        self.configured_set1.flip()
        self.configured_set1.move((3,5))
        self.configured_set1.rotate(clockwise=False)
        snapshot1 = set(self.configured_set1)
        config1 = self.configured_set1.config

        self.configured_set1.flip()
        self.configured_set1.rotate(clockwise=True)
        self.configured_set1.rotate(clockwise=True)
        snapshot2 = set(self.configured_set1)
        config2 = self.configured_set1.config

        self.configured_set1.reset()
        self.configured_set1.config = config2
        self.assertEqual(self.configured_set1, snapshot2)

        self.configured_set1.config = config1
        self.assertEqual(self.configured_set1, snapshot1)


class ShapeMovementTest(MovementTest, unittest.TestCase):
    shapes = shapes
    shape_factory = staticmethod(shape_factory)


class ShapeConfigTest(ConfigTest, unittest.TestCase):
    shape_factory = staticmethod(shape_factory)


class GridMovementTest(MovementTest, unittest.TestCase):
    shapes = grids
    shape_factory = staticmethod(grid_factory)


class GridConfigTest(ConfigTest, unittest.TestCase):
    shape_factory = staticmethod(grid_factory)


if __name__ == '__main__':
    unittest.main()
