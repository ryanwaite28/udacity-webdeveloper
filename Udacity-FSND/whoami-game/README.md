# Who Am I?
## Guessing Game!
---
### Link To Deployed Site - https://gamewai-142922.appspot.com/
---
This is a game that is implemented using Google App Engine + Cloud Endpoints.
Users can create an account and play games where they must guess a person after
being given a few hints.

#Technologies Used
This Web App Includes:

* HTML
* CSS
* JavaScript
* Python
* Google App Engine
* Cloud Endpoints
* JinJa

#How To Play

First, a user must make an account with the api application. Only google accounts
are accepted. Once an account is created, users can start a new guessing game.
They are given 3 hints and 3 tries to guess a person. Score is based on win over
the total amount of games played. Each game will update the user's scores.

#Endpoint Methods

* testonemethod - made for testing
* testtwomethod - made for testing
* createuser - creates and/or return account info by google signin
* getuser - if exists, returns current users account info
* creategame - creates a new game. users can only play 1 game at a time
* getcurrentgame - if exists, returns current user's current game
* deletecurrentgame - deletes user's current game
* guessanswer - guesses an answer for current game. requires request body with 'msg' field

#How To Setup

To run this app on your local machine, please follow the below steps:

1. make sure a python interpreter is installed
2. download and install google app engine, as well as the SDKs
3. in the terminal/command line, install jinja (pip install jinja2)
4. launch google app engine launcher
5. open existing application (download this zip or clone this repo)
6. click run
7. In a web browser, go to - http://localhost:8080/_ah/api/explorer (or whatever the port you specified)
8. Explore The API and Happy Guessing!
