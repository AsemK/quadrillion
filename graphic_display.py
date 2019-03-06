import tkinter as tk
CELL_Len = 64


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
        style = kwargs.get('style', 'arc')
        outline = kwargs.get('outline', '')
        width = kwargs.get('width', 0)
        canvas.create_arc(GraphicUtils.cell2bbox(cell, 0, cell_span),
                          width=width, extent=extent, style=style, outline=outline, **kwargs)

    @staticmethod
    def rectangle_over_cells(canvas, start_cell, end_cell, cell_span=1, **kwargs):
        width = kwargs.get('width', 2)
        outline = kwargs.get('outline', 'black')
        canvas.create_rectangle(GraphicUtils.cell2bbox(start_cell, end_cell, cell_span), width=width, outline=outline, **kwargs)


class GraphicDecorator:
    def __init__(self, dot_set, canvas):
        self._dot_set = dot_set
        self._canvas = canvas
        self.draw()

    def __getattr__(self, item):
        getattr(self._dot_set, item)

    def draw(self):
        pass


class GridGraphicDecorator(GraphicDecorator):
    def draw(self):
        self._canvas.delete(id(self._dot_set))
        start_cell = self._dot_set.get_config()[2]
        end_cell = (start_cell[0] + 3, start_cell[1] + 3)
        valid_color, invalid_color = self._dot_set.get_color()
        GraphicUtils.rectangle_over_cells(self._canvas, start_cell, end_cell, fill=valid_color, tag=id(self._dot_set))
        for dot in self._dot_set.get_valid():
            GraphicUtils.circle_in_cell(self._canvas, dot, 0.7, fill='#999999', tag=id(self._dot_set))
        for dot in self._dot_set.get_invalid():
            GraphicUtils.circle_in_cell(self._canvas, dot, 0.7, fill=invalid_color, tag=id(self._dot_set))


class ShapeGraphicDecorator(GraphicDecorator):
    def draw(self):
        self._canvas.delete(id(self._dot_set))
        for dot in self._dot_set.get():
            GraphicUtils.circle_in_cell(self._canvas, dot, 0.9, fill=self._dot_set.get_color(), tag=id(self._dot_set))


class QuadrillionGraphicDisplay:
    def __init__(self, quadrillion_game):
        self.parent = tk.Tk()
        self.quadrillion = quadrillion_game

        self.parent.resizable(0,0)
        self.parent.title('SmartGames Quadrillion')

        vertical_cells, horizontal_cells = self.quadrillion.dot_space_dim
        self.canvas = tk.Canvas(self.parent, width=horizontal_cells*CELL_Len, height=vertical_cells*CELL_Len,
                                bg='#BBBBBB', highlightthickness=0)
        self.canvas.grid(rowspan=int(vertical_cells/2), columnspan=int(horizontal_cells/2), padx=2, pady=2)

        self.items = dict()
        for grid in self.quadrillion.grids.values():
            self.items[id(grid)] = GridGraphicDecorator(grid, self.canvas)
        for shape in self.quadrillion.shapes.values():
            self.items[id(shape)] = ShapeGraphicDecorator(shape, self.canvas)
        tk.mainloop()

