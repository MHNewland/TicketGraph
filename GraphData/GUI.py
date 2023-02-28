import tkinter as tk
from tkinter.ttk import Notebook
from ttkwidgets import CheckboxTreeview
import GraphData as gd
import datetime as dt
import numpy as np
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)

#region Selection Frame
'''
| team_box  | data_box  |
'''
def create_selection_frame(window):
    selection_frame = tk.Frame(window, background="red", padx=5, pady=5)
    selection_frame.grid(row=0, column=0, sticky='nsw')
    selection_frame.columnconfigure(0, weight=1)
    selection_frame.columnconfigure(1, weight=1)
    selection_frame.widgetName = "Selection_frame"
    create_team_box(selection_frame)
    create_data_box(selection_frame)

def create_team_box(frame):
    teams = sorted((list)(gd.get_teams()))
    team_frame = tk.Frame(frame,background='teal', padx=5, pady=5)
    team_frame.widgetName = "Team_frame"
    team_frame.grid(row=0, column=0, sticky='w')    
    create_box(team_frame, teams, "Teams")

def create_data_box(frame):
    data = sorted((list)(gd.get_data_headers()))
    data_frame = tk.Frame(frame,background='lime', padx=5, pady=5)
    data_frame.widgetName = "Data_frame"
    data_frame.grid(row=0, column=1, sticky='w')
    create_box(data_frame, data, "Data")

def create_box(frame, items, label):
    treeview = CheckboxTreeview(frame, )
    treeview.widgetName = f"{label}_treeview"
    treeview.heading('#0', text=label, anchor='w')
    treeview.column("#0", width=235)    
    sb=tk.Scrollbar(frame, orient='vertical')
    treeview.config(yscrollcommand=sb.set)
    sb.config(command = treeview.yview, width=15)
    for item in items:
        treeview.insert("", 'end', item, text=item)
    treeview.grid(row=0, column=0)
    sb.grid(row=0, column=1,sticky='ns')
#endregion
    
#region Data Table
'''
Data_table_frame
_________________________________
|Tab1*  |Tab2    |               |
---------------------------------
|Data1 Title     |Data2 Title    |
|This week  | #  |This week  | # |
|Last week  | #  |Last week  | # |
|4 week avg.| #  |4 week avg.| # |
'''
def create_data_table(frame):
    data_table_frame = tk.Frame(frame, background='purple', padx=5, pady=5)
    data_table_frame.widgetName = "Data_table_frame"
    data_table_frame.columnconfigure(0, weight=1)
    data_table_frame.rowconfigure(0, weight=1)
    data_table_frame.grid(row=0, column=1, sticky='nsew')
    data_table_frame.grid_propagate(False)
    data_nb = Notebook(data_table_frame)
    data_nb.grid(row=0, column=0, sticky='nsew')
    data_nb.widgetName = "Data_notebook"

def fill_data_table(frame, teams, data_checked, graph):
    team_frames = []
    data_nb = find_widget(frame, "Data_notebook")
    if data_nb == None:
        create_data_table(get_master_window(frame))
    if data_nb.tabs() != None:
        for tab in data_nb.tabs():
            data_nb.forget(tab)
    for t in range(len(teams)):
        team_frames.append(tk.Frame(data_nb,background="pink", padx=5, pady=5))
        team_frames[t].rowconfigure(0, weight=1)
        data_nb.add(team_frames[t], text=f"{teams[t]}")
        for d in range(len(data_checked)):
            team_frames[t].columnconfigure(d, weight=1)
            create_tab_data_frame(team_frames[t], data_checked[d], d, teams[t], graph)

def create_tab_data_frame(frame, data_name, data_col, team_name, graph):
    tab_data_frame = tk.Frame(frame,background="lavender", padx=5, pady=5, highlightbackground="black", highlightthickness=2)
    for row in range(4):
        tab_data_frame.rowconfigure(row, weight=1)
    tab_data_frame.grid(row=0, column = data_col, sticky='nsew')
    tab_info(tab_data_frame, data_name, team_name, graph)

def tab_info(frame, data_name, team_name, graph):
    header_font = ("Arial Black", 18)
    label_font = ("Arial", 14)
    title_label = tk.Label(frame, text=f"{data_name}", font=header_font)  
    title_label.grid(row=0, column=0, columnspan=2, sticky='w')
    
    data_line = None
    this_week = 0
    last_week = 0
    week_avg = 0
    weeks = 0
    for plot in graph.axes:
        for line in plot.get_lines():
            team, data = line.get_label().split(": ")
            if team == team_name and data == data_name:
                data_line=line
                break
    if data_line == None:
        return
    
    today=dt.date.today()
    xdata=data_line.get_xdata()
    ydata=data_line.get_ydata()

    weeks_before = 4
    # if the line doesn't have at least 4 weeks worth of data
    # set the number of weeks to look for to the number of weeks it has data for.
    if len(xdata) < weeks_before:
        weeks_before = len(xdata)

    for day in range(weeks_before,0,-1):
        if today - xdata[-day] < dt.timedelta(days=(7*day)):
            if week_avg ==0:
                week_avg = np.average(ydata[-day:])
                weeks = day
            if day==2:
                last_week = ydata[-day]
            if day==1:
                this_week = ydata[-day]
        
        
    this_week_label = tk.Label(frame, text=f"This week:", font=label_font)
    this_week_label.grid(row=1, column=0,sticky='w')
    #makes the background of this week's number lime green if it's less than last week, otherwise it makes it red.
    this_week_num = tk.Label(frame, text=this_week, font=label_font, background=(lambda t, l: "lime green" if t<l else "red")(this_week, last_week))
    this_week_num.grid(row=1, column=1, sticky='w')

    last_week_label = tk.Label(frame, text=f"Last week:", font=label_font)
    last_week_label.grid(row=2, column=0,sticky='w')
    last_week_num = tk.Label(frame, text=last_week, font=label_font)
    last_week_num.grid(row=2, column=1, sticky='w')

    four_week_avg_label = tk.Label(frame, text=f"{weeks} week avg.:", font=label_font)
    four_week_avg_label.grid(row=3, column=0, sticky='w')
    four_week_avg_num = tk.Label(frame, text=week_avg, font=label_font)
    four_week_avg_num.grid(row=3, column=1, sticky='w')      
#endregion

#region Button Frame
'''
| submit_button | unselect_button   |
'''
def create_button_frame(frame):
    button_frame = tk.Frame(frame, background="blue", padx=5, pady=5)#, width=535, height=40)
    #button_frame.grid_propagate(False)
    button_frame.widgetName = "Button_frame"
    button_frame.grid(row=1, column=0, sticky='nsw')

    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)

    create_submit_button(button_frame)
    create_unselect_button(button_frame)

def create_submit_button(frame):
    submit_frame = tk.Frame(frame, background="green", height=30, padx=5, pady=5)
    submit_frame.widgetName = "Submit_frame"
    submit_frame.grid(row=0, column=0, sticky='w')
    submit = tk.Button(submit_frame, text="Submit", command=lambda: get_data(frame))
    submit.grid(row=0, column=0)

def create_unselect_button(frame):
    unselect_frame = tk.Frame(frame, background="aqua", height=30, padx=5, pady=5)
    unselect_frame.widgetName = "Unselect_frame"
    unselect_frame.grid(row=0, column=1, sticky='w')
    unselect = tk.Button(unselect_frame, text="Unselect all", command=lambda: unselect_all(frame))
    unselect.grid(row=0, column=0)
#endregion

#region Button Commands
def unselect_all(selection_frame):
    master_window = get_master_window(selection_frame)
    try:
        for frame in master_window.winfo_children():
            frame.destroy()
        master_window.withdraw()
        create_app(master_window)
    except Exception as err:
        print(err) 

#Graph
def get_data(frame):
    #CheckboxTreeview.get_checked() returns a list of all checked items in that checkbox
    selection_frame = find_widget(get_master_window(frame), "Selection_frame")
    if selection_frame != None:
        teams_checked = find_widget(get_master_window(frame), "Teams_treeview").get_checked()
        data_checked = find_widget(get_master_window(frame), "Data_treeview").get_checked()
        if len(teams_checked)==0 or len(data_checked)==0:
            return
        team_dict = gd.create_dictionary(gd.get_tables()[0], teams_checked, data_checked)
        graph = graph_data(selection_frame, team_dict, teams_checked, data_checked)
        fill_data_table(get_master_window(frame), teams_checked, data_checked, graph)

def graph_data(frame, team_dict, teams_checked, data_checked):
    graph_frame = tk.Frame(get_master_window(frame), background="black", padx=5, pady=5)
    graph_frame.grid(row=2, column=0, columnspan=2, sticky='new')

    graph = gd.display_graph(team_dict, teams_checked, data_checked)
    canvas = FigureCanvasTkAgg(graph, graph_frame)
    canvas.draw()
    canvas.get_tk_widget().widgetName = "Graph"
    canvas.get_tk_widget().grid(sticky='nsew')
    set_window_size(canvas.get_width_height()[0]+20, canvas.get_width_height()[1]+globals()['window_height']+10,frame)
    return graph
#endregion
   
#region App controls
def find_widget(frame, widget_name):
    try:
        for item in frame.winfo_children():
            if item.widgetName == widget_name:
                return item
            if type(item) == tk.Frame:
                if item.winfo_children() != None:
                    widget = find_widget(item, widget_name)
                    if widget != None:
                        return widget
    except Exception as err:
        print(err)
    return None

def delete_widget(widget):
    widget.destroy()

def set_window_size(w, h, frame):
    master= get_master_window(frame)
    master.geometry(f"{w}x{h}")

def get_master_window(frame):
    try:
        master = frame
        while master.master != None:
            master=master.master
    except Exception as err:
        print(err)
        return None
    return master
#endregion

#region Main Window
def create_window(w, h):
    window = tk.Tk()
    window.title("Ticket data")
    window.resizable(False,False)
    window.geometry(f"{w}x{h}") 
    return window

'''

grid(row, column)
____________________________________________________________________
|(0,0) Selection Frame |(0,1) Data Table Frame (weight=1 to resize)|
|----------------------|-------------------------------------------|
|(1,0)   Button Frame  |(1,1) Excel button (not implemented)       |
|------------------------------------------------------------------|
|(2,0)                 Graph (columnspan=2)                        |
|__________________________________________________________________|

'''
def create_app(window):
    set_window_size(globals()["window_width"], globals()["window_height"],window)
    window.config(background='yellow', padx=5, pady=5)
    window.grid_columnconfigure(1, weight=1)
    window.grid_rowconfigure(2, weight=1)
    window.deiconify()
    create_selection_frame(window)
    create_data_table(window)
    create_button_frame(window)

def quit_me(window):
    window.quit()
    window.destroy()
#endregion

def main():
    globals()['window_width'] = 560
    globals()['window_height'] = 300
    window = create_window(globals()['window_width'], globals()['window_height'])
    window.protocol("WM_DELETE_WINDOW", lambda:quit_me(window))
    create_app(window)
    

    window.mainloop()

main()