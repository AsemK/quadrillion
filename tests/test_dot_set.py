import unittest
from dot_set import DotShape, DotGrid


class TestDotShape(unittest.TestCase):
    """
    shapes1:
    X X        X X        X O        O X
    O X rot -> X O rot -> X X rot -> X X

    shapes2:
    X X O        O X
    O X X rot -> X X
    O O O        X O
    flip
      |
      v
    O X X        X O
    X X O rot -> X X
    O O O        O X

    shapes3:
    X X X        X O        O X X        X X
    X X O rot -> X X rot -> X X X rot -> X X
    O O O        X X        O O O        O X
     flip
      |
      v
    X X O        O X        X X X        X X
    X X X rot -> X X rot -> O X X rot -> X X
    O O O        X X        O O O        X O
    """

    shapes1 = [{(0, 0), (0, 1), (1, 1)},
               {(0, 0), (0, 1), (1, 0)},
               {(0, 0), (1, 0), (1, 1)},
               {(0, 1), (1, 0), (1, 1)}]
    shapes2 = [{(0, 0), (0, 1), (1, 1), (1, 2)},
               {(0, 1), (2, 0), (1, 0), (1, 1)},
               {(0, 1), (1, 0), (1, 1), (0, 2)},
               {(1, 0), (0, 0), (1, 1), (2, 1)}]
    shapes3 = [{(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)},
               {(0, 0), (2, 1), (2, 0), (1, 0), (1, 1)},
               {(0, 1), (1, 2), (0, 2), (1, 0), (1, 1)},
               {(0, 1), (0, 0), (2, 1), (1, 0), (1, 1)},
               {(1, 2), (0, 1), (0, 0), (1, 0), (1, 1)},
               {(0, 1), (2, 1), (2, 0), (1, 0), (1, 1)},
               {(0, 1), (1, 2), (0, 0), (1, 1), (0, 2)},
               {(0, 1), (0, 0), (2, 0), (1, 0), (1, 1)}]

    def setUp(self):
        self.dot1 = DotShape(self.shapes1[0])
        self.dot2 = DotShape(self.shapes2[0])
        self.dot3 = DotShape(self.shapes3[0])

    def test_initial(self):
        self.assertEqual(self.shapes1[0], self.dot1.get())
        self.assertEqual(self.shapes2[0], self.dot2.get())
        self.assertEqual(self.shapes3[0], self.dot3.get())

    def test_rotations_flips_shape1(self):
        for shape in self.shapes1[1:] + [self.shapes1[0]]:
            self.dot1.rotate()
            self.assertEqual(shape, self.dot1.get())

        self.dot1.rotate(2)
        self.assertEqual(self.shapes1[2], self.dot1.get())
        self.dot1.flip()
        self.assertEqual(self.shapes1[1], self.dot1.get())
        self.dot1.flip()
        self.assertEqual(self.shapes1[2], self.dot1.get())

    def test_rotations_flips_shape2(self):
        for shape in [self.shapes2[1], self.shapes2[0]]:
            self.dot2.rotate()
            self.assertEqual(shape, self.dot2.get())

        self.dot2.rotate(3)
        self.assertEqual(self.shapes2[1], self.dot2.get())
        self.dot2.flip()
        self.assertEqual(self.shapes2[3], self.dot2.get())
        self.dot2.flip()
        self.assertEqual(self.shapes2[1], self.dot2.get())

    def test_rotations_flips_shape3(self):
        for shape in self.shapes3[1:4] + [self.shapes3[0]]:
            self.dot3.rotate()
            self.assertEqual(shape, self.dot3.get())

        self.dot3.rotate(3)
        self.assertEqual(self.shapes3[3], self.dot3.get())
        self.dot3.flip()
        self.assertEqual(self.shapes3[5], self.dot3.get())
        for shape in self.shapes3[6:] + self.shapes3[4:6]:
            self.dot3.rotate()
            self.assertEqual(shape, self.dot3.get())
        self.dot3.flip()
        self.assertEqual(self.shapes3[3], self.dot3.get())

    def test_unique_orients(self):
        for dot, shapes in [(self.dot1, self.shapes1), (self.dot2, self.shapes2), (self.dot3, self.shapes3)]:
            configs = dot.get_unique_configs(loc=(0, 0))
            self.assertEqual(len(shapes), len(configs))
            shape_at_configs = [dot._get_at_config(*config) for config in configs]
            for shape in shapes:
                self.assertIn(shape, shape_at_configs)

    def test_movement_away(self):
        flp = 1
        rot = 2
        loc = (3, 5)
        dot1 = DotShape(self.shapes3[0], flp, rot, loc)
        dot2 = DotShape(self.shapes3[0])
        dot2.set_config(flp, rot, loc)

        equivalent_dots1 = {(pos[0] + loc[0], pos[1] + loc[1]) for pos in self.shapes3[6]}
        self.assertEqual(equivalent_dots1, dot1.get())
        self.assertEqual(equivalent_dots1, dot2.get())

        dot1.flip()
        dot2.flip()
        equivalent_dots2 = {(pos[0] + loc[0], pos[1] + loc[1]) for pos in self.shapes3[2]}
        self.assertEqual(equivalent_dots2, dot1.get())
        self.assertEqual(equivalent_dots2, dot2.get())

        dot1.rotate()
        dot2.rotate()
        equivalent_dots2 = {(pos[0] + loc[0], pos[1] + loc[1]) for pos in self.shapes3[3]}
        self.assertEqual(equivalent_dots2, dot1.get())
        self.assertEqual(equivalent_dots2, dot2.get())

        dot1.flip()
        dot2.flip()
        equivalent_dots2 = {(pos[0] + loc[0], pos[1] + loc[1]) for pos in self.shapes3[5]}
        self.assertEqual(equivalent_dots2, dot1.get())
        self.assertEqual(equivalent_dots2, dot2.get())

        dot1.reset()
        dot2.reset()
        self.assertEqual(equivalent_dots1, dot1.get())
        self.assertEqual(self.shapes3[0], dot2.get())


