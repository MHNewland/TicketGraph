import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as tk
import mplcursors as mpc
import DBInfo as dbi

#region Graph
'''
create the arrays to use as coordinates to plot

structure of team_dict
team_dict = {'team': "Team Name"
                {'date': 2020-01-01
                    {'data1': 5}
                    {'data2': 7} 
                }
                {'date': 2020-01-08
                    {'data1': 9}
                    {'data2': 2} 
                }
            }

for each team in the dictionary,
    add the date to the x coordinates
    then create an array for each data set for the y coordinates

from example above,
x= [date(01-01-2020), date(01-08-2020)]
data1 = [5, 9]
data2 = [7, 2]

'''
def display_graph(team_dict, teams, data_requested):
    # plot
    fig, ax = plt.subplots(len(data_requested))
    loc = locals()
    current_team = ''
    most_info = 0
    for team in teams:
        x = [] #date
        data = [] #names of line to graph

        #grabs the date
        for date_key, data_dict in team_dict[(str)(team)].items():
            day, month, year = date_key.split('-')
            date = (dt.datetime((int)(year), (int)(month), (int)(day)).date())
            x.append(date)

            #whenever team changes, create/clear data variables
            if current_team != team: 
                for data_name in data_dict.keys():
                    if data_name in data_requested:   
                        data_name_str = (str)(data_name)
                        #creates a local variable {data_name}[] if it doesn't exist or clears it if it does
                        loc[data_name_str]=[] 
                current_team=team
            
            #if the name of the dataset doesn't appear in the names of line to graph, add it in            
            #add the data_value to the local variable {data_name}[]
            for data_name, data_value in data_dict.items():
                if data_name in data_requested:
                    if data_name not in data:
                        data.append(data_name)
                    data_name_str = (str)(data_name)
                    loc[data_name_str].append(data_value)


        #create the plots and graph for current team
        if len(data) == 1:
            ax.plot(x, loc[data[0]], linewidth=7.0, label = f"{team}: {data[0]}")
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.TH, interval=2))
            ax.xaxis.set_minor_locator(tk.AutoMinorLocator(2))
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        else:
            for i in range(len(data)):
                if len(loc[data[i]]) == len(x): 
                    ax[i].plot(x, loc[data[i]], linewidth=5.0, label = f"{team}: {data[i]}")
                    ax[i].xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.TH, interval=2))
                    ax[i].xaxis.set_minor_locator(tk.AutoMinorLocator(2))
                    ax[i].legend(loc='center left', bbox_to_anchor=(1, 0.5))
                else:
                    print("data doesn't match")
        #if a list doesn't have all the dates, find the one with the most dates
        if len(x)> most_info:
            most_info=len(x)

    #set the figure width to accommodate the 
    fig.set_figwidth((most_info/6) + 10)
    fig.autofmt_xdate()
    fig.tight_layout(pad=1, w_pad=0, h_pad=1)
    cursor = mpc.cursor(hover=2)
    @cursor.connect("add")
    def on_add(sel):
        sel_date = mdates.num2date(sel[1][0]).date() 
        if(sel_date.weekday() != mdates.TH.weekday): 
            sel_date = sel_date + dt.timedelta(days=(mdates.TH.weekday - sel_date.weekday()))
        graph_title=sel.artist.get_label()
        anno_team, anno_data = graph_title.split(": ")
        try:
            dict_data = round(team_dict[anno_team][sel_date.strftime('%d-%m-%Y')][anno_data])
        except KeyError:
            dict_data= round(sel[1][1])
        sel.annotation.set_text(f"{sel.artist.get_label()}\n" \
                                f"{sel_date}: " \
                                f"{dict_data}")
        cursor.visible=True

        
    #plt.show()
    return fig

#endregion

def main():
    teams = ["CAB"]
    for team in teams:
        print(team)
    headers = dbi.get_data_headers()[1:3]
    for header in headers:
        print(header)
    table = dbi.get_tables()

    dict = dbi.create_dictionary(table[0], teams, headers)
    display_graph(dict, teams, headers)

#main()