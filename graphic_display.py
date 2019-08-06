import traceback
import tkinter as tk
from quadrillion_exception import *
CELL_Len = 32
DOT_COLOR = '#999999'
BG_COLOR = '#BBBBBB'


class QuadrillionGraphicDisplay:
    def __init__(self, quadrillion_game):
        self.master = tk.Tk()
        self._quadrillion = quadrillion_game
        self._quadrillion.attach_view(self)

        self.master.resizable(0, 0)
        self.master.title('SmartGames Quadrillion')

        vertical_cells, horizontal_cells = self._quadrillion.dot_space_dim
        self.canvas = tk.Canvas(self.master, width=horizontal_cells * CELL_Len, height=vertical_cells * CELL_Len,
                                bg=BG_COLOR, highlightthickness=0)
        self.canvas.grid(padx=2, pady=2)

        self._grid_decorator = GridGraphicDecoratorFlyweight(self.canvas)
        self._shape_decorator = ShapeGraphicDecoratorFlyweight(self.canvas)

        self.update()
        self._picked = None
        self.canvas.bind("<Button-1>", self._on_cell_clicked)
        self.canvas.bind("<Key>", self._on_key_press)

    def update(self, item=None):
        if item is None:
            self.canvas.delete('all')
            for item in list(self._quadrillion.grids) + list(self._quadrillion.shapes):
                self._decorate(item).draw()
        else:
            self._decorate(item).draw()

    def _on_cell_clicked(self, event):
        if not self._quadrillion._is_picked:
            if event.num == 1:  # if mouse left button
                self._pick_at((event.x, event.y))
        else:
            if event.num == 1:
                self._release()
            else:
                self._quadrillion.unpick()

    def _on_mouse_motion(self, event):
        if self._quadrillion._is_picked and self._picked:
            current_cell = GraphicUtils.pos2cell(event.x, event.y)
            self._picked.move_to(current_cell)
            self._picked.draw()
        else:
            self._do_after_release()

    def _on_key_press(self, event):
        key = event.keysym
        if key == 'r' or key == 'R':           self._quadrillion.reset()
        elif self._quadrillion._is_picked and self._picked:
            if key == 'Left':                  self._picked.rotate(clockwise=False)
            elif key == 'Right':               self._picked.rotate(clockwise=True)
            elif key == 'Up' or key == 'Down': self._picked.flip()
            elif key == 'w' or key == 'W':     self._picked.move((-1, 0))
            elif key == 'a' or key == 'A':     self._picked.move((0, -1))
            elif key == 's' or key == 'S':     self._picked.move((1, 0))
            elif key == 'd' or key == 'D':     self._picked.move((0, 1))
            elif key == 'Return':              self._release()
            elif key == 'Escape':              self._quadrillion.unpick()
            else: return
            if self._picked:
                self._picked.draw()

    def _pick_at(self, pos):
        try:
            cell = GraphicUtils.pos2cell(*pos)
            picked = self._quadrillion.get_at(cell)
            self._quadrillion.pick([picked])
            self._do_after_pick(picked, cell)
        except (NoItemException, IllegalPickException):
            pass

    def _release(self):
        try:
            self._quadrillion.release()
        except IllegalReleaseException:
            self._quadrillion.unpick()

    def _do_after_pick(self, picked, cell):
        self._picked = self._decorate(picked)
        self._picked.hook(cell)
        self.canvas.tag_raise(self._picked.tag)
        self.canvas.focus_set()
        self.canvas.bind("<Button-3>", self._on_cell_clicked)
        self.canvas.bind("<Motion>", self._on_mouse_motion)

    def _do_after_release(self):
        self._picked = None
        self.canvas.unbind("<Button-3>")
        self.canvas.unbind("<Motion>")

    def _decorate(self, item):
        if item in self._quadrillion.shapes:
            self._shape_decorator.set_dot_set(item)
            return self._shape_decorator
        elif item in self._quadrillion.grids:
            self._grid_decorator.set_dot_set(item)
            return self._grid_decorator


