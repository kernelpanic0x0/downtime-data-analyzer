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
import matplotlib.pyplot as plt

# Seperated out config of plot to just do it once
def config_plot():
    fig, ax = plt.subplots(facecolor='beige')
    ax.set(xlabel='time (s)', ylabel='voltage (mV)',
           title='Graph One????')
    return (fig, ax)

def config_pie():
    fig, ax = plt.subplots()
    #ax.set(xlabel='time (s)', ylabel='voltage (mV)',
    #       title='Graph One????')
    return (fig, ax)

class matplotlibSwitchGraphs(Frame):
    def __init__(self, master, myData, date_picker_arr):
        print("This is me data", myData)
        print("This is my date", date_picker_arr)
        Frame.__init__(self, master)
        self.master = master
        self.frame = Frame(self.master)
        self.graph_page = "0 / 12"
        self.fig, self.ax = config_plot()
        #self.ax2 = config_plot()
        self.graphIndex = 1
        self.var = StringVar()
        self.canvas = FigureCanvasTkAgg(self.fig, self.master)

        self.config_window()


        # Date picker values from main frame
        self.date_picker_sel = date_picker_arr
        # Data frame values from main frame
        self.dt_val = myData
        self.draw_graph_one()
        #print("From other class", data)
        #self.on_key_press()


    def config_window(self):

        # Configure window Using Grid
        self.mainframe = ttk.Frame(self.master, padding="3 3 12 12")
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Set position of the plot
        self.canvas.get_tk_widget().grid(column=0, rowspan=1, row=0, sticky=N+S+W+E, columnspan=1)

        self.label_frame = ttk.LabelFrame(self.master, text='Switch Graphs', labelanchor="n")
        self.label_frame.grid(column=0, row=2, padx=50, columnspan=1)
        # Set position of the switch graphs button
        ttk.Button(self.label_frame, text="<< Previous",
                   command=self.previous_graph).grid(column=0, rowspan=1, row=0, padx=20)
        # Set position of the switch graphs button
        ttk.Button(self.label_frame, text="Next >>",
                   command=self.next_graph).grid(column=3, rowspan=1, row=0, padx=20)

        # Create Equipment & Downtime Label
        label = ttk.Label(self.label_frame)
        label.config(textvariable=self.var)
        self.var.set('1 / 4')
        label.grid(column=2, rowspan=1, row=0, padx=20)


        # Configure button style
        style = ttk.Style()
        style.theme_use('clam')
        # Configure button style
        style.configure('TButton', background='#8B8B83', foreground='black', borderwidth=3, focusthickness=1,
                        focuscolor='red', height=5)

        # Set position of the switch graphs button
        #ttk.Button(self.master, text="Switch Graphs",
        #           command=self.switch_graphs).grid(column=0, rowspan=1, row=0, padx=20)

        # Set position of the matplotlib toolbar
        # row 4
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master, pack_toolbar=False)
        self.toolbar.grid(column=0, rowspan=1, row=2, sticky=W)
        self.toolbar.update()



    def draw_graph_one(self):
        """
                This function plots System Availability bar chart
                :return:
                """
        print("graph one")
        # Calculating system availability - PM downtime included
        # Availability = Uptime / (Uptime + Downtime)
        print("Executing test py second chart")


        # down_not_available = self.dt_val.iloc[0:int((len(self.dt_val) / 2)), 4].values.tolist()
        # down_partially_available = self.dt_val.iloc[int((len(self.dt_val) / 2)):len(self.dt_val), 4].values.tolist()
        # Set max value for the Y axis based on greatest y-offset

        # total_downtime = [elem_x + elem_y for elem_x, elem_y in zip(down_not_available, down_partially_available)]
        total_downtime = [122.8, 0.0, 16.4, 4.9, 133.4, 77.3, 241.3, 83.4, 16.0, 396.70000000000005, 121.9, 256.1, 0.0,
                          0.0]  # test data
        print("the total downtime is:", total_downtime)

        self.ax.clear()

        self.ax.set_facecolor('lightblue')

        columns = ('PTA01', 'PTA02', 'PTA03', 'PTA04', 'PTA05',
                   'PTA06', 'PTA07', 'PTA08', 'PTA09', 'PTA10',
                   'TMA11', 'TMA12', 'TMA13', 'TMA14')
        col_width = 1 / len(columns)
        print("Col width is:", col_width)
        print("Half of that", col_width / 2)

        rows = ['Availability %: ']
        data = [total_downtime]

        print(data)
        print(type(data))
        availability_arr = []
        colors = []
        date_frmt = '%Y-%m-%d %H:%M:%S'  # '2022-05-26 10:37:08'
        start_date_str = datetime.strptime(self.date_picker_sel[0], '%m/%d/%Y')
        end_date_str = datetime.strptime(self.date_picker_sel[1], '%m/%d/%Y')
        uptime = self.get_duration((end_date_str - start_date_str).total_seconds())

        for elem in data[0]:
            result_availab = (uptime * 100.0 / (uptime + elem))
            availability_arr.append(result_availab)
            if result_availab < 80:
                colors.append('r')
            else:
                colors.append('g')
        print(availability_arr)
        availability_arr = [availability_arr]

        # Get lowest availability value:
        min_val = min(availability_arr[0])
        min_index = []
        # Find index of the lowest value:
        for i in range(0, len(availability_arr[0])):
            if min_val == availability_arr[0][i]:
                min_index.append(i)

        min_index.append(availability_arr[0][min_index[0]])
        print(min_index)

        # Set max value for the Y axis based on greatest y-offset
        # max_offset = max([elem_x + elem_y for elem_x, elem_y in zip(down_not_available, down_partially_available)])
        max_offset = 100
        # tick_value = round(int(max_offset / 8), -2) --- to be fixed
        tick_value = 20
        print("The tick value is", tick_value)

        print("The maximum offset is", max_offset)
        values = np.arange(0, int(max_offset + 10), tick_value)  # (0 , max_y, y_tick)
        value_increment = 1

        # Get some pastel shades for the colors
        # colors = ['Red', 'Yellow']
        n_rows = len(data)
        print("The length of data:", len(data))

        index = np.arange(len(columns)) + 0.3
        bar_width = 0.4
        print(index)
        # Initialize the vertical-offset for the stacked bar chart.
        y_offset = np.zeros(len(columns))
        print("This is init of y offset", y_offset)

        # Plot bars and create text labels for the table

        cell_text = []
        for row in range(n_rows):
            print("This is row", row)
            print("This is index:", index)
            self.ax.bar(index, availability_arr[row], bar_width, bottom=y_offset, color=colors)
            print(colors[row])
            y_offset = y_offset + data[row]
            # cell_text.append(['%1.1f' % (x / 1000.0) for x in y_offset])
            cell_text.append(['%1.1f' % (x / 1.0) for x in availability_arr[row]])
        # Reverse colors and text labels to display the last value at the top.
        # colors = colors[::-1]
        # cell_text.reverse()

        # Add a table at the bottom of the axes
        the_table = self.ax.table(cellText=cell_text,
                                  rowLabels=rows,
                                  rowColours=colors,
                                  colLabels=columns,
                                  cellLoc='center',
                                  loc='bottom')
        the_table.scale(1, 2)


        # plt.subplots_adjust(left=0.25, bottom=0.2)

        # Set titles for the figure and the subplot respectively
        self.fig.suptitle('Availability = Uptime / (Uptime + Downtime)', fontsize=12, fontweight='bold')
        self.ax.legend()
        self.ax.set_ylabel("Availability, %", loc='center')
        self.ax.set_yticks(values * value_increment, ['%d' % val for val in values])
        self.ax.set_xticks([])
        self.ax.set_title('Availability: ' + self.date_picker_sel[0] + " : " + self.date_picker_sel[1])
        self.ax.grid(axis='both')

        # Annotates lowest availability equipment:
        x = min_index[0] + 0.3
        y = min_index[1]
        self.ax.annotate('Lowest Availability', xy=(x, y), xytext=(x + 1, 80),
                         arrowprops=dict(facecolor='black', shrink=0.05))
        # Adjust layout to make room for the table:
        self.fig.tight_layout()
        self.ax.plot()
        self.canvas.draw()

    def draw_graph_two(self):

        """
                This function plots downtime duration Bar Chart
                :return:
                """
        print("graph two")
        # Data for the bar chart - from downtime calculation
        # The buffer is split in two - 0 to 14 and 14 to 28, for two types of downtime
        down_not_available = self.dt_val.iloc[0:int((len(self.dt_val) / 2)), 4].values.tolist()
        down_partially_available = self.dt_val.iloc[int((len(self.dt_val) / 2)):len(self.dt_val), 4].values.tolist()
        data = [down_not_available, down_partially_available]

        columns = ('PTA01', 'PTA02', 'PTA03', 'PTA04', 'PTA05',
                   'PTA06', 'PTA07', 'PTA08', 'PTA09', 'PTA10',
                   'TMA11', 'TMA12', 'TMA13', 'TMA14')

        rows = ['Not Available', 'Partially Available']

        self.ax.clear()
        self.ax.set_facecolor('lightblue')

        # Set max value for the Y axis based on greatest y-offset
        max_offset = max([elem_x + elem_y for elem_x, elem_y in zip(down_not_available, down_partially_available)])
        # tick_value = round(int(max_offset / 8), -2) --- to be fixed
        tick_value = 50
        print("The tick value is", tick_value)

        print("The maximum offset is", max_offset)
        values = np.arange(0, int(max_offset + 25), tick_value)  # (0 , max_y, y_tick)
        value_increment = 1

        # Get some pastel shades for the colors
        colors = ['Red', 'Yellow']
        n_rows = len(data)

        index = np.arange(len(columns)) + 0.3
        bar_width = 0.4

        # Initialize the vertical-offset for the stacked bar chart.
        y_offset = np.zeros(len(columns))
        print("This is init of y offset", y_offset)

        # Plot bars and create text labels for the table
        cell_text = []
        for row in range(n_rows):
            print("This is row", row)
            print("This is index:", index)
            self.ax.bar(index, data[row], bar_width, bottom=y_offset, color=colors[row])
            y_offset = y_offset + data[row]
            # cell_text.append(['%1.1f' % (x / 1000.0) for x in y_offset])
            cell_text.append(['%1.1f' % (x / 1.0) for x in data[row]])
        # Reverse colors and text labels to display the last value at the top.
        # colors = colors[::-1]
        # cell_text.reverse()

        # Add a table at the bottom of the axes
        the_table = self.ax.table(cellText=cell_text,
                                  rowLabels=rows,
                                  rowColours=colors,
                                  colLabels=columns,
                                  loc='bottom')
        the_table.scale(1, 2)

        # plt.subplots_adjust(left=0.25, bottom=0.2)

        # Set titles for the figure and the subplot respectively
        self.fig.suptitle('Downtime Duration', fontsize=12, fontweight='bold')
        self.ax.legend()
        self.ax.set_ylabel("Downtime, hrs", loc='center')
        self.ax.set_yticks(values * value_increment, ['%d' % val for val in values])
        self.ax.set_xticks([])
        self.ax.set_title('Availability: ' + self.date_picker_sel[0] + " : " + self.date_picker_sel[1])
        self.ax.grid(axis='both')
        # Adjust layout to make room for the table:
        self.fig.tight_layout()
        self.ax.plot()
        self.canvas.draw()

    def draw_graph_three(self):
        """
        This function calculates system availability and plots it in chart
        :return:
        """
        """
               This function plots donut chart for Tool Group Downtime
               :return:
               """
        print("graph 3")

        # Values for downtime duration in hrs
        data = [221.1, 1067.6000000000001, 69.8, 241.8, 128.6, 229.6, 207.8]
        recipe = ['PM', 'N/A', '5T Hoist', 'Long travel', 'PLC or I/O', 'Extractor', '36T Hoist']

        #data = self.values_time
        #recipe = self.keys_time
        # Values in downtime events by count
        #data_2 = self.values_frequency
        #ingredients_2 = self.keys_frequency



        self.ax.clear()
        self.ax.remove()
        #self.ax.set_facecolor('lightblue')


        #self.ax = plt.subplots(figsize=(9.5, 4.5), subplot_kw=dict(aspect="equal"), facecolor='beige')
        self.ax2 = self.fig.subplots()

        #self.fig, self.ax2 = plt.subplots(figsize=(6.5, 4.5), subplot_kw=dict(aspect="equal"), facecolor='beige')

        wedges, texts = self.ax2.pie(data, wedgeprops=dict(width=0.5), startangle=-40)


        # Set bat chart
        # x = np.arange(len(recipe))  # the label locations
        # width = 0.35
        # rects1 = ax[1].bar(x, data_2, width, label='Downtime Events')
        # ax[1].set_ylabel('Events')
        # ax[1].set_title('Downtime events count')
        # ax[1].set_xticks(x,ingredients_2 )
        # ax[1].legend()
        # ax[1].bar_label(rects1, padding=3)
        # plt.xticks(rotation=90)
        columns = ('PTA01', 'PTA02', 'PTA03')

        rows = ['Not Available', 'Partially Available']

        bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
        kw = dict(arrowprops=dict(arrowstyle="-"),
                  bbox=bbox_props, zorder=0, va="center")

        for i, p in enumerate(wedges):
            ang = (p.theta2 - p.theta1) / 2. + p.theta1
            y = np.sin(np.deg2rad(ang))
            x = np.cos(np.deg2rad(ang))
            horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
            connectionstyle = "angle,angleA=0,angleB={}".format(ang)
            kw["arrowprops"].update({"connectionstyle": connectionstyle})
            self.ax2.annotate(recipe[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
                        horizontalalignment=horizontalalignment, **kw)

        # Get some pastel shades for the colors
        colors = ['Red', 'Green', 'Blue']
        n_rows = len(data)

        # Initialize the vertical-offset for the stacked bar chart.
        y_offset = np.zeros(len(columns))
        print("This is init of y offset", y_offset)

        # Plot bars and create text labels for the table

        cell_text = [[12 , 5 , 6], [12 , 5 , 6], [12 , 5 , 6]]
        columns = ('Freeze', 'Wind', 'Flood')
        rows = ["Row 1 name", "YRow 2 name", "Row 3 name"]
        #for row in range(n_rows):
        #    cell_text.append(['%1.1f' % (x / 1.0) for x in data[row]])

        # Add a table at the bottom of the axes
        the_table = self.ax2.table(cellText=cell_text,
                                      rowLabels=rows,
                                      rowColours=colors,
                                      colLabels=columns,
                                      loc='bottom',
                                  bbox=[0.25, -0.5, 0.5, 0.3])
        the_table.scale(1, 2)



        # Set titles for the figure and the subplot respectively
        self.fig.suptitle('Equipment Downtime by Tool Group', fontsize=12, fontweight='bold')
        self.ax2.set_title('Downtime by Tool Group: ' + self.date_picker_sel[0] + " : " + self.date_picker_sel[1])
        #self.fig.set_size_inches(5, 5)
        self.ax2.legend()
        # Adjust layout to make room for the table:
        self.fig.tight_layout()
        self.ax2.plot()
        self.canvas.draw()

    def draw_graph_four(self):
        """
        This function plots downtime duration Bar Chart
        :return:
        """
        print("graph 4")
        # Data for the bar chart - from downtime calculation
        # The buffer is split in two - 0 to 14 and 14 to 28, for two types of downtime
        down_not_available = self.dt_val.iloc[0:int((len(self.dt_val) / 2)), 4].values.tolist()
        down_partially_available = self.dt_val.iloc[int((len(self.dt_val) / 2)):len(self.dt_val), 4].values.tolist()
        data = [down_not_available, down_partially_available]

        columns = ('PTA01', 'PTA02', 'PTA03', 'PTA04', 'PTA05',
                   'PTA06', 'PTA07', 'PTA08', 'PTA09', 'PTA10',
                   'TMA11', 'TMA12', 'TMA13', 'TMA14')

        rows = ['Not Available', 'Partially Available']

        self.ax2.remove()
        self.ax = self.fig.subplots()

        self.ax.set_facecolor('lightblue')



        # Set max value for the Y axis based on greatest y-offset
        max_offset = max([elem_x + elem_y for elem_x, elem_y in zip(down_not_available, down_partially_available)])
        #tick_value = round(int(max_offset / 8), -2) --- to be fixed
        tick_value = 50
        print("The tick value is", tick_value)


        print("The maximum offset is", max_offset)
        values = np.arange(0, int(max_offset + 25), tick_value)  # (0 , max_y, y_tick)
        value_increment = 1

        # Get some pastel shades for the colors
        colors = ['Red', 'Yellow']
        n_rows = len(data)

        index = np.arange(len(columns)) + 0.3
        bar_width = 0.4

        # Initialize the vertical-offset for the stacked bar chart.
        y_offset = np.zeros(len(columns))
        print("This is init of y offset", y_offset)

        # Plot bars and create text labels for the table
        cell_text = []
        for row in range(n_rows):
            print("This is row", row)
            print("This is index:", index)
            self.ax.bar(index, data[row], bar_width, bottom=y_offset, color=colors[row])
            y_offset = y_offset + data[row]
            # cell_text.append(['%1.1f' % (x / 1000.0) for x in y_offset])
            cell_text.append(['%1.1f' % (x / 1.0) for x in data[row]])
        # Reverse colors and text labels to display the last value at the top.
        # colors = colors[::-1]
        # cell_text.reverse()

        # Add a table at the bottom of the axes
        the_table = self.ax.table(cellText=cell_text,
                              rowLabels=rows,
                              rowColours=colors,
                              colLabels=columns,
                              loc='bottom')
        the_table.scale(1, 2)

        #plt.subplots_adjust(left=0.25, bottom=0.2)

        # Set titles for the figure and the subplot respectively
        self.fig.suptitle('Downtime Duration', fontsize=12, fontweight='bold')
        self.ax.legend()
        self.ax.set_ylabel("Downtime, hrs", loc='center')
        self.ax.set_yticks(values * value_increment, ['%d' % val for val in values])
        self.ax.set_xticks([])
        self.ax.set_title('Availability: ' + self.date_picker_sel[0] + " : " + self.date_picker_sel[1])
        self.ax.grid(axis='both')
        # Adjust layout to make room for the table:
        self.fig.tight_layout()
        self.ax.plot()
        self.canvas.draw()

    def get_duration(self, duration):
        minutes = (duration / 60)
        hours = minutes / 60
        return round(hours, 1)
    def get_screen_coordinates(self):
        """
        This function determines screen coordinates
        :return: integer values of x & y
        """
        # Get screen width and height
        win_width = self.master.winfo_screenwidth()
        win_height = self.master.winfo_screenheight()

        root_width = 1000
        root_height = 500

        # Calculate x and y coordinates for the Tk root window
        x = (win_width / 2) - (root_width / 2)
        y = (win_height / 2) - (root_height / 2)

        return int(x), int(y)
    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)

    def _quit(self):
        self.master.quit()  # stops mainloop
    def previous_graph(self):
        if self.graphIndex <= 0:
            self.graphIndex = 4
        else:
            self.graphIndex -= 1
        self.switch_graphs()
    def next_graph(self):
        if self.graphIndex >= 4:
            self.graphIndex = 0
        else:
            self.graphIndex += 1
        self.switch_graphs()
    def switch_graphs(self):
        # Need to call the correct draw, whether we're on graph one or two
        print("The index is", self.graphIndex)

        self.var.set(str(self.graphIndex) + "/ 4")

        if self.graphIndex == 1:
            self.draw_graph_one()

        elif self.graphIndex == 2:
            self.draw_graph_two()

        elif self.graphIndex == 3:
            self.draw_graph_three()

        elif self.graphIndex == 4:
            self.draw_graph_four()
            self.graphIndex = 0


if __name__ == '__main__':
    pass