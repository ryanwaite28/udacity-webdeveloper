# --- Imports --- #

import random, string
from datetime import datetime

import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote

from google.appengine.api import memcache
from google.appengine.api import taskqueue
from google.appengine.api import app_identity
from google.appengine.api import mail
from google.appengine.ext import ndb

from WAIoptions import options

from models import aMessage
from models import guessMessage
from models import topScoresMSG
from models import recentGamesMSG
from models import NewUserCont
from models import aMessageCont
from models import aGameMSGout
from models import guessMessageCont

from models import ConflictException
from models import Users
from models import Games
from models import newUserMSGin
from models import newUserMSGout
from models import getUserMSGout
from models import newGameMSGin
from models import newGameMSGout

# --- Setup Code --- #

WEB_CLIENT_ID = '1084459565417-7gbdjm8cdcggu1ngfimlf3gmv9rmo68e.apps.googleusercontent.com'
API_EXP_CLIENT_ID = endpoints.API_EXPLORER_CLIENT_ID

allowed_clients = [
    WEB_CLIENT_ID,
    API_EXP_CLIENT_ID
]

# --- Tools --- #

def randomVal():
    uv = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(33))

    return uv

# --- API & Endpoints --- #

@endpoints.api(name='whoamigame',
                version='v1',
                allowed_client_ids=allowed_clients)
