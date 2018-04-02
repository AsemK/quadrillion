import tkinter as tk

CELL_Len = 64
HOR_CELLS = 4*4
VER_CELLS = 2*4+2
COLORS = {'s<': '#91D8F7', 's2': '#B93A3F', 'sb': '#80CCC0', 'sU': '#90C74B',
          'sT': '#009D6F', 'sC': '#00AFEE', 's/': '#853B93', 'sZ': '#2A57A4',
          'sF': '#F79734', 'sL': '#ED3338', 's1': '#FFDD23', 's9': '#F078AD',
          'W': '#FFFFFF', 'B': '#373535', 'E': '#999999'}
SHAPES_INIT_POS_SETS = {'s/': {(1, 10), (2, 10), (1, 9), (0, 9), (0, 8)}, 's2': {(2, 8), (3, 10), (3, 9), (2, 9)},
                        'sZ': {(1, 12), (1, 13), (0, 11), (2, 13), (1, 11)}, 's<': {(3, 15), (2, 14), (3, 14)},
                        'sT': {(2, 6), (0, 6), (1, 8), (1, 6), (1, 7)}, 'sU': {(0, 1), (1, 2), (2, 1), (2, 2), (0, 2)},
                        's1': {(2, 7), (3, 8), (3, 6), (3, 7), (3, 5)}, 's9': {(3, 2), (3, 3), (2, 5), (3, 4), (2, 4)},
                        'sC': {(0, 15), (0, 14), (0, 13), (1, 15), (2, 15)}, 'sF': {(1, 3), (1, 4), (1, 5), (2, 3), (0, 4)},
                        'sL': {(0, 0), (3, 0), (3, 1), (2, 0), (1, 0)}, 'sb': {(3, 12), (3, 13), (2, 11), (3, 11), (2, 12)}}
SHAPES_INIT_POS_SETS = {shape: {(pos[0]+VER_CELLS, pos[1]) for pos in SHAPES_INIT_POS_SETS[shape]}
                        for shape in list(SHAPES_INIT_POS_SETS.keys())}


class QuadrillionGraphicDisplay:
    def __init__(self, quadrillion_game):
        self.parent = tk.Tk()
        self.quadrillion = quadrillion_game

        self.parent.resizable(0,0)
        self.parent.title('SmartGames Quadrillion')

        self.solution_button = tk.Button(self.parent, text='Find Solution!', command=self.show_solution)
        self.help_button = tk.Button(self.parent, text='Help me!', command=self.help_solve)
        self.reset_button = tk.Button(self.parent, text='Reset', command=self.reset)
        self.clear_button = tk.Button(self.parent, text='Clear Board', command=self.clear_board)
        self.state_label = tk.Label(self.parent, anchor='w')
        self.result_label = tk.Label(self.parent, anchor='w')
        self.canvas = tk.Canvas(self.parent, width=HOR_CELLS*CELL_Len, height=(VER_CELLS+4)*CELL_Len, bg='#BBBBBB', highlightthickness=0)

        self.solution_button.grid(row=0, columnspan=2, sticky="ew", padx=2, pady=2)
        self.help_button.grid(row=1, columnspan=2, sticky="ew", padx=2, pady=2)
        self.reset_button.grid(row=0, column=6, columnspan=2, sticky="ew", padx=2, pady=2)
        self.clear_button.grid(row=1, column=6, columnspan=2, sticky="ew", padx=2, pady=2)
        self.state_label.grid(row=0, column=2, columnspan=4, sticky="w")
        self.result_label.grid(row=1, column=2, columnspan=4, sticky="w")
        self.canvas.grid(row=2, rowspan=int(VER_CELLS/2), columnspan=int(HOR_CELLS/2), padx=2, pady=2)

        self.reset()
        tk.mainloop()

    @staticmethod
    def pos2cell(x, y):
        return (y)//CELL_Len, (x)//CELL_Len

    @staticmethod
    def cell2pos(i, j):
        return j*CELL_Len, i*CELL_Len

    def cell2bbox(self, start_cell, diameter=1, end_cell=0):
        x1, y1 = self.cell2pos(*start_cell)
        x1 += (1 - diameter)/2 * CELL_Len
        y1 += (1 - diameter)/2 * CELL_Len
        if not end_cell: end_cell = start_cell
        x2, y2 = self.cell2pos(end_cell[0]+1, end_cell[1]+1)
        x2 -= (1 - diameter)/2 * CELL_Len
        y2 -= (1 - diameter)/2 * CELL_Len
        return x1, y1, x2, y2

    def circle_in_cell(self, cell, diameter, fill, outline, tag='all'):
        self.canvas.create_arc(self.cell2bbox(cell, diameter), fill=fill, outline=outline,
                               width=1, extent= 359.0, style='chord', tags=tag)

    def rectangle_over_cells(self, start_cell, end_cell, fill, outline, tag = 'all', width=2, diameter=1):
        self.canvas.create_rectangle(self.cell2bbox(start_cell, diameter, end_cell),
                                     fill=fill, outline=outline, width=width, tags=tag)

    def draw_grid(self, grid, config):
        self.canvas.delete(grid)
        start_cell, black, rotation = config
        dots_cells = self.quadrillion.get_grid_dots(grid, config)
        if black:
            bg = COLORS['B']
            dot_color = COLORS['W']
        else:
            bg = COLORS['W']
            dot_color = COLORS['B']
        end_cell = (start_cell[0]+3, start_cell[1]+3)
        self.rectangle_over_cells(start_cell, end_cell, bg, 'black', grid)
        for i in range(start_cell[0],start_cell[0]+4):
            for j in range(start_cell[1], start_cell[1] + 4):
                self.circle_in_cell((i,j), 0.7, COLORS['E'], '', grid)
        for cell in dots_cells:
            self.circle_in_cell(cell, 0.7, dot_color, '', grid)

    def draw_grids(self):
        for grid, config in self.grids_configs.items():
            self.draw_grid(grid, config)

    def draw_shape(self, shape, pos_set):
        self.canvas.delete(shape)
        for pos in pos_set:
            self.circle_in_cell(pos, 0.9, COLORS[shape], '', shape)

    def draw_shapes(self):
        for shape, pos_set in self.shapes_locs.items():
            self.draw_shape(shape, pos_set)

    def draw_shapes_pane(self):
        self.canvas.create_rectangle(0, VER_CELLS*CELL_Len, HOR_CELLS*CELL_Len, (VER_CELLS+4)*CELL_Len,
                                     fill='#CCCCCC', outline='', width=0, tags='pan')
        for i in range(VER_CELLS,VER_CELLS+4):
            for j in range(0, HOR_CELLS):
                self.circle_in_cell((i,j), 0.7, COLORS['E'], '')
        self.draw_shapes()

    def clear_board(self):
        if self.solution:
            for shape in self.assignments:
                self.solution[shape] = self.assignments[shape]
        self.assignments=dict()
        self.shapes_locs=SHAPES_INIT_POS_SETS.copy()
        self.draw_shapes()
        self.state_label.config(text='')
        self.result_label.config(text='')

    def get_solution(self):
        if self.last_configs != self.grids_configs:
            self.solution = self.quadrillion.get_solution(self.grids_configs, self.assignments)
            self.last_configs = self.grids_configs.copy()
            self.last_assignments = self.assignments.copy()
            return True
        elif self.solution:
            for shape in self.assignments:
                if ((shape in self.last_assignments) and (self.assignments[shape] != self.last_assignments[shape]))\
                  or ((shape in self.solution) and (self.assignments[shape] != self.solution[shape])):
                    self.solution = self.quadrillion.get_solution(self.grids_configs, self.assignments)
                    self.last_assignments = self.assignments.copy()
                    return True
        elif not self.solution:
            for shape in self.last_assignments:
                if shape not in self.assignments\
                  or (shape in self.assignments and self.last_assignments[shape] != self.assignments[shape]):
                    self.solution = self.quadrillion.get_solution(self.grids_configs, self.assignments)
                    self.last_assignments = self.assignments.copy()
                    return True
        return False

    def help_solve(self):
        if len(self.assignments) == 12:
            self.state_label.config(text='A correct solution is already on board!')
            self.result_label.config(text='')
            return
        self.get_solution()
        if self.solution:
            self.state_label.config(text='You are doing well!')
            self.result_label.config(text='A shape was added to the board.')
            shape = (set(self.solution.keys())-set(self.assignments.keys())).pop()
            self.assignments[shape] = self.solution[shape]
            self.last_assignments[shape] = self.solution[shape]
            self.shapes_locs[shape] = self.solution[shape]
            self.draw_shape(shape, self.solution[shape])
        else:
            self.state_label.config(text='No solution for the current situation.')
            self.result_label.config(text='You may need to change something.')

    def show_solution(self):
        if len(self.assignments) == 12:
            self.state_label.config(text='A correct solution is already on board!')
            self.result_label.config(text='')
            return
        self.state_label.config(text='Looking for a solution...')
        is_new_solution = self.get_solution()
        if self.solution:
            for shape in self.solution:
                self.assignments[shape] = self.solution[shape]
            self.shapes_locs = self.assignments.copy()
            self.draw_shapes()
        if is_new_solution:
            if self.solution:
                self.state_label.config(
                    text='Found a solution in ' + str(self.quadrillion.get_search_time()) + ' seconds.')
            else:
                self.state_label.config(
                    text='Found no solution in ' + str(self.quadrillion.get_search_time()) + ' seconds.')
            self.result_label.config(
                text='Search investigated ' + str(self.quadrillion.get_search_iterations()) + ' (partial) assignments.')
        else:
            if self.solution:
                self.state_label.config(
                    text='Already found a solution.')
            else:
                self.state_label.config(
                    text='Already found no solution.')
            self.result_label.config(
                text='No search was needed.')

    def reset(self):
        self.state_label.config(text='')
        self.result_label.config(text='')
        self.canvas.bind("<Button-1>", self.on_cell_clicked)

        self.assignments = self.quadrillion.get_initial_assignments().copy()
        self.grids_configs = self.quadrillion.get_grids_configs().copy()
        self.shapes_locs = SHAPES_INIT_POS_SETS.copy()
        for shape in self.assignments:
            self.shapes_locs[shape] = self.assignments[shape]

        self.moving_item = None
        self.grid_is_moving = False

        self.solution = None
        self.last_assignments = None
        self.last_configs = None

        # FIXME: Only delete shapes on reset and don't redraw grids
        self.canvas.delete('all')
        self.draw_grids()
        self.draw_shapes_pane()

    def on_cell_clicked(self, event):
        if self.moving_item:
            self.place_moving_item()
            self.canvas.unbind("<Motion>")
            self.canvas.unbind("<Key>")
            self.moving_item = None
            self.grid_is_moving = False
        else:
            clicked_cell = self.pos2cell(event.x, event.y)
            self.moving_item = self.quadrillion.is_on_shape(clicked_cell, self.shapes_locs)
            if self.moving_item:
                self.moving_dots = self.shapes_locs[self.moving_item]
            elif not self.assignments:
                self.moving_item = self.quadrillion.is_on_grid(clicked_cell, self.grids_configs)
                if self.moving_item:
                    self.grid_is_moving = True
                    self.displacement = (0, 0)
            if self.moving_item:
                self.canvas.tag_raise(self.moving_item)
                self.start_loc = clicked_cell
                self.canvas.focus_set()
                self.canvas.bind("<Key>", self.on_key_press)
                self.canvas.bind("<Motion>", self.on_mouse_motion)

    def is_valid_motion(self, cell_offset):
        if self.grid_is_moving:
            displacement = (self.displacement[0] + cell_offset[0], self.displacement[1] + cell_offset[1])
            grid_loc = self.grids_configs[self.moving_item][0]
            grid_loc = (grid_loc[0] + displacement[0], grid_loc[1] + displacement[1])
            if 0 <= grid_loc[0] < VER_CELLS - 3 \
                    and 0 <= grid_loc[1] < HOR_CELLS - 3:
                self.displacement = displacement
                return True
        else:
            moving_dots = {(pos[0] + cell_offset[0], pos[1] + cell_offset[1])
                           for pos in self.moving_dots}
            max_y = max(pos[0] for pos in moving_dots)
            max_x = max(pos[1] for pos in moving_dots)
            min_y = min(pos[0] for pos in moving_dots)
            min_x = min(pos[1] for pos in moving_dots)
            if 0 <= min_y < max_y < VER_CELLS + 4 and 0 <= min_x < max_x < HOR_CELLS:
                self.moving_dots = moving_dots
                return True
        return False

    def on_mouse_motion(self, event):
        current_cell = self.pos2cell(event.x, event.y)
        cell_offset = ((current_cell[0]-self.start_loc[0]), (current_cell[1]-self.start_loc[1]))
        if not (cell_offset[0]==0 and cell_offset[1]==0):
            if self.is_valid_motion(cell_offset):
                self.start_loc = current_cell
                self.canvas.move(self.moving_item, cell_offset[1]*CELL_Len, cell_offset[0]*CELL_Len)

    def rotate_flip_moving_item(self, rotation):
        if self.grid_is_moving:
            if rotation:
                self.grids_configs[self.moving_item] = self.quadrillion.rotate_grid(self.grids_configs[self.moving_item], rotation)
            else:
                self.grids_configs[self.moving_item] = self.quadrillion.flip_grid(self.grids_configs[self.moving_item])
            # FIXME: Only move the dots and change colors without redrawing the entire grid
            grid_config = self.quadrillion.move_grid(self.grids_configs[self.moving_item], self.displacement)
            self.draw_grid(self.moving_item, grid_config)
        else:
            if rotation:
                self.moving_dots = self.quadrillion.rotate_shape(self.moving_dots, rotation)
            else:
                self.moving_dots = self.quadrillion.flip_shape(self.moving_dots)
            self.draw_shape(self.moving_item, self.moving_dots)

    def on_key_press(self, event):
        if event.keysym == 'Left':
            rotation = 1
        elif event.keysym == 'Right':
            rotation = -1
        elif event.keysym == 'Up' or event.keysym == 'Down':
            rotation = 0
        else:
            return
        self.rotate_flip_moving_item(rotation)

    def place_moving_item(self):
        if self.moving_item:
            if self.grid_is_moving:
                if self.displacement != (0, 0):
                    grid_config = self.quadrillion.move_grid(self.grids_configs[self.moving_item], self.displacement)
                    if self.quadrillion.is_valid_grid_loc(self.moving_item, grid_config[0], self.grids_configs):
                        self.grids_configs[self.moving_item] = grid_config
                    else:
                        self.canvas.move(self.moving_item, -self.displacement[1]*CELL_Len, -self.displacement[0]*CELL_Len)
            else:
                if max(pos[0] for pos in self.moving_dots) >= VER_CELLS:
                    if self.moving_item in self.assignments:
                        del self.assignments[self.moving_item]
                    self.shapes_locs[self.moving_item] = SHAPES_INIT_POS_SETS[self.moving_item]
                    self.draw_shape(self.moving_item, self.shapes_locs[self.moving_item])
                elif self.quadrillion.is_valid_shape_loc(self.moving_item, self.moving_dots, self.grids_configs, self.assignments):
                    self.assignments[self.moving_item] = self.moving_dots
                    self.shapes_locs[self.moving_item] = self.moving_dots
                else:
                    self.draw_shape(self.moving_item, self.shapes_locs[self.moving_item])
