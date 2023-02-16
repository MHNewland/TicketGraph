import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as tk
import sqlalchemy as sa

def create_dictionary(table, teams, data_wanted, engine = sa.create_engine("sqlite:///TicketData.db")):
    if table == None or len(teams)==0 or len(data_wanted)==0:
        return
    param_list = ['Team', 'Date']
    ''' structure of team_dict
    team_dict = {'team':
                    {'date':
                        {'data1': ''}
                        {'data2': ''} 
                    }
                }
    '''        
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

def display_graph(team_dict, teams, data):
    # plot
    fig, ax = plt.subplots(len(data))
    loc = locals()
    current_team = ''
    most_info = 0
    for team in teams:
        x = [] #date
        data = [] #number of lines to graph
        for key, value in team_dict[(str)(team)].items():
            day, month, year = key.split('-')
            date = (dt.datetime((int)(year), (int)(month), (int)(day)).date())
            x.append(date)
            if current_team != team: #whenever team changes, create/clear data variables
                for k in value.keys():    
                    var = (str)(k)
                    loc[var]=[] #creates the key if it doesn't exist or clears it if it does
                current_team=team
            for k, v in value.items():
                var = (str)(k)
                loc[var].append(v)
                if var not in data:
                    data.append(var)
        if len(data) == 1:
            ax.plot(x, loc[data[0]], linewidth=2.0, label = f"{team}: {data[0]}")
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.TH, interval=2))
            ax.xaxis.set_minor_locator(tk.AutoMinorLocator(2))
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))   
        else:
            for i in range(len(data)):
                if len(loc[data[i]]) == len(x): 
                    ax[i].plot(x, loc[data[i]], linewidth=2.0, label = f"{team}: {data[i]}")
                    ax[i].xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.TH, interval=2))
                    ax[i].xaxis.set_minor_locator(tk.AutoMinorLocator(2))
                    ax[i].legend(loc='center left', bbox_to_anchor=(1, 0.5))
                else:
                    print("data doesn't match")
        if len(x)> most_info:
            most_info=len(x)
    fig.set_figwidth(most_info/2)
    fig.autofmt_xdate()
    fig.tight_layout(pad=.5, w_pad=0, h_pad=1)
    #plt.show()
    return fig

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

def main():
    teams = get_teams()[:3]
    for team in teams:
        print(team)
    headers = get_data_headers()[1:3]
    for header in headers:
        print(header)
    table = get_tables()

    dict = create_dictionary(table[0], teams, headers)
    display_graph(dict, teams, headers)

#main()