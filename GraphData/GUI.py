import tkinter as tk
from tkinter.ttk import Notebook, Treeview
from ttkwidgets import CheckboxTreeview
import datetime as dt
import numpy as np
import collections
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)

import GraphData as gd
import DBInfo as dbi

#region default sizes
DEFAULT_WINDOW_SIZE = "650x300"
GRAPH_ONLY_SIZE = "1400x900"
RANK_ONLY_SIZE = "950x300"
RANK_AND_GRAPH_SIZE="1700x900"
#endregion

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
    data_table_frame = tk.Frame(frame, background='purple', padx=5, pady=5)

    data_table_frame.columnconfigure(0, weight=1)
    data_table_frame.rowconfigure(1, weight=1)
    data_table_frame.grid(row=0, column=1, sticky='nsew')
    data_table_frame.widgetName = "Data_table_frame"
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
    
    data_line = get_line(graph, team_name, data_name)
    if data_line == None:
        return
    
    this_week = 0
    last_week = 0
    x_week_avg = 0
    weeks = 0
    roc = 0
    
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
        if this_week == ydata[-weeks]:
            roc = 0
        else:
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
            try:
                this_week_untouched = team_dict[team_name][latest_date]["Update Age >=30"]
            except KeyError:
                this_week_untouched = 0
            if this_week == 0 and this_week_untouched==0:
                pct_untouched = 0
            else:
                pct_untouched = np.divide(this_week_untouched, this_week)*100
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
    unselect = tk.Button(unselect_frame, text="Unselect all", command=lambda: unselect_all(get_master_window(frame)))
    unselect.grid(row=0, column=0)
#endregion

#region Ranking Button Frame

def create_ranking_button_frame(frame):
    ranking_button_frame = tk.Frame(frame, background="fuchsia", padx=5, pady=5)
    ranking_button_frame.widgetName = "Ranking_button_frame"
    ranking_button_frame.grid(row=1, column=1, sticky='nsw')
    ranking_button_frame.grid_rowconfigure(0, weight=1)
    ranking_button_frame.grid_columnconfigure(0, weight=1)
    create_ranking_button(ranking_button_frame)

def create_ranking_button(frame):
    ranking_button = tk.Button(frame, text="Show Ranking", command=lambda: show_ranking(frame))
    ranking_button.widgetName="Show_ranking_button"
    ranking_button.grid()

def create_hide_ranking_button(frame):
    hide_ranking_button = tk.Button(frame, text="Hide Ranking", command=lambda: hide_ranking(frame))
    hide_ranking_button.widgetName="Hide_ranking_button"
    hide_ranking_button.grid()
    return hide_ranking_button
#endregion

#region Button Commands
def get_data(frame):
    #CheckboxTreeview.get_checked() returns a list of all checked items in that checkbox
    selection_frame = find_widget(master:=get_master_window(frame), "Selection_frame")
    if selection_frame != None:
        teams_checked = find_widget(master, "Teams_treeview").get_checked()
        data_checked = find_widget(master, "Data_treeview").get_checked()
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
    if (graph_frame:= find_widget(\
            (master:=get_master_window(frame)),\
            "Graph_frame"))!=None:

        graph_frame.grid()
    else:
        graph_frame = tk.Frame(master, background="black", padx=5, pady=5)
        graph_frame.grid(row=2, column=0, columnspan=2, sticky='new')
        graph_frame.columnconfigure(0, weight=1)
        graph_frame.widgetName = "Graph_frame"
    if (graph:=find_widget(graph_frame, "Graph")) !=None:
        graph.destroy()
    graph = gd.display_graph(team_dict, teams_checked, data_checked)
    canvas = FigureCanvasTkAgg(graph, graph_frame)
    canvas.draw()
    canvas.get_tk_widget().widgetName = "Graph"
    canvas.get_tk_widget().grid(sticky='nsew')
    set_window_size((lambda x: GRAPH_ONLY_SIZE if x==None else RANK_AND_GRAPH_SIZE)(find_widget(get_master_window(frame), "Ranking_frame")), frame)
    return graph

def show_ranking(frame):
    master_window = get_master_window(frame)
    swap_ranking_buttons(master_window)

    window_size = DEFAULT_WINDOW_SIZE
    graph = find_widget(master_window, "Graph_frame")
    if graph == None:
        window_size = RANK_ONLY_SIZE
    else:
        if not graph.winfo_ismapped():
            window_size = RANK_ONLY_SIZE
        else:
            window_size = RANK_AND_GRAPH_SIZE

    set_window_size(window_size, master_window)

    if (rank_frame:=find_widget(master_window, "Ranking_frame")) != None:
        rank_frame.grid()
    else:
        ranking_frame = tk.Frame(master_window, background="wheat", padx=5, pady=5)
        ranking_frame.widgetName = "Ranking_frame"
        ranking_frame.grid_rowconfigure(1, weight=1)
        ranking_frame.grid(row = 0, column=2, rowspan=3, sticky='nsew')

        ranking_title = tk.Label(ranking_frame, text="Team ranking")
        ranking_title.grid(row=0, column=0, sticky='nw')

        rank_box = Treeview(ranking_frame, columns=2, show="headings")
        
        rank_box['columns']=('Rank', 'Team', 'Score')
        rank_box.column('#0', width=0)
        rank_box.column('Rank', width=40, anchor='e')
        rank_box.column('Team', width=200)
        rank_box.column('Score', width=40)

        rank_box.heading('#0', text='')
        rank_box.heading('Rank', text='Rank')
        rank_box.heading('Team', text='Team')
        rank_box.heading('Score', text='Score')
        rank_box.grid(row=1, column=0, sticky='nsew')

        
        sb=tk.Scrollbar(ranking_frame, orient='vertical')
        rank_box.config(yscrollcommand=sb.set)
        sb.config(command = rank_box.yview, width=15)
        sb.grid(row=0, column=1, rowspan=3, sticky='ns')

        data = ["# of Tickets", "Update Age >=30"]
        team_dict = dbi.create_dictionary(dbi.get_tables()[0],dbi.get_teams(), data)

        team_rank = calculate_team_score(team_dict)
        
        team_rank = sorted(team_rank.items(), key=lambda x:x[1])

        for index in range(len(team_rank)):
            rank_box.insert("",'end', values=([index+1]+(list)(team_rank[index])))