class QuadrillionSolverGraphicDisplay(QuadrillionGraphicDisplay):
    def __init__(self, quadrillion_csp_adapter):
        self._quadrillion_solver = quadrillion_csp_adapter
        super().__init__(self._quadrillion_solver.quadrillion)
        self.master.report_callback_exception = self.report_callback_exception

        control_bar = tk.Frame(self.master, height=40)
        self.solve_button = tk.Button(control_bar, text='Find Solution!', relief='groove',
                                      command=self._quadrillion_solver.solve)
        self.help_button  = tk.Button(control_bar, text='Help me!', relief='groove',
                                      command=self._quadrillion_solver.help)
        self.reset_button = tk.Button(control_bar, text='Reset', relief='groove',
                                      command=self._quadrillion.reset)
        self.save_button = tk.Button(control_bar, text='Save', relief='groove',
                                      command=self._quadrillion.save_game)
        self.load_button = tk.Button(control_bar, text='Load', relief='groove',
                                      command=self._quadrillion.load_game)
        self.text_area = tk.Label(control_bar, anchor='w', text='')

        for item in self.master.grid_slaves():
            item.grid_forget()

        control_bar.pack(side='top', fill='x', expand=True)
        self.canvas.pack(side='bottom', padx=2, pady=2)

        self.solve_button.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.help_button.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        self.save_button.grid(row=0, column=2, sticky="nsew", padx=2, pady=2)
        self.load_button.grid(row=1, column=2, sticky="nsew", padx=2, pady=2)
        self.reset_button.grid(row=0, column=3, rowspan=2, sticky="nsew", padx=2, pady=2)
        self.text_area.grid(row=0, column=1, rowspan=2, sticky="ew", padx=2, pady=2)
        control_bar.columnconfigure(1, weight=1)

        # remove printed messages after clicks or presses
        self.master.bind("<Button>", lambda event: self._show_text(''))
        self.master.bind("<Key>", lambda event: self._show_text(''))

    def report_callback_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, QuadrillionException):
            self._show_text(exc_value) # print quadrillion exceptions messages in the GUI
        else:
            traceback.print_exception(exc_type, exc_value, exc_traceback)

    def _on_key_press(self, event):
        key = event.keysym
        if   key == 'f' or key == 'F': self._quadrillion_solver.solve()
        elif key == 'h' or key == 'H': self._quadrillion_solver.help()
        else: super()._on_key_press(event)

    def _show_text(self, text=''):
        self.text_area.config(text=text)


class GraphicDecoratorFlyweight:
    def __init__(self, canvas):
        self._canvas = canvas
        self._dots_set = None

    def set_dot_set(self, dot_set):
        self._dots_set = dot_set

    def __getattr__(self, item):
        return getattr(self._dots_set, item)

    @property
    def tag(self):
        return str(id(self._dots_set)) + 't'

    def draw(self):
        pass

    def hook(self, cell):
        self.hook_loc = cell

    def move_to(self, cell):
        self.move((cell[0] - self.hook_loc[0], cell[1] - self.hook_loc[1]))
        self.hook(cell)


class GridGraphicDecoratorFlyweight(GraphicDecoratorFlyweight):
    def draw(self):
        self._canvas.delete(self.tag)
        start_cell = self.config.location
        end_cell = (start_cell[0] + 3, start_cell[1] + 3)
        open_color, closed_color = self.color
        GraphicUtils.rectangle_over_cells(self._canvas, start_cell, end_cell, fill=open_color, tags=self.tag)
        for dot in self.open_dots:
            GraphicUtils.circle_in_cell(self._canvas, dot, 0.7, fill=DOT_COLOR, tags=self.tag)
        for dot in self.closed_dots:
            GraphicUtils.circle_in_cell(self._canvas, dot, 0.7, fill=closed_color, tags=self.tag)


class ShapeGraphicDecoratorFlyweight(GraphicDecoratorFlyweight):
    def draw(self):
        self._canvas.delete(self.tag)
        for dot in self._dots_set:
            GraphicUtils.circle_in_cell(self._canvas, dot, 0.9, fill=self.color, tags=self.tag)


class GraphicUtils:
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
    def pos2cell(x, y):
        return y // CELL_Len, x // CELL_Len

    @staticmethod
    def cell2pos(i, j):
        return j * CELL_Len, i * CELL_Len
