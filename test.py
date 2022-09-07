import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
from tkinter import *
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler

# Seperated out config of plot to just do it once
def config_plot():
    fig, ax = plt.subplots()
    ax.set(xlabel='time (s)', ylabel='voltage (mV)',
           title='Graph One')
    return (fig, ax)

class matplotlibSwitchGraphs:
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.fig, self.ax = config_plot()
        self.graphIndex = 0
        self.canvas = FigureCanvasTkAgg(self.fig, self.master)
        self.config_window()
        self.draw_graph_one()
        self.frame.pack(expand=YES, fill=BOTH)
        #self.on_key_press()

    def config_window(self):
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self.button = Button(self.master, text="Quit", command=self._quit)
        self.button.pack(side=BOTTOM)
        self.button_switch = Button(self.master, text="Switch Graphs", command=self.switch_graphs)
        self.button_switch.pack(side=BOTTOM)

    def draw_graph_one(self):
        t = np.arange(0.0, 2.0, 0.01)
        s = 1 + np.sin(2 * np.pi * t)
        self.ax.clear() # clear current axes
        self.ax.plot(t, s)
        self.ax.set(title='Graph One')
        self.canvas.draw()

    def draw_graph_two(self):

        labels = ['G1', 'G2', 'G3', 'G4', 'G5']
        men_means = [20, 35, 30, 35, 27]
        women_means = [25, 32, 34, 20, 25]
        men_std = [2, 3, 4, 1, 2]
        women_std = [3, 5, 2, 3, 3]
        self.ax.clear()
        width = 0.35  # the width of the bars: can also be len(x) sequence
        self.ax.bar(labels, men_means, width, yerr=men_std, label='Men')
        self.ax.bar(labels, women_means, width, yerr=women_std, bottom=men_means,
               label='Women')

        self.ax.set_ylabel('Scores')
        self.ax.set_title('Scores by group and gender')
        self.ax.legend()
        #t = np.arange(0.0, 2.0, 0.01)
        #s = 1 + np.cos(2 * np.pi * t)

        self.ax.plot()
        #self.ax.set(title='Graph Two')
        self.canvas.draw()

    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)

    def _quit(self):
        self.master.quit()  # stops mainloop

    def switch_graphs(self):
        # Need to call the correct draw, whether we're on graph one or two
        self.graphIndex = (self.graphIndex + 1 ) % 2
        if self.graphIndex == 0:
            self.draw_graph_one()
        else:
            self.draw_graph_two()

def main():
    root = Tk()
    matplotlibSwitchGraphs(root)
    root.mainloop()

if __name__ == '__main__':
    main()