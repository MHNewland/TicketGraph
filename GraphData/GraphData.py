import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as tk
import sqlalchemy as sa
import mplcursors as mpc

#region Data setup

'''
structure of team_dict

team_dict = {'team':
                {'date':
                    {'data1': ''}
                    {'data2': ''} 
                }
            }

'''   
def create_dictionary(table, teams, data_wanted, engine = sa.create_engine("sqlite:///TicketData.db")):
    if table == None or len(teams)==0 or len(data_wanted)==0:
        return
    param_list = ['Team', 'Date']
     
    #make sure all teams listed are valid
    valid_teams = (list)(get_teams(engine))
    validated_teams = validate_information(teams, valid_teams)

    team_list = create_sql_list("Team", validated_teams)

    #make sure data is valid
    valid_data = (list)(get_data_headers(engine))
    validated_data = validate_information(data_wanted, valid_data)
    
    team_dict = {}
    var = locals()
    for item in validated_data:
        data_name = f"data.{item}"
        var[data_name] = ''
        param_list.append(f'"{item}"')


    with engine.connect() as conn:
        data = pd.read_sql(sa.text(f"select {', '.join(param_list)} from {table}\
                                     where ({''.join(team_list)})"), con=conn).values
        for line in data:
            team = line[0]
            date = line[1]
            if team_dict.get(team) == None:
                team_dict[team]={}
            if team_dict[team].get(date) == None:
                team_dict[team][date] = {}

            if len(data_wanted) == len(line)-2:
                for i in range(len(data_wanted)):
                    var[f"data.{data_wanted[i]}"] = line[i+2]
                    
            for d in data_wanted:
                if d not in team_dict[team][date].keys():
                    team_dict[team][date][d]=''
                team_dict[team][date].update({d:var[f"data.{d}"]})
     
    return team_dict

def validate_information(info, test_against):
    new_arr = info
    remove_info = []
    for data in info:
        if data not in test_against:
            remove_info.append(data)
    for item in remove_info:
        print(f"removing invalid item: {item}")        
        new_arr.remove(item)
    return new_arr

def create_sql_list(data_name, list):
    sql_list = []
    for item in list:
        sql_list.append(f'{data_name} = "{item}"')
        sql_list.append(" or ")
    else:
        sql_list.pop()
    return sql_list
#endregion

#region DB read (for validation)
def get_teams(engine = sa.create_engine("sqlite:///TicketData.db")):
    with engine.connect() as conn:
        table_names = get_tables(engine = engine)
        for table in table_names:
            data = pd.read_sql(sa.text(f"Select distinct Team from {table}"), con=conn, index_col="Team")
        return(data.index)

def get_tables(engine = sa.create_engine("sqlite:///TicketData.db")):
    with engine.connect() as conn:
        inspector = sa.inspect(conn)
        return inspector.get_table_names(engine=engine)

def get_data_headers(engine = sa.create_engine("sqlite:///TicketData.db")):
    with engine.connect() as conn:
        inspector = sa.inspect(conn)
        columns = []
        for table in inspector.get_table_names():
            column = inspector.get_columns(table)
            for col in column:
                col_name = col["name"]
                if col_name not in ['index', 'Team', 'Date']:
                    line = f'{col_name}'
                    columns.append(line)
        return columns
#endregion

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
                    data_name_str = (str)(data_name)
                    #creates a local variable {data_name}[] if it doesn't exist or clears it if it does
                    loc[data_name_str]=[] 
                current_team=team
            
            #if the name of the dataset doesn't appear in the names of line to graph, add it in            
            #add the data_value to the local variable {data_name}[]
            for data_name, data_value in data_dict.items():
                if data_name_str not in data:
                    data.append(data_name_str)
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
    fig.tight_layout(pad=.5, w_pad=0, h_pad=1)
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
    headers = get_data_headers()[1:3]
    for header in headers:
        print(header)
    table = get_tables()

    dict = create_dictionary(table[0], teams, headers)
    display_graph(dict, teams, headers)

#main()