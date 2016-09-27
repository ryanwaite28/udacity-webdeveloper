#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# --- Imports

import os, cgi, hashlib, hmac, random, string, re
import webapp2
import jinja2
from jinja2 import Template as renderTemplate
import cgi
import urllib
from google.appengine.ext import db
from google.appengine.ext.db import GqlQuery
from google.appengine.api import app_identity


# --- Setup Code

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)
user = {}

secret = 'hvo7eirudfsiv69u9eids'
salt = 'rsbi78h45t3rs89h4ijakw9'
GAE_APP_ID = app_identity.get_application_id()



USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

def makeSalt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def makePwsrdHash(name, pswrd, salt=None):
    if not salt:
        salt = makeSalt()
    h = hashlib.sha256(name + pswrd + salt).hexdigest()
    return '%s,%s' % (salt, h)

def validPswrd(name, pswrd, h):
    salt = h.split(',')[0]
    return h == makePwsrdHash(name, pswrd, salt)

def hashStr(k):
    return hmac.new(secret , k).hexdigest()

def makeSecureValue(k):
    return '%s|%s' % (k , hashStr(k))

def checkSecureValue(k):
    value = k.split('|')[0]
    if k == makeSecureValue(value):
        return value
    else:
        return None

# --- Entities (Tables)

class Users(db.Model):

    username = db.StringProperty(required = True)
    pswrdhash = db.StringProperty(required = True)
    icon = db.StringProperty(default = 'null')

    @classmethod
    def byID(cls, uid):
        return Users.get_by_id(uid)

    @classmethod
    def byUsername(cls, username):
        return Users.all().filter('username =' , username).get()

    @classmethod
    def signUp(cls, username, pswrd):
        pswrdhash = makePwsrdHash(username, pswrd)
        return Users(username=username, pswrdhash=pswrdhash)

    @classmethod
    def logIn(cls, username, pswrd):
        user = cls.byUsername(username)

        if user and validPswrd(username, pswrd, user.pswrdhash):
            return user

# ---


class Posts(db.Model):

    owner = db.IntegerProperty(required = True)

    title = db.StringProperty(required = True)
    contents = db.TextProperty(required = True)

    ownerName = db.TextProperty(required = True, default = '')
    ownerIcon = db.TextProperty(required = True, default = '')

    dateCreated = db.DateTimeProperty(auto_now_add = True)
    lastModified = db.DateTimeProperty(auto_now = True)



class PostLikes(db.Model):

    owner = db.IntegerProperty(required = True)

    post_id = db.IntegerProperty(required = True)

    ownerName = db.TextProperty(required = True, default = 'null')
    ownerIcon = db.TextProperty(required = True, default = 'null')

    dateCreated = db.DateTimeProperty(auto_now_add = True, default = 'null')

# ---

class Comments(db.Model):

    owner = db.IntegerProperty(required = True)
    post_id = db.IntegerProperty(required = True)

    contents = db.TextProperty(required = True)

    ownerName = db.TextProperty(required = True, default = '')
    ownerIcon = db.TextProperty(required = True, default = '')

    dateCreated = db.DateTimeProperty(auto_now_add = True)
    lastModified = db.DateTimeProperty(auto_now = True)



class CommentLikes(db.Model):

    owner = db.IntegerProperty(required = True)
    comment_id = db.IntegerProperty(required = True)

    ownerName = db.TextProperty(required = True)
    ownerIcon = db.TextProperty(required = True)

    dateCreated = db.DateTimeProperty(auto_now_add = True)



# --- SuperClass Handlers

class MainHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    #
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


    #

    def set_secure_cookie(self, name, val):
        cookie_val = makeSecureValue(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and checkSecureValue(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))


    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')


    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and Users.byID(int(uid))
        self.lg = 'null'


# --- HTTP Handlers

class WelcomeHandler(MainHandler):
    def get(self):
        posts = Posts.all().order('-dateCreated')

        return self.render('welcome.html', posts=posts, user=self.user)

#

class LogInHandler(MainHandler):
    def get(self):
        if self.user:
            return self.redirect('/profile')

        return self.render('login.html', user=self.user)

    def post(self):
        uname = self.request.get('uname')
        pswrd = self.request.get('pswrd')

        user = Users.logIn(uname, pswrd)

        if user:
            self.login(user)
            return self.redirect('/profile')

        else:
            msg = 'Invalid Credentials'
            return self.render('login.html', msg=msg)


class LogOutHandler(MainHandler):
    def get(self):
        if self.user:
            self.logout()
            return self.redirect('/')

        else:
            return self.redirect('/')


class SignUpHandler(MainHandler):
    def get(self):
        msg = ''
        if self.user:
            return self.redirect('/profile')

        return self.render('signup.html', msg=msg)

    def post(self):
        error = None

        self.uname = self.request.get('uname')
        self.pswrd = self.request.get('pswrd')
        self.verify = self.request.get('verify')

        params = { 'uname': self.uname }

        if not valid_username(self.uname):
            params['error'] = 'Username Does Not Exist.'
            error = True

        if not valid_password(self.pswrd):
            params['error'] = 'Password Is Not Valid.'
            error = True

        if  self.pswrd != self.verify:
            params['error'] = 'Passwords Did Not Match.'
            error = True

        if error == True:
            msg = params['error']
            return self.render('signup.html', msg=msg)

        else:
            user = Users.byUsername(self.uname)
            if user:
                msg = 'Username is already in use.'
                return self.render('signup.html', msg=msg)

            else:
                newUser = Users.signUp(username=self.uname,
                                        pswrd=self.pswrd)
                newUser.put()

                self.login(newUser)
                return self.redirect('/profile')

