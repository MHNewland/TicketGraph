# TicketGraph
## Description
This app was built to be able to view trend data at my workplace for each team. I was put in charge of building a report to show the number of tickets each team has and information about those tickets. The original reports were created using Excel. 

Due to being in the healthcare system, I am not able to show the raw Excel data as it could contain sensitive data. This is the encapsullated portion of the app that only deals with the snapshot database (see Read Data In) and creates a graph showing trend lines and a table showing information at a quick glance.

</br>

## Packages needed
No packages will be needed if ran from the "Ticket Graph.exe" file within the "Ticket Graph app" folder, only other file that's needed is a TicketData.db file with an actual database within it.

Requirements to run the python files within the GraphData foler are listed in "requirements.txt".

### List of modules: 
* matplotlib==3.6.3
* mplcursors==0.5.2
* numpy==1.24.1
* pandas==1.5.2
* SQLAlchemy==2.0.4
* ttkwidgets==0.13.0

</br>

## Special instructions
There are two options in running the app. You can either launch the "Ticket Graph.exe" application from the "Ticket Graph app" folder, or you can run "GUI.py" from the "GraphData" folder.

</br>
</br>
</br>

# Features

## Read Data In
Data for the ticket graphs are stored in the TicketData.db file.

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
*This is a very broad category, but you’ll have an idea of
how to “clean” and manipulate the data once you see a few videos, so we’re not being
too particular here about what that means for you. For example, if you had telephone
numbers in a DataFrame, some might be written as “(502) 234-2434” and some might be
“502-234-2434”. Still, some might be “5022342434”. Obviously this presents challenges
if you’re trying to compare them, so you might need RegEx to pull out the relevant info.
That’s only an example though, and your mentors can explain further.*

There are a few places where I've cleaned the data.
In the file I used to create the database, I had to replace all instances of character – (En Dash, unicode: U+2013) with - (Hyphen Minus, unicode U+002D) so if the list was sent with regular text, it wouldn't break.

Another spot is within DBInfo.py create_dictionary method. I created a list of valid teams and data headers by pulling from the database again, and created another method called validate_information to compare each requested information to the valid set.

</br>

## Analyze your data
Within GUI.py I have both a data table to show snapshot information about the team that's requested.

Within the dataframe, if "# of Tickets" is requested, it will calculate the X (1-4) week average (if data is missing for any of those weeks), the rate of change over the last 4 weeks, the % of the total tickets, and the percent of the tickets that are untouched.

I also created a team ranking frame that shows most improved to most worsened. It's calculated as

```
(average team ticket % of Grand Total for last 4 weeks) 
- (this week's % of Grand Total) 
+ (% of tickets that haven't been touched in 30+ days)
```


</br>

## Visualize your data
*The standard choice here is just making a couple visualizations then
interpreting them to say something about your data. It can literally be as simple as
writing plt.plot(x,y) and dropping that in the middle of your Jupyter Notebook then saying

a few things about it. This is an extremely useful skill to have. Options 2 and 3 below are
outside the scope of the class, but still worth mentioning because some students have
had particular interests in these areas and have resulted in really interesting projects. If
you don’t want to do the extra work, though, that’s completely okay.*

</br>

## Interpret your data and graphical output
*If your project is in a Jupyter Notebook, this
should be between the important cells. If you’re in a .py file, include your interpretation of
your project in the README. This is often overlooked, but we want to know why you’re
programming certain things. Make sure to put this in markdown in between the cells. No
one, even the best data scientists, will be able to just look at your raw code and
understand your motivation behind why you’re doing certain things. Your explanations
don’t have to be complicated, a quick 2 or 3 sentences on topics is sufficient.*