# Ride-Graph

Ride sharing app implemented using Graphs

[+] Requirements and Dependancies:

1. Python 3.5+
2. Neo4J (communtiy editions recommended)

[+] USAGE:

Start Neo4j Server: 
$cd <NEO4J_HOME>
$./bin/neo4j console

Run main menu file: 
$python main_menu.py

Select required options 

To run the application as in demo:

python3 client.py

This will run the client side of applciation UI that gets a user name and his login credentials.
And upon successful login requests a ride to a destination. And then displays the route navigation
line by line.


python3 driver.py

This will invoke the driver side of the UI that will also authenticate the inputted drivers login
credential and then looking for users around requesting rides. Provides an option to accept/reject
users requesting rides. And then displays the route navigation line by line.


To check the map view of the current world in matplotlib run,

python gui.py

You can find sample historic data that can preloaded to your instance of neo4j under the data/ of this 
project folder. You can use the following API functions available in the api.py to load the function.


python3 main_menu.py

Displays a partial UI of a full-fledge ride sharing application with simple options to register a new user,
login a user and exit.


python3 menu.py

Again, a partial UI of a full-fledge ride sharing application with the menu option after login for the user to 
book a ride, book a ride-share, look for history and logout. 


This is just an UI to showcase how a completed version of the app will look like, although we have not integrated 
major portion of this to our backend as the main focus of this project is maintaining a backend with variety of 
API functionalities and run a powerful matching operation using ML techniques to improve user experience.



