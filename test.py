import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
import logging
from datetime import datetime
import pathlib

# Seperated out config of plot to just do it once
def config_plot():
    fig, ax = plt.subplots()
    ax.set(xlabel='time (s)', ylabel='voltage (mV)',
           title='Graph One')
    return (fig, ax)

class matplotlibSwitchGraphs(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)

        self.master = master
        self.frame = Frame(self.master)
        self.fig, self.ax = config_plot()
        self.graphIndex = 0
        self.canvas = FigureCanvasTkAgg(self.fig, self.master)
        self.config_window()
        self.draw_graph_one()
        #self.frame.pack(expand=YES, fill=BOTH)
        #self.on_key_press()


    def config_window(self):
        # Using Grid


        self.mainframe = ttk.Frame(self.master, padding="3 3 12 12")
        #self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        #
        #self.label_frame = ttk.LabelFrame(self.mainframe, text='Filters')
        #self.label_frame.grid(column=0, row=0, sticky=W, pady=10)
        #ttk.Label(self.master, text="Start Date:").grid(column=0, row=0, pady=5, sticky=W)

        # Set position of the matplotlib toolbar
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master, pack_toolbar=False)
        self.toolbar.grid(column=0, rowspan=1, row=4, sticky=W)
        self.toolbar.update()

        # Set position of the plot
        self.canvas.get_tk_widget().grid(column=0, rowspan=1, row=0, sticky=W+E)

        # Set position of the quit button
        self.button = Button(self.master, text="Quit", command=self._quit)
        self.button.grid(column=0, rowspan=1, row=3, padx=20)

        # Set position of the switch graphs button
        self.button_switch = Button(self.master, text="Switch Graphs", command=self.switch_graphs)
        self.button_switch.grid(column=0, rowspan=1, row=2, padx=20)

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
    root.title("Downtime Data Analyzer v0.1.1")
    img_file_name = "small_icon.ico"
    curr_dirr = pathlib.Path(img_file_name).parent.resolve()
    img_path = curr_dirr.joinpath(img_file_name)
    print(img_path)
    # my_icon = tk.PhotoImage(file=img_path)
    # root.iconphoto(True, my_icon)

    root.resizable(False, False)

    # Width and Height for root = Tk()
    root_width = 1000
    root_height = 700

    # Get screen width and height
    win_width = root.winfo_screenwidth()
    win_height = root.winfo_screenheight()

    # Calculate x and y coordinates for the Tk root window
    x = (win_width / 2) - (root_width / 2)
    y = (win_height / 2) - (root_height / 2)

    # Set dimensions and position of the screen
    root.geometry('%dx%d+%d+%d' % (root_width, root_height, x, y))
    logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
    logging.info(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    root.iconbitmap(img_path)
    #matplotlibSwitchGraphs(root)
    #root.mainloop()
    my_plots = matplotlibSwitchGraphs(root)
    my_plots.mainloop()

if __name__ == '__main__':
    #main()
    root = Tk()
    root.title("Downtime Data Analyzer v0.1.1")
    img_file_name = "small_icon.ico"
    curr_dirr = pathlib.Path(img_file_name).parent.resolve()
    img_path = curr_dirr.joinpath(img_file_name)
    print(img_path)
    # my_icon = tk.PhotoImage(file=img_path)
    # root.iconphoto(True, my_icon)

    root.resizable(False, False)

    # Width and Height for root = Tk()
    root_width = 1000
    root_height = 700

    # Get screen width and height
    win_width = root.winfo_screenwidth()
    win_height = root.winfo_screenheight()

    # Calculate x and y coordinates for the Tk root window
    x = (win_width / 2) - (root_width / 2)
    y = (win_height / 2) - (root_height / 2)

    # Set dimensions and position of the screen
    root.geometry('%dx%d+%d+%d' % (root_width, root_height, x, y))
    logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
    logging.info(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    root.iconbitmap(img_path)
    # matplotlibSwitchGraphs(root)
    # root.mainloop()
    my_plots = matplotlibSwitchGraphs(root)
    my_plots.mainloop()