class WhoAmIGameApi(remote.Service):

    # --- Game Endpoints --- # user = endpoints.get_current_user()

    # --- Create User
    @endpoints.method(message_types.VoidMessage, newUserMSGout,
                        path='createuser', http_method='POST',
                        name='createuser')
    def createUser(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
            return newUserMSGout(msg='Not Logged In!',
                                    displayname='', email='', uv='')

        displayname = user.nickname()
        email = user.email()
        uv = randomVal()

        user2 = Users.query(Users.email == email).get()
        if user2:
            return newUserMSGout(msg='Account Already Exists!',
                                    displayname=user2.displayname,
                                    email=user2.email,
                                    uv=user2.uv)

        newUser = Users(displayname=displayname, email=email, uv=uv)
        k = newUser.put()

        taskqueue.add(params={'email': email,
        'userInfo': repr(newUser) + ' - https://gamewai-142922.appspot.com/'},
            url='/tasks/send_newuser_email'
        )

        return newUserMSGout(displayname=displayname, email=email, uv=uv,
                                msg='Account Created!')

    # --- Get User
    @endpoints.method(message_types.VoidMessage, getUserMSGout, path='getuser',
                        http_method='POST', name='getuser')
    def getUser(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
            return getUserMSGout(msg='Not Logged In!',
                                    displayname='', email='', uv='',
                                    current_game_id=0, games_played=0,
                                    games_won=0, games_lost=0,
                                    created='',modified='')

        email = user.email()
        user2 = Users.query(Users.email == email).get()

        if user2:
            created = str(user2.created)
            modified = str(user2.modified)
            return getUserMSGout(msg='User Acount Info.',
                                    displayname=user2.displayname,
                                    email=user2.email,
                                    uv=user2.uv,
                                    current_game_id=user2.current_game_id,
                                    games_played=user2.games_played,
                                    games_won=user2.games_won,
                                    games_lost=user2.games_lost,
                                    created=created,
                                    modified=modified)
        else:
            return getUserMSGout(msg='Account Does Not Exists.',
                                    displayname='', email='', uv='',
                                    current_game_id=0, games_played=0,
                                    games_won=0, games_lost=0,
                                    created='',modified='')

    # --- Create Game
    @endpoints.method(message_types.VoidMessage, newGameMSGout,
                        path='creategame', http_method='POST',
                        name='creategame')
    def createGame(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
            return newGameMSGout(msg='Not Logged In!',
                                    uv='', game_id=0,
                                    hint_one='',hint_two='',hint_three='')
        email = user.email()
        user2 = Users.query(Users.email == email).get()
        # print user2
        if not user2:
            msg = 'Email Does Not Exist In App. Please Create Account.'
            return newGameMSGout(msg=msg,
                                    uv='', game_id=0,
                                    hint_one='',hint_two='',hint_three='')

        user_id = user2.key.id()
        checkGame = Games \
        .query(ndb.AND(Games.user_id == user_id, Games.active == True)).get()
        if checkGame:
            msg = ''' You already have an active game. That game must be
                finished before starting a new one.
                You Guessed %s Times.''' % checkGame.tries
            return newGameMSGout(msg=msg,
                                    uv='', game_id=0,
                                    hint_one='',hint_two='',hint_three='')

        game = random.choice(options)
        uv = randomVal()

        newGame = Games(user_id=user_id, uv=uv,
                        answer=game['answer'], hint_one=game['hintONE'],
                        hint_two=game['hintTWO'], hint_three=game['hintTHREE'])

        ng = newGame.put()
        # print ng
        ng = ng.id()
        user2.current_game_id = ng
        user2.put()

        taskqueue.add(params={'email': email, 'gameInfo':
            'New Game!!! https://gamewai-142922.appspot.com/'},
            url='/tasks/send_newgame_email'
        )

        return newGameMSGout(msg='New Game Created! Guess Who It Is...',
                                uv=newGame.uv, game_id=ng,
                                hint_one=newGame.hint_one,
                                hint_two=newGame.hint_two,
                                hint_three=newGame.hint_three)


    # --- Get Current Game
    @endpoints.method(message_types.VoidMessage, newGameMSGout,
                        path='getcurrentgame', http_method='POST',
                        name='getcurrentgame')
    def getCurrentGame(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
            return newGameMSGout(msg='Not Logged In!',
                                    uv='', game_id=0,
                                    hint_one='',hint_two='',hint_three='')

        email = user.email()
        user2 = Users.query(Users.email == email).get()
        user_id = user2.key.id()
        if not user2:
            return newGameMSGout(msg='Account Does Not Exist!',
                                    uv='', game_id=0,
                                    hint_one='',hint_two='',hint_three='')

        checkGame = Games \
        .query(ndb.AND(Games.user_id == user_id, Games.active == True)).get()
        if checkGame:
            game_id = checkGame.key.id()
            return newGameMSGout(msg='Current Game.',
                                    uv=checkGame.uv,
                                    game_id=game_id,
                                    hint_one=checkGame.hint_one,
                                    hint_two=checkGame.hint_two,
                                    hint_three=checkGame.hint_three)

        else:
            return newGameMSGout(msg='No Current Game.',
                                    uv='', game_id=0,
                                    hint_one='',hint_two='',hint_three='')


    # --- Delete Current Game
    @endpoints.method(message_types.VoidMessage, aMessage,
                        path='deletecurrentgame', http_method='POST',
                        name='deletecurrentgame')
    def deleteCurrentGame(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
            return aMessage(msg='Not Logged In!')

        email = user.email()
        user2 = Users.query(Users.email == email).get()
        user_id = user2.key.id()
        if not user2:
            return aMessage(msg='Account Does Not Exist!')

        checkGame = Games \
        .query(ndb.AND(Games.user_id == user_id, Games.active == True)).get()
        if not checkGame:
            return aMessage(msg='You Are Not Currently Playing A Game.')

        else:
            checkGame.active = False
            checkGame.status = 'lost'
            user2.games_played = user2.games_played + 1
            user2.games_lost = user2.games_lost + 1

            gk = checkGame.put()
            uk = user2.put()
            return aMessage(msg='Current Game Deleted. Lost Score Increased.')


    # --- Guess Answer
    @endpoints.method(guessMessageCont, guessMessage,
                        path='guessanswer', http_method='POST',
                        name='guessanswer')
    def guessAnswer(self, request):
        if request.msg == '':
            return guessMessage(msg='msg Field Was Black.')

        user = endpoints.get_current_user()
        email = user.email()
        user2 = Users.query(Users.email == email).get()

        if not user2:
            msg = 'Email Does Not Exist In App. Please Create Account.'
            return guessMessage(msg=msg)

        user_id = user2.key.id()

        # print '--- request msg = ' + request.msg

        checkGame = Games \
        .query(ndb.AND(Games.user_id == user_id, Games.active == True)).get()
        if not checkGame:
            msg = 'You do not have an active game. Start a new game.'
            return guessMessage(msg=msg)

        guess = request.msg.lower()
        answer = checkGame.answer.lower()
        checkGame.tries = checkGame.tries + 1

        if guess == answer:
            checkGame.active = False
            checkGame.status = 'won'
            user2.games_played = user2.games_played + 1
            user2.games_won = user2.games_won + 1

            gk = checkGame.put()
            uk = user2.put()
            msg = 'Right! You Win! Your Score Went Up! You Can Start A New Game!'

            return guessMessage(msg=msg)

        else:
            if checkGame.tries == 3:
                checkGame.active = False
                checkGame.status = 'lost'
                user2.games_played = user2.games_played + 1
                user2.games_lost = user2.games_lost + 1

                gk = checkGame.put()
                uk = user2.put()
                msg = 'Wrong, Game Over! Answer = %s' % checkGame.answer
                return guessMessage(msg=msg)

            else:
                gk = checkGame.put()
                msg = 'Wrong! You Guessed ' + str(checkGame.tries) + ' Times.'

                return guessMessage(msg=msg)


    # --- Get User Rankings
    @endpoints.method(message_types.VoidMessage, topScoresMSG,
                        path='getuserrankings',
                        http_method='POST', name='getuserrankings')
    def getUserRankings(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
            return topScoresMSG(msg='Not Logged In!', users=[])

        topScores = Users.query().order(-Users.games_won).fetch(5)
        # print topScores

        if len(topScores) == 0:
            return topScoresMSG(msg='No Top Scores...', users=[])

        else:
            users = []
            for u in topScores:
                created = str(u.created)
                modified = str(u.modified)
                userMSG = getUserMSGout(msg='User.',
                                        displayname=u.displayname,
                                        email=u.email,
                                        uv=u.uv,
                                        current_game_id=u.current_game_id,
                                        games_played=u.games_played,
                                        games_won=u.games_won,
                                        games_lost=u.games_lost,
                                        created=created,
                                        modified=modified)
                users.append(userMSG)

            return topScoresMSG(msg='Top Scores.', users=users)

    # --- Get Recent Games
    @endpoints.method(message_types.VoidMessage, recentGamesMSG,
                        path='getrecentgames',
                        http_method='POST', name='getrecentgames')
    def getRecentGames(self, request):
        user = endpoints.get_current_user()
        if not user:
            raise endpoints.UnauthorizedException('Authorization required')
            return recentGamesMSG(msg='Not Logged In!', games=[])

        recentGames = Games \
        .query(Games.active == False).order(-Games.modified).fetch(5)
        # print recentGames

        if len(recentGames) == 0:
            return recentGamesMSG(msg='No Recent Games...', games=[])

        else:
            games = []
            for rg in recentGames:
                user = Users.get_by_id(rg.user_id)
                date = str(rg.modified)

                gameMSG = aGameMSGout(user=user.displayname,
                                        tries=rg.tries,
                                        msg=rg.status,
                                        date=date)
                games.append(gameMSG)

            return recentGamesMSG(msg='Recent Games', games=games)

    @staticmethod
    def notifyUsersActiveGames():
        activeGames = Games.query(Games.active == True).fetch()
        # print activeGames

        for ag in activeGames:
            user = Users.get_by_id(ag.user_id)
            mail.send_mail(
                'noreply@%s.appspotmail.com' % (
                    app_identity.get_application_id()),     # from
                user.email,                                 # to
                'Reminder',                                 # subj
                'Reminder: You have an active game! '       # body
                # 'gameInfo:\r\n\r\n%s' % ag.
            )

        # print 'done!'





# --- API Server --- #

api = endpoints.api_server([WhoAmIGameApi])
