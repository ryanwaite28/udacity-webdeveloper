# Tournament Project

### Overview
> This is a project that demonstrates the use of SQL and Databases.
All CRUD(Create|Read|Update|Destroy) functionality are implemented,
as well as creating views. The Database used is Postgresql and manipulated
by Python.

## Game
This is a swiss-style game, which means players are matches based on their
wins and loses. Players that win often will play against others that do
the same.

## How To Setup
* Make sure python 2x is installed (python 3x will work; 2x is preferred)
* Make sure Vagrant and VirtualBox is Installed
* Clone/Download this repository to your local machine
* Open Terminal and change directory to this folder
* Run -> vagrant up , then run -> vagrant ssh
* Change to the tournament folder
* Run -> psql   for postgres cli
* Use tournament.sql to initialize the database
* Run -> python tournament_test.py
* Enjoy the Results!
