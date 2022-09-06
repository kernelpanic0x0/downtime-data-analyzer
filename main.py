# ################################
#
# Downtime data plotting script
# September 4, 2022
# Version 0.1.1
#
##################################
import tkinter
import tkinter.filedialog
from collections import Counter
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
import babel.numbers
import logging
from tkinter import messagebox

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
        self.ui_labels()
        self.ui_calendars()
        self.ui_comboboxes()
        self.ui_tree_view_table()
        self.ui_file_menues()
        self.ui_buttons()
        self.df_temp = pd.DataFrame()
        self.df = pd.DataFrame()
        self.df_date = pd.DataFrame()
        self.df_buff = pd.DataFrame()

    def init_ui(self):
        """

        This function sets canvas style & theme

        """

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
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 11, 'bold'), background='grey',
                        foreground='black')  # Modify the font of the headings
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0,
                        font=('Calibri', 11))  # Modify the font of the body

        # Configure button style
        style.configure('TButton', background='#8B8B83', foreground='black', borderwidth=3, focusthickness=1,
                        focuscolor='red', height=5)

    def ui_buttons(self):
        """

        This function sets UI Button Elements

        """
        ttk.Button(self.label_frame, text="Calculate Downtime",
                   command=self.button_plot).grid(column=5, rowspan=2, row=2, padx=20)
        ttk.Button(self.label_frame, text="Save Results in .csv",
                   command=self.dict_manipulation).grid(column=6, rowspan=2, row=2, padx=20)
        # ttk.Button(self.label_frame, text="test dict",
        #           command=self.dict_test).grid(column=6, rowspan=2, row=2, padx=20)

    def ui_comboboxes(self):
        """

        This function sets UI ComboBox Elements

        """
        # Create a combobox for Equipment Type
        # self.selected_equipment = tk.StringVar()
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
        # self.selected_downtime = tk.StringVar()
        downtime_comb = ttk.Combobox(self.label_frame, textvariable=self.selected_downtime)
        downtime_comb.grid(column=3, row=3, padx=10, sticky=W)
        # self.selected_equipment.trace('w', self.get_selected_equipmnt())
        downtime_comb['values'] = ('Duration & Count', 'Tool Group')
        downtime_comb['state'] = 'readonly'
        downtime_comb.current(0)
        downtime_comb.bind('<<ComboboxSelected>>', self.get_selected_downtime)

    def ui_file_menues(self):
        """

        This function sets UI Top Menu - File / Open / Exit

        """
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

    def ui_calendars(self):
        """

        This function sets UI Calendar widgets

        """
        # Calendar
        today = datetime.today()
        # Create Calendar Input drop down - Start Date
        self.cal_start_date = DateEntry(self.label_frame, selectmode='day',
                                        date_pattern='mm/dd/y', maxdate=today, textvariable=self.string_var_strt)
        self.cal_start_date.grid(column=1, row=2, padx=10, sticky=W)
        self.cal_start_date.bind("<<DateEntrySelected>>", self.get_start_date)

        # Create Calendar Input drop down - End Date
        self.cal_end_date = DateEntry(self.label_frame, selectmode='day',
                                      date_pattern='mm/dd/y', maxdate=today, textvariable=self.string_var_end)
        self.cal_end_date.grid(column=1, row=3, padx=10, sticky=W)
        self.cal_end_date.bind("<<DateEntrySelected>>", self.get_end_date)

    def ui_labels(self):
        """

        This function sets UI Label Elements

        """
        # Create Calendar Label
        ttk.Label(self.label_frame, text="Start Date:").grid(column=0, row=2, pady=5, sticky=W)
        ttk.Label(self.label_frame, text="End Date").grid(column=0, row=3, pady=5, sticky=W)

        # Create Equipment & Downtime Label
        ttk.Label(self.label_frame, text="Equipment:").grid(column=2, row=2, pady=5, sticky=W)
        ttk.Label(self.label_frame, text="Downtime by:").grid(column=2, row=3, pady=5, sticky=W)

    def ui_tree_view_table(self, *args):
        """

        This function builds Tree View Table
        By default table is populated with <<empty>> text on first row

        """
        # Configure tree viewer style
        style = ttk.Style()
        style.theme_use('clam')

        # Modify the font of the headings
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 11, 'bold'), background='grey',
                        foreground='black')

        # Modify the font of the body
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0,
                        font=('Calibri', 11))

        # Create frame for the treeview widget
        frame_tree = ttk.Frame(self.mainframe)
        frame_tree.grid(column=0, row=2, sticky=W)

        # Create Tree View Table widget
        # Define column names
        columns = ('Equipment Name', 'Tool Group', 'Status', 'Date', 'Downtime Duration (hrs)', 'Downtime Count')
        self.tree = ttk.Treeview(frame_tree, show='headings', height=18, style="mystyle.Treeview")
        self.tree['columns'] = columns
        self.tree.grid(column=0, row=2, sticky=W)

        # Set  Tree View Table <<Column>> for each element of columns list
        self.tree.column('#0', width=0, stretch=NO)
        for elem in range(0, len(columns)):
            self.tree.column(columns[elem], anchor=CENTER, width=162)

        # Set  Tree View Table <<Heading>> for each element of columns list
        self.tree.heading('#0', text='', anchor=CENTER)
        for elem in columns:
            self.tree.heading(elem, text=elem, anchor=CENTER)

        # Set Tree View Table <<ScrollBar>>
        scrl_bar = tk.Scrollbar(frame_tree, orient=VERTICAL, command=self.tree.yview)
        scrl_bar.grid(column=1, row=2, sticky=NS)
        self.tree.config(yscrollcommand=scrl_bar.set)

        # Populate Tree View Table with Default values
        treeview_default = (
            '(empty)...', '(empty)...', '(empty)...', '(empty)...', '(empty)...', '(empty)...')
        self.tree.insert(parent='', index=0, iid=0,
                         values=treeview_default, tags=('even_row',))

        # Set background colors for each row - by default show one row with <<empty text>>
        self.tree.tag_configure('odd_row', background='#F0F0FF')
        self.tree.tag_configure('even_row', background='#C1C1CD')

    def tree_insert(self, *args):
        """

        This function inserts values into Tree View Table

        """

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

        # df_3 = pd.DataFrame({'Count': downtime_cnt, 'downtime_minutes': downtime_durr})
        # ax = self.df_accum_time.plot.bar(x='Equipment', y='downtime_minutes', rot=0, title='Downtime')
        # ax.plot()
        # plt.show()

    def get_selected_downtime(self, *args):
        print(self.selected_downtime.get())
        self.tree_insert()

    def drop_down_activate(self, *args):

        if self.is_file_date_valid():
            print("Sort dataframe by Start Date")
            self.filter_data_by_date(datetime.strptime(self.string_var_strt.get(), '%m/%d/%Y').date(),
                                     datetime.strptime(self.string_var_end.get(), '%m/%d/%Y').date())
            if self.selected_equipment.get() != "All PTA & TMA":
                self.df_temp = self.df_temp.loc[self.df_temp['cr483_name'] == self.selected_equipment.get()]
            self.df_temp.index = pd.RangeIndex(len(self.df_temp.index))
            print("sorted by name")
            print(self.df_temp)
            self.tree_insert()
        else:
            pass

    def get_selected_equipmnt(self, *args):
        print(self.selected_equipment.get())
        self.my_selected_equipment = self.selected_equipment.get()

    def get_start_date(self, *args):
        """
            This function gets START date/time from calendar
            It checks if start date is before end date
            Filter data by given date/time
        """
        start_date = datetime.strptime(self.string_var_strt.get(), '%m/%d/%Y').date()
        end_date = datetime.strptime(self.string_var_end.get(), '%m/%d/%Y').date()
        default_date = datetime.today()

        if start_date > end_date:
            print("Start date can't be after end date")
            self.cal_start_date.set_date(default_date)
        else:
            pass

        print("Sort dataframe by Start Date")
        self.filter_data_by_date(start_date, end_date)

    def get_end_date(self, *args):
        """
            This function gets END date/time from calendar
            It checks if end date is before start date
            Filter data by given date/time
        """
        start_date = datetime.strptime(self.string_var_strt.get(), '%m/%d/%Y').date()
        end_date = datetime.strptime(self.string_var_end.get(), '%m/%d/%Y').date()
        default_date = datetime.today()

        if end_date < start_date:
            print("End date can't be before start date")
            self.cal_end_date.set_date(default_date)
        else:
            pass

        print("Sort dataframe by End Date")
        self.filter_data_by_date(start_date, end_date)

    def filter_data_by_date(self, start_date, end_date):
        """
            This function filter dataframe df_temp by
            start and end date
        """
        print("Start & End dates:")
        start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')

        try:
            self.df_temp = self.df.loc[self.df['createdon'].between(start_date, end_date)]
            self.df_temp.index = pd.RangeIndex(len(self.df_temp.index))
            self.tree_insert()
        except KeyError:
            print("Dataframe was not loaded")

    def convert_date(self, *args):
        print("converting date")
        self.selected_end_date_obj = datetime.strptime(self.string_var_end, '%m/%d/%Y').date()
        print(self.selected_end_date_obj)

    def button_plot(self, *args):
        """
        This function executes calculation of downtime

        """
        if self.is_file_date_valid():
            print("Calculate downtime")
            self.calculate_downtime_durr()
        else:
            pass

    def is_file_date_valid(self, *args):
        """

        This function checks if .csv file imported
        Check if date time range not set

        """
        start_date = datetime.strptime(self.string_var_strt.get(), '%m/%d/%Y').date()
        end_date = datetime.strptime(self.string_var_end.get(), '%m/%d/%Y').date()
        default_date = datetime.today()

        if self.df.empty:
            print("Start date can't be equal to end date")
            messagebox.showwarning("Date File not selected", "You must load .csv file!")
        elif start_date == end_date:
            print("Start date can't be equal to end date")
            messagebox.showwarning("Date Range not selected", "You must select start date!")

        else:
            return True

    def calculate_downtime_durr(self, *args):
        """
        This function calculates downtime duration & count
        """

        # Date format for time difference calculation
        date_frmt = '%Y-%m-%d %H:%M:%S'  # '2022-05-26 10:37:08'
        start_date_str = datetime.strptime(self.string_var_strt.get(), '%m/%d/%Y').strftime('%m/%d/%y')
        end_date_str = datetime.strptime(self.string_var_end.get(), '%m/%d/%Y').strftime('%m/%d/%y')
        drop_down_selection = self.selected_equipment.get()

        if drop_down_selection == 'All PTA & TMA':
            equipment_list = ['PTA01', 'PTA02', 'PTA03', 'PTA04',
                              'PTA05', 'PTA06', 'PTA07', 'PTA08', 'PTA09', 'PTA10',
                              'TMA11', 'TMA12', 'TMA13', 'TMA14']
        else:
            equipment_list = [drop_down_selection]

        self.df_buff = pd.DataFrame()  # Data frame for values going to tree view table
        self.df_date = self.df_temp.copy()  # Data frame stores values filtered by Date Range

        mem_tool = []
        mem_downt_arr = []
        # Dictionary to store deltas for each calculation
        self.downtime_delta = {"equipment_name": [], "tool_group": [], "status": [], "downtime_duration": []}

        # Nested dictionary for each piece of equipment
        self.temp_dict = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {},
                           7: {}, 8: {}, 9: {}, 10: {}, 11: {}, 12: {}, 13: {}}
        for key in range(0,len(self.temp_dict)):
            self.temp_dict[key] = {"equipment_name": [], "tool_group": [], "status": [], "downtime_duration": []}

        # Iterate over each element of the dataframe sorted by equipment name
        # Determine when status changed from Not Available to Available
        # Determine when status changed from Partially Available to Available
        # Record time difference
        for num, element in enumerate(equipment_list, start=0):

            # Sort dataframe by equipment name && Reset index of the dataframe
            self.df_temp = self.df_date.loc[self.df_date['cr483_name'] == equipment_list[num]]
            self.df_temp.index = pd.RangeIndex(len(self.df_temp.index))

            ### test
            self.temp_dict[num]["equipment_name"].append(equipment_list[num])
            self.downtime_delta["equipment_name"].append(equipment_list[num])

            # Get first value from first row of dataframe
            # Reject first row if it has garbage name (early database entries have garbage)
            first_row = 0
            for i in range(0, len(self.df_temp)):

                mem_date = datetime.strptime(self.df_temp['createdon'].iloc[i], date_frmt)
                mem_status = self.df_temp['cr483_cranestatus'].iloc[i]

                if mem_status == "Not Available":
                    self.downtime_delta["tool_group"].append(self.df_temp['cr483_toolgroup'].iloc[i])
                    self.temp_dict[num]["tool_group"].append(self.df_temp['cr483_toolgroup'].iloc[i])
                    break
                elif mem_status == "Partially Available":
                    self.downtime_delta["tool_group"].append(self.df_temp['cr483_toolgroup'].iloc[i])
                    self.temp_dict[num]["tool_group"].append(self.df_temp['cr483_toolgroup'].iloc[i])
                    break
                elif mem_status == "Available":
                    break
                else:
                    first_row += 1

            # Set downtime counters
            full_downtime_cnt = 0
            partial_downtime_cnt = 0
            sum_full_downtime_durr = 0
            sum_partial_downtime_durr = 0

            # For each row of dataframe sorted by equipment name
            for k in range(first_row, len(self.df_temp)):

                curr_status = self.df_temp['cr483_cranestatus'].iloc[k]  # Get current status
                curr_date = datetime.strptime(self.df_temp['createdon'].iloc[k], date_frmt)  # Get current date

                # Start of Downtime
                if ((curr_status == 'Not Available' and mem_status == 'Available')
                        or (curr_status == 'Partially Available' and mem_status == 'Available')):
                    mem_date = datetime.strptime(self.df_temp['createdon'].iloc[k], date_frmt)
                    mem_status = self.df_temp['cr483_cranestatus'].iloc[k]

                    self.temp_dict[num]["tool_group"].append(self.df_temp['cr483_toolgroup'].iloc[k])

                    if drop_down_selection != 'All PTA & TMA':
                        self.downtime_delta["tool_group"].append(self.df_temp['cr483_toolgroup'].iloc[k])
                        self.temp_dict[num]["tool_group"].append(self.df_temp['cr483_toolgroup'].iloc[k])

                    print("Change in status mem date = ", mem_date)
                else:
                    print("No change in Status")

                # End of Downtime
                if ((curr_status == 'Available' and mem_status == 'Not Available')
                        or (curr_status == 'Partially Available' and mem_status == 'Not Available')):
                    # Record time difference - this is Time of being Fully out of service
                    durr_full_downtime = curr_date - mem_date

                    # Downtime duration for each iteration
                    self.downtime_delta["downtime_duration"].append(get_duration(durr_full_downtime.total_seconds()))
                    self.downtime_delta["status"].append(mem_status)

                    self.temp_dict[num]["downtime_duration"].append(get_duration(durr_full_downtime.total_seconds()))
                    self.temp_dict[num]["status"].append(mem_status)

                    # Sum of downtime in hrs - total
                    sum_full_downtime_durr += get_duration(
                        durr_full_downtime.total_seconds())  # Sum of Full Downtime in hrs

                    print("Full downtime duration = ", sum_full_downtime_durr)
                    # Set memory variable
                    mem_date = curr_date
                    mem_status = curr_status
                    full_downtime_cnt += 1  # Full downtime counter

                elif ((curr_status == 'Not Available') and (mem_status == 'Partially Available')
                      or (curr_status == 'Available') and (mem_status == 'Partially Available')):
                    # Record time difference - this is Time of being Partially out of service
                    durr_partial_downtime = curr_date - mem_date

                    # Downtime duration for each iteration
                    self.downtime_delta["downtime_duration"].append(get_duration(durr_partial_downtime.total_seconds()))
                    self.downtime_delta["status"].append(mem_status)

                    self.temp_dict[num]["downtime_duration"].append(get_duration(durr_partial_downtime.total_seconds()))
                    self.temp_dict[num]["status"].append(mem_status)

                    # Sum of partial downtime in hrs - total
                    sum_partial_downtime_durr += get_duration(
                        durr_partial_downtime.total_seconds())  # Sum of Partial Downtime in hrs
                    print("Partial downtime duration = ", sum_partial_downtime_durr)
                    # Set memory variable
                    mem_date = curr_date
                    mem_status = curr_status
                    partial_downtime_cnt += 1  # Partial Downtime counter

            # Write value to first half of the table [ rows 0 to 13 - depends on number of equipment ]
            self.df_buff.loc[num, 'Equipment Name'] = equipment_list[num]
            self.df_buff.loc[num, 'Tool Group'] = "All Tools"
            self.df_buff.loc[num, 'Status'] = "Not Available"
            self.df_buff.loc[num, 'Date'] = start_date_str + "_to_" + end_date_str
            self.df_buff.loc[num, 'Downtime Duration'] = round(sum_full_downtime_durr, 1)
            self.df_buff.loc[num, 'Downtime Count'] = full_downtime_cnt

            # Write values to second half of the table [ rows 13 to 27 - depends on number of equipment]
            self.df_buff.loc[num + len(equipment_list), 'Equipment Name'] = equipment_list[num]
            self.df_buff.loc[num + len(equipment_list), 'Tool Group'] = "All Tools"
            self.df_buff.loc[num + len(equipment_list), 'Status'] = "Partially Available"
            self.df_buff.loc[num + len(equipment_list), 'Date'] = start_date_str + "_to_" + end_date_str
            self.df_buff.loc[num + len(equipment_list), 'Downtime Duration'] = round(sum_partial_downtime_durr, 1)
            self.df_buff.loc[num + len(equipment_list), 'Downtime Count'] = partial_downtime_cnt

        # Store results of downtime calculation in temporary dataframe
        self.df_buff = self.df_buff.sort_index(ascending=True)
        self.df_temp = self.df_buff

        print("Downtime delta")
        print(self.downtime_delta)
        print(self.downtime_delta["tool_group"])
        print(self.downtime_delta["status"])
        print(self.downtime_delta["downtime_duration"])
        print("temp dictionaery")
        print(self.temp_dict[0])
        print(self.temp_dict[1])
        print(self.temp_dict[2])

        # If drop down selection is not for all devices plot pie chart by Tool Group
        if drop_down_selection != 'All PTA & TMA':
            print(self.downtime_delta)
            self.tree_insert()
            self.dict_test()
        else:
            # If drop down selection is for all devices then plot bar chart
            # print(self.df_buff.duplicated(subset='Tool Group', keep=False).sum())
            self.tree_insert()
            self.plot_barchart()
            self.plot_system_availability()
            #self.dict_test()
            self.dict_manipulation()
            plt.show()


    def file_save(self, *args):
        """
        This function saves .csv through file save dialog

        """

        if self.is_file_date_valid():
            try:
                file_to_save = fd.asksaveasfile(mode='w', defaultextension=".csv")
                self.df_temp.to_csv(file_to_save, line_terminator='\r', encoding='utf-8')
                messagebox.showinfo("File Saved Successfully", "File Saved Successfully!")
            except AttributeError:
                logging.exception("User cancelled save operation")

    def load_datafile(self, *args):
        """
         This function loads .csv file
         It converts data column from zulu to PST
         Data is sorted in ascending order
         """
        filetypes = [('Excel files', '*.csv'), ('All files', '*')]  # File type
        data_columns = ['cr483_name', 'cr483_cranestatus', 'createdon', 'cr483_toolgroup']
        data_columns_reindex = ['cr483_name', 'cr483_cranestatus', 'cr483_toolgroup', 'createdon']

        # Show the open file dialog
        file_name = fd.askopenfilename(title='Open .*CSV file', initialdir='/', filetypes=filetypes)
        print(file_name)

        # Check if file was selected
        try:
            self.df = pd.read_csv(file_name, usecols=data_columns, na_filter=False)  # Columns to read from .csv
            self.df = self.df.reindex(columns=data_columns_reindex)  # Reassign order of columns:

            # Check if valid column exists & sort by date
            try:
                # CreateOn column conversion from Zulu to PST time
                self.df['createdon'] = pd.to_datetime(self.df['createdon'])
                pacific_t = pytz.timezone('US/Pacific')
                self.df['createdon'].dt.tz_convert(pacific_t)
                self.df['createdon'] = self.df['createdon'].dt.strftime('%Y-%m-%d %H:%M:%S')
                self.df.sort_values(by='createdon', ascending=True, inplace=True)  # Sort  Data by Date
                # Reset index of dataframe
                self.df.index = pd.RangeIndex(len(self.df.index))

                # Create a deep copy of dataframe
                # Modifications to new dataframe will not modify original

                self.df_temp = self.df.copy(deep=True)
                print(self.df)
                print(self.df_temp)
                print('Insert data into tree view table')
                self.tree_insert()
            except KeyError:
                logging.exception("Wrong column names")
                self.error_message("Wrong column names")

        except FileNotFoundError:
            logging.exception("No File Selected")
            self.error_message("No File Selected")
        except ValueError:
            logging.exception("File Columns missing")
            self.error_message("File Columns missing")

    def error_message(self, str_msg):
        """
            This function prints error message to Tree view Table
        """
        data_columns = self.tree['columns']  # Column names in tree view table

        # For each element in tree view column names
        # Add error message to column of df_temp
        for i in range(0, len(data_columns)):
            self.df_temp.loc[0, data_columns[i]] = str_msg
        self.tree_insert()  # Write message to tree view table

    def calculate(self):
        print("empty")

    def plot_barchart(self):

        # Data for the bar chart - from downtime calculation
        # The buffer is split in two - 0 to 14 and 14 to 28, for two types of downtime
        down_not_available = self.df_buff.iloc[0:int((len(self.df_buff) / 2)), 4].values.tolist()
        down_partially_available = self.df_buff.iloc[int((len(self.df_buff) / 2)):len(self.df_buff), 4].values.tolist()
        data = [down_not_available, down_partially_available]

        columns = ('PTA01', 'PTA02', 'PTA03', 'PTA04', 'PTA05',
                   'PTA06', 'PTA07', 'PTA08', 'PTA09', 'PTA10',
                   'TMA11', 'TMA12', 'TMA13', 'TMA14')

        rows = ['Not Available', 'Partially Available']

        # Set face color and anchor points
        fig, ax = plt.subplots(facecolor='beige', figsize=(9.5, 4.5))
        ax.set_aspect(aspect='auto', anchor='C')
        ax.set_adjustable(adjustable='datalim')
        ax.set_facecolor('lightblue')

        # Set max value for the Y axis based on greatest y-offset
        max_offset = max([elem_x + elem_y for elem_x, elem_y in zip(down_not_available, down_partially_available)])
        #tick_value = round(int(max_offset / 8), -2) --- to be fixed
        tick_value = 50
        print("The tick value is", tick_value)


        print("The maximum offset is", max_offset)
        values = np.arange(0, int(max_offset + 100), tick_value)  # (0 , max_y, y_tick)
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
            plt.bar(index, data[row], bar_width, bottom=y_offset, color=colors[row])
            y_offset = y_offset + data[row]
            # cell_text.append(['%1.1f' % (x / 1000.0) for x in y_offset])
            cell_text.append(['%1.1f' % (x / 1.0) for x in data[row]])
        # Reverse colors and text labels to display the last value at the top.
        # colors = colors[::-1]
        # cell_text.reverse()

        # Add a table at the bottom of the axes
        the_table = plt.table(cellText=cell_text,
                              rowLabels=rows,
                              rowColours=colors,
                              colLabels=columns,
                              loc='bottom')
        the_table.scale(1, 2)
        # Adjust layout to make room for the table:
        plt.subplots_adjust(left=0.25, bottom=0.2)

        plt.ylabel("Downtime, hrs")
        plt.yticks(values * value_increment, ['%d' % val for val in values])
        plt.xticks([])
        plt.title('Downtime Duration: ' + self.string_var_strt.get() + " : " + self.string_var_end.get())
        plt.grid(axis='both')

        # Set titles for the figure and the subplot respectively
        fig.suptitle('Downtime Duration', fontsize=14, fontweight='bold')

        # Get screen coordinates and use them to position bar chart slightly below main canvas
        screen_coord = self.get_screen_coordinates()
        x_shift = screen_coord[0] - 50
        y_shift = screen_coord[1] + 250

        plt.get_current_fig_manager().canvas.manager.set_window_title("Equipment Downtime - combined")
        # Move window "+<x-pos>+<y-pos>"
        plt.get_current_fig_manager().window.wm_geometry("+" + str(x_shift) + "+" + str(y_shift))

        #plt.show()

    def plot_system_availability(self):
        """
        This function calculates system availability and plots it in chart
        :return:
        """
        # Calculating system availability - PM downtime included
        # Availability = Uptime / (Uptime + Downtime)

        down_not_available = self.df_buff.iloc[0:int((len(self.df_buff) / 2)), 4].values.tolist()
        down_partially_available = self.df_buff.iloc[int((len(self.df_buff) / 2)):len(self.df_buff), 4].values.tolist()
        # Set max value for the Y axis based on greatest y-offset

        total_downtime = [elem_x + elem_y for elem_x, elem_y in zip(down_not_available, down_partially_available)]
        #total_downtime = [122.8, 0.0, 16.4, 4.9, 133.4, 77.3, 241.3, 83.4, 16.0, 396.70000000000005, 121.9, 256.1, 0.0, 0.0] # test data
        print(total_downtime)

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
        start_date_str = datetime.strptime(self.string_var_strt.get(), '%m/%d/%Y')
        end_date_str = datetime.strptime(self.string_var_end.get(), '%m/%d/%Y')
        uptime = get_duration((end_date_str - start_date_str).total_seconds())

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

        # Set face color and anchor points
        fig, ax = plt.subplots(facecolor='beige', figsize=(9.5, 4.5))
        ax.set_aspect(aspect='auto', anchor='C')
        ax.set_adjustable(adjustable='datalim')
        ax.set_facecolor('lightblue')

        # Set max value for the Y axis based on greatest y-offset
        #max_offset = max([elem_x + elem_y for elem_x, elem_y in zip(down_not_available, down_partially_available)])
        max_offset = 100
        # tick_value = round(int(max_offset / 8), -2) --- to be fixed
        tick_value = 20
        print("The tick value is", tick_value)

        print("The maximum offset is", max_offset)
        values = np.arange(0, int(max_offset + 10), tick_value)  # (0 , max_y, y_tick)
        value_increment = 1

        # Get some pastel shades for the colors
        #colors = ['Red', 'Yellow']
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
            plt.bar(index, availability_arr[row], bar_width, bottom=y_offset, color=colors)
            print(colors[row])
            y_offset = y_offset + data[row]
            # cell_text.append(['%1.1f' % (x / 1000.0) for x in y_offset])
            cell_text.append(['%1.1f' % (x / 1.0) for x in availability_arr[row]])
        # Reverse colors and text labels to display the last value at the top.
        # colors = colors[::-1]
        # cell_text.reverse()

        # Add a table at the bottom of the axes
        the_table = plt.table(cellText=cell_text,
                              rowLabels=rows,
                              rowColours=colors,
                              colLabels=columns,
                              cellLoc='center',
                              loc='bottom')
        the_table.scale(1, 2)
        # Adjust layout to make room for the table:
        plt.subplots_adjust(left=0.25, bottom=0.2)

        # Set titles for the figure and the subplot respectively
        fig.suptitle('Availability = Uptime / (Uptime + Downtime)', fontsize=14, fontweight='bold')
        plt.ylabel("Availability, %", loc='center')
        plt.yticks(values * value_increment, ['%d' % val for val in values])
        plt.xticks([])
        plt.title('Availability: ' + self.string_var_strt.get() + " : " + self.string_var_end.get())
        plt.grid(axis='both')

        # Annotates lowest availability equipment:
        x = min_index[0] + 0.3
        y = min_index[1]
        ax.annotate('Lowest Availability', xy=(x, y), xytext=(x + 1, 80), arrowprops=dict(facecolor='black', shrink=0.05))

        # Get screen coordinates and use them to position bar chart slightly below main canvas
        screen_coord = self.get_screen_coordinates()
        x_shift = screen_coord[0] - 200
        y_shift = screen_coord[1] + 150

        plt.get_current_fig_manager().canvas.manager.set_window_title("Equipment Availability - %")
        # Move window "+<x-pos>+<y-pos>"
        plt.get_current_fig_manager().window.wm_geometry("+" + str(x_shift) + "+" + str(y_shift))

        #plt.show()

    def dict_manipulation(self):
        # test data:
        combined_dict = {'tool_group': [],'status': [],'downtime_duration': []}
        #test_data = {
        #    0:{'equipment_name': ['PTA01'], 'tool_group': ['Cabin', 'PM', "Extractor", "Bridge", "Some very very long name tool"],'status': ['Partially Available', 'Not Available'],'downtime_duration': [10.7, 122.8, 13.0, 11.0, 25.0]},
        #    1:{'equipment_name': ['PTA02'], 'tool_group': ['PM'], 'status': [], 'downtime_duration': []},
        #    2:{'equipment_name': ['PTA03'], 'tool_group': ['N/A', 'N/A', 'N/A', 'N/A'],'status': ['Not Available', 'Not Available', 'Partially Available', 'Not Available'],'downtime_duration': [8.9, 2.5, 0.0, 16.4]}
        #}
        test_data = self.temp_dict
        # Empty list to store lists after join command
        result = [[], [], [], []]

        # For each element in dictionary join lists for each key
        for num, elem in enumerate(combined_dict, start=0):
            for index in range(0, len(test_data)):
                if test_data[index]['downtime_duration']:  # List is not empty
                    result[num] = result[num] + test_data[index][elem]
            combined_dict[elem].append(result[num])
        logging.info(f"Combined dictionary: {combined_dict}")

        self.tool_frequency = {}
        # For each element in tool group key find tool breakdown frequency
        # Count number of duplicates in the tool_group list
        for items in combined_dict['tool_group'][0]:
            self.tool_frequency[items] = combined_dict['tool_group'][0].count(items)
        counter = Counter(self.tool_frequency)
        self.keys_frequency = list(counter.keys())
        self.values_frequency = list(counter.values())

        logging.info(f"Tool breakdown events Dictionary: {self.tool_frequency}")
        logging.info(f"Tool breakdown events Values: {self.values_frequency}")
        logging.info(f"Tool breakdown events Keys: {self.keys_frequency}")

        tool_downtime = {}
        # For each item in tool group key find downtime per tool group
        for index, items in enumerate(combined_dict['tool_group'][0], start=0):

            if items in tool_downtime:   # Key Already Exists
                tool_downtime[items].append(combined_dict['downtime_duration'][0][index])
            else:  # Key Doesn't Exist
                logging.info("Key Doesn't Exist")
                tool_downtime[items] = [combined_dict['downtime_duration'][0][index]]

        # Find Sum of downtime duration per tool group
        logging.info(f"Tool downtime Dictionary Before Sum(): { tool_downtime.items()}")
        self.tool_time = {dict_key: sum(val) for dict_key, val in tool_downtime.items()}
        logging.info(f"Sum() of downtime per tool group calculated: {self.tool_time}")

        counter = Counter(self.tool_time)
        self.keys_time = list(counter.keys())
        self.values_time = list(counter.values())

        logging.info(f"Tool breakdown frequency Dictionary: {self.tool_time}")
        logging.info(f"Tool breakdown frequency Values: {self.values_time}")
        logging.info(f"Tool breakdown frequency Keys: {self.keys_time}")

        self.plot_tool_downtime()

    def plot_tool_downtime(self):
        """
        This function plots donut chart for Tool Group Downtime
        :return:
        """

        # Values for downtime duration in hrs
        data = self.values_time
        recipe = self.keys_time
        # Values in downtime events by count
        data_2 = self.values_frequency
        ingredients_2 = self.keys_frequency

        fig, ax = plt.subplots( figsize=(9.5, 4.5), subplot_kw=dict(aspect="equal"), facecolor='beige')

        wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-40)

        # Set bat chart
        #x = np.arange(len(recipe))  # the label locations
        #width = 0.35
        #rects1 = ax[1].bar(x, data_2, width, label='Downtime Events')
        #ax[1].set_ylabel('Events')
        #ax[1].set_title('Downtime events count')
        #ax[1].set_xticks(x,ingredients_2 )
        #ax[1].legend()
        #ax[1].bar_label(rects1, padding=3)
        #plt.xticks(rotation=90)

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
            ax.annotate(recipe[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
                        horizontalalignment=horizontalalignment, **kw)


        # Set titles for the figure and the subplot respectively
        fig.suptitle('Equipment Downtime by Tool Group', fontsize=14, fontweight='bold')

        # Get screen coordinates and use them to position bar chart slightly below main canvas
        screen_coord = self.get_screen_coordinates()
        x_shift = screen_coord[0] - 300
        y_shift = screen_coord[1] + 250

        plt.get_current_fig_manager().canvas.manager.set_window_title("Equipment Downtime by Tool Group")
        # Move window "+<x-pos>+<y-pos>"
        plt.get_current_fig_manager().window.wm_geometry("+" + str(x_shift) + "+" + str(y_shift))
        fig.tight_layout()
        plt.show()

    def dict_test(self):
        """
        This function is for plotting Pie Chart
        of Downtime by Events and duration

        """
        # my_dict = {'equipment_name': [], 'tool_group': ['N/A', 'N/A', 'N/A', 'Extractor', 'N/A'],
        # 'status': ['Not Available', 'Not Available', 'Not Available', 'Partially Available', 'Partially Available'],
        # 'downtime_duration': [156.2, 14.9, 24.1, 229.6, 241.3]}
        # dict = { key: }

        my_dict = self.downtime_delta
        # For each element in tool group key find tool breakdown frequency
        tool_frequency = {}
        for items in my_dict['tool_group']:
            tool_frequency[items] = my_dict['tool_group'].count(items)
        counter = Counter(tool_frequency)
        keys_frequency = list(counter.keys())
        values_frequency = list(counter.values())

        print(" Tool breakdown frequency list", tool_frequency)
        print(" Tool breakdown frequency values : ", values_frequency)
        print(" Tool breakdown frequency keys : ", keys_frequency)

        # For each item in tool group key find downtime per tool group
        tool_downtime = {}
        for index, items in enumerate(my_dict['tool_group'], start=0):

            if items in tool_downtime:
                print("key already exists")
                tool_downtime[items].append(my_dict['downtime_duration'][index])
            else:
                print("key doesnt exists")
                tool_downtime[items] = [my_dict['downtime_duration'][index]]

        # Find Sum of downtime duration per tool group
        print("Tool downtime array pre-calc", tool_downtime.items())
        tool_time = {dict_key: sum(val) for dict_key, val in tool_downtime.items()}
        print("Sum of downtime per tool group calculated: ", tool_time)

        counter = Counter(tool_time)
        keys_time = list(counter.keys())
        values_time = list(counter.values())

        print(" Tool breakdown frequency list", tool_time)
        print(" Tool breakdown frequency values : ", values_time)
        print(" Tool breakdown frequency keys : ", keys_time)

        # Pie chart, where the slices will be ordered and plotted counter-clockwise
        fig, axs = plt.subplots(1, 2, figsize=(9.5, 4.5), subplot_kw=dict(aspect="equal"))

        explode = (0, 0.1)
        recipe = ["375 g flour",
                  "75 g sugar",
                  "250 g butter",
                  "300 g berries"]

        # Values for downtime duration in hrs
        data = values_time
        ingredients = keys_time
        # Values in downtime events by count
        data_2 = values_frequency
        ingredients_2 = keys_frequency

        def func(pct, allvals):
            absolute = int(np.round(pct / 100. * np.sum(allvals)))
            return "{:.1f}%\n({:d} hrs)".format(pct, absolute)

        def func2(pct, allvals):
            absolute = int(np.round(pct / 100. * np.sum(allvals)))
            return "{:.1f}%\n({:d} events)".format(pct, absolute)

        wedges, texts, autotexts = axs[0].pie(data_2, autopct=lambda pct: func2(pct, data_2),
                                              textprops=dict(color="w"))

        wedges, texts, autotexts = axs[1].pie(data, autopct=lambda pct: func(pct, data),
                                              textprops=dict(color="w"))

        axs[0].legend(wedges, ingredients,
                      title="Downtime events by Tool Group - " + self.selected_equipment.get(),  # repalce self later
                      loc="lower center",
                      bbox_to_anchor=(0.3, -0.3, 0.5, 1))  # x, y , width, height

        axs[1].legend(wedges, ingredients,
                      title="Downtime Duration by Tool Group - " + self.selected_equipment.get(),  # replace self later
                      loc="lower center",
                      bbox_to_anchor=(0.3, -0.3, 0.5, 1))  # x, y , width, height

        plt.setp(autotexts, size=8, weight="bold")
        # ax.pie(data, shadow=True, explode=explode)
        axs[0].set_title("Downtime Events / Duration by tool group")
        axs[1].set_title(self.string_var_strt.get() + " : " + self.string_var_end.get())
        plt.get_current_fig_manager().canvas.manager.set_window_title("Equipment Downtime by Tool Group")
        plt.show()

    def get_screen_coordinates(self):
        """
        This function determines screen coordinates
        :return: integer values of x & y
        """
        # Get screen width and height
        win_width = root.winfo_screenwidth()
        win_height = root.winfo_screenheight()

        # Calculate x and y coordinates for the Tk root window
        x = (win_width / 2) - (root_width / 2)
        y = (win_height / 2) - (root_height / 2)

        return int(x), int(y)


def get_duration(duration):
    minutes = (duration / 60)
    hours = minutes / 60
    return round(hours, 1)


def about_msg():
    top = Toplevel(root)
    top.geometry('%dx%d+%d+%d' % (root_width / 2, root_height / 2, x + 50, y + 50))
    top.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = Tk()
    root.title("Downtime Data Analyzer v0.1.1")
    # img_file_name = "analyzer_icon.png"
    # curr_dirr = pathlib.Path(img_file_name).parent.resolve()
    # img_path = curr_dirr.joinpath(img_file_name)
    # print(img_path)
    # my_icon = tk.PhotoImage(file=img_path)
    # root.iconphoto(True, my_icon)
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
    logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
    logging.info(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
    myapp = App(root)
    myapp.mainloop()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
