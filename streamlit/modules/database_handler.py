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

# Function to get a game using the game_id
def get_game_by_id(game_id):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    SELECT created_by, game_name, number_of_rounds, 
                           num_inputs, password, timestamp_game_creation, 
                           timestamp_submission_deadline 
                    FROM game
                    WHERE game_id = %s;
                """

                cur.execute(query, (game_id,))

                result = cur.fetchone()
                
                if result:
                    return {
                        "created_by": result[0],
                        "game_name": result[1],
                        "number_of_rounds": result[2],
                        "num_inputs": result[3],
                        "password": result[4],
                        "timestamp_game_creation": result[5],
                        "timestamp_submission_deadline": result[6],
                    }
                return False
            
    except Exception:
        return False

# Function to fetch game data
def fetch_games_data():
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    SELECT game_id, created_by, game_name, number_of_rounds, \
                            num_inputs, password, timestamp_game_creation, timestamp_submission_deadline 
                    FROM game;
                """
        
                cur.execute(query)

                games_data = cur.fetchall()
                if games_data:
                    games = []
                    for row in games_data:
                        game = {
                            "game_id": row[0],
                            "created_by": row[1],
                            "game_name": row[2],
                            "number_of_rounds": row[3],
                            "num_inputs": row[4],
                            "password": row[5],
                            "timestamp_game_creation": row[6],
                            "timestamp_submission_deadline": row[7]
                        }
                        games.append(game)
            
                    return games
                return []
    
    except Exception:
        return []
    
# Function to fetch current (or past) games data by userID
def fetch_current_games_data_by_userID(sign, user_id):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = f"""
                        SELECT * FROM game g
                        JOIN plays p ON g.game_id = p.game_id
                        WHERE (p.userID = '{user_id}'
                        AND CURRENT_TIMESTAMP {sign} g.timestamp_submission_deadline);"""
        
                cur.execute(query)

                games_data = cur.fetchall()
                if games_data:
                    games = []
                    for row in games_data:
                        game = {
                            "game_id": row[0],
                            "created_by": row[1],
                            "game_name": row[2],
                            "number_of_rounds": row[3],
                            "num_inputs": row[4],
                            "password": row[5],
                            "timestamp_game_creation": row[6],
                            "timestamp_submission_deadline": row[7]
                        }
                        games.append(game)
            
                    return games
                return []
    
    except Exception:
        return []

# Function to retrieve the last gameID from the database and increment it
def get_next_game_id():
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                cur.execute("SELECT MAX(game_id) FROM game;")
         
                # Fetch the result
                last_game_id = cur.fetchone()[0]
                print(f"last_game_id: {last_game_id}")

                # Increment the last game ID or start at 1 if none exists
                return (last_game_id + 1) if last_game_id is not None else 1
            
    except Exception:
        return False
    
# Function to update game details in the database
def update_game_in_db(game_id, created_by, game_name, number_of_rounds, num_inputs, password, timestamp_game_creation, submission_deadline):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    UPDATE game
                    SET created_by = %(param1)s, game_name = %(param2)s, number_of_rounds = %(param3)s, num_inputs = %(param4)s,
                        password = %(param5)s, timestamp_game_creation = %(param6)s, timestamp_submission_deadline = %(param7)s
                    WHERE game_id = %(param8)s;
                """

                cur.execute(query, {
                    'param1': created_by, 
                    'param2': game_name, 
                    'param3': number_of_rounds, 
                    'param4': num_inputs, 
                    'param5': password, 
                    'param6': timestamp_game_creation,
                    'param7': submission_deadline,
                    'param8': game_id
                })

                return True
            
    except Exception:
        return False

# Function to store game details in the database
def store_game_in_db(created_by, game_name, number_of_rounds, num_inputs, password, timestamp_game_creation, submission_deadline):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    INSERT INTO game (created_by, game_name, number_of_rounds, num_inputs, password, timestamp_game_creation, timestamp_submission_deadline)
                    VALUES (%(param1)s, %(param2)s, %(param3)s, %(param4)s, %(param5)s, %(param6)s, %(param7)s);
                """

                cur.execute(query, {
                    'param1': created_by, 
                    'param2': game_name, 
                    'param3': number_of_rounds, 
                    'param4': num_inputs, 
                    'param5': password, 
                    'param6': timestamp_game_creation,
                    'param7': submission_deadline
                })

                return True
            
    except Exception:
        return False
    
# Function to get the id of the group from game_id and user_id
def get_group_id_from_game_id_and_user_id(game_id, user_id):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = f"SELECT group_id FROM plays WHERE (game_id = {game_id} AND userID = '{user_id}');"
                cur.execute(query)
                group_id = cur.fetchone()[0]

                return group_id

    except Exception:
        return False

# Function to get the id of the professor that created the game
def get_professor_id_from_game_id(game_id):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = f"SELECT created_by FROM game WHERE game_id = {game_id};"

                cur.execute(query)
                professor_id = cur.fetchone()[0]

                return professor_id

    except Exception:
        return False

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

                cur.execute(query, {
                    'param1': userID, 
                    'param2': email, 
                    'param3': otp, 
                    'param4': academic_year, 
                    'param5': class_
                })
         
                return True
            
    except Exception:
        return False

# Function to check user credentials
def authenticate_user(email, password_hash):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = "SELECT 1 FROM user_ WHERE email = %(param1)s AND password = %(param2)s;"

                cur.execute(query, {'param1': email, 'param2':password_hash})

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
                cur.execute(query, {'param1': new_password, 'param2': email})
                
                return True
            
    except Exception:
        return False
    
# Function to get userID by email
def get_userID_by_email(email):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                
                query = "SELECT userID FROM user_ WHERE email = %s;"

                cur.execute(query, (email,))
                
                # Fetch the result
                userID = cur.fetchone()[0]
                
                return userID
            
    except Exception:
        return False
