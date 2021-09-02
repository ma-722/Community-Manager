#PROJECT TITLE Community Manager
#### Video Demo:  https://youtu.be/UrBAV67j-HY
#### Description:

##### The contents of the project
I made an application to manage community information such as circles and club activities.
In this application, anyone can add and check information such as money, location of activity, schedule, and members of such a community.

First, I implemented the login feature.
This allows the application to determine who is operating the app and manage the members who participate in the activity.

Once you have logged in, you will be able to see your activity schedule and money information.
In the activity schedule, you can check the activity content, activity location, date and time, and the number of participants at a glance.
In the money information, income is summarized at the top and expenditure is summarized at the bottom.

Participate is a page that indicates whether or not to participate.
Select the activity you want to participate in and press the button to participate, which will be reflected in the number of participants in the schedule.
The same applies to absences.

The remaining items are settings. You can set schedules, income and expenses.


##### The contents and functions of each file created for the project

###### Folder
Inside "static", there are files that decorate this app.
Inside "templates", there are many html files.

###### File
"Layout.html" represents the layout of the application. Other HTML files are created by adding functions to this.
"login.html" gets the username and password.
"register.html" gets the username, password and confirmation password.
"index.html" displays the appointment.
"participate.html" displays the appointment. The app then gets information about which events the user is willing to attend.
"setschedule.html" gets the content, location, date, start time, and end time of schedule.
"setincome.html" gets the content, date and amount of income.
"setexpence.html" gets the content, date and amount of expence.

"Application.py" is the main part of this application.
Insert the input from HTML into the database.
It also displays database information to the user.
If there is an input error, let the user know what it is and ask them to enter it again.
In summary, it's the interface between the user and the database.

"Helpers.py" assists the operation of "application.py".
There is a function called "login_required" that checks if the session has a user ID and returns to the login screen if it doesn't.
This allows you to implement the login function.

"finance.db" is the database for this application.
The structure is as follows. Stores information about users, schedules, participants, assets, and liabilities.

CREATE TABLE users (id INTEGER, username TEXT NOT NULL, hash TEXT NOT NULL, PRIMARY KEY(id));
CREATE UNIQUE INDEX username ON users (username);
CREATE TABLE schedule(id INTEGER, contents TEXT NOT NULL UNIQUE, location TEXT NOT NULL, date DATE NUT NULL, start_time TIME NOT NULL , end_time TIME NOT NULL, participants INTEGER NOT NULL, PRIMARY KEY(id));
CREATE TABLE participation(id INTEGER, schedule_id INTEGER NOT NULL, user_id INTEGER NOT NULL, PRIMARY KEY(id), FOREIGN KEY(schedule_id) references schedule(id), FOREIGN KEY(user_id) references users(id));
CREATE TABLE assets(id INTEGER, accounting_title TEXT, amount INTEGER NUT NULL, date DATE NUT NULL, PRIMARY KEY(id));
CREATE TABLE liabilities(id INTEGER, accounting_title TEXT, amount INTEGER NUT NULL, date DATE NUT NULL, PRIMARY KEY(id));
