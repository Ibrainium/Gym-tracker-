# Gym Tracker

A Flask and PostgreSQL web application based on the workout-tracker E/R model:

**Workout Plans → Workout Sessions → Performed Exercises → Exercise Sets**

The application allows users to create, view, update, and delete workout data.
Each user can only access their own workout plans, sessions, exercises, and
sets. The exercise catalogue is shared between all users.

The project uses Flask, SQLAlchemy, PostgreSQL, Bootstrap, HTML, CSS, and
JavaScript.

## Authentication

* Users can log in with either username or email and password.
* Passwords are stored as hashed values and are never saved in plain text.
* Sessions expire after 30 minutes of inactivity.
* CSRF protection is enabled for forms and API requests.
* Unauthenticated users are redirected to the login page.
* User accounts are managed through CLI commands.



### Application Structure

* The database schema is defined in `schema.sql`.
* The SQLAlchemy models correspond to the database tables.
* The API provides CRUD operations for all entities.
* The front end allows users to manage data through a web interface.

## 2. Prerequisites

* Python 3.12 (A MUST, otherwise some packages won't run)
* PostgreSQL 13+

## 3. Setup: 
This is setup uses Bash commands, which we know works for Linux systems, and should work for macbook users, if you are on windows, well, you might have to user some different commands. 

### Step 1: Create a virtual environment

```bash
conda create -n dbs_env python=3.12
conda activate dbs_env
```
Head to the app directory then run 
```bash
pip install -r requirements.txt
```

### Step 2: Create the database

```bash
sudo -u postgres createdb workout_tracker
sudo -u postgres psql -d workout_tracker -f schema.sql
```


### Step 3: Run the application

```bash
python app.py
```

## 5. Regular Expression Search

The application includes regular expression matching in the search fields.
Also when creating an account, matching is used for the length of passwords and and correctness of emails. 

## 6. API

The application provides CRUD (CREATE; READ; UPDATE; DELETE) functionality for:

* Exercises
* Workout Plans
* Workout Sessions
* Performed Exercises
* Exercise Sets

Supported operations:

* GET
* POST
* PUT
* DELETE

All API endpoints require authentication.

## 7. Database Design

The database contains the following entities:

* Users
* Exercises
* Workout Plans
* Workout Sessions
* Performed Exercises
* Exercise Sets

See the attached E/R diagram for the complete database design.

