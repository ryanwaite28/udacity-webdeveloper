# Udacity Full Stack NanoDegree - Linux Server configuration

## Emerald Server
visit public website - http://54.71.49.86/

> This is a project from Udacity's Full Stack NanoDegree Program called Linux Server configuration.
This project demonstrates the understanding of linux servers,
command-line interface(s), terminal and shell, user management, file permissions and groups,
web security, software and packages, and databases, all from a basic installation.

# Installed Packages/Softwares

* ntp
* apache2
* postgresql
* libapache2-mod-wsgi
* flask
* sqlalchemy
* oauth2client
* python-pip
* psycopg2
* finger
* git

# Server Info

Application URL - http://54.71.49.86/ <br />
Public IP Address - 54.71.49.86 <br />
SSH Port - 2200 <br />
NTP Port - 123 <br />

# Overview

### user management
* A basic installation of Ubuntu Server is created
* The root user creates the 'grader' user with sudo access
* the grader has an ssh key-pair generated for ssh logging in
* the grader user hereby acts on behalf of root user; <br />
  root user is no longer used(security measure)

### web security

* remote login for root is disabled/prohibited
* all remote logins required key-based authentication only
* all users with sudo access will be asked for password to use sudo at least once
* all firewall settings start from default - deny all incoming and allow all outgoing
* http is configured to serve on port 80
* ssh is configured to serve on port 2200 (non-default)
* ntp is configured to serve on port 123
* all necessary packages are installed and updated
* ntp is configured to use UTC time zone

### app functionality

* postgresql database is installed and used to serve data-driven results
* the server (VM/AWS) can be accessed remotely
* the web server is configured to serve web app (Python scripts)

# How To Setup

1. download ssh private key from Udacity online development environment
   to your .ssh folder, which should be in your home directory
2. connect using: ssh -i ~/.ssh/udacity_key.rsa root@54.71.49.86
3. once logged in(as root), create user grader with command: adduser grader;
   fullname is grader; other fields are optional
4. open file: nano /etc/sudoers.d/grader <br />
   (The nano command allows one to edit text files.
    If directory does not exit, an error will be returned.
    If the file does not exist, then it will be created)
5. add line: grader ALL=(ALL) NOPASSWD:ALL (This will give grader sudo access)
6. hit "ctrl + x" to exit; press y to save; press enter key to finish
7. create a directory for grader's ssh-authorized keys: mkdir /home/grader/.ssh
8. create file: touch /home/grader/.ssh/authorized_keys
* change owner to grader: chmod 700 .ssh; then run: chmod 644 .ssh/authorized_keys
  (if denied, change owner and group to grader: chown grader .ssh; chgrp grader .ssh)
9. in another terminal, not logged into ubuntu, run: ssh-keygen
10. save the key-pair to local .ssh folder
11. copy public key from file(the file created that ends with .pub) to the authorized_keys
    file in previous terminal(ubuntu server) with: nano /home/grader/.ssh/authorized_keys
12. log out of root with: logout
13. log into user with: ssh -i ~/.ssh/(name of key file; not the one that ends with .pub) grader@54.71.49.86 -p 2200
14. install: sudo apt-get install apache2; sudo apt-get install libapache2-mod-wsgi
15. install: sudo apt-get install postgresql
16. install: sudo apt-get install ntp
17. install: sudo apt-get install python-pip; sudo apt-get install git
18. install: sudo apt-get install python-psycopg2
19. install: sudo pip install flask
20. install: sudo pip install sqlalchemy
21. install: sudo pip install oauth2client
22. switch to postgres db user: sudo -u postgres -i
23. use psql: psql
24. run the following:
* CREATE USER grader WITH PASSWORD 'grader';
* CREATE DATABASE catalog;
* GRANT ALL PRIVILEGES ON DATABASE "catalog" to grader;
* \q (to exit psql)
* logout of postgres user: logout
25. Configure SSH Port:
* edit line "Port 22" to be "Port 2200": sudo nano /etc/ssh/sshd_config <br />
  turn root ssh off: change "PermitRootLogin without-password" to "PermitRootLogin no" <br />
  force ssh key-pair authentication: change "PasswordAuthentication yes" to "PasswordAuthentication no"
* restart server with: sudo service ssh restart
26. Configure firewall:
* sudo ufw default deny incoming
* sudo ufw default allow outgoing
* sudo ufw default allow ssh
* sudo ufw default allow 2200/tcp
* sudo ufw default allow www
* sudo ufw default deny 22
* sudo ufw default allow 123/tcp
* sudo ufw enable (Enables firewall)
26. Configure Time Zone: sudo dpkg-reconfigure tzdata (Pick UTC)
27. Configure Apache:
* edit: sudo nano /etc/apache2/sites-enabled/000-default.conf
* add: WSGIScriptAlias / /var/www/html/myapp.wsgi inside VirtualHost 
* create file: sudo nano /var/www/html/myapp.wsgi
* write: <br />
   import sys<br />
   sys.path.insert(0, '/var/www/html/catalog-two/')<br />
   from project import app as application
   <br /><br />

   Then Save

* get project files: git clone https://github.com/ryanwaite28/catalog-two.git
  (make sure it is cloned to: /var/www/html/)
* setup database: python database_setup.py
  (file has been edited so sqlalchemy will use this postgresql database; project.py edited as well)

### open the app URL

# Enjoy!!! - PearadoX