#

class PostPage(MainHandler):
    def get(self, post_id):

        key = db.Key.from_path('Posts', int(post_id))
        post = db.get(key)

        keyTwo = db.Key.from_path('Users', int(post.owner))
        owner = db.get(keyTwo)

        comments = GqlQuery('select * from Comments where post_id = ' + post_id)
        likes = GqlQuery('select * from PostLikes where post_id = ' + post_id)

        liked = 'no'

        for l in likes:
            if l.ownerName == self.user.username:
                liked = 'yes'

        if not post:
            self.error(404)
            return

        return self.render('blog-post.html',
                    post=post,
                    comments=comments,
                    likes=likes,
                    owner=owner,
                    liked=liked,
                    you=self.user)

#

class profileHandler(MainHandler):
    def get(self):
        if self.user:
            userID = str(self.user.key().id())
            posts = GqlQuery('select * from Posts where owner = ' + userID)
            return self.render('profile.html',
                        you = self.user,
                        posts = posts)
        else:
            return self.redirect('/login')

#

class userPageHandler(MainHandler):
    def get(self, username):
        if self.user:
            user = Users.byUsername(username)
            if not user:
                return self.render('error.html', msg='User Not Found...')

            userID = str(user.key().id())
            posts = GqlQuery('select * from Posts where owner = ' + userID)
            return self.render('user.html',
                                you = self.user,
                                user = user,
                                posts = posts)
        else:
            return self.redirect('/login')


#

class NewPost(MainHandler):
    def get(self):
        if self.user:
            return self.render("create-blogpost.html",
                            title='',
                            contents='',
                            msg='',
                            user=self.user)

        else:
            return self.redirect("/login")

    def post(self):
        if not self.user:
            return self.redirect("/login")

        owner = int(self.user.key().id())

        title = cgi.escape(self.request.get('title'))
        contents = cgi.escape(self.request.get('contents'))

        ownerName = str(self.user.username)
        ownerIcon = str(self.user.icon)
        if ownerIcon == '' or ownerIcon == None:
            ownerIcon = 'null'

        if title and contents \
        and title != '' and contents != '':
            newPost = Posts(title=title,
                            contents=contents,
                            owner=owner,
                            ownerName=ownerName,
                            ownerIcon=ownerIcon)
            newPost.put()

            return self.redirect('/blog/post/%s' % str(newPost.key().id()))

        else:
            msg = 'Title and Contents are Required.'
            return self.render("create-blogpost.html",
                        title=title,
                        contents=contents,
                        msg=msg,
                        user=self.user)

#

class EditPost(MainHandler):
    def get(self, post_id):
        if not self.user:
            return self.redirect("/login")

        key = db.Key.from_path('Posts', int(post_id))
        post = db.get(key)

        if post.ownerName != self.user.username:
            return self.render('error.html',
                                msg='You Are Not The Owner Of This Post...')

        return self.render("edit-blogpost.html",
                        post=post,
                        you=self.user)

    def post(self, post_id):
        if not self.user:
            return self.redirect("/login")

        key = db.Key.from_path('Posts', int(post_id))
        editPost = db.get(key)

        if editPost.ownerName != self.user.username:
            return self.render('error.html',
                                msg='You Are Not The Owner Of This Post...')

        owner = int(self.user.key().id())
        title = cgi.escape(self.request.get('title'))
        contents = cgi.escape(self.request.get('contents'))
        ownerName = str(self.user.username)
        ownerIcon = str(self.user.icon)

        if ownerIcon == '' or ownerIcon == None:
            ownerIcon = 'null'

        if title and contents \
        and title != '' and contents != '':
            editPost.title = title
            editPost.contents = contents

            editPost.put()

            return self.redirect('/blog/post/%s' % str(post_id))

        else:
            msg = 'Title and Contents are Required.'
            return self.render("create-blogpost.html",
                                title=title,
                                contents=contents,
                                msg=msg,
                                user=self.user)

#

class DeletePost(MainHandler):
    def get(self, post_id):
        if not self.user:
            return self.redirect("/login")

        key = db.Key.from_path('Posts', int(post_id))
        post = db.get(key)

        if post.ownerName != self.user.username:
            return self.render('error.html',
                                msg='You Are Not The Owner Of This Post...')

        return self.render("delete-blogpost.html",
                            post=post,
                            you=self.user)

    def post(self, post_id):
        if not self.user:
            return self.redirect("/login")

        key = db.Key.from_path('Posts', int(post_id))
        deletePost = db.get(key)

        if deletePost.ownerName != self.user.username:
            return self.render('error.html',
                                msg='You Are Not The Owner Of This Post...')

        deletePost.delete()

        return self.redirect('/')

