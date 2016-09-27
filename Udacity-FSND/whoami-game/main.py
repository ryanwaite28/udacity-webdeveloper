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

# --- Imports --- #

import os, cgi, hashlib, hmac, random, string, re, urllib
import jinja2
from jinja2 import Template as renderTemplate

import webapp2, endpoints
from google.appengine.api import app_identity
from google.appengine.api import mail
from game import WhoAmIGameApi

# --- Setup Code --- #

gameAPI = WhoAmIGameApi()

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

# --- Classes --- #

class MainHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class WelcomeHandler(MainHandler):
    def get(self):
        # WhoAmIGameApi.notifyUsersActiveGames()
        return self.render('index.html')



class NewUserConfirmHandler(MainHandler):
    def post(self):
        """Send email confirming user creation."""
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You created a new Account!',            # subj
            'Hi, you have created a following '         # body
            'userInfo:\r\n\r\n%s' % self.request.get(
                'userInfo')
        )

class NewGameConfirmHandler(MainHandler):
    def post(self):
        """Send email confirming game creation."""
        mail.send_mail(
            'noreply@%s.appspotmail.com' % (
                app_identity.get_application_id()),     # from
            self.request.get('email'),                  # to
            'You created a new Game!',            # subj
            'Hi, you have created a following '         # body
            'gameInfo:\r\n\r\n%s' % self.request.get(
                'gameInfo')
        )


class NotifyUsersActiveGames(MainHandler):
    def get(self):
        """Notify Users Of Their Active Games"""
        WhoAmIGameApi.notifyUsersActiveGames()
        self.response.set_status(204)


# --- App Settings --- #

api = endpoints.api_server([WhoAmIGameApi])

app = webapp2.WSGIApplication([
    ('/', WelcomeHandler),
    ('/tasks/send_newuser_email', NewUserConfirmHandler),
    ('/tasks/send_newgame_email', NewGameConfirmHandler),
    ('/crons/notify_users_active_games', NotifyUsersActiveGames),
], debug=True)
