import tkinter as tk
from tkinter.ttk import Notebook
from ttkwidgets import CheckboxTreeview
import GraphData as gd
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)


def create_selection_frame(window):
    '''
    | team_box  | data_box  |
    '''
    selection_frame = tk.Frame(window, background="red", padx=5, pady=5)
    selection_frame.grid(row=0, column=0, columnspan=2, sticky='nsew')
    selection_frame.widgetName = "Selection_frame"
    create_team_box(selection_frame)
    create_data_box(selection_frame)

def create_team_box(frame):
    teams = sorted((list)(gd.get_teams()))
    team_frame = tk.Frame(frame,background='teal', padx=5, pady=5)
    team_frame.widgetName = "Team_frame"
    team_frame.grid(row=0, column=0)    
    create_box(team_frame, teams, "Teams")

def create_data_box(frame):
    data = sorted((list)(gd.get_data_headers()))
    data_frame = tk.Frame(frame,background='lime', padx=5, pady=5)
    data_frame.widgetName = "Data_frame"
    data_frame.grid(row=0, column=1)
    create_box(data_frame, data, "Data")

def create_box(frame, items, label):
    #frame.config(width=300,height=200)
    treeview = CheckboxTreeview(frame)
    treeview.widgetName = f"{label}_treeview"
    treeview.heading('#0', text=label, anchor='w')
    treeview.column("#0", width=250)
    sb=tk.Scrollbar(frame, orient='vertical')
    treeview.config(yscrollcommand=sb.set)
    sb.config(command = treeview.yview)
    treeview.grid(row=0, column=0, sticky='w')
    sb.grid(row=0, column=1,sticky='ns')
    for item in items:
        treeview.insert("", 'end', item, text=item)
    

def create_data_table(frame):
    data_table_frame = tk.Frame(frame, background='purple', padx=5, pady=5)
    data_table_frame.grid(row=0, column=2, rowspan=2, sticky='nsew')
    data_nb = Notebook(data_table_frame)
    data_nb.grid(row=0, column=0, sticky='w')
    data_nb.config(height=200)
    data_nb.widgetName = "Data_notebook"

def fill_data_table(frame, teams):
    team_frames = []
    data_nb = find_widget(frame, "Data_notebook")
    if data_nb.tabs() != None:
        for tab in data_nb.tabs():
            data_nb.forget(tab)
    for i in range(len(teams)):
        team_frames.append(tk.Frame(data_nb,background="white"))
        data_nb.add(team_frames[i], text=f"{teams[i]}")
        label_test = tk.Label(team_frames[i], text=f"{teams[i]}")
        label_test.grid(row=0, column=0)

def create_button_frame(frame):
    '''
    | submit_button | unselect_button   |
    '''
    button_frame = tk.Frame(frame, background="blue", padx=5, pady=5)
    button_frame.widgetName = "Button_frame"
    button_frame.grid(row=1, column=0, columnspan=2, sticky='nsew')

    button_frame.columnconfigure(0,weight=1)
    button_frame.columnconfigure(1, weight=1, uniform="1")

    create_submit_button(button_frame)
    create_unselect_button(button_frame)

def create_submit_button(frame):
    submit_frame = tk.Frame(frame, background="green", height=30)
    submit_frame.widgetName = "Submit_frame"
    submit_frame.grid(row=0, column=0, sticky='nsew')
    submit_frame.grid_propagate(False)
    submit = tk.Button(submit_frame, text="Submit", command=lambda: get_data(frame))
    submit.grid(row=0, column=0)

def create_unselect_button(frame):
    unselect_frame = tk.Frame(frame, background="aqua", height=30)
    unselect_frame.widgetName = "Unselect_frame"
    unselect_frame.grid(row=0, column=1, sticky='nsew')
    unselect_frame.grid_propagate(False)
    unselect = tk.Button(unselect_frame, text="Unselect all", command=lambda: unselect_all(frame))
    unselect.grid(row=0, column=0)


def get_data(frame):
    # CheckboxTreeview.get_checked() returns a list of all checked items in that checkbox
    # teams_checked will be the list of teams
    # data_checked will be the list of data requested
    selection_frame = find_widget(get_master_window(frame), "Selection_frame")
    if selection_frame != None:
        teams_checked = find_widget(get_master_window(frame), "Teams_treeview").get_checked()
        data_checked = find_widget(get_master_window(frame), "Data_treeview").get_checked()
        if len(teams_checked)==0 or len(data_checked)==0:
            return
        team_dict = gd.create_dictionary(gd.get_tables()[0], teams_checked, data_checked)
        graph = gd.display_graph(team_dict, teams_checked, data_checked)
        canvas = FigureCanvasTkAgg(graph, get_master_window(selection_frame))
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=0, columnspan=3, sticky='ew', pady=10)
        set_window_size(canvas.get_width_height()[0], canvas.get_width_height()[1]+globals()['window_height'],selection_frame)
        fill_data_table(get_master_window(frame), teams_checked)

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

def unselect_all(selection_frame):
    master_window = get_master_window(selection_frame)
    set_window_size(globals()["window_width"], globals()["window_height"],master_window)

    try:
        teams = find_widget(master_window, "Teams_treeview")
        for item in teams.get_checked():
                teams.change_state(item, "unchecked")
        data = find_widget(master_window, "Data_treeview")
        for item in data.get_checked():
            data.change_state(item, "unchecked")
    except Exception as err:
        print(err)

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

def create_window(w, h):
    window = tk.Tk()
    window.title("Ticket data")
    #window.resizable(False,False)
    window.geometry(f"{w}x{h}") 
    return window
    
def quit_me(window):
    window.quit()
    window.destroy()


def main():
    globals()['window_width'] = 560
    globals()['window_height'] = 260
    window = create_window(globals()['window_width'], globals()['window_height'])
    window.protocol("WM_DELETE_WINDOW", lambda:quit_me(window))
    #window.grid_columnconfigure(1, weight=1)
    #window.grid_columnconfigure(2, weight=1)
    #window.grid_columnconfigure(3, weight=2)

    '''
    | [selection_frame | selection_frame] |   [data_table]  |
    |    [button_frame | button_frame]    |   [data_table]  |
    |          [canvas |     canvas       | canvas]         |
    '''
    window_frame = tk.Frame(window, background='yellow', padx=5, pady=5)
    window_frame.grid(row=0, column=0)
    create_selection_frame(window_frame)
    create_data_table(window_frame)
    create_button_frame(window_frame)

    window.mainloop()

main()