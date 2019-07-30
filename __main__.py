from quadrillion import Quadrillion
from quadrillion_csp import QuadrillionCSPAdapter
from graphic_display import QuadrillionSolverGraphicDisplay
import tkinter

quadrillion = Quadrillion()
quadrillion_csp = QuadrillionCSPAdapter(quadrillion)
view = QuadrillionSolverGraphicDisplay(quadrillion_csp)
tkinter.mainloop()
