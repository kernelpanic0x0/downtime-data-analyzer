# This is a sample Python script.
#
#
#
import tkinter
import tkinter.filedialog
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import pandas as pd
import pytz
from datetime import datetime
import matplotlib.pyplot as plt

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

    def init_ui(self):

        #Selected choice
        def calculate():
            try:
                choice = variable.get()
                print(choice)
                open_text_file(choice)
            except ValueError:
                pass

        # Drop Down variable
        variable = StringVar(root)
        # Drop down menu items
        DROPDOWN_ITEMS = [
            'PTA01', 'PTA02',
            'PTA03', 'PTA04',
            'PTA05', 'PTA06',
            'PTA07', 'PTA08',
            'PTA09', 'PTA10',
            'TMA11', 'TMA12',
            'TMA13', 'TMA14']
        variable.set(DROPDOWN_ITEMS[0])  # default value
        # Create menu item
        my_menu = Menu(root)
        root.config(menu=my_menu)
        # Create submenus File, Help, etc.
        file_menu = Menu(my_menu, tearoff=False)
        help_menu = Menu(my_menu, tearoff=False)

        # Top bar File menu
        my_menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open data file", command=open_text_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        # Top bar Help menu
        my_menu.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=about_msg)


        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=3, row=3, sticky=W)

        w = OptionMenu(mainframe, variable, *DROPDOWN_ITEMS)
        w.grid(column=4, row=3, sticky=W)


        # text = tkinter.Text(root, height=24)
        # text.grid(column=0, row=0, sticky='nsew')
        # text.insert('1.0', open_text_file())


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
            #print(mem_date)


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
    df_3 = pd.DataFrame({'Count': downtime_cnt, 'downtime_minutes': downtime_durr })
    ax = df_3.plot.bar(x='Count', y='downtime_minutes', rot=0, title=my_choice)
    ax.plot()
    plt.show()
    print(df_2.to_string())
    print(time_diff)
    # print(df.to_string())


def get_duration(duration):
    minutes = (duration / 60)
    return minutes


# About message window
def about_msg():
    top = Toplevel(root)
    top.geometry('%dx%d+%d+%d' % (root_width/2, root_height/2, x+50, y+50))
    top.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = Tk()
    root.title("Downtime Data Analyzer")
    my_icon = PhotoImage(file="images/analyzer_icon.png")
    root.iconphoto(True, my_icon)
    root.resizable(False, False)

    # Width and Height for root = Tk()
    root_width = 500
    root_height = 500

    # Get screen width and height
    win_width = root.winfo_screenwidth()
    win_height = root.winfo_screenheight()

    # Calculate x and y coordinates for the Tk root window
    x = (win_width/2) - (root_width/2)
    y = (win_height/2) - (root_height/2)

    # Set dimensions and position of the screen
    root.geometry('%dx%d+%d+%d' % (root_width, root_height, x, y))

    myapp = App(root)
    myapp.mainloop()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