def calculate_team_score(team_dict):
    team_data = {}
    team_score = {}
    num_tickets = "# of Tickets"
    untouched = "Update Age >=30"
    #calculate Grand Total first
    team_data["Grand Total"] = {}
    team_data["Grand Total"][num_tickets] = dbi.process_dictionary(team_dict, "Grand Total", num_tickets)[1]

    for team in team_dict.keys():
        if team != "Grand Total":
            team_data[team] = {}        
            team_data[team][num_tickets] = dbi.process_dictionary(team_dict, team, num_tickets)[1]
            team_data[team][untouched] = dbi.process_dictionary(team_dict, team, untouched)[1]
            # % of Grand Total last 4 weeks
            avg_pct_total_arr =[ \
                np.divide(t,GT)*100  \
                for t, GT in zip(team_data[team][num_tickets][-4:], team_data["Grand Total"][num_tickets][-4:])]
            
            # Avg % of Grand Total
            avg_pct_total = np.nanmean(avg_pct_total_arr)
            
            # Calculate % of Grand Total this week
            # subtract avg_pct_total to get deviation (neg is good)
            # add in % untouched
            # round to 3 decimal places
            team_score[team] = round(   (np.divide(team_data[team][num_tickets][-1], \
                                         team_data["Grand Total"][num_tickets][-1])*100) \
                                      -  avg_pct_total \
                                      + (np.divide(team_data[team][untouched][-1], \
                                         team_data["Grand Total"][num_tickets][-1])*100), \
                               3)


    return team_score

def unselect_all(selection_frame):
    if (team_selection := find_widget(selection_frame, "Teams_treeview")) != None:
        team_selection.uncheck_all()
    if (data_selection := find_widget(selection_frame, "Data_treeview")) != None:
        data_selection.uncheck_all()
    keep_frames = ["Selection_frame", "Button_frame", "Data_table_frame", "Ranking_button_frame"]
    for child in get_master_window(selection_frame).winfo_children():
        if type(child)==tk.Frame:
            if child.widgetName not in keep_frames:
                child.grid_remove()
            else:
                if child.widgetName == "Data_table_frame":
                    data_nb = find_widget(child, "Data_notebook")
                    if data_nb.tabs() != None:
                        for tab in data_nb.tabs():
                            data_nb.forget(tab)  
                if child.widgetName ==  "Ranking_button_frame":
                    for button in child.winfo_children():
                        if type(button) == tk.Button:
                            button.grid_remove()
    swap_ranking_buttons(selection_frame)                
    set_window_size(DEFAULT_WINDOW_SIZE, selection_frame)

    

def hide_ranking(frame):
    rank_button_frame = find_widget(master_window:=get_master_window(frame), "Ranking_frame")
    rank_button_frame.grid_remove()
    swap_ranking_buttons(frame)
    
    window_size = DEFAULT_WINDOW_SIZE
    graph = find_widget(master_window, "Graph_frame")
    if graph != None:
        if graph.winfo_ismapped():
            window_size = GRAPH_ONLY_SIZE
    
    set_window_size(window_size, master_window)

def swap_ranking_buttons(frame):
    rank_frame = find_widget((master_window := get_master_window(frame)), "Ranking_frame")
    rank_button_frame = find_widget(master_window, "Ranking_button_frame")
    show_rank_button = find_widget(rank_button_frame, "Show_ranking_button")
    hide_rank_button = find_widget(rank_button_frame, "Hide_ranking_button")
    if hide_rank_button == None:
        hide_rank_button = create_hide_ranking_button(rank_button_frame)

    #if the show button is mapped, hide it and show the hide button
    if show_rank_button.winfo_ismapped():
        show_rank_button.grid_remove()
        hide_rank_button.grid()            
    #if the show button isn't mapped, check if hide button is
    elif hide_rank_button.winfo_ismapped():
        hide_rank_button.grid_remove()
        show_rank_button.grid()
    #if neither are mapped, check if rank_button_frame is mapped
    #and add button accordingly
    else:
        hide_rank_button.grid_remove()
        show_rank_button.grid_remove()

        if rank_frame != None:
            if rank_frame.winfo_ismapped():
                hide_rank_button.grid()
            else:
                show_rank_button.grid()
        else:
            show_rank_button.grid()

#endregion
   
#region App controls
def get_line(graph, team_name, data_name):

    data_line= None
    for plot in graph.axes:
        for line in plot.get_lines():
            team, data = line.get_label().split(": ")
            if team == team_name and data == data_name:
                data_line=line
                break
    
    return data_line

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

def set_window_size(size, frame):
    master= get_master_window(frame)
    master.geometry(size)

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
def create_window():
    window = tk.Tk()
    window.title("Ticket data")
    window.resizable(False,False)
    window.geometry(DEFAULT_WINDOW_SIZE) 
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
    set_window_size(DEFAULT_WINDOW_SIZE,window)
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
    window = create_window()
    window.protocol("WM_DELETE_WINDOW", lambda:quit_me(window))
    create_app(window)
    

    window.mainloop()

main()