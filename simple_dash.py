import tkinter as tk
from tkinter import E, N, S, W

import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from gui import InterfaceStatus, MessageBox
from utils import Interface


class LiveGraph(tk.Frame):
    def __init__(self, parent, interface, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.telemetry = interface

        self.fig = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.line, = self.ax.plot([], [], lw=2)
        self.ax.grid()
        self.xdata, self.ydata = [], []

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=1)

        ani = animation.FuncAnimation(self.fig, self.updatedata, blit=True, interval=10,
                                      repeat=False, init_func=self.initfigure)

    def initfigure(self):
        self.ax.set_ylim(0, 50)
        self.ax.set_xlim(0, 10000)
        del self.xdata[:]
        del self.ydata[:]
        self.line.set_data(self.xdata, self.ydata)
        return self.line,

    def updatedata(self, data):
        dataList = self.telemetry.data
        self.xdata, self.ydata = [], []

        xmin, xmax = self.ax.get_xlim()

        for eachLine in dataList:
            if len(eachLine) > 1:
                x, y = eachLine[1:3]
                self.xdata.append(int(x))
                self.ydata.append(int(y))
        if self.xdata:
            if max(self.xdata) > xmax:
                self.ax.set_xlim(xmin, 2*xmax)

        self.line.set_data(self.xdata, self.ydata)

        return self.line,


class MainApplication(tk.Frame):
    """ TKinter frame holding some useful widgets to control the Launch Pad Station

    Parameters
    ----------
    parent : Tkinter TK() instance
        TK() instance to hold the widgets
    interface : Interface instance
        Interface instance correctly set for the LPS Interface

    """

    def __init__(self, parent, interface, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.lps = interface

        self.lps_messages = MessageBox(
            self, self.lps, borderwidth=2, relief="groove")
        self.graph = LiveGraph(self, self.lps)
        self.lps_status = InterfaceStatus(self, self.lps)

        self.lps_status.grid(
            row=0, column=1, sticky=W+E+N+S, padx=5, pady=5)
        self.graph.grid(
            row=0, rowspan=2, column=2, sticky=W+E+N+S, padx=5, pady=5)
        self.lps_messages.grid(
            row=1, column=1, sticky=W+E+N+S, padx=5, pady=5)


if __name__ == "__main__":
    baudrate = 115200
    path = './data'
    lps = Interface(baudrate=baudrate, path=path, bonjour="TELEMETRY")

    root = tk.Tk()
    root.title("Launch Pad Control")

    MainApplication(root, lps).pack(side="top", fill="both", expand=True)

    root.mainloop()