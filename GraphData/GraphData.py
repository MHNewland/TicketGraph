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

    #if only 1 set of data is requested, can't access ax[i].plot, must use ax.plot
    if len(data_requested)==1:
        for team in teams:
            date_array, data_array = dbi.process_dictionary(team_dict, team, data_requested[0])                    
            ax.plot(date_array, data_array, linewidth=7.0, label = f"{team}: {data_requested[0]}")

        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.TH, interval=2))
        ax.xaxis.set_minor_locator(tk.AutoMinorLocator(2))
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    else:
        for i in range(len(data_requested)):
            for team in teams:
                date_array, data_array = dbi.process_dictionary(team_dict, team, data_requested[i])                    
                ax[i].plot(date_array, data_array, linewidth=7.0, label = f"{team}: {data_requested[i]}")

            ax[i].xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.TH, interval=2))
            ax[i].xaxis.set_minor_locator(tk.AutoMinorLocator(2))
            ax[i].legend(loc='center left', bbox_to_anchor=(1, 0.5))


    #set the figure width to accommodate the 
    #weeks = (dt.date.today() - date_array[0]).days // 7
    px = (1/plt.rcParams['figure.dpi'])
    fig.set_size_inches(1350*px, 550*px)
    fig.autofmt_xdate()
    fig.tight_layout(pad=1, w_pad=0, h_pad=1)
    #hover=2 means Transient 
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