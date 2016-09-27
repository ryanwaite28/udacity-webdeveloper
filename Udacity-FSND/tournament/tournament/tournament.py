#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import sys
# import tournament


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""

    #print ('--- connect function called.')
    return psycopg2.connect("dbname=tournament")



def deleteMatches():
    """Remove all the match records from the database."""

    #print ('--- Delete Matches function called.')
    DB = connect()
    cursor = DB.cursor()
    cursor.execute('delete from games')
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""

    #print ('--- Delete Players function called.')
    DB = connect()
    cursor = DB.cursor()
    cursor.execute('delete from players')
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""

    #print ('--- Count Players function called.')
    DB = connect()
    cursor = DB.cursor()
    cursor.execute('select count(*) from players')
    data = cursor.fetchone()[0]
    print (data)
    DB.close()

    return data


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """

    #print ('--- Register Player function called.')

    DB = connect()
    cursor = DB.cursor()
    cursor.execute('insert into players (name) values (%s)', (name , ) )
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    #print ('--- Player Standings function called.')

    DB = connect()
    cursor = DB.cursor()
    cursor.execute('select * from standings')
    data = cursor.fetchall()
    print (data)
    DB.close()

    return data



def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    #print ('--- Report Match function called.')

    DB = connect()
    cursor = DB.cursor()
    cursor.execute(
        '''insert into games (winner , loser)
        values (%s , %s)''',
        (winner , loser , )
    )
    DB.commit()
    DB.close()


# /// --- /// #

def played_before(p1 , p2):
    # if the two arguments are the same, return
    if p1 == p2:
        return 1

    DB = connect()
    cursor = DB.cursor()
    # Selecting those who won matches
    cursor.execute(""" select count(winner) as CountId from games
        where winner = %s and loser = %s """, (p1 , p2))
    # collects data
    number = cursor.fetchone()[0]
    DB.close()

    return number


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    #print ('--- Swiss Pairings function called.')

    DB = connect()
    cursor = DB.cursor()
    cursor.execute('select id,name from standings')
    info = cursor.fetchall()
    DB.close()

    print (info)

    match_list = []
    has_opponent = []

    length = len(info)
    print (length)

    # Starts The Pairing
    for index, player1 in enumerate(info):
        if not index in has_opponent:
            for index2 in range(index , length):
                # if the players played before
                if played_before(player1[0] , info[index2][0]) == 0:
                    has_opponent.extend([index,index2])
                    # append tuples (pairs) to match_list
                    match_list.append(
                        (player1[0],player1[1],info[index2][0],info[index2][1])
                    )
                    break

    print (match_list)
    return match_list


# """
# /// --- /// #
# /// --- /// #
# /// --- /// #
# """


def testing():
    """
        This Is Just a Function I Created to Tests The connect Function And
        That The DataBase Is Working And Returns a DataBase Connection/Object!
        If It Returns An Error, I Know Something's Wrong.
    """
    tst = connect()
    print (tst)
    #print ('L-20: DataBase Connection Successful')
