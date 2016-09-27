from flask import Flask, make_response, g
from flask import render_template, url_for, request, redirect, flash, jsonify
from flask import session as login_session
import random, string
from functools import wraps

app = Flask(__name__)

# -------------

from database_setup import Base , Restaurant , MenuItem
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu"

# --------------------

def login_required(f):
    ''' Checks If User Is Logged In '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            # flash('You are not allowed to access there')
            return redirect('/login')
    return decorated_function

# --------------

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    ''' Initiates 3rd Party Google Login Process
    Creates a State Key, saves It In Session and
    Sends It To Login Page. '''

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# --------------

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user Already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 300px; height: 300px;
                border-radius: 150px;-webkit-border-radius: 150px;
                -moz-border-radius: 150px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    ''' Checks If There Is a User Currently Logged In.
    If So, Request Google To Sign Out Then Delete Session Info '''

    if 'access_token' in login_session:
        access_token = login_session['access_token']
    else:
        access_token = None

    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	del login_session['access_token']
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']
    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:

    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response

# --------------------

@app.route('/')
def homePage():
	''' Loads Restaurants and MenuItems, Then Render Them
	To The Home Page '''
    restaurants = session.query(Restaurant).all()
    items = session.query(MenuItem).all()

    return render_template('main.html', restaurants=restaurants, items=items)

@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    ''' Loads The Selected Restaurant and Its MenuItems,
    Then Render The Page With The Info '''

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)

    return render_template('restaurant.html',
							restaurant=restaurant,
							items=items)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/')
def viewItem(restaurant_id, menu_id):
    ''' Loads The Selected MenuItem And Render The Page With The Info '''

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id = menu_id).one()

    return render_template('menuitem.html', restaurant=restaurant, item=item)


# ---------------


@app.route('/restaurants/new/', methods=['GET', 'POST'])
@login_required
def newRestaurant():
    ''' Renders a Form Page For Creating a Restaurant '''

    if request.method == 'POST':
        newItem = Restaurant( name=request.form['itemname'] )
        session.add( newItem )
        session.commit()

        return redirect('/')

    else:
        return render_template('new-restaurant.html')


@app.route('/restaurants/edit/<int:restaurant_id>/', methods=['GET', 'POST'])
@login_required
def editRestaurant(restaurant_id):
    ''' Renders a Form Page For Editing The Selected Restaurant '''

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        restaurant.name = request.form['itemname']
        session.add( restaurant )
        session.commit()

        return redirect(url_for('restaurantMenu', restaurant_id=restaurant.id))

    else:
        return render_template('edit-restaurant.html', restaurant=restaurant)


@app.route('/restaurants/delete/<int:restaurant_id>/', methods=['GET', 'POST'])
@login_required
def deleteRestaurant(restaurant_id):
    ''' Renders a Form Page For Deleting The Selected Restaurant '''

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    print items
    if request.method == 'POST':

        session.delete(restaurant)
        session.commit()

        return redirect('/')

    else:
        return render_template('delete-restaurant.html', restaurant=restaurant)

# ----------------

# Task 1: Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
@login_required
def newMenuItem(restaurant_id):
    ''' Renders a Form Page For Creating a MenuItem
    Under Selected Restaurant '''

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        newItem = MenuItem(
            name=request.form['itemname'],
            price=request.form['itemprice'],
            description=request.form['itemdesc'],
            restaurant_id=restaurant_id)
        session.add( newItem )
        session.commit()

        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    else:
        return render_template('new-menuitem.html',
                                restaurant_id=restaurant_id,
                                restaurant=restaurant)


# Task 2: Create route for editMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET','POST'])
@login_required
def editMenuItem(restaurant_id, menu_id):
    ''' Renders a Form Page For Editing The Selected MenuItem '''

    editItem = session.query(MenuItem).filter_by(id = menu_id).one()

    if request.method == 'POST':
        editItem.name = request.form['itemname']
        editItem.price = request.form['itemprice']
        editItem.description = request.form['itemdesc']
        session.add(editItem)
        session.commit()

        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    else:
        return render_template('edit-menuitem.html',
                                restaurant_id=restaurant_id,
                                menu_id=menu_id, item=editItem)


# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods=['GET','POST'])
@login_required
def deleteMenuItem(restaurant_id, menu_id):
    ''' Renders a Form Page For Deleting The Selected MenuItem '''

    deleteItem = session.query(MenuItem).filter_by(id = menu_id).one()

    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()

        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    else:
        return render_template('delete-menuitem.html',
                                restaurant_id=restaurant_id,
                                menu_id=menu_id, item=deleteItem)

# ------------- #

# Making API EndPoint (GET Request)
@app.route('/restaurants/JSON')
def restaurantsJSON():
    ''' Selects All Restaurants From Database And Returns
    Info In JSON '''

    restaurants = session.query(Restaurant).all()

    return jsonify(Restaurants = [i.serialize for i in restaurants])

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON')
def menuitemJSON(restaurant_id, menu_id):
    ''' Selects MenuItem From Database And Returns
    Info In JSON '''

    item = session.query(MenuItem).filter_by(id = menu_id).one()

    return jsonify(MenuItem = item.serialize)

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    ''' Selects All Restaurant's MenuItem From Database And Returns
    Info In JSON '''

    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

    return jsonify(MenuItems = [i.serialize for i in items])


# ------------- #

if __name__ == '__main__':
    app.secret_key = 'superkey'
    app.debug = True
    app.run( host = '0.0.0.0' , port = 5000 )
