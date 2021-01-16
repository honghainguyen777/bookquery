# BookQuery

## Visit and try this app on Heroku

### http://bookquery.herokuapp.com/

## Features of the app

### Login page
![](https://i.imgur.com/XbAHZY1.jpg)

### Register page
![](https://i.imgur.com/f56rn3X.jpg)

### Search result page
![](https://i.imgur.com/8fdo2nl.jpg)

### Book page
![](https://i.imgur.com/HTTXT7s.jpg)

### Review features
![](https://i.imgur.com/Jpkl8X7.jpg)

### Question and answer features
![](https://i.imgur.com/jlOXMm3.jpg)

### Changing password page
![](https://i.imgur.com/jjs9K9i.jpg)

### Request for book API
https://bookquery.herokuaapp.com/api/ + book-ISBN

## :gear: Setup local environment and run the flask application

### Install Python and flask

#### Download and install Python:

- [Link here](https://www.python.org/downloads/)
- Remember to check the pip installation box or [install it](https://pip.pypa.io/en/stable/installing/) separately

#### Install Flask through terminal (first time only):
```bash
$ pip install Flask
$ pip install SQLAlchemy
$ pip install Flask-Session
$ pip install Werkzeug
$ pip install requests
```

#### Download the BookQuery
```bash
$ git clone https://github.com/honghainguyen777/bookquery.git
$ cd bookquery
```

#### Start the BookQuery application
```bash
# Install requrements for the application (pip or pip3)
$ pip3 install -r requirements.txt

# set environment variable (Windows)
$ set FLASK_APP=application.py
$ set FLASK_DEBUG=1
$ set DATABASE_URL= (paste Postgres database URI here, register see below)

# set environment variable (for Mac or Linux)
$ export FLASK_APP=application.py
$ export FLASK_DEBUG=1
$ export DATABASE_URL= (paste Postgres database URI here, register see below)
```

##### Update all tables and data into the Heroku database server
```bash
$ python import.py
```

## Run the program and enjoy developing
```bash
$ flask run
```

#### Register and get a free database (10000 rows)
1. Register for a free account [https://www.heroku.com/](https://www.heroku.com/)
2. On Heroku's Dashboard click "New" and choose "Create new app."
3. Name your app and "Create app"
4. On your "Overview" page, click "Configure Add-ons"
5. In the "Add-ons", and select a free "Heroku Postgres"
6. Choose the "Hobby Dev - Free" plan
7. Click "Heroku Postgress:: Database"
8. Click "Setings" and the "View Credentials" you can find all needed information

Alternative: Download your own through this [link](https://www.postgresql.org/download/)
