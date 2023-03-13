# TicketGraph
## Description
This app was built to be able to view trend data at my workplace for each team. I was put in charge of building a report to show the number of tickets each team has and information about those tickets. The original reports were created using Excel. 

Due to being in the healthcare system, I am not able to show the raw Excel sheets as it could contain sensitive data. This is the encapsullated portion of the app that only deals with the snapshot database (see Read Data In) and creates a graph showing trend lines and a table showing information at a quick glance.

</br>

## Packages needed
No packages will be needed if ran from the "Ticket Graph.exe" file within the "Ticket Graph app" folder, only other file that's needed is a TicketData.db file with an actual database within it.

Requirements to run the python files within the GraphData foler are listed in "requirements.txt".

### List of modules: 
* matplotlib==3.6.3
* mplcursors==0.5.2
* numpy==1.24.1
* pandas==1.5.3
* SQLAlchemy==2.0.1
* ttkwidgets==0.13.0

</br>

## Special instructions
There are two options in running the app. You can either launch the "Ticket Graph.exe" application from the "Ticket Graph app" folder, or you can run "GUI.py" from the "GraphData" folder.

</br>
</br>
</br>

# Features

## Read Data In
### Not shown in project

The sensitive portion of the project was mainly coded in VBA. My workplace uses the Sysaid ticketing system which I set up to email me a report every week. I created a template file in which I could pull the data from the emailed report, and it would format the data into readable sheets. I'd then save a copy of the excel file in a reports folder with the date at the end of the name.

I used VBA to automate this portion. Those excel files were used to create the TicketData.db file by pulling the information from the first sheet of each excel file (the snapshot information) and storing it in the database, adding a column for the date the data came from.

### In the project

Within GraphData.py, the information is read in using pandas and SQLAlchemy within the "create_dictionary()" method.
The param_list variable is a list containing "Team" and "Date" by default and adds any other requested data to the list.
The team_list contains a string created by taking the requested team names, validating the list, then joining the teams together in a string with "or" in between.

```python
data = pd.read_sql(sa.text(f"select {', '.join(param_list)} from {table}\
                                where ({''.join(team_list)})"), con=conn).values

``` 
For example if create_dictionary was called with these parameters:
```python
teams = ["End User Computing", "Service Desk"]
data_wanted = ["# of Tickets"]
```
the string would be:
```python
sa.text(f"SELECT 'Team', 'Date', '# of Tickets' from {table} where Team = 'End User Computing' or Team = 'Service Desk'")
```

</br>

## Manipulate and clean your data
There are a few places where I've cleaned the data.
In the file I used to create the database, I had to replace all instances of character – (En Dash, unicode: U+2013) with - (Hyphen Minus, unicode U+002D) so if the list was sent with regular text, it wouldn't break.

Another spot is within DBInfo.py create_dictionary method. I created a list of valid teams and data headers by pulling from the database again, and created another method called validate_information to compare each requested information to the valid set.

</br>

## Analyze your data
In GUI.py I have both a data table to show snapshot information about the team that's requested.

Within the dataframe, if "# of Tickets" is requested, it will calculate the X (1-4) week average (if data is missing for any of those weeks), the rate of change over the last 4 weeks, the percent of the total tickets, and the percent of the tickets that are untouched.

I also created a team ranking frame that shows most improved to most worsened. It's calculated as

```
(this week's % of Grand Total)  
- (average team ticket % of Grand Total for last 4 weeks)
+ (% of tickets that haven't been touched in 30+ days)
```

</br>

## Visualize your data
The app allows the user to select each team and type of data they want to view using the fields in the Selection Frame. After checking at least one team and one dataset, clicking "Submit" will generate a line graph showing the trend lines as well as fill out the Data Table with information about each team selected.

The graph also allows the user to hover over sections to give more detailed information on the numbers for that part of the line.

</br>

## Interpret your data and graphical output
I chose to use a line graph so that it would be easier to see how a team's staus is trending. I also wanted to make sure information was easily seen at a glance, which is why I added the data table at top. The ranking frame is to be able to see how much progress a team has made (or how much they've slipped) compared to recent weeks without having to go through each team's graph.