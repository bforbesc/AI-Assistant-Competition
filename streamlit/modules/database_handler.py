import psycopg2
import pandas as pd
from flask import Flask

app = Flask(__name__)
app.secret_key = 'key' 

DB_HOST="db.tecnico.ulisboa.pt"
DB_USER="ist199317" 
DB_DATABASE=DB_USER
DB_PASSWORD="yjxp3222"
DB_CONNECTION_STRING = "host=%s dbname=%s user=%s password=%s" % (DB_HOST, DB_DATABASE, DB_USER, DB_PASSWORD)

# Function to remove a student from the database
def remove_student(userID):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = "DELETE FROM user_ WHERE userID = %s;"

                cur.execute(query, (userID,))
         
                return True
            
    except Exception:
        return False

# Function to fetch student data from the database
def get_students_from_db():
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                
                query = """
                    SELECT u.userID, u.email, u.academic_year, u.class, u.timestamp_user
                    FROM user_ AS u LEFT JOIN professor AS p 
                        ON u.userID = p.userID
                    WHERE p.userID IS NULL;
                """
                cur.execute(query)
                
                # Fetch all results from the query
                rows = cur.fetchall()
                
                # If data exists, create a DataFrame
                if rows:
                    # Convert the result set into a pandas DataFrame
                    df = pd.DataFrame(rows, columns=["userID", "email", "academic_year", "class", "timestamp_user"])
                    return df
                else:
                    return pd.DataFrame(columns=["userID", "email", "academic_year", "class", "timestamp_user"])
    
    except Exception:
        return False

# Function to insert email and OTP into the user table
def insert_student_data(userID, email, otp, academic_year, class_):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    INSERT INTO user_ (userID, email, password, academic_year, class)
                    VALUES (%(param1)s, %(param2)s, %(param3)s, %(param4)s, %(param5)s);
                """

                cur.execute(query, ({'param1': userID, 'param2': email, 'param3': otp, 'param4': academic_year, 'param5': class_}))
         
                return True
            
    except Exception:
        return False

# Function to check user credentials
def authenticate_user(email, password_hash):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = "SELECT 1 FROM user_ WHERE email = %(param1)s AND password = %(param2)s;"

                cur.execute(query, ({'param1': email, 'param2':password_hash}))

                # Fetch the result
                exists = cur.fetchone()[0]
                
                return exists

    except Exception:
        return False

# Function to validate if an email belongs to a professor
def is_valid_professor_email(email):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                
                query = "SELECT EXISTS(SELECT 1 FROM user_ WHERE email = %s);"

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
                                  FROM professor AS p JOIN user_ AS u
                                    ON p.userID = u.userID
                                  WHERE email = %s);
                """

                cur.execute(query, (email,))
                
                # Fetch the result
                is_prof = cur.fetchone()[0]
                
                return is_prof
            
    except Exception:
        return False


# Function to see if exists the user
def exists_user(email):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                
                query = """
                    SELECT EXISTS(
                                  SELECT 1 
                                  FROM user_ 
                                  WHERE email = %s);
                """

                cur.execute(query, (email,))
                
                # Fetch the result
                exists = cur.fetchone()[0]
                
                return exists
            
    except Exception:
        return False
    

# Function to update the user's password
def update_password(email, new_password):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                
                query = """
                    UPDATE user_
                    SET password = %(param1)s
                    WHERE email = %(param2)s;
                """
                cur.execute(query, ({'param1': new_password, 'param2': email}))
                
                return True
            
    except Exception:
        return False
    
# Function to get userID by email
def get_userID_by_email(email):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                
                query_to_get_userID = "SELECT userID FROM user_ WHERE email = %s;"

                cur.execute(query_to_get_userID, (email,))
                
                return query_to_get_userID
            
    except Exception:
        return False