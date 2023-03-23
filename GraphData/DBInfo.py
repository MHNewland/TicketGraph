import sqlalchemy as sa
import pandas as pd
import datetime as dt

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

#region DB processing
def process_dictionary(team_dict, team, data_requested):
    date_array = [] 
    data_array = []

    #grabs the date
    for date_key, data_dict in team_dict[(str)(team)].items():
        day, month, year = date_key.split('-')
        date = (dt.datetime((int)(year), (int)(month), (int)(day)).date())
        date_array.append(date)
        data_array.append(data_dict[data_requested])

    today = dt.date.today()
    num_weeks = (today - date_array[0]).days//7

    missing_reports=[
        dt.date(2022, 6,  23),
        dt.date(2022, 9,  1 ),
        dt.date(2022, 10, 27),
        dt.date(2022, 11, 24),
        dt.date(2022, 12, 8 ),
        dt.date(2022, 12, 22),
        dt.date(2022, 12, 29),
        dt.date(2023, 1,  5 ), 
        dt.date(2023, 1,  19)
    ]

    # if date_array starts after a missing report,
    # subtract how many reports it starts after.
    missing_weeks=len(missing_reports)
    for i in range(missing_weeks):
        if date_array[0] < missing_reports[i]:
            missing_weeks-=i
            break
    #if a date doesn't exist in the date array, set value to 0.
    for index in range(num_weeks):
        if index < len(date_array):
            #while the next week is in the missing_reports array, add 1 to the weeks to skip
            weeks = 1
            while date_array[index]+dt.timedelta(weeks=weeks) in missing_reports:
                weeks+=1 

        if index+1 < len(date_array):
            if   date_array[index+1] > (date_array[index]+dt.timedelta(days=10)) \
            and (date_array[index]+dt.timedelta(weeks=weeks)) not in date_array:
                    
                    date_array.insert(index+1, (date_array[index]+dt.timedelta(weeks=weeks)))
                    data_array.insert(index+1, 0)

        else:
            while date_array[-1]+dt.timedelta(weeks=1)<=today:
                date_array.append(date_array[-1]+dt.timedelta(weeks=weeks))
                data_array.append(0)

    return (date_array, data_array)

#endregion
