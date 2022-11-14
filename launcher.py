# ################################
#
# Downtime data plotting script
# September 4, 2022
# Version 0.2.2
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

import plots
import platform
import locale
import sys
from dateutil.relativedelta import relativedelta
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

        self.df_sorted = pd.DataFrame()
        self.df = pd.DataFrame()
        self.df_sorted = pd.DataFrame()
        self.df_date = pd.DataFrame()
        self.df_buff = pd.DataFrame()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.app_version = "v0.2.2"

        self.tool_calc_result = {'duration': [], 'event_count': [], 'keys': []}
        self.launched_flag = []

    def on_closing(self):
        """
        This function to check if user closing window
        :return:
        """
        if messagebox.askokcancel("Quit", "Do you want to close window?"):
            root.quit()
            self.master.destroy()

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
                   command=self.file_save).grid(column=6, rowspan=2, row=2, padx=20)
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
        equipment_comb['values'] = ('PTA & TMA', 'ABRF', 'Gantry', 'CTC',
                                    '2x20', 'MLLB', 'Fiberlabs', 'Raising Girders', 'Hoppers')
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
        help_menu.add_command(label="About", command=self.about_msg)

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

        logging.info(self.tree.get_children())
        for item in self.tree.get_children():
            self.tree.delete(item)

        elem_count = 0
        for index in range(0, len(self.df_sorted)):
            if elem_count % 2 == 0:  # even row
                self.tree.insert(parent='', index=index, iid=index,
                                 values=self.df_sorted.loc[index, :].values.tolist(), tags=('odd_row',))
            else:
                self.tree.insert(parent='', index=index, iid=index,
                                 values=self.df_sorted.loc[index, :].values.tolist(), tags=('even_row',))
            elem_count += 1

        self.tree.tag_configure('odd_row', background='#F0F0FF')
        self.tree.tag_configure('even_row', background='#C1C1CD')

    def get_selected_downtime(self, *args):
        print(self.selected_downtime.get())
        self.tree_insert()

    def drop_down_activate(self, *args):

        if self.is_file_date_valid():
            logging.info("Sort dataframe by Start Date")
            # Filter data by date range based on drop down values
            self.filter_data_by_date(datetime.strptime(self.string_var_strt.get(), '%m/%d/%Y').date(),
                                     datetime.strptime(self.string_var_end.get(), '%m/%d/%Y').date())

            self.filter_data_by_name()
            # Clear dataframe that holds calculation
            self.launched_flag.clear()
            logging.info(f"Data sorted by drop down selection - name : {self.df_sorted}")

            self.tree_insert()
            logging.info("Data inserted into tree view")
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
            logging.warning("Start date can't be after end date")
            self.cal_start_date.set_date(default_date)
        else:
            pass

        logging.info("Sort dataframe by Start Date")
        # Clear dataframe that holds calculation
        self.launched_flag.clear()
        # Filter data by date raw data
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
            logging.warning("End date can't be before start date")
            self.cal_end_date.set_date(default_date)
        else:
            pass

        logging.info("Sort dataframe by End Date")
        # Clear dataframe that holds calculation
        self.launched_flag.clear()
        # Filter data by date raw data
        self.filter_data_by_date(start_date, end_date)

    def filter_data_by_date(self, start_date, end_date):
        """
        This function filter dataframe df_temp by start and end date
        """

        start_date = start_date.strftime('%Y-%m-%d %H:%M:%S')
        end_date = end_date.strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"Start date is: {start_date}")
        logging.info(f"End date is: {end_date}")

        try:
            self.df_sorted = self.df.loc[self.df['createdon'].between(start_date, end_date)]
            self.df_sorted.index = pd.RangeIndex(len(self.df_sorted.index))
            self.filter_data_by_name()
            self.tree_insert()
        except KeyError:
            logging.exception("Dataframe was not loaded")

    def filter_data_by_name(self):
        """
        This function filters data based on drop down selection for equipment name
        :return:
        """

        # Filter rows that contain equipment in drop down selection
        if self.selected_equipment.get() == "PTA & TMA":
            self.df_sorted = self.df_sorted.loc[self.df_sorted['cr483_name'].str.contains("PTA|TMA")]
        elif self.selected_equipment.get() == "Fiberlabs":
            self.df_sorted = self.df_sorted.loc[self.df_sorted['cr483_name'].str.contains("Fiberlab")]

        elif self.selected_equipment.get() == "Raising Girders":
            self.df_sorted = self.df_sorted.loc[self.df_sorted['cr483_name'].str.contains("Girder")]

        elif self.selected_equipment.get() == "Hoppers":
            self.df_sorted = self.df_sorted.loc[self.df_sorted['cr483_name'].str.contains("Hopper")]

        else:
            self.df_sorted = self.df_sorted.loc[self.df_sorted['cr483_name'].str.contains(self.selected_equipment.get())]

        # Re-index data frame
        self.df_sorted.index = pd.RangeIndex(len(self.df_sorted.index))
        logging.info(f"Filtered data by equipment name: {self.df_sorted}")

    def convert_date(self, *args):
        logging.info("Converting date")
        self.selected_end_date_obj = datetime.strptime(self.string_var_end, '%m/%d/%Y').date()
        logging.info(f"Converted date format:{self.selected_end_date_obj}")

    def button_plot(self, *args):
        """
        This function executes calculation of downtime

        """
        if self.is_file_date_valid():
            logging.info("Calculate downtime")
            logging.info(f".csv loaded - user clicked button plot")
            # If date selection not changed do not recalculate
            if not self.launched_flag:

                logging.info(f"The data frame is empty - calculating downtime")
                self.launched_flag.append("Launched")

                # Calculate downtime duration
                self.calculate_downtime_durr()

                # Insert calculated downtime tree table on main canvas
                self.tree_insert()

                # Calculate downtime and events by tool group
                self.calculate_tool_group()

                # Open the top window with plotlib embedded in tkinter
                self.open_top_window()

            else:
                logging.info(f"The data frame is not empty - reopening old window")
                self.open_top_window() # Re-open plots with current data
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
            logging.warning("Start date can't be equal to end date")
            messagebox.showwarning("Date File not selected", "You must load .csv file!")
        elif start_date == end_date:
            logging.warning("Start date can't be equal to end date")
            messagebox.showwarning("Date Range not selected", "You must select start date!")

        else:
            return True

    def change(self, frame, **kwargs):
        self.frame = frame(self, **kwargs)

    def file_save(self, *args):
        """
        This function saves .csv through file save dialog

        """

        if self.is_file_date_valid():
            try:
                file_to_save = fd.asksaveasfile(mode='w', defaultextension=".csv")
                self.df_sorted.to_csv(file_to_save, line_terminator='\r', encoding='utf-8')
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
        logging.info(f"Loaded csv file name is:{file_name}")

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

                self.df_sorted = self.df.copy(deep=True)
                self.filter_data_by_name()
                print(self.df)
                print(self.df_sorted)
                logging.info(f"Filtered data by equipment name: {self.df_sorted}")
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
            self.df_sorted.loc[0, data_columns[i]] = str_msg
        self.tree_insert()  # Write message to tree view table

    def find_latest_entry(self, num):
        """
        This function finds the latest timestap if the current date range doesn't
        contain any values for this equipment
        :return:
        """

        # Find data frame range in months
        # datetime.strptime(self.string_var_strt.get(), '%m/%d/%Y').date()
        lower_date_val = datetime.strptime(self.df['createdon'].min(), '%Y-%m-%d %H:%M:%S').date()
        upper_date_val = datetime.strptime(self.df['createdon'].max(), '%Y-%m-%d %H:%M:%S').date()
        logging.info(f"Upper {lower_date_val.month}")
        logging.info(f"Lower {upper_date_val.month}")
        max_range_months = (upper_date_val.month - lower_date_val.month)
        logging.info(f"Max range in months is {max_range_months}")

        self.df_searched = pd.DataFrame()
        for i in range(1, max_range_months):

            if self.df_searched.empty:
                # Start / end date bounds
                self.this_start_date = self.calendar_start_date - relativedelta(months=i)
                self.this_end_date = self.calendar_start_date

                # Start / end date bounds - string
                self.this_start_date = self.this_start_date.strftime('%Y-%m-%d %H:%M:%S')
                self.this_end_date = self.this_end_date.strftime('%Y-%m-%d %H:%M:%S')

                logging.info(f"This is the date calendar -1 month - {self.this_start_date}")
                logging.info(f"This is the date - {self.this_end_date}")
                self.df_searched = self.df.loc[self.df['createdon'].between(self.this_start_date, self.this_end_date)]

                # Sort dataframe by equipment name && Reset index of the dataframe
                self.df_searched = self.df_searched.loc[self.df_searched['cr483_name'] == self.equipment_list[num]]
                self.df_searched.index = pd.RangeIndex(len(self.df_searched.index))
            else:
                logging.info("Search found most recent entry")
                break
        try:
            last_timestamp = self.df_searched['createdon'].max()  # will cause exception if empty frame
            last_timestamp_index = self.df_searched.loc[self.df_searched['createdon'] == last_timestamp].index.item()

            name_of_equipment = self.df_searched['cr483_name'].iloc[last_timestamp_index]
            name_of_tool = self.df_searched['cr483_toolgroup'].iloc[last_timestamp_index]
            name_of_status = self.df_searched['cr483_cranestatus'].iloc[last_timestamp_index]

            logging.info(f"Index value for searched index {last_timestamp_index}")
            logging.info(f"Searched equipment name {name_of_equipment}")
            logging.info(f"Searched tool group name {name_of_tool}")
            logging.info(f"Searched equipment status {name_of_status}")
            logging.info(f"Search date stamp {last_timestamp}")


        except ValueError:
            logging.info(ValueError)

        return [name_of_status, name_of_tool]


    def calculate_downtime_durr(self, *args):
        """
        This function calculates downtime duration & number of downtime events
        """

        # Date format for time difference calculation
        date_frmt = '%Y-%m-%d %H:%M:%S'  # '2022-05-26 10:37:08'

        # Calendar selections for start / end dates - in date time format
        self.calendar_start_date = datetime.strptime(self.string_var_strt.get(), '%m/%d/%Y')
        self.calendar_end_date = datetime.strptime(self.string_var_end.get(), '%m/%d/%Y')

        # Convert calendar values to string
        calendar_start_date_str = datetime.strptime(self.string_var_strt.get(), '%m/%d/%Y').strftime('%m/%d/%y')
        calendar_end_date_str = datetime.strptime(self.string_var_end.get(), '%m/%d/%Y').strftime('%m/%d/%y')

        # Selected equipment in drop down menu
        drop_down_selection = self.selected_equipment.get()

        # Select equipment list based on drop down selection
        if drop_down_selection == 'PTA & TMA':
            self.equipment_list = ['PTA01', 'PTA02', 'PTA03', 'PTA04',
                              'PTA05', 'PTA06', 'PTA07', 'PTA08', 'PTA09', 'PTA10',
                              'TMA11', 'TMA12', 'TMA13', 'TMA14']
        elif drop_down_selection == 'ABRF':
            self.equipment_list = ['ABRF01', 'ABRF02']

        elif drop_down_selection == 'Gantry':
            self.equipment_list = ['Gantry']

        elif drop_down_selection == 'CTC':
            self.equipment_list = ['CTC']

        elif drop_down_selection == '2x20':
            self.equipment_list = ['2x20']

        elif drop_down_selection == 'MLLB':
            self.equipment_list = ['MLLB01', 'MLLB02', 'MLLB03', 'MLLB04', 'MLLB05', 'MLLB06']

        elif drop_down_selection == 'Fiberlabs':
            self.equipment_list = ['Fiberlab01', 'Fiberlab02', 'Fiberlab03', 'Fiberlab04']

        elif drop_down_selection == 'Raising Girders':
            self.equipment_list = ['Girder1000', 'Girder2000', 'Girder3000', 'Girder4000']

        elif drop_down_selection == 'Hoppers':
            self.equipment_list = ['Hopper01', 'Hopper02', 'Hopper03', 'Hopper04', 'Hopper05',
                              'Hopper06', 'Hopper07', 'Hopper08', 'Hopper09', 'Hopper10']
        else:
            self.equipment_list = [drop_down_selection]

        # Data frame to use for calculation is copy of data sorted by date
        self.df_date = self.df_sorted.copy()  # Data frame stores values filtered by Date Range

        # Data frame to store results to be stored in tree view
        self.df_buff = pd.DataFrame()  # Data frame for values going to tree view table

        # Nested dictionary for each piece of equipment
        self.tool_dict = {}
        for i in range(len(self.equipment_list)):
            self.tool_dict[i] = {}
        logging.info(f"Empty Tool Dictionary: {self.tool_dict}")

        # Add keys to tool dictionary
        # self.temp_dict = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, etc}
        for key in range(0, len(self.tool_dict)):
            self.tool_dict[key] = {"equipment_name": [], "tool_group": [], "status": [], "downtime_duration": []}
        logging.info(f"Tool Dictionary with keys: {self.tool_dict}")

        # Iterate over each element of the dataframe sorted by equipment name
        # Determine when status changed from Not Available to Available
        # Determine when status changed from Partially Available to Available
        # Record time difference
        for num, element in enumerate(self.equipment_list, start=0):

            logging.info(f"The current element of dataframe -  {element}")
            # Sort dataframe by equipment name && Reset index of the dataframe
            self.df_sorted = self.df_date.loc[self.df_date['cr483_name'] == self.equipment_list[num]]
            self.df_sorted.index = pd.RangeIndex(len(self.df_sorted.index))

            # Attach equipment name to data frame
            self.tool_dict[num]["equipment_name"].append(self.equipment_list[num])

            # Get first value from first row of dataframe
            # Reject first row if it has garbage name (early database entries have garbage)
            first_row = 0
            for i in range(0, len(self.df_sorted)):

                mem_date = datetime.strptime(self.df_sorted['createdon'].iloc[i], date_frmt)
                mem_status = self.df_sorted['cr483_cranestatus'].iloc[i]

                if mem_status == "Not Available" or mem_status == "Partially Available":
                    self.tool_dict[num]["tool_group"].append(self.df_sorted['cr483_toolgroup'].iloc[i])
                    break
                elif mem_status == "Available":
                    break
                else:
                    first_row += 1

            # Set downtime counters
            full_downtime_cnt = 0
            partial_downtime_cnt = 0
            sum_downtime_complete_hrs = 0
            sum_downtime_partial_hrs = 0

            # For each row of dataframe sorted by equipment name
            for k in range(first_row, len(self.df_sorted)):

                logging.info(f"The k index is {k}")
                logging.info(f"The first row is is {first_row}")
                logging.info(f"The length of the frame for this {element} is - {len(self.df_sorted)}")

                row_status = self.df_sorted['cr483_cranestatus'].iloc[k]  # Get current status
                row_timestamp = datetime.strptime(self.df_sorted['createdon'].iloc[k], date_frmt)  # Get current date

                # Start of Downtime
                if ((row_status == 'Not Available' and mem_status == 'Available')
                        or (row_status == 'Partially Available' and mem_status == 'Available')):

                    # Set memory variable
                    mem_date = row_timestamp
                    mem_status = row_status

                    # If not last row of the table
                    if k != (len(self.df_sorted) - 1):
                        logging.info(f"Not last row and element is {element}")
                        self.tool_dict[num]["tool_group"].append(self.df_sorted['cr483_toolgroup'].iloc[k])
                    else:
                        # If the record is last in the row with "Not Available" status
                        # record tool group and calculate time difference from the time stamp to drop down end date
                        logging.info(f"The record is last in the row with out of service status {element} index is {k}")
                        downtime_complete_hrs = self.calendar_end_date - row_timestamp
                        downtime_complete_hrs = convert_to_hrs(downtime_complete_hrs.total_seconds())

                        # Record tool group
                        self.tool_dict[num]["tool_group"].append(self.df_sorted['cr483_toolgroup'].iloc[k])

                        # Record time difference - this is Time of being out of service
                        self.tool_dict[num]["downtime_duration"].append(downtime_complete_hrs)
                        self.tool_dict[num]["status"].append(row_status)

                    logging.info(f"Change in status mem date = {mem_date}")
                else:
                    logging.info("No change in Status")

                # End of Downtime
                # If first entry begins with "Available" assume "Not Available"
                # Example: selected date range 11/11/2022 to 21/11/2022
                # The first entry for machine was 15/11/2022 - "Available" which means from 11/11/2022 to 15/11/2022
                # it was out of service for 4 days, we then search for the most recent "Not Available / Partially" tag
                # and find Tool Group. Duration is still from drop down start to end date

                if (row_status == 'Available') and (k == first_row):

                    # 0.2.4
                    logging.info("The first entry is 'Available' - looking for last entry from previous date range")
                    logging.info(f"The element is {element}")
                    # Call function
                    search_result = self.find_latest_entry(num)
                    logging.info(f"Function return is {search_result}")

                    # Find most recent tool group for downtime entry - outside date picker selection
                    # record tool group and calculate time difference from the time stamp to drop down end date
                    downtime_complete_hrs = row_timestamp - self.calendar_start_date
                    downtime_complete_hrs = convert_to_hrs(downtime_complete_hrs.total_seconds())

                    # Record tool group
                    self.tool_dict[num]["tool_group"].append(search_result[1])

                    # Record time difference - this is Time of being out of service
                    self.tool_dict[num]["downtime_duration"].append(downtime_complete_hrs)
                    self.tool_dict[num]["status"].append(search_result[0])

                    full_downtime_cnt += 1  # Full downtime counter

                elif ((row_status == 'Available' and mem_status == 'Not Available')
                        or (row_status == 'Partially Available' and mem_status == 'Not Available')):
                    # Record time difference - this is Time of being Fully out of service
                    downtime_complete_hrs = row_timestamp - mem_date
                    downtime_complete_hrs = convert_to_hrs(downtime_complete_hrs.total_seconds())

                    # Downtime duration for each iteration
                    self.tool_dict[num]["downtime_duration"].append(downtime_complete_hrs)
                    self.tool_dict[num]["status"].append(mem_status)

                    # Sum of complete downtime in hrs - total
                    sum_downtime_complete_hrs += downtime_complete_hrs
                    logging.info(f"Sum of complete downtime in hrs: {sum_downtime_complete_hrs}")

                    # Set memory variable
                    mem_date = row_timestamp
                    mem_status = row_status
                    full_downtime_cnt += 1  # Full downtime counter

                elif ((row_status == 'Not Available') and (mem_status == 'Partially Available')
                      or (row_status == 'Available') and (mem_status == 'Partially Available')):
                    # Record time difference - this is Time of being Partially out of service
                    downtime_partial_hrs = row_timestamp - mem_date
                    downtime_partial_hrs = convert_to_hrs(downtime_partial_hrs.total_seconds())

                    # Downtime duration for each iteration
                    self.tool_dict[num]["downtime_duration"].append(downtime_partial_hrs)
                    self.tool_dict[num]["status"].append(mem_status)

                    # Sum of partial downtime in hrs - total
                    sum_downtime_partial_hrs += downtime_partial_hrs
                    logging.info(f" Sum of partial downtime in hrs: {sum_downtime_partial_hrs}")

                    # Set memory variable
                    mem_date = row_timestamp
                    mem_status = row_status
                    partial_downtime_cnt += 1  # Partial Downtime counter

            ########################################################################################
            # Check if table has entries for this equipment within given date range
            # if not - find the latest record in range calendar_start_date - (n month)
            if self.df_sorted.empty:
                logging.info("The record is empty - looking for last entry from previous date range")
                logging.info(f"The element is {element}")
                # Call function
                search_result = self.find_latest_entry(num)
                logging.info(f"Function return is {search_result}")
                time_slice_hrs = (self.calendar_end_date - self.calendar_start_date).total_seconds()
                time_slice_hrs = convert_to_hrs(time_slice_hrs)
                # [name_of_status, name_of_tool]
                if search_result[0] == 'Not Available':
                    full_downtime_cnt = 1  # Full downtime counter
                    sum_downtime_complete_hrs = time_slice_hrs
                    logging.info(f"Time slice fully Unavailable {sum_downtime_complete_hrs}")
                elif search_result[0] == 'Partially Available':
                    partial_downtime_cnt = 1  # Partial Downtime counter
                    sum_downtime_partial_hrs = time_slice_hrs
                    logging.info(f"Time slice Partially Available {sum_downtime_partial_hrs}")

            ########################################################################################
                    # Write value to first half of the table [ rows 0 to 13 - depends on number of equipment ]

            self.df_buff.loc[num, 'Equipment Name'] = self.equipment_list[num]
            self.df_buff.loc[num, 'Tool Group'] = "All Tools"
            self.df_buff.loc[num, 'Status'] = "Not Available"
            self.df_buff.loc[num, 'Date'] = calendar_start_date_str + "_to_" + calendar_end_date_str
            self.df_buff.loc[num, 'Downtime Duration'] = round(sum_downtime_complete_hrs, 1)
            self.df_buff.loc[num, 'Downtime Count'] = full_downtime_cnt

            # Write values to second half of the table [ rows 13 to 27 - depends on number of equipment]
            self.df_buff.loc[num + len(self.equipment_list), 'Equipment Name'] = self.equipment_list[num]
            self.df_buff.loc[num + len(self.equipment_list), 'Tool Group'] = "All Tools"
            self.df_buff.loc[num + len(self.equipment_list), 'Status'] = "Partially Available"
            self.df_buff.loc[num + len(self.equipment_list), 'Date'] = calendar_start_date_str + "_to_" + calendar_end_date_str
            self.df_buff.loc[num + len(self.equipment_list), 'Downtime Duration'] = round(sum_downtime_partial_hrs, 1)
            self.df_buff.loc[num + len(self.equipment_list), 'Downtime Count'] = partial_downtime_cnt

        # Store results of downtime calculation in temporary dataframe
        self.df_buff = self.df_buff.sort_index(ascending=True)
        self.df_sorted = self.df_buff

        # If drop down selection is not for all devices plot pie chart by Tool Group
        self.date_picker = []
        self.date_picker.append(self.string_var_strt.get())
        self.date_picker.append(self.string_var_end.get())

        # If drop down selection is for all devices then plot bar chart
        # print(self.df_buff.duplicated(subset='Tool Group', keep=False).sum())


    def calculate_tool_group(self):
        """
        This function calculates downtime for each Tool Group
        Calculate: downtime in (hrs) , donwtime in (events) by Tool Group
        :return:
        """
        # Test data:
        combined_dict = {'tool_group': [],'status': [],'downtime_duration': []}
        #test_data = {
        #    0:{'equipment_name': ['PTA01'], 'tool_group': ['Cabin', 'PM', "Extractor", "Bridge", "Some tool"],'status': ['Partially Available', 'Not Available'],'downtime_duration': [10.7, 122.8, 13.0, 11.0, 25.0]},
        #    1:{'equipment_name': ['PTA02'], 'tool_group': ['PM'], 'status': [], 'downtime_duration': []},
        #    2:{'equipment_name': ['PTA03'], 'tool_group': ['N/A', 'N/A', 'N/A', 'N/A'],'status': ['Not Available', 'Not Available', 'Partially Available', 'Not Available'],'downtime_duration': [8.9, 2.5, 0.0, 16.4]}
        #}
        test_data = self.tool_dict
        logging.info(f"Data from frame - {test_data}")

        # Empty list to store lists after join command
        result = [[], [], [], []]

        # For each element in dictionary join lists for each key
        for num, elem in enumerate(combined_dict, start=0):
            for index in range(0, len(test_data)):
                if test_data[index]['downtime_duration']:  # List is not empty
                    result[num] = result[num] + test_data[index][elem]
            combined_dict[elem].append(result[num])
        logging.info(f"Combined dictionary: {combined_dict}")

        # For each element in tool group key find tool breakdown frequency
        # Count number of duplicates in the tool_group list
        self.tool_frequency = {}
        for items in combined_dict['tool_group'][0]:
            self.tool_frequency[items] = combined_dict['tool_group'][0].count(items)

        logging.info("Duplicates Calculated")
        logging.info(f"The tool event frequency results: {self.tool_frequency}")
        # Sort dictionary in descending order
        self.tool_frequency = dict(sorted(self.tool_frequency.items(), key=lambda item: item[1], reverse=True))

        counter = Counter(self.tool_frequency)
        self.keys_frequency = list(counter.keys())
        self.values_frequency = list(counter.values())

        logging.info(f"Tool breakdown events Dictionary: {self.tool_frequency}")
        logging.info(f"Tool breakdown events Values: {self.values_frequency}")
        logging.info(f"Tool breakdown events Keys: {self.keys_frequency}")


        # For each item in tool group key find downtime per tool group
        tool_downtime = {}
        logging.info(f"For each item in tool group key find downtime per tool group: {tool_downtime}")
        logging.info(f"Combined Dictionary by Tool Group: {combined_dict['tool_group'][0]}")
        for index, items in enumerate(combined_dict['tool_group'][0], start=0):
            logging.info(f"Tool group index is {index}")
            if items in tool_downtime:   # Key Already Exists
                tool_downtime[items].append(combined_dict['downtime_duration'][0][index])
                logging.info(f"Combined dict is {combined_dict['downtime_duration'][0][index]}")
                logging.info("Key Exist - add record to the dict")
            else:  # Key Doesn't Exist
                logging.info("Key Doesn't Exist")
                tool_downtime[items] = [combined_dict['downtime_duration'][0][index]]

        # Find Sum of downtime duration per tool group
        logging.info(f"Tool downtime Dictionary Before Sum(): { tool_downtime.items()}")
        self.tool_time = {dict_key: round(sum(val),1) for dict_key, val in tool_downtime.items()}

        # Sort dictionary in descending order
        self.tool_time = dict(sorted(self.tool_time.items(), key=lambda item: item[1], reverse=True))
        logging.info(f"Sum() of downtime per tool group calculated: {self.tool_time}")

        counter = Counter(self.tool_time)
        self.keys_time = list(counter.keys())
        self.values_time = list(counter.values())

        logging.info(f"Tool breakdown frequency Dictionary: {self.tool_time}")
        logging.info(f"Tool breakdown frequency Values: {self.values_time}")
        logging.info(f"Tool breakdown frequency Keys: {self.keys_time}")

        self.tool_calc_result['duration'] = self.values_time
        self.tool_calc_result['event_count'] = self.values_frequency
        self.tool_calc_result['keys'] = self.keys_time

    def open_top_window(self):
        window = TopWindow(self.master, self.df_buff, self.tool_calc_result, self.date_picker, self.equipment_list)
        window.grab_set()

    def about_msg(self):
        about_window = AboutTopWindow(self.master, self.app_version)
        about_window.grab_set()