#

class PostComment(MainHandler):
    def get(self, post_id):
        return self.redirect('/')

    def post(self, post_id):
        if not self.user:
            return

        owner = int(self.user.key().id())
        post_id = int(post_id)
        contents = cgi.escape(self.request.get('contents'))
        ownerName = str(self.user.username)
        ownerIcon = str(self.user.icon)
        if ownerIcon == '' or ownerIcon == None:
            ownerIcon = 'null'


        if contents and contents != '':
            newPostComment = Comments(owner=owner,
                                        post_id=post_id,
                                        contents=contents,
                                        ownerName=ownerName,
                                        ownerIcon=ownerIcon)
            newPostComment.put()

            return self.redirect('/blog/post/' + str(post_id))

        else:
            msg = 'Contents Is Required.'
            return self.render("blog-post.html",
                                post_id=post_id,
                                contents=contents,
                                msg=msg,
                                user=self.user)

#

class EditComment(MainHandler):
    def get(self, c_id):
        if not self.user:
            return self.redirect("/login")

        key = db.Key.from_path('Comments', int(c_id))
        comment = db.get(key)

        if comment.ownerName != self.user.username:
            return self.render('error.html',
                                msg='You Are Not The Owner Of This Comment...')

        return self.render("edit-comment.html",
                            comment=comment,
                            you=self.user)

    def post(self, c_id):
        if not self.user:
            return self.redirect("/login")

        key = db.Key.from_path('Comments', int(c_id))
        editComment = db.get(key)

        if editComment.ownerName != self.user.username:
            return self.render('error.html',
                                msg='You Are Not The Owner Of This Comment...')

        contents = cgi.escape(self.request.get('contents'))

        if contents and contents != '':
            editComment.contents = contents

            editComment.put()

            return self.redirect('/blog/post/%s' % str(editComment.post_id))

        else:
            msg = 'Contents is Required.'
            return self.render("edit-comment.html",
                                contents=contents,
                                msg=msg,
                                you=self.user)

#

class DeleteComment(MainHandler):
    def get(self, c_id):
        if not self.user:
            return self.redirect("/login")

        key = db.Key.from_path('Comments', int(c_id))
        comment = db.get(key)

        if comment.ownerName != self.user.username:
            return self.render('error.html',
                                msg='You Are Not The Owner Of This Comment...')

        return self.render("delete-comment.html",
                            comment=comment,
                            you=self.user)

    def post(self, c_id):
        if not self.user:
            return self.redirect("/login")

        key = db.Key.from_path('Comments', int(c_id))
        deleteComment = db.get(key)

        post_id = deleteComment.post_id

        if deleteComment.ownerName != self.user.username:
            return self.render('error.html',
                                msg='You Are Not The Owner Of This Comment...')

        deleteComment.delete()

        return self.redirect('/blog/post/' + str(post_id))


#

class LikePost(MainHandler):
    def get(self, post_id):
        return self.redirect('/')

    def post(self, post_id):
        if not self.user:
            return

        msg = ''

        action = str(self.request.get('action'))

        if action == None:
            msg = 'There Was An Error With Liking That Post...'
            return self.render('error.html', msg=msg)

        owner = int(self.user.key().id())
        post_id = int(post_id)
        ownerName = str(self.user.username)
        ownerIcon = str(self.user.icon)

        if ownerIcon == '' or ownerIcon == None:
            ownerIcon = 'null'

        if action == 'like':
            checkPostLike = PostLikes.all() \
                            .filter('post_id =', post_id) \
                            .filter('owner =', owner).get()

            if checkPostLike != None:
                return self.redirect('/blog/post/' + str(post_id))

            else:
                newPostLike = PostLikes(owner=owner,
                                    post_id=post_id,
                                    ownerName=ownerName,
                                    ownerIcon=ownerIcon)

                newPostLike.put()
                return self.redirect('/blog/post/' + str(post_id))

        if action == 'unlike':
            postLike = PostLikes.all() \
                            .filter('post_id =', post_id) \
                            .filter('owner =', owner).get()

            if postLike == None:
                return self.redirect('/blog/post/' + str(post_id))

            else:
                postLike.delete()
                return self.redirect('/blog/post/' + str(post_id))

# --- Routes Listeners

app = webapp2.WSGIApplication([
    ('/', WelcomeHandler),
    #
    ('/login', LogInHandler),
    ('/logout', LogOutHandler),
    ('/signup', SignUpHandler),
    #
    ('/profile', profileHandler),
    ('/profile/([a-zA-Z0-9]+)', userPageHandler),
    #
    ('/blog/post/([0-9]+)', PostPage),
    ('/post/([0-9]+)/leavecomment', PostComment),
    ('/comment/([0-9]+)/edit', EditComment),
    ('/comment/([0-9]+)/delete', DeleteComment),
    ('/post/([0-9]+)/likepost', LikePost),
    #
    ('/blog/post/new', NewPost),
    ('/post/([0-9]+)/edit', EditPost),
    ('/post/([0-9]+)/delete', DeletePost),
    ],
    debug=True)

# --- End Of File
