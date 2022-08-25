# ################################
#
# Downtime data plotting script
# August 21, 2022
# Version 0.0.2
#
##################################
import tkinter
import tkinter.filedialog
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog as fd

import numpy as np
import pandas as pd
import pytz
from datetime import datetime
import matplotlib.pyplot as plt
from tkcalendar import Calendar, DateEntry
import pathlib

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Imported by Pyinstaller at runtime - splash screen
try:
    import pyi_splash

    pyi_splash.update_text('UI Loaded...')
    pyi_splash.close()
except:
    pass


class App(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        self.init_ui()
        self.labels()
        self.calendars()
        self.comboboxes()
        self.tree_view_table()
        self.file_menues()
        self.buttons()





    def init_ui(self):

        self.mainframe = ttk.Frame(root, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        self.label_frame = ttk.LabelFrame(self.mainframe, text='Filters')
        self.label_frame.grid(column=0, row=0, sticky=W, pady=10)

        # Create a combobox for Equipment Type
        self.selected_equipment = tk.StringVar()

        # Create a combobox for Downtime type
        self.selected_downtime = tk.StringVar()

        # Calendar
        self.string_var_strt = tk.StringVar()
        self.string_var_end = tk.StringVar()



        # Configure tree viewer style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 11, 'bold'), background='grey', foreground='black')  # Modify the font of the headings
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri', 11))  # Modify the font of the body

        # Configure button style
        style.configure('TButton', background='#8B8B83', foreground='black', borderwidth=3, focusthickness=1, focuscolor='red', height=5)

        #w = OptionMenu(self.mainframe, variable, *DROPDOWN_ITEMS)
        #w.grid(column=1, row=1, sticky=W)

    def buttons(self):
        ttk.Button(self.label_frame, text="Calculate",
                   command=self.exec_btn_command).grid(column=5, rowspan=2, row=2, padx=20)
        ttk.Button(self.label_frame, text="Plot",
                   command=self.calculate_downtime_durr).grid(column=6, rowspan=2, row=2, padx=20)

    def comboboxes(self):
        # Create a combobox for Equipment Type
        #self.selected_equipment = tk.StringVar()
        equipment_comb = ttk.Combobox(self.label_frame, textvariable=self.selected_equipment)
        equipment_comb.grid(column=3, row=2, padx=10, sticky=W)
        # self.selected_equipment.trace('w', self.get_selected_equipmnt())
        equipment_comb['values'] = ('All PTA & TMA', 'PTA01', 'PTA02', 'PTA03', 'PTA04',
                                    'PTA05', 'PTA06', 'PTA07', 'PTA08', 'PTA09', 'PTA10',
                                    'TMA11', 'TMA12', 'TMA13', 'TMA14')
        equipment_comb['state'] = 'readonly'
        equipment_comb.current(0)
        equipment_comb.bind('<<ComboboxSelected>>', self.drop_down_activate)

        # Create a combobox for Downtime type
        #self.selected_downtime = tk.StringVar()
        downtime_comb = ttk.Combobox(self.label_frame, textvariable=self.selected_downtime)
        downtime_comb.grid(column=3, row=3, padx=10, sticky=W)
        # self.selected_equipment.trace('w', self.get_selected_equipmnt())
        downtime_comb['values'] = ('Duration & Count', 'Tool Group')
        downtime_comb['state'] = 'readonly'
        downtime_comb.current(0)
        downtime_comb.bind('<<ComboboxSelected>>', self.get_selected_downtime)
    def file_menues(self):
        # Create menu item
        my_menu = Menu(root)
        root.config(menu=my_menu)
        # Create submenus File, Help, etc.
        file_menu = Menu(my_menu, tearoff=False)
        help_menu = Menu(my_menu, tearoff=False)

        # Top bar File menu
        my_menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open data file", command=self.load_datafile)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        # Top bar Help menu
        my_menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=about_msg)
    def calendars(self):
        # Calendar
        #self.string_var_strt = tk.StringVar()
        #self.string_var_end = tk.StringVar()
        # Create Calendar Input drop down - Start Date
        DateEntry(self.label_frame, selectmode='day', textvariable=self.string_var_strt).grid(column=1, row=2, padx=10,
                                                                                              sticky=W)
        self.string_var_strt.trace('w', self.get_start_date)

        # Create Calendar Input drop down - End Date
        DateEntry(self.label_frame, selectmode='day', textvariable=self.string_var_end).grid(column=1, row=3, padx=10,
                                                                                             sticky=W)
        self.string_var_end.trace('w', self.get_end_date)
    def labels(self):
        # Create Calendar Label
        ttk.Label(self.label_frame, text="Start Date:").grid(column=0, row=2, pady=5, sticky=W)
        ttk.Label(self.label_frame, text="End Date").grid(column=0, row=3, pady=5, sticky=W)

        # Create Equipment & Downtime Label
        ttk.Label(self.label_frame, text="Equipment:").grid(column=2, row=2, pady=5, sticky=W)
        ttk.Label(self.label_frame, text="Downtime by:").grid(column=2, row=3, pady=5, sticky=W)


    def tree_view_table(self, *args):
        # Configure tree viewer style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 11, 'bold'), background='grey',
                        foreground='black')  # Modify the font of the headings
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0,
                        font=('Calibri', 11))  # Modify the font of the body

        # Create frame for the treeview widget
        frame_tree = ttk.Frame(self.mainframe)
        frame_tree.grid(column=0, row=2, sticky=W)
        # Create treeview widget
        # Name / Tool Group / Status / Date / Downtime Duration / Downtime Count
        columns = ('Equipment Name', 'Tool Group', 'Status', 'Date', 'Downtime Duration', 'Downtime Count')
        self.tree = ttk.Treeview(frame_tree, show='headings', height=18, style="mystyle.Treeview")
        self.tree['columns'] = ('Equipment Name', 'Tool Group', 'Status', 'Date', 'Downtime Duration', 'Downtime Count')
        self.tree.grid(column=0, row=2, sticky=W)

        # Tree Column
        self.tree.column('#0', width=0, stretch=NO)
        col_count = 0
        for elem in columns:
            self.tree.column(columns[col_count], anchor=W, width=162)
            col_count += 1

        # Tree Heading
        self.tree.heading('#0', text='', anchor=CENTER)
        for elem in columns:
            self.tree.heading(elem, text=elem, anchor=CENTER)

        scrl_bar = tk.Scrollbar(frame_tree, orient=VERTICAL, command=self.tree.yview)
        scrl_bar.grid(column=1, row=2, sticky=NS)
        self.tree.config(yscrollcommand=scrl_bar.set)

        # Default values for the Tree View
        treeview_default = (
            '(empty)...', '(empty)...', '(empty)...', '(empty)...', '(empty)...', '(empty)...')
        self.tree.insert(parent='', index=0, iid=0,
                            values=treeview_default, tags=('even_row',))

        self.tree.tag_configure('odd_row', background='#F0F0FF')
        self.tree.tag_configure('even_row', background='#C1C1CD')
    def tree_insert(self, *args):

        print(self.tree.get_children())
        for item in self.tree.get_children():
            self.tree.delete(item)

        elem_count = 0
        for index in range(0, len(self.df_temp)):
            if elem_count % 2 == 0:  # even row
                self.tree.insert(parent='', index=index, iid=index,
                                values=self.df_temp.loc[index, :].values.tolist(), tags=('odd_row',))
            else:
                self.tree.insert(parent='', index=index, iid=index,
                                values=self.df_temp.loc[index, :].values.tolist(), tags=('even_row',))
            elem_count += 1

        self.tree.tag_configure('odd_row', background='#F0F0FF')
        self.tree.tag_configure('even_row', background='#C1C1CD')

    def plot_graphs(self, *args):
        print("Plots")
        index = ['PTA01', 'PTA02', 'PTA03', 'PTA04',
             'PTA05', 'PTA06', 'PTA07', 'PTA08', 'PTA09', 'PTA10',
             'TMA11', 'TMA12', 'TMA13', 'TMA14']

        #df_3 = pd.DataFrame({'Count': downtime_cnt, 'downtime_minutes': downtime_durr})
        #ax = self.df_accum_time.plot.bar(x='Equipment', y='downtime_minutes', rot=0, title='Downtime')
        #ax.plot()
        #plt.show()
    def get_selected_downtime(self, *args):
        print(self.selected_downtime.get())
        self.tree_insert()

    def drop_down_activate(self, *args):
        self.df_temp = self.df.loc[self.df['cr483_name'] == self.selected_equipment.get()]
        self.df_temp.index = pd.RangeIndex(len(self.df_temp.index))
        print("sorted by name")
        print(self.df_temp)
        self.tree_insert()
    def get_selected_equipmnt(self, *args):
        print(self.selected_equipment.get())
        self.my_selected_equipment = self.selected_equipment.get()


    def get_start_date(self, *args):
        print(self.string_var_strt.get())

    def get_end_date(self, *args):
        print(self.string_var_end.get())

    # Execute this function on Button Click Calculate
    def exec_btn_command(self, *args):


        equip_name_arr = []
        equip_time_arr = []
        if self.selected_equipment.get() == 'All PTA & TMA':
            print("all equipment selected")
            equipment_list = ( 'PTA01', 'PTA02', 'PTA03', 'PTA04',
             'PTA05', 'PTA06', 'PTA07', 'PTA08', 'PTA09', 'PTA10',
             'TMA11', 'TMA12', 'TMA13', 'TMA14')
            arrindex = 0

            for num, element in enumerate(equipment_list, start=0):

                self.df_temp = self.df.loc[self.df['cr483_name'] == equipment_list[num]]
                self.df_temp.index = pd.RangeIndex(len(self.df_temp.index))

                print(self.df_temp)
                print("==========================")
                self.calculate_downtime_durr()


                equip_name_arr.append(equipment_list[num])
                equip_time_arr.append(self.downtime_durr_sum)
                #self.df_accum_time.loc[self.df_accum_time.index[num], 'Crane Name'] = equipment_list[num]
                #self.df_accum_time.loc[self.df_accum_time.index[num], 'Downtime Duration'] = self.downtime_durr_sum
                #self.df_accum_time['crane_name'] = equipment_list[num]
                #self.df_accum_time['downtime_durration'] = self.downtime_durr_sum
                print(num, element)
                arrindex += 1
            print("accumulated downtime")


            print("updated dataframe")
            self.tree_insert()
            self.df_accum_time = pd.DataFrame({'Equipment Name':equip_name_arr, 'Downtime': equip_time_arr})
            self.df_temp = self.df_accum_time
            self.tree_insert()
            print(self.df_accum_time)
            index = ['PTA01', 'PTA02', 'PTA03', 'PTA04',
                     'PTA05', 'PTA06', 'PTA07', 'PTA08', 'PTA09', 'PTA10',
                     'TMA11', 'TMA12', 'TMA13', 'TMA14']

            # df_3 = pd.DataFrame({'Count': downtime_cnt, 'downtime_minutes': downtime_durr})
            ax = self.df_accum_time.plot.bar(x='Equipment Name', y='Downtime', rot=0, title='Downtime')
            ax.plot()
            ax.bar_label(ax.containers[0])
            plt.show()
        else:
            print("not all selevted")
            self.calculate_downtime_durr()
            pass
    def calculate_downtime_ver2(self):
        pass

    def calculate_downtime_durr(self, *args):
        """
        This function calculates downtime duration & count
        """

        # Date format for time difference calculation
        date_frmt = '%Y-%m-%d %H:%M:%S'  # '2022-05-26 10:37:08'

        equipment_list = ['PTA01', 'PTA02', 'PTA03', 'PTA04',
                 'PTA05', 'PTA06', 'PTA07', 'PTA08', 'PTA09', 'PTA10',
                 'TMA11', 'TMA12', 'TMA13', 'TMA14']
        self.df_buff = pd.DataFrame()

        # Iterate over each element of the dataframe sorted by equipment name
        # Determine when status changed from Not Available to Available
        # Determine when status changed from Partially Available to Available
        # Record time difference
        for num, element in enumerate(equipment_list, start=0):

            # Sort dataframe by equipment name && Reset index of the dataframe
            self.df_temp = self.df.loc[self.df['cr483_name'] == equipment_list[num]]
            self.df_temp.index = pd.RangeIndex(len(self.df_temp.index))

            # Get first value from first row of dataframe
            mem_date = datetime.strptime(self.df_temp['createdon'].iloc[0], date_frmt)
            mem_status = self.df_temp['cr483_cranestatus'].iloc[0]

            # Set downtime counters
            full_downtime_cnt = 0
            partial_downtime_cnt = 0
            sum_full_downtime_durr = 0
            sum_partial_downtime_durr = 0
            print(self.df_temp)
            print("memory statusd" + mem_status)
            print("mem date")
            print(mem_date)

            for k in range(1, len(self.df_temp)):

                curr_status = self.df_temp['cr483_cranestatus'].iloc[k]                         # Get current status
                curr_date = datetime.strptime(self.df_temp['createdon'].iloc[k], date_frmt)     # Get current date

                # Start of Downtime
                if ((curr_status == 'Not Available' and mem_status == 'Available')
                        or (curr_status == 'Partially Available' and mem_status == 'Available')):
                    mem_date = datetime.strptime(self.df_temp['createdon'].iloc[k], date_frmt)
                    mem_status = self.df_temp['cr483_cranestatus'].iloc[k]
                    print("Change in Status")
                    print("Change in status mem date = ", mem_date)
                else:
                    print("No change in Status")

                # End of Downtime
                if ((curr_status == 'Available' and mem_status == 'Not Available')
                        or (curr_status == 'Partially Available' and mem_status == 'Not Available')):
                    # Record time difference - this is Time of being Fully out of service
                    durr_full_downtime = curr_date - mem_date
                    sum_full_downtime_durr += get_duration(
                        durr_full_downtime.total_seconds())         # Sum of Full Downtime in hrs
                    print("Full downtime duration = ", sum_full_downtime_durr)
                    # Add values to List
                    mem_date = curr_date
                    mem_status = curr_status
                    full_downtime_cnt += 1      # Full downtime counter

                elif ((curr_status == 'Not Available') and (mem_status == 'Partially Available')
                        or (curr_status == 'Available') and (mem_status == 'Partially Available')):
                    # Record time difference - this is Time of being Partially out of service
                    durr_partial_downtime = curr_date - mem_date
                    sum_partial_downtime_durr += get_duration(
                        durr_partial_downtime.total_seconds())      # Sum of Partial Downtime in hrs
                    print("Partial downtime duration = ",  sum_partial_downtime_durr)
                    # Add values to List
                    mem_date = curr_date
                    mem_status = curr_status
                    partial_downtime_cnt += 1   # Partial Downtime counter


            self.df_buff.loc[num, 'Equipment Name'] = equipment_list[num]
            self.df_buff.loc[num, 'Tool Group'] = "All tools"
            self.df_buff.loc[num, 'Status'] = "Not Available"
            self.df_buff.loc[num, 'Date'] = "1984"
            self.df_buff.loc[num, 'Downtime Duration'] = sum_full_downtime_durr
            self.df_buff.loc[num, 'Downtime Count'] = full_downtime_cnt

            self.df_buff.loc[num + len(equipment_list), 'Equipment Name'] = equipment_list[num]
            self.df_buff.loc[num + len(equipment_list), 'Tool Group'] = "All Tools"
            self.df_buff.loc[num + len(equipment_list), 'Status'] = "Partially Available"
            self.df_buff.loc[num + len(equipment_list), 'Date'] = "1984"
            self.df_buff.loc[num + len(equipment_list), 'Downtime Duration'] = sum_partial_downtime_durr
            self.df_buff.loc[num + len(equipment_list), 'Downtime Count'] = partial_downtime_cnt


        self.df_buff = self.df_buff.sort_index(ascending=True)
        self.df_temp = self.df_buff
        self.tree_insert()
        index_1 = self.df_buff.iloc[0:14, 0].values.tolist()
        down_1 = self.df_buff.iloc[0:14, 4].values.tolist()

        down_2 = self.df_buff.iloc[14:len(self.df_buff), 4].values.tolist()
        df_plot = pd.DataFrame({"Not Available": down_1, "Partially Avaialble": down_2}, index=index_1)
        ax = df_plot.plot.bar(rot=0)
        ax.plot()
        plt.show()
        print(down_1)
        print(down_2)
        print(self.df_temp.to_string())
        print('downtime calced')
        print(self.df_temp)
        print(self.df_buff)
        print(self.df_buff.index)
        #self.tree_insert()

    def load_datafile(self, *args):
        file_types = [('Excel files', '*.csv'), ('All files', '*')]  # File type
        # Show the open file dialog
        file_name = fd.askopenfilename()
        print(file_name)
        print(self.string_var_strt.get())
        self.df = pd.read_csv(file_name,
                         usecols=['cr483_name', 'cr483_cranestatus', 'createdon', 'cr483_toolgroup'])  # Columns to read from .csv

        # Reassign order of columns:
        self.df = self.df.reindex(columns=['cr483_name', 'cr483_cranestatus',  'cr483_toolgroup', 'createdon'])
        print(self.df)
        # CreateOn column conversion from Zulu to PST time
        self.df['createdon'] = pd.to_datetime(self.df['createdon'])
        pacific_t = pytz.timezone('US/Pacific')
        self.df['createdon'].dt.tz_convert(pacific_t)
        #self.df['createdon'].dt.strftime('%Y-%m-%d %H:%M:%S')  # Drop timezone from trailing end
        self.df['createdon'] = self.df['createdon'].dt.strftime('%Y-%m-%d %H:%M:%S')


        #self.df.index.rename('conv_date', inplace=True)
        self.df.sort_values(by='createdon', ascending=True, inplace=True)  # Sort by Date
        #self.df['index_col'] = self.df.index
        self.df.index = pd.RangeIndex(len(self.df.index))

        self.df_temp = self.df
        print(self.df)
        print(self.df_temp)
        print('calling tree')
        self.tree_insert()

    def calculate(self):
        print("empty")

def open_text_file(my_choice):
    file_types = [('Excel files', '*.csv'), ('All files', '*')]  # File type
    # Show the open file dialog
    file_name = fd.askopenfilename()

    df = pd.read_csv(file_name, usecols=['cr483_name', 'cr483_cranestatus', 'createdon'])  # Columns to read from .csv

    # CreateOn column conversion from Zulu to PST time
    df.index = pd.to_datetime(df['createdon'])
    pacific_t = pytz.timezone('US/Pacific')
    df.index = df.index.tz_convert(pacific_t)
    df.index = df.index.strftime('%Y-%m-%d %H:%M:%S')  # Drop timezone from trailing end
    df.index.rename('conv_date', inplace=True)
    df.sort_values(by='conv_date', ascending=True, inplace=True)  # Sort by Date
    df['index_col'] = df.index

    s1 = '2022-05-26 10:37:08'
    s2 = '2022-05-27 11:48:22'
    date_frmt = '%Y-%m-%d %H:%M:%S'
    time_1 = datetime.strptime(s1, date_frmt)
    time_2 = datetime.strptime(s2, date_frmt)
    time_diff = time_2 - time_1

    df_2 = df.loc[df['cr483_name'] == my_choice]
    df_2.index.rename('conv_date', inplace=True)
    # Iterate all rows using DataFrame.index
    print(df.index)
    mem_date = '2022-05-26 10:37:08'
    mem_status = 'Available'
    count_dt = 0
    downtime_durr = []
    downtime_cnt = []

    for i in range(len(df_2) - 2):
        # Determine when status changed from Not Available to Available
        # Record time difference

        curr_status = df_2['cr483_cranestatus'].iloc[i]
        next_status = df_2['cr483_cranestatus'].iloc[i + 1]
        curr_date = df_2['index_col'].iloc[i]

        if (curr_status == 'Not Available'):

            mem_date = curr_date
            mem_status = curr_status
            count_dt += 1
            # print(mem_date)


        elif (curr_status == 'Available') and (mem_status == 'Not Available'):
            date_diff = datetime.strptime(curr_date, date_frmt) - datetime.strptime(mem_date, date_frmt)
            mem_status = 'Available'

            print("Downtime duration:")
            print(curr_date + ' - ' + mem_date)
            print(get_duration(date_diff.total_seconds()))
            downtime_durr.append(get_duration(date_diff.total_seconds()))
            downtime_cnt.append(count_dt)
    print(count_dt)
    print("PLots")
    df_3 = pd.DataFrame({'Count': downtime_cnt, 'downtime_minutes': downtime_durr})
    ax = df_3.plot.bar(x='Count', y='downtime_minutes', rot=0, title=my_choice)
    ax.plot()
    plt.show()
    print(df_2.to_string())
    print(time_diff)
    # print(df.to_string())


def get_duration(duration):
    minutes = (duration / 60)
    hours = minutes / 60
    return hours


# About message window
def about_msg():
    top = Toplevel(root)
    top.geometry('%dx%d+%d+%d' % (root_width / 2, root_height / 2, x + 50, y + 50))
    top.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = Tk()
    root.title("Downtime Data Analyzer")
    #img_file_name = "analyzer_icon.png"
    #curr_dirr = pathlib.Path(img_file_name).parent.resolve()
    #img_path = curr_dirr.joinpath(img_file_name)
    #print(img_path)
    #my_icon = tk.PhotoImage(file=img_path)
    #root.iconphoto(True, my_icon)
    root.resizable(False, False)

    # Width and Height for root = Tk()
    root_width = 1000
    root_height = 500

    # Get screen width and height
    win_width = root.winfo_screenwidth()
    win_height = root.winfo_screenheight()

    # Calculate x and y coordinates for the Tk root window
    x = (win_width / 2) - (root_width / 2)
    y = (win_height / 2) - (root_height / 2)

    # Set dimensions and position of the screen
    root.geometry('%dx%d+%d+%d' % (root_width, root_height, x, y))

    myapp = App(root)
    myapp.mainloop()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