def convert_to_hrs(duration):
    """
    Function to convert seconds to hours
    :param duration:
    :return: hours
    """
    minutes = (duration / 60)
    hours = minutes / 60
    return round(hours, 1)

class AboutTopWindow(tk.Toplevel):
    def __init__(self, parent, appversion):
        super().__init__(parent)
        self.app_version = appversion

        self.set_title_name()
        self.set_window_size()
        self.set_window_icon()
        self.set_window_frame()
        self.set_window_labels()


    def set_title_name(self):
        self.title("Downtime Data Analyzer" + self.app_version + "- About")

    def set_window_size(self):
        self.resizable(False, False)

        # Width and Height for root = Tk()
        root_width = 525
        root_height = 225

        # Get screen width and height
        win_width = root.winfo_screenwidth()
        win_height = root.winfo_screenheight()

        # Calculate x and y coordinates for the Tk root window
        x = (win_width / 2) - (root_width / 2) + 50
        y = (win_height / 2) - (root_height / 2)

        # Set dimensions and position of the screen
        self.geometry('%dx%d+%d+%d' % (root_width, root_height, x, y))
        logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
        logging.info(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    def set_window_icon(self):
        img_file_name = "small_icon.ico"
        curr_dirr = pathlib.Path(img_file_name).parent.resolve()
        img_path = curr_dirr.joinpath(img_file_name)
        logging.info(f"The image path for window icon is:{img_path}")
        self.iconbitmap(img_path)

    def set_window_frame(self):
        # Configure window Using Grid
        self.mainframe = ttk.Frame(self, padding="3 3 12 12")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Set label frame to hold buttons and page label
        self.label_frame = ttk.LabelFrame( self.mainframe, text='Version Information:')
        self.label_frame.grid(column=0, row=0, sticky=N+W+E+S, columnspan=1)

    def set_window_labels(self):
        pass
        # Create Calendar Label
        ttk.Label(self.label_frame, text="Environment:").grid(column=0, row=2, pady=5, sticky=W)
        ttk.Label(self.label_frame, text="Version:").grid(column=0, row=3, pady=5, sticky=W)
        ttk.Label(self.label_frame, text="Locale:").grid(column=0, row=4, pady=5, sticky=W)
        ttk.Label(self.label_frame, text="User Interface:").grid(column=0, row=5, pady=5, sticky=W)
        ttk.Label(self.label_frame, text="Python Version:").grid(column=0, row=6, pady=5, sticky=W)
        ttk.Label(self.label_frame, text="Author: ").grid(column=0, row=7, pady=5, sticky=W)

        # Create Calendar Label
        ttk.Label(self.label_frame, text=platform.platform()).grid(column=1, row=2, pady=5, sticky=W)
        ttk.Label(self.label_frame, text=self.app_version).grid(column=1, row=3, pady=5, sticky=W)
        ttk.Label(self.label_frame, text=locale.getdefaultlocale()).grid(column=1, row=4, pady=5, sticky=W)
        ttk.Label(self.label_frame, text=("Tkinter: " + str(tkinter.TkVersion))).grid(column=1, row=5, pady=5, sticky=W)
        ttk.Label(self.label_frame, text=sys.version).grid(column=1, row=6, pady=6, sticky=W)
        ttk.Label(self.label_frame, text=" VAL").grid(column=1, row=7, pady=6, sticky=W)


class TopWindow(tk.Toplevel):
    def __init__(self, parent, myData, myToolData, myDate, equipment_list):
        super().__init__(parent)

        self.date_picker = myDate
        self.df_buff = myData
        self.tool_data = myToolData
        self.equipment_list = equipment_list

        self.title("Downtime Data Analyzer v0.2.3 - Plots")
        img_file_name = "small_icon.ico"
        curr_dirr = pathlib.Path(img_file_name).parent.resolve()
        img_path = curr_dirr.joinpath(img_file_name)
        print(img_path)

        self.resizable(False, False)

        # Width and Height for root = Tk()
        root_width = 1000
        root_height = 550

        # Get screen width and height
        win_width = root.winfo_screenwidth()
        win_height = root.winfo_screenheight()

        # Calculate x and y coordinates for the Tk root window
        x = (win_width / 2) - (root_width / 2) + 50
        y = (win_height / 2) - (root_height / 2)

        # Set dimensions and position of the screen
        self.geometry('%dx%d+%d+%d' % (root_width, root_height, x, y))
        logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
        logging.info(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

        self.iconbitmap(img_path)
        plots.MatplotlibSwitchGraphs(self, self.df_buff, self.tool_data, self.date_picker, self.equipment_list)

        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to close window?"):
                self.destroy()

        logging.info("Top window for matplotlib created")
        self.protocol("WM_DELETE_WINDOW", on_closing)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = Tk()
    root.title("Downtime Data Analyzer v0.2.3")
    img_file_name = "small_icon.ico"
    curr_dirr = pathlib.Path(img_file_name).parent.resolve()
    img_path = curr_dirr.joinpath(img_file_name)
    logging.info(f"The image path for window icon is:{img_path}")

    # Root not resizable
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

    # Configure debug logger
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(funcName)20s()] [%(levelname)-5.5s] %(message)s",
                        handlers=[
                            logging.FileHandler("debug.log"),
                            logging.StreamHandler(sys.stdout)
                        ])
    #logging.basicConfig(filename='debug.log', encoding='utf-8', level=logging.DEBUG, filemode='w')
    #logging.info(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))

    root.iconbitmap(img_path)

    myapp = App(root)
    myapp.mainloop()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