class TestDotGrid(unittest.TestCase):
    """
    grids1:
    O X X O        O O O O        O O O O        O O O O
    O O O O rot -> X O O O rot -> O O O O rot -> O O O X
    O O O O        X O O O        O O O O        O O O X
    O O O O        O O O O        O X X O        O O O O
     flip
      |
      v
    O O O X        X O O O        O O O O        O O O O
    O O O O rot -> O O X O rot -> O X O O rot -> O O O O
    O O X O        O O O O        O O O O        O X O O
    O O O O        O O O O        X O O O        O O O X

    grids2:
    X O O        O O        O O O        O X
    O O O rot -> O O rot -> O O X rot -> O O
                 X O                     O O
     flip
      |
      v
    O O O        O O        O O X        X O
    X O O rot -> O O rot -> O O O rot -> O O
                 O X                     O O
    """
    grids1 = [{(0, 1), (0, 2)}, {(2, 0), (1, 0)}, {(3, 2), (3, 1)}, {(1, 3), (2, 3)},
              {(0, 3), (2, 2)}, {(1, 2), (0, 0)}, {(3, 0), (1, 1)}, {(3, 3), (2, 1)}]
    grids1_dim = (4, 4)

    grids2 = [{(0, 0)}, {(2, 0)}, {(1, 2)}, {(0, 1)},
              {(1, 0)}, {(2, 1)}, {(0, 2)}, {(0, 0)}]
    grids2_dim = (2, 3)

    def setUp(self):
        self.grid1 = DotGrid(self.grids1[0], self.grids1[4], height=self.grids1_dim[0], width=self.grids1_dim[1])
        self.grid2 = DotGrid(self.grids2[0], self.grids2[4], height=self.grids2_dim[0], width=self.grids2_dim[1])

        self.grids1_all = {(h, w) for h in range(self.grids1_dim[0]) for w in range(self.grids1_dim[1])}
        self.grids2_all = {(h, w) for h in range(self.grids2_dim[0]) for w in range(self.grids2_dim[1])}
        self.grids2_all2 = {(w, h) for (h, w) in self.grids2_all}

    def assert_equal_grid(self, dot_grid, expected_grid, expected_all):
        self.assertEqual(expected_grid, dot_grid.get_invalid())
        self.assertEqual(expected_all, dot_grid.get())
        self.assertEqual(expected_all - expected_grid, dot_grid.get_valid())

    def check_two_sides_rotations(self, dot_grid, grids):
        for grid in grids[1:4] + [grids[0]]:
            dot_grid.rotate()
            self.assertEqual(grid, dot_grid.get_invalid())

        dot_grid.flip()
        self.assertEqual(grids[4], dot_grid.get_invalid())

        for grid in grids[5:] + [grids[4]]:
            dot_grid.rotate()
            self.assertEqual(grid, dot_grid.get_invalid())

        dot_grid.flip()
        self.assertEqual(grids[0], dot_grid.get_invalid())

    def test_initial(self):
        self.assertEqual(self.grids1[0], self.grid1.get_invalid())
        self.grid1.flip()
        self.assertEqual(self.grids1[4], self.grid1.get_invalid())

        self.assertEqual(self.grids2[0], self.grid2.get_invalid())
        self.grid2.flip()
        self.assertEqual(self.grids2[4], self.grid2.get_invalid())

    def test_two_sides_rotations_grid1(self):
        self.check_two_sides_rotations(self.grid1, self.grids1)

    def test_two_sides_rotations_grid2(self):
        self.check_two_sides_rotations(self.grid2, self.grids2)

    def test_rotations_flips_grid1(self):
        self.grid1.rotate(3)
        self.assert_equal_grid(self.grid1, self.grids1[3], self.grids1_all)

        self.grid1.flip()
        self.assert_equal_grid(self.grid1, self.grids1[5], self.grids1_all)

        self.grid1.rotate(-3)
        self.assert_equal_grid(self.grid1, self.grids1[6], self.grids1_all)

        self.grid1.flip()
        self.assert_equal_grid(self.grid1, self.grids1[2], self.grids1_all)

        self.grid1.reset()
        self.assert_equal_grid(self.grid1, self.grids1[0], self.grids1_all)

    def test_rotations_flips_grid2(self):
        self.grid2.rotate(6)
        self.assert_equal_grid(self.grid2, self.grids2[2], self.grids2_all)

        self.grid2.flip()
        self.assert_equal_grid(self.grid2, self.grids2[6], self.grids2_all)

        self.grid2.rotate(-7)
        self.assert_equal_grid(self.grid2, self.grids2[7], self.grids2_all2)

        self.grid2.flip()
        self.assert_equal_grid(self.grid2, self.grids2[1], self.grids2_all2)

        self.grid2.reset()
        self.assert_equal_grid(self.grid2, self.grids2[0], self.grids2_all)

    def test_movement_away(self):
        flp = 1
        rot = 2
        loc = (3, 5)
        grid1 = DotGrid(self.grids2[0], self.grids2[4], flp, rot, loc, *self.grids2_dim)
        grid2 = DotGrid(self.grids2[0], self.grids2[4], height=self.grids2_dim[0], width=self.grids2_dim[1])
        grid2.set_config(flp, rot, loc)

        equivalent_dots1 = {(dot[0] + loc[0], dot[1] + loc[1]) for dot in self.grids2[6]}
        equivalent_all1 = {(dot[0] + loc[0], dot[1] + loc[1]) for dot in self.grids2_all}
        self.assert_equal_grid(grid1, equivalent_dots1, equivalent_all1)
        self.assert_equal_grid(grid2, equivalent_dots1, equivalent_all1)

        grid1.flip()
        grid2.flip()
        equivalent_dots2 = {(pos[0] + loc[0], pos[1] + loc[1]) for pos in self.grids2[2]}
        self.assert_equal_grid(grid1, equivalent_dots2, equivalent_all1)
        self.assert_equal_grid(grid2, equivalent_dots2, equivalent_all1)

        grid1.rotate()
        grid2.rotate()
        equivalent_dots2 = {(pos[0] + loc[0], pos[1] + loc[1]) for pos in self.grids2[3]}
        equivalent_all2 = {(dot[0] + loc[0], dot[1] + loc[1]) for dot in self.grids2_all2}
        self.assert_equal_grid(grid1, equivalent_dots2, equivalent_all2)
        self.assert_equal_grid(grid2, equivalent_dots2, equivalent_all2)

        grid1.flip()
        grid2.flip()
        equivalent_dots2 = {(pos[0] + loc[0], pos[1] + loc[1]) for pos in self.grids2[5]}
        self.assert_equal_grid(grid1, equivalent_dots2, equivalent_all2)
        self.assert_equal_grid(grid2, equivalent_dots2, equivalent_all2)

        grid1.reset()
        grid2.reset()
        self.assert_equal_grid(grid1, equivalent_dots1, equivalent_all1)
        self.assert_equal_grid(grid2, self.grids2[0], self.grids2_all)


if __name__ == '__main__':
    unittest.main()
