# --- Imports --- #

import httplib
import endpoints
from protorpc import messages
from google.appengine.ext import ndb

# --- Classes --- #

class ConflictException(endpoints.ServiceException):
    """ConflictException -- exception mapped to HTTP 409 response"""
    http_status = httplib.CONFLICT

# --- DataStore Kinds

class Users(ndb.Model):
    displayname       = ndb.StringProperty(required=True)
    email             = ndb.StringProperty(required=True)
    uv                = ndb.StringProperty()

    current_game_id   = ndb.IntegerProperty(default = 0)
    games_played      = ndb.IntegerProperty(default = 0)
    games_won         = ndb.IntegerProperty(default = 0)
    games_lost        = ndb.IntegerProperty(default = 0)

    created           = ndb.DateTimeProperty(auto_now_add=True)
    modified          = ndb.DateTimeProperty(auto_now=True)



class Games(ndb.Model):
    user_id           = ndb.IntegerProperty(required=True)
    uv                = ndb.StringProperty()
    status            = ndb.StringProperty()
    active            = ndb.BooleanProperty(required=True, default = True)
    tries             = ndb.IntegerProperty(required=True, default = 0)

    answer            = ndb.StringProperty(required=True)
    hint_one          = ndb.StringProperty(required=True)
    hint_two          = ndb.StringProperty(required=True)
    hint_three        = ndb.StringProperty(required=True)

    created           = ndb.DateTimeProperty(auto_now_add=True)
    modified          = ndb.DateTimeProperty(auto_now=True)

# --- Request/Response Messages

class aMessage(messages.Message):
    ''' TestOne message '''
    msg = messages.StringField(1)

class guessMessage(messages.Message):
    ''' TestOne message '''
    msg = messages.StringField(1)

class newUserMSGin(messages.Message):
    displayname    = messages.StringField(1)
    email          = messages.StringField(2)

class newUserMSGout(messages.Message):
    displayname    = messages.StringField(1)
    email          = messages.StringField(2)
    uv             = messages.StringField(3)
    msg            = messages.StringField(4)


class getUserMSGout(messages.Message):
    displayname    = messages.StringField(1)
    email          = messages.StringField(2)
    uv             = messages.StringField(3)
    msg            = messages.StringField(4)

    current_game_id   = messages.IntegerField(5)
    games_played      = messages.IntegerField(6)
    games_won         = messages.IntegerField(7)
    games_lost        = messages.IntegerField(8)

    created           = messages.StringField(9)
    modified          = messages.StringField(10)


class newGameMSGin(messages.Message):
    user_id        = messages.IntegerField(1)

    answer         = messages.StringField(2)
    hint_one       = messages.StringField(3)
    hint_two       = messages.StringField(4)
    hint_three     = messages.StringField(5)

class newGameMSGout(messages.Message):
    game_id        = messages.IntegerField(1)
    uv             = messages.StringField(2)
    msg            = messages.StringField(3)

    hint_one       = messages.StringField(4)
    hint_two       = messages.StringField(5)
    hint_three     = messages.StringField(6)


class aGameMSGout(messages.Message):
    user           = messages.StringField(1)
    tries          = messages.IntegerField(2)
    msg            = messages.StringField(3)
    date           = messages.StringField(4)

class topScoresMSG(messages.Message):
    msg            = messages.StringField(1)
    users          = messages.MessageField(getUserMSGout, 2, repeated=True)

class recentGamesMSG(messages.Message):
    msg            = messages.StringField(1)
    games          = messages.MessageField(aGameMSGout, 2, repeated=True)


# --- Resource Containers --- #

NewUserCont = endpoints.ResourceContainer(
        # The request body
        newUserMSGin,
        # Accept one url parameter: and integer named 'id'
        )

aMessageCont = endpoints.ResourceContainer(
        # The request body
        aMessage,
        # Accept one url parameter: and integer named 'id'
        )

guessMessageCont = endpoints.ResourceContainer(
        # The request body
        guessMessage,
        # Accept one url parameter: and integer named 'id'
        )
