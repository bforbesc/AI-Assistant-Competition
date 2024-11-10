import psycopg2

from flask import flash
from flask import Flask
from flask import render_template
from flask import request
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'key' 

DB_HOST="db.tecnico.ulisboa.pt"
DB_USER="ist199317" 
DB_DATABASE=DB_USER
DB_PASSWORD="fpwf5329"
DB_CONNECTION_STRING = "host=%s dbname=%s user=%s password=%s" % (DB_HOST, DB_DATABASE, DB_USER, DB_PASSWORD)

# Function to check user credentials
def authenticate_user(email, password_hash):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = "SELECT 1 FROM Users WHERE email = %(param1)s AND password = %(param2)s;"

                cur.execute(query, ({'param1': email, 'param2':password_hash}))

                # Fetch the result
                exists = cur.fetchone()[0]
                
                return exists

    except Exception:
        return False


# Function to register a new user
def update_professor(username, email, password_hash):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    UPDATE Users
                    SET username = %(param1)s, password = %(param3)s
                    WHERE email = %(param2)s;
                """
                cur.execute(query, ({'param1':username, 'param2': email, 'param3':password_hash}))

                return True

    except Exception:
        return False

# Function to validate if an email belongs to a professor
def is_valid_professor_email(email):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                
                query = "SELECT EXISTS(SELECT 1 FROM Users WHERE email = %s);"

                cur.execute(query, (email,))
                
                # Fetch the result
                exists = cur.fetchone()[0]
                
                return exists
            
    except Exception:
        return False

# Function to validate if the user that logged in is a Professor
def is_professor(email):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                
                query = """
                    SELECT EXISTS(
                                  SELECT 1 
                                  FROM Professors AS p JOIN Users AS u
                                    ON p.user_id = u.user_id
                                  WHERE email = %s);
                """

                cur.execute(query, (email,))
                
                # Fetch the result
                is_prof = cur.fetchone()[0]
                
                return is_prof
            
    except Exception:
        return False
