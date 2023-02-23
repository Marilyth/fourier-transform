from matplotlib import pyplot
from matplotlib.widgets import Slider
import math
from typing import *
import numpy as np


class RingSystem:
    def __init__(self):
        self.fig = None
        self.reset_points()
        self.set_period()

    def setup_plot(self):
        self.fig, self.ax = pyplot.subplots(nrows=1, ncols=2)
        self.ax[0].set_aspect('equal')
        self.ax[0].set_title("Ring system")
        self.ax[1].set_aspect('equal')
        self.ax[1].set_title("Fourier transform")
        self.plot, = self.ax[0].plot([], [], zorder=1)
        self.fourier_real, = self.ax[-1].plot([],[], zorder=1)
        self.fourier_imaginary, = self.ax[-1].plot([],[], zorder=1, c="y")
        self.fourier_scatter = self.ax[-1].scatter([], [], c="r", zorder=2)
        self.scatter = self.ax[0].scatter([], [], c="r", zorder=2)
        self.slider_ax = self.fig.add_axes([0.25, 0.1, 0.5, 0.03])
        self.period_slider = Slider(self.slider_ax, "Period [x]", valmin=0.1, valmax=10, valinit=self.period)
        self.period_slider.on_changed(self.update_period)
        self.fig.show()

    def update_period(self, period):
        self.period = period
        self.draw_points()

        self.fig.canvas.draw_idle()

    def set_period(self, period: float = 0, shift: float = 0):
        """Sets the x period for this RingSystem.

        Args:
            period (float, optional): How long one rotation should be for the x coordinate. Defaults to automatic.
            shift (float, optional): An optional shift for the start of the period. Defaults to 0.
        """
        self.shift = shift
        self.period = period

        if self.fig:
            self.period_slider.set_val(self.period)

    def coordinate_to_ring(self, x: float, y: float):
        """Transforms the value y at x into the respective coordinate in the periodic ring.

        Args:
            x (float): _description_ 
            y (float): _description_
        """
        # e^ib = cos(b) + i*sin(b)
        x_radian = ((x + self.shift) / self.period) * 2 * math.pi
        coordinate = y * complex(math.e, 0) ** (complex(0, x_radian))

        return (coordinate.real, coordinate.imag)

    def add_point(self, x: float, y: float):
        self.x_data.append(x)
        self.y_data.append(y)

    def add_function(self, from_x: float, to_x: float, samples: int, f: Callable[[float], float]):
        """Adds a specified amount of datapoints from from_x to to_x for the function f.

        Args:
            from_x (float): The start of the samples.
            to_x (float): The end of the samples.
            samples (int): The amount of data points.
            f (function): The function f(x)
        """
        self.reset_points()
        step = (to_x - from_x) / samples

        for x in np.arange(from_x, to_x + step, step):
            self.add_point(x, f(x))

    def reset_points(self):
        self.x_data = []
        self.y_data = []
        self.fourier_data = {}

    def draw_points(self):
        """Draws the provided data points on a ring.
        """
        if self.x_data:
            if self.period == 0:
                self.period = max(self.x_data) - min(self.x_data)
                self.shift = -min(self.x_data)

            x_ring_vec = []
            y_ring_vec = []
            mean_x, mean_y = 0, 0
            for i in range(len(self.x_data)):
                x, y = self.coordinate_to_ring(self.x_data[i], self.y_data[i])
                mean_x += x / len(self.x_data)
                mean_y += y / len(self.y_data)

                x_ring_vec.append(x)
                y_ring_vec.append(y)

            if not self.fig:
                self.setup_plot()

            self.plot.set_ydata(y_ring_vec)
            self.plot.set_xdata(x_ring_vec)
            self.scatter.set_offsets([(mean_x, mean_y)])
            boundary = max(self.y_data)
            self.plot.axes.set_ylim(-boundary, boundary)
            self.plot.axes.set_xlim(-boundary, boundary)

            self.fourier_data[self.period] = [mean_x, mean_y]
            fourier_list = [(x, self.fourier_data[x]) for x in sorted(self.fourier_data.keys())]
            self.fourier_real.set_ydata([x[1][0] for x in fourier_list])
            self.fourier_real.set_xdata([x[0] for x in fourier_list])
            self.fourier_real.axes.set_ylim(-boundary, boundary)
            self.fourier_real.axes.set_xlim(0, fourier_list[-1][0])
            self.fourier_imaginary.set_ydata([x[1][1] for x in fourier_list])
            self.fourier_imaginary.set_xdata([x[0] for x in fourier_list])
            self.fourier_imaginary.axes.set_ylim(-boundary, boundary)
            self.fourier_imaginary.axes.set_xlim(0, fourier_list[-1][0])
            self.fourier_scatter.set_offsets([self.period, max(self.fourier_data[self.period])])


if __name__ == "__main__":
    system = RingSystem()
    system.add_function(-10, 10, 1000, lambda x: math.cos(x) + math.sin(2*x))
    system.set_period(5)
    system.draw_points()
    input()