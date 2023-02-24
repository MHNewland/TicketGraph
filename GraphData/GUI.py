from tkinter import *
from tkinter.ttk import *
from ttkwidgets import CheckboxTreeview
import GraphData as gd
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)

def create_team_box(window):
    teams = sorted((list)(gd.get_teams()))
    team_frame = Frame(window)
    team_frame.grid(row=0, column=0)    
    create_box(team_frame, teams, "Teams")

def create_data_box(window):
    data = sorted((list)(gd.get_data_headers()))
    data_frame = Frame(window)
    data_frame.grid(row=0, column=1)
    create_box(data_frame, data, "Data")


def create_box(frame, items, label):
    frame.config(width=300,height=200)
    treeview = CheckboxTreeview(frame)
    treeview.heading('#0', text=label, anchor=W)
    treeview.column("#0", width=260, stretch=NO)
    sb=Scrollbar(frame, orient=VERTICAL)
    treeview.config(yscrollcommand=sb.set)
    sb.config(command = treeview.yview)
    treeview.grid(row=0, column=0, sticky=W)
    sb.grid(row=0, column=1,sticky=NS)
    for item in items:
        treeview.insert("", END, item, text=item)

def create_submit_button(window):
    submit = Button(window, text="Submit", command=lambda: get_data(window))
    submit.grid(row=1, column=0, sticky=W)

def create_unselect_button(window):
    unselect = Button(window, text="Unselect all", command=lambda: unselect_all(window))
    unselect.grid(row=1, column=1, sticky=W)

def get_data(selection_frame):
    test = []
    for frame in selection_frame.winfo_children():
        if type(frame) == Frame:
            for f in frame.winfo_children():
                if type(f) == CheckboxTreeview:
                    test.append(f.get_checked())
    if len(test[0])==0 or len(test[1])==0:
        return
    team_dict = gd.create_dictionary(gd.get_tables()[0], test[0], test[1])
    graph = gd.display_graph(team_dict, test[0], test[1])

    canvas = FigureCanvasTkAgg(graph, get_master_window(selection_frame))
    canvas.draw()
    canvas.get_tk_widget().grid(row=2, column=0, columnspan=3, sticky=EW, pady=10)
    set_window_size(canvas.get_width_height()[0], canvas.get_width_height()[1]+globals()['window_height'],selection_frame)

def unselect_all(selection_frame):
    set_window_size(globals()["window_width"], globals()["window_height"],selection_frame)
    for frame in selection_frame.winfo_children():
        if type(frame) == Frame:
            for f in frame.winfo_children():
                if type(f) == CheckboxTreeview:
                    for item in f.get_checked():
                        f.change_state(item, "unchecked")

def create_selection_frame(window):
    selection_frame = Frame(window)
    create_team_box(selection_frame)
    create_data_box(selection_frame)
    create_submit_button(selection_frame)
    create_unselect_button(selection_frame)
    selection_frame.grid(row=0, column=0, sticky=W)

def set_window_size(w, h, frame):
    master= get_master_window(frame)
    master.geometry(f"{w}x{h}")

def get_master_window(frame):
    try:
        master = frame.master
        while master.master != None:
            master=master.master
    except Exception as err:
        print(err)
        return None
    return master

def create_window(w, h):
    window = Tk()
    window.title("Ticket data")
    window.resizable(False,False)
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
    create_selection_frame(window)
    window.mainloop()

main()