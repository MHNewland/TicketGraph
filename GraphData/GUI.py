import tkinter as tk
from tkinter.ttk import Notebook, Treeview
from ttkwidgets import CheckboxTreeview
import datetime as dt
import numpy as np
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)

import GraphData as gd
import DBInfo as dbi

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
    teams = sorted((list)(dbi.get_teams()))
    team_frame = tk.Frame(frame,background='teal', padx=5, pady=5)
    team_frame.widgetName = "Team_frame"
    team_frame.grid(row=0, column=0, sticky='w')    
    create_box(team_frame, teams, "Teams")

def create_data_box(frame):
    data = sorted((list)(dbi.get_data_headers()))
    data_frame = tk.Frame(frame,background='lime', padx=5, pady=5)
    data_frame.widgetName = "Data_frame"
    data_frame.grid(row=0, column=1, sticky='w')
    create_box(data_frame, data, "Data")

def create_box(frame, items, label):
    treeview = CheckboxTreeview(frame)
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
    data_table_frame = tk.Frame(frame, background='purple', padx=5, pady=5)#, width=10)
    data_table_frame.widgetName = "Data_table_frame"
    data_table_frame.columnconfigure(0, weight=1)
    data_table_frame.rowconfigure(1, weight=1)
    data_table_frame.grid(row=0, column=1, sticky='nsew')
    data_table_frame.grid_propagate(False)

    data_nb_title = tk.Label(data_table_frame, text="Data Table")
    data_nb_title.grid(row=0, column=0, sticky='w')

    data_nb = Notebook(data_table_frame)
    data_nb.grid(row=1, column=0, sticky='nsew')
    data_nb.widgetName = "Data_notebook"

def fill_data_table(frame, teams, data_checked, graph, team_dict):
    team_frames = []
    data_nb = find_widget(frame, "Data_notebook")
    if data_nb == None:
        create_data_table(get_master_window(frame))
    if data_nb.tabs() != None:
        for tab in data_nb.tabs():
            data_nb.forget(tab)

    if "Grand Total" in teams:
        teams.append(teams.pop(teams.index("Grand Total")))
    for t in range(len(teams)):
        team_frames.append(tk.Frame(data_nb,background="pink", padx=5, pady=5))
        team_frames[t].rowconfigure(0, weight=1)
        data_nb.add(team_frames[t], text=f"{teams[t]}")
        for d in range(len(data_checked)):
            team_frames[t].columnconfigure(d, weight=1)
            create_tab_data_frame(team_frames[t], data_checked[d], d, teams[t], graph, team_dict)

def create_tab_data_frame(frame, data_name, data_col, team_name, graph, team_dict):
    tab_data_frame = tk.Frame(frame,background="lavender", padx=5, pady=5, highlightbackground="black", highlightthickness=2)
    for row in range(10):
        tab_data_frame.rowconfigure(row, weight=1)
    tab_data_frame.grid(row=0, column = data_col, sticky='nsew')
    tab_info(tab_data_frame, data_name, team_name, graph, team_dict)

def tab_info(frame, data_name, team_name, graph, team_dict):
    header_font = ("Arial Black", 19-len(graph.axes))
    label_font = ("Arial", 15-len(graph.axes))
    title_label = tk.Label(frame, text=f"{data_name}", font=header_font)  
    title_label.grid(row=0, column=0, columnspan=2, sticky='w')
    
    data_line = None
    this_week = 0
    last_week = 0
    x_week_avg = 0
    weeks = 0
    roc = 0
    for plot in graph.axes:
        for line in plot.get_lines():
            team, data = line.get_label().split(": ")
            if team == team_name and data == data_name:
                data_line=line
                break
    if data_line == None:
        return
    
    grand_total = team_dict["Grand Total"]
    today=dt.date.today()
    xdata=data_line.get_xdata()
    ydata=data_line.get_ydata()
    latest_date = xdata[-1].strftime("%d-%m-%Y")
    weeks_before = 4
    # if the line doesn't have at least 4 weeks worth of data
    # set the number of weeks to look for to the number of weeks it has data for.
    if len(xdata) < weeks_before:
        weeks_before = len(xdata)

    for day in range(weeks_before,0,-1):
        if today - xdata[-day] < dt.timedelta(days=(7*day)):
            if x_week_avg ==0:
                x_week_avg = np.average(ydata[-day:])
                weeks = day
            if day==2:
                last_week = ydata[-day]
            if day==1:
                this_week = ydata[-day]

    if weeks != 0:
        roc = ((np.divide(this_week, ydata[-weeks]))-1) * 100
        
    this_week_label = tk.Label(frame, text=f"This week:", font=label_font)
    this_week_label.grid(row=1, column=0,sticky='w')
    #makes the background of this week's number lime green if it's less than last week, otherwise it makes it red.
    this_week_num = tk.Label(frame, text=f"{round(this_week, 2)}", font=label_font, background=(lambda t, l: "lime green" if t<l or t==0 else "red")(this_week, last_week))
    this_week_num.grid(row=1, column=1, sticky='w')

    last_week_label = tk.Label(frame, text=f"Last week:", font=label_font)
    last_week_label.grid(row=2, column=0,sticky='w')
    last_week_num = tk.Label(frame, text=f"{round(last_week,2)}", font=label_font)
    last_week_num.grid(row=2, column=1, sticky='w')

    x_week_avg_label = tk.Label(frame, text=f"{weeks} week avg.:", font=label_font)
    x_week_avg_label.grid(row=3, column=0, sticky='w')
    x_week_avg_num = tk.Label(frame, text=f"{round(x_week_avg, 2)}", font=label_font)
    x_week_avg_num.grid(row=3, column=1, sticky='w')

    roc_label = tk.Label(frame, text=f"{weeks} week rate of change:", font=label_font)
    roc_label.grid(row=4, column=0, sticky='w')
    roc_num = tk.Label(frame, text=f"{round(roc,2)}%", font=label_font)
    roc_num.grid(row=4, column=1, sticky='w')

    if (num_tickets:=data_name == "# of Tickets") or data_name == "Update Age >=30":
        if num_tickets:
            pct_untouched = np.divide(team_dict[team_name][latest_date]["Update Age >=30"], this_week)*100
            pct_untouched_label = tk.Label(frame, text=f"% not touched in 30 days:", font=label_font)
            pct_untouched_label.grid(row=5, column=0, sticky='w')
            pct_untouched_num = tk.Label(frame, text=f"{round(pct_untouched,2)}%", font=label_font)
            pct_untouched_num.grid(row=5, column=1, sticky='w')        
        if team_name != "Grand Total":
            pct_total = np.divide(this_week, grand_total[latest_date][data_name])*100
            pct_total_label = tk.Label(frame, text=f"% of Total:", font=label_font)
            pct_total_label.grid(row=6, column=0, sticky='w')
            pct_total_num = tk.Label(frame, text=f"{round(pct_total,2)}%", font=label_font)
            pct_total_num.grid(row=6, column=1, sticky='w')

#endregion

#region Selection Button Frame
'''
| submit_button | unselect_button   |
'''
def create_selection_button_frame(frame):
    button_frame = tk.Frame(frame, background="blue", padx=5, pady=5)
    button_frame.widgetName = "Button_frame"
    button_frame.grid(row=1, column=0, sticky='nsw')

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

#region Ranking Button Frame

def create_ranking_button_frame(frame):
    ranking_button_frame = tk.Frame(frame, background="fuchsia", padx=5, pady=5)
    ranking_button_frame.widgetName = "Ranking_Button_frame"
    ranking_button_frame.grid(row=1, column=1, sticky='nsw')
    ranking_button_frame.grid_rowconfigure(0, weight=1)
    ranking_button_frame.grid_columnconfigure(0, weight=1)
    create_ranking_button(ranking_button_frame)

def create_ranking_button(frame):
    ranking_button = tk.Button(frame, text="Show Ranking", command=lambda: show_ranking(frame))
    ranking_button.grid()
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
        
        #if # of tickets is selected, grab data for update age >=30 to calculate % haven't been touched
        data_needed = list(data_checked)
        teams_needed = list(teams_checked)

        if "Grand Total" not in teams_checked:
            teams_needed.append("Grand Total")
        if "# of Tickets" in data_checked and "Update Age >=30" not in data_checked:
            data_needed.append("Update Age >=30")

        team_dict = dbi.create_dictionary(dbi.get_tables()[0], teams_needed, data_needed)
        graph = graph_data(selection_frame, team_dict, teams_checked, data_checked)
        fill_data_table(get_master_window(frame), teams_checked, data_checked, graph, team_dict)

def graph_data(frame, team_dict, teams_checked, data_checked):
    graph_frame = tk.Frame(get_master_window(frame), background="black", padx=5, pady=5)
    graph_frame.grid(row=2, column=0, columnspan=2, sticky='new')
    graph_frame.columnconfigure(0, weight=1)

    graph = gd.display_graph(team_dict, teams_checked, data_checked)
    canvas = FigureCanvasTkAgg(graph, graph_frame)
    canvas.draw()
    canvas.get_tk_widget().widgetName = "Graph"
    canvas.get_tk_widget().grid(sticky='nsew')
    set_window_size(canvas.get_width_height()[0]+50, canvas.get_width_height()[1]+globals()['window_height']+10,frame)
    return graph

def show_ranking(frame):
    master_window = get_master_window(frame)
    if find_widget(master_window, "Ranking_frame") == None:
        set_window_size(master_window.winfo_width()+200, master_window.winfo_height(), master_window)
        ranking_frame = tk.Frame(master_window, background="wheat", padx=5, pady=5)
        ranking_frame.widgetName = "Ranking_frame"
        ranking_frame.grid_rowconfigure(1, weight=1)
        ranking_frame.grid(row = 0, column=2, rowspan=3, sticky='nsew')

        ranking_title = tk.Label(ranking_frame, text="Team ranking")
        ranking_title.grid(row=0, column=0, sticky='nw')

        rank_box = Treeview(ranking_frame, width=75, columns=2, show="headings")
        rank_box.grid(row=1, column=0, sticky='nsew')

        team_rank = {}
        for team in find_widget(master_window, "Teams_treeview").get_children():
            team_rank[team]=calculate_team_score(team)
        
        team_rank = sorted(team_rank.items(), key=lambda x:x[1])
        for team in team_rank:
            rank_box.insert("",'end',team,)

def calculate_team_score(team):
    return np.random.randint(0,100)
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
____________________________________________________________________________________________
|(0,0)      Selection Frame     |(0,1) Data Table Frame (weight=1 to resize)|               |
|-------------------------------|-------------------------------------------|    (0, 2)     |
|(1,0)  Selection Button Frame  |(1,1)          Ranking button Frame        | Team ranking  |
|---------------------------------------------------------------------------|  rowspan=3    |
|(2,0)                     Graph (columnspan=2)                             |               |
|___________________________________________________________________________|_______________|

'''
def create_app(window):
    set_window_size(globals()["window_width"], globals()["window_height"],window)
    window.config(background='yellow', padx=5, pady=5)

    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(1, minsize=100)

    window.grid_rowconfigure(0, weight=1)
    window.grid_rowconfigure(2, weight=2)
    window.deiconify()
    create_selection_frame(window)
    create_data_table(window)
    create_selection_button_frame(window)
    create_ranking_button_frame(window)

def quit_me(window):
    window.quit()
    window.destroy()
#endregion

def main():
    globals()['window_width'] = 650
    globals()['window_height'] = 300
    window = create_window(globals()['window_width'], globals()['window_height'])
    window.protocol("WM_DELETE_WINDOW", lambda:quit_me(window))
    create_app(window)
    

    window.mainloop()

main()