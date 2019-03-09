import tkinter as tk
CELL_Len = 48
DOT_COLOR = '#999999'
BG_COLOR = '#BBBBBB'


class GraphicUtils:
    @staticmethod
    def pos2cell(x, y):
        return y // CELL_Len, x // CELL_Len

    @staticmethod
    def cell2pos(i, j):
        return j * CELL_Len, i * CELL_Len

    @staticmethod
    def cell2bbox(start_cell, end_cell=0, cell_span=1):
        x1, y1 = GraphicUtils.cell2pos(*start_cell)
        x1 += (1 - cell_span) / 2 * CELL_Len
        y1 += (1 - cell_span) / 2 * CELL_Len
        if not end_cell: end_cell = start_cell
        x2, y2 = GraphicUtils.cell2pos(end_cell[0] + 1, end_cell[1] + 1)
        x2 -= (1 - cell_span) / 2 * CELL_Len
        y2 -= (1 - cell_span) / 2 * CELL_Len
        return x1, y1, x2, y2

    @staticmethod
    def circle_in_cell(canvas, cell, cell_span, **kwargs):
        extent = kwargs.get('extent', 359.0)
        style = kwargs.get('style', 'chord')
        outline = kwargs.get('outline', '')
        canvas.create_arc(GraphicUtils.cell2bbox(cell, 0, cell_span),
                          extent=extent, style=style, outline=outline, **kwargs)

    @staticmethod
    def rectangle_over_cells(canvas, start_cell, end_cell, cell_span=1, **kwargs):
        width = kwargs.get('width', 2)
        outline = kwargs.get('outline', 'black')
        canvas.create_rectangle(GraphicUtils.cell2bbox(start_cell, end_cell, cell_span),
                                width=width, outline=outline, **kwargs)


class GraphicDecorator:
    def __init__(self, dot_set, canvas):
        self._dot_set = dot_set
        self._canvas = canvas
        self.tag = str(id(self._dot_set))+'t'
        self.draw()

    def __getattr__(self, item):
        return getattr(self._dot_set, item)

    def draw(self):
        pass

    def hook(self, cell):
        self.hook_loc = cell

    def move_to(self, cell):
        self.move((cell[0]-self.hook_loc[0], cell[1]-self.hook_loc[1]))
        self.hook(cell)


class GridGraphicDecorator(GraphicDecorator):
    def draw(self):
        self._canvas.delete(self.tag)
        start_cell = self.get_config()[2]
        end_cell = (start_cell[0] + 3, start_cell[1] + 3)
        valid_color, invalid_color = self.get_color()
        GraphicUtils.rectangle_over_cells(self._canvas, start_cell, end_cell, fill=valid_color, tags=self.tag)
        for dot in self.get_valid():
            GraphicUtils.circle_in_cell(self._canvas, dot, 0.7, fill=DOT_COLOR, tags=self.tag)
        for dot in self.get_invalid():
            GraphicUtils.circle_in_cell(self._canvas, dot, 0.7, fill=invalid_color, tags=self.tag)


class ShapeGraphicDecorator(GraphicDecorator):
    def draw(self):
        self._canvas.delete(self.tag)
        for dot in self.get():
            GraphicUtils.circle_in_cell(self._canvas, dot, 0.9, fill=self.get_color(), tags=self.tag)


class QuadrillionGraphicDisplay:
    def __init__(self, quadrillion_game):
        self.parent = tk.Tk()
        self.quadrillion = quadrillion_game
        self.quadrillion.attach_view(self)

        self.parent.resizable(0,0)
        self.parent.title('SmartGames Quadrillion')

        vertical_cells, horizontal_cells = self.quadrillion.dot_space_dim
        self.canvas = tk.Canvas(self.parent, width=horizontal_cells*CELL_Len, height=vertical_cells*CELL_Len,
                                bg=BG_COLOR, highlightthickness=0)
        self.canvas.grid(rowspan=int(vertical_cells/2), columnspan=int(horizontal_cells/2), padx=2, pady=2)

        self.items = dict()
        for grid in self.quadrillion.grids.values():
            self.items[id(grid)] = GridGraphicDecorator(grid, self.canvas)
        for shape in self.quadrillion.shapes.values():
            self.items[id(shape)] = ShapeGraphicDecorator(shape, self.canvas)

        self.picked = None
        self.canvas.bind("<Button-1>", self.on_cell_clicked)

        tk.mainloop()

    def update(self, item=None):
        if item is None:
            for item in self.items.values():
                item.draw()
        else:
            self.items[id(item)].draw()

    def on_cell_clicked(self, event):
        if self.picked is None:
            cell = GraphicUtils.pos2cell(event.x, event.y)
            picked = self.quadrillion.pick(cell)
            if picked:
                self.picked = self.items[id(picked)]
                self.picked.hook(cell)
                self.canvas.tag_raise(self.picked.tag)
                self.canvas.focus_set()
                self.canvas.bind("<Key>", self.on_key_press)
                self.canvas.bind("<Motion>", self.on_mouse_motion)
        else:
            self.quadrillion.release()
            self.picked = None
            self.canvas.unbind("<Key>")
            self.canvas.unbind("<Motion>")

    def on_mouse_motion(self, event):
        current_cell = GraphicUtils.pos2cell(event.x, event.y)
        self.picked.move_to(current_cell)
        self.picked.draw()

    def on_key_press(self, event):
        key = event.keysym
        if key == 'Left':
            self.picked.rotate()
        elif key == 'Right':
            self.picked.rotate(-1)
        elif key == 'Up' or key == 'Down':
            self.picked.flip()
        elif key == 'w' or key == 'W':
            self.picked.move((-1, 0))
        elif key == 'a' or key == 'A':
            self.picked.move((0, -1))
        elif key == 's' or key == 'S':
            self.picked.move((1, 0))
        elif key == 'd' or key == 'D':
            self.picked.move((0, 1))
        self.picked.draw()
