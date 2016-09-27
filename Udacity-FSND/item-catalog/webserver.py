import os
import sys
import cgi
from BaseHTTPServer import BaseHTTPRequestHandler , HTTPServer

from database_setup import Base , Restaurant , MenuItem

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

#

class webserverHandler(BaseHTTPRequestHandler):

    restaurants = session.query(Restaurant).all()

    def do_GET(self):
        try:
            if self.path.endswith('/hello'):
                self.send_response(200)
                self.send_header('Content-type' , 'text/html')
                self.end_headers()

                output = '<html><body>'
                output += '''<form method="POST" enctype="multipart/form-data" action="/hello">
                <p>What To Say?</p>
                <input name="message" type="text">
                <input type="submit" value="submit"></form>'''
                output += '</body></html>'
                self.wfile.write(output)
                print ('GET Request')
                return

            if self.path.endswith('/restaurant'):
                self.send_response(200)
                self.send_header('Content-type' , 'text/html')
                self.end_headers()

                restaurants = session.query(Restaurant).all()

                output = '<html><body>'
                output += ''' <center>
                    <a href="/restaurant/new">Create Restaurant</a><hr>
                    </center> '''
                for restaurant in restaurants:
                    output += ''' <div>
                        <span> %s </span><br>
                        <a href="/restaurant/%s/edit">Edit</a>
                        <a href="/restaurant/%s/delete">Delete</a><br>
                        </div><br>''' % (restaurant.name , restaurant.id , restaurant.id)
                output += '</body></html>'
                self.wfile.write(output)
                print ('GET Request')
                return

            if self.path.endswith('/restaurant/new'):
                self.send_response(200)
                self.send_header('Content-type' , 'text/html')
                self.end_headers()

                output = '<html><body>'
                output += '''<form method="POST" enctype="multipart/form-data" action="/restaurant/new">
                <h1>Create A Restaurant</h1>
                <input name="restaurant" type="text" placeholder="Type Restaurant Name">
                <input type="submit" value="submit"></form><br>
                <center>
                <a href="/restaurant">Back To Restaurants</a><br>
                </center>'''
                output += '</body></html>'
                self.wfile.write(output)
                print ('GET Request')
                return

            if self.path.endswith('/edit'):
                IDpath = self.path.split('/')[2]
                query = session.query(Restaurant).filter_by(id = IDpath).one()

                if query != []:
                    output = '<html><body>'
                    output += '''<form method="POST" enctype="multipart/form-data" action="/restaurant/%s/edit">
                    <h1>Edit A Restaurant</h1>
                    <h3>%s</h3>
                    <input name="restaurant" type="text" placeholder="Type New Name">
                    <input type="submit" value="submit"></form><br>
                    <center>
                    <a href="/restaurant">Back To Restaurants</a><br>
                    </center>''' % (query.id , query.name)
                    output += '</body></html>'
                    self.wfile.write(output)

            if self.path.endswith('/delete'):
                IDpath = self.path.split('/')[2]
                query = session.query(Restaurant).filter_by(id = IDpath).one()

                if query != []:
                    output = '<html><body>'
                    output += '''<form method="POST" enctype="multipart/form-data" action="/restaurant/%s/delete">
                    <h1>Delete This Restaurant?</h1>
                    <h3>%s</h3>

                    <a href="/restaurant"><input type="button" value="No"></a>
                    <input type="submit" value="Yes">
                    </form><br>
                    <center>
                    <a href="/restaurant">Back To Restaurants</a><br>
                    </center>''' % (query.id , query.name)
                    output += '</body></html>'
                    self.wfile.write(output)


                print ('GET Request')


        except IOError:
            self.send_error(404 , 'File Not Found %s' % self.path)


# -------


    def do_POST(self):
        try:
            if self.path.endswith('/restaurant/new'):

                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    print fields
                    print fields.get('restaurant')[0]

                    new_restaurant = Restaurant(name = fields.get('restaurant')[0])
                    session.add(new_restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type' , 'text/html')
                    self.send_header('Location' , '/restaurant')
                    self.end_headers()

            if self.path.endswith('/edit'):

                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                content = fields.get('restaurant')[0]
                IDpath = self.path.split('/')[2]

                query = session.query(Restaurant).filter_by(id = IDpath).one()

                if query != []:
                    query.name = content
                    session.add(query)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type' , 'text/html')
                    self.send_header('Location' , '/restaurant')
                    self.end_headers()

            if self.path.endswith('/delete'):

                ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
                IDpath = self.path.split('/')[2]

                query = session.query(Restaurant).filter_by(id = IDpath).one()

                if query != []:
                    session.delete(query)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type' , 'text/html')
                    self.send_header('Location' , '/restaurant')
                    self.end_headers()

            print ('POST Request')



        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port) , webserverHandler)
        print 'Web Server running on port %s ...' % port
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C Entered. Stopping Web Server.'
        server.socket_close()


if __name__ == '__main__':
        main()
