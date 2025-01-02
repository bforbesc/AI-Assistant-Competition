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

# Function to populate the 'plays' table with students who match the academic year and class of the created game
def populate_plays_table(game_id, game_academic_year, game_class):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    SELECT u.user_id
                    FROM user_ AS u LEFT JOIN professor AS p 
                        ON u.user_id = p.user_id
                    WHERE p.user_id IS NULL AND u.academic_year = %(param1)s AND u.class = %(param2)s;
                """
                cur.execute(query, {'param1': game_academic_year, 'param2': game_class})
                students = cur.fetchall()

                if students:

                    # Delete existing rows in the 'plays' table for the given game_id
                    query = """
                        DELETE FROM plays
                        WHERE game_id = %s;
                    """
                    cur.execute(query, (game_id,))

                    # Insert eligible students into 'plays' table
                    query = """
                        INSERT INTO plays (user_id, game_id)
                        VALUES (%(param1)s, %(param2)s);
                    """
                    for student in students:
                        cur.execute(query, {'param1': student[0], 'param2': game_id})

                    return True

                return False
            
    except Exception:
        return False

# Function to retrieve academic year and class combinations
def get_academic_year_class_combinations():
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    SELECT DISTINCT u.academic_year, u.class
                    FROM user_ AS u LEFT JOIN professor AS p 
                        ON u.user_id = p.user_id
                    WHERE p.user_id IS NULL
                    ORDER BY u.academic_year ASC, u.class ASC;
                """

                cur.execute(query)

                possible_academic_year_class_combs = cur.fetchall()
                
                if possible_academic_year_class_combs:
                    # Process the result into a dictionary
                    combinations = {}
                    for row in possible_academic_year_class_combs:
                        academic_year, class_ = row
                        if academic_year not in combinations:
                            combinations[academic_year] = []
                        combinations[academic_year].append(class_)
                    
                    return combinations
                return False
    
    except Exception:
        return False

# Function to get a game using the game_id
def get_game_by_id(game_id):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    SELECT created_by, game_name, number_of_rounds, 
                           num_inputs, game_academic_year, game_class, password, timestamp_game_creation, 
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
                        "game_academic_year": result[4],
                        "game_class": result[5],
                        "password": result[6],
                        "timestamp_game_creation": result[7],
                        "timestamp_submission_deadline": result[8]
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
                    SELECT game_id, available, created_by, game_name, number_of_rounds, \
                            num_inputs, game_academic_year, game_class, password, timestamp_game_creation, timestamp_submission_deadline 
                    FROM game;
                """
        
                cur.execute(query)

                games_data = cur.fetchall()
                if games_data:
                    games = []
                    for row in games_data:
                        game = {
                            "game_id": row[0],
                            "available": row[1],
                            "created_by": row[2],
                            "game_name": row[3],
                            "number_of_rounds": row[4],
                            "num_inputs": row[5],
                            "game_academic_year": row[6],
                            "game_class": row[7],
                            "password": row[8],
                            "timestamp_game_creation": row[9],
                            "timestamp_submission_deadline": row[10]
                        }
                        games.append(game)
            
                    return games
                return []
    
    except Exception:
        return []
    
# Function to fetch current (or past) games data by user_id
def fetch_current_games_data_by_user_id(sign, user_id):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = f"""
                    SELECT * 
                    FROM game g JOIN plays p 
                        ON g.game_id = p.game_id                
                    WHERE (p.user_id =  %(param1)s 
                    AND CURRENT_TIMESTAMP {sign} g.timestamp_submission_deadline); """
        
                cur.execute(query , {'param1': user_id})

                games_data = cur.fetchall()
                if games_data:
                    games = []
                    for row in games_data:
                        game = {
                            "game_id": row[0],
                            "available": row[1],
                            "created_by": row[2],
                            "game_name": row[3],
                            "number_of_rounds": row[4],
                            "num_inputs": row[5],
                            "game_academic_year": row[6],
                            "game_class": row[7],
                            "password": row[8],
                            "timestamp_game_creation": row[9],
                            "timestamp_submission_deadline": row[10]
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
def update_game_in_db(game_id, created_by, game_name, number_of_rounds, num_inputs, game_academic_year, game_class, password, timestamp_game_creation, submission_deadline):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query1 = """
                    UPDATE game
                    SET created_by = %(param1)s, game_name = %(param2)s, number_of_rounds = %(param3)s, num_inputs = %(param4)s,
                        game_academic_year = %(param5)s, game_class = %(param6)s, password = %(param7)s, timestamp_game_creation = %(param8)s, 
                        timestamp_submission_deadline = %(param9)s
                    WHERE game_id = %(param10)s;
                """

                cur.execute(query1, {
                    'param1': created_by, 
                    'param2': game_name, 
                    'param3': number_of_rounds, 
                    'param4': num_inputs,
                    'param5': game_academic_year,
                    'param6': game_class,
                    'param7': password, 
                    'param8': timestamp_game_creation,
                    'param9': submission_deadline,
                    'param10': game_id
                })

                query2 = """
                    SELECT * 
                    FROM game
                    ORDER BY game_id;
                """

                cur.execute(query2)        

                return True
            
    except Exception:
        return False
    
# Function to update access of negotatiation chats to students 
def update_access_to_chats(access, game_id):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query1 = """
                    UPDATE game
                    SET available = %(param1)s
                    WHERE game_id = %(param2)s;
                """

                cur.execute(query1, {
                    'param1': access,
                    'param2': game_id
                })

                return True
            
    except Exception:
        print('not done')
        return False

# Function to store game details in the database
def store_game_in_db(game_id, available, created_by, game_name, number_of_rounds, num_inputs, game_academic_year, game_class, password, timestamp_game_creation, submission_deadline):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    INSERT INTO game (game_id, available, created_by, game_name, number_of_rounds, num_inputs, game_academic_year, game_class, password, timestamp_game_creation, timestamp_submission_deadline)
                    VALUES (%(param1)s, %(param2)s, %(param3)s, %(param4)s, %(param5)s, %(param6)s, %(param7)s, %(param8)s, %(param9)s, %(param10)s, %(param11)s);
                """

                cur.execute(query, {
                    'param1': game_id,
                    'param2': available,
                    'param3': created_by, 
                    'param4': game_name, 
                    'param5': number_of_rounds, 
                    'param6': num_inputs, 
                    'param7': game_academic_year,
                    'param8': game_class,
                    'param9': password, 
                    'param10': timestamp_game_creation,
                    'param11': submission_deadline
                })

                return True
            
    except Exception:
        return False
    
# Function to get the id of the group from game_id and user_id
def get_group_id_from_user_id(user_id):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = "SELECT group_id FROM user_ WHERE user_id = %(param1)s;"

                cur.execute(query, {'param1': user_id})
                group_id = cur.fetchone()[0]

                return group_id

    except Exception:
        return False

# Function to get the game availability from the game_id 
def get_game_access(game_id): 
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = "SELECT available FROM game WHERE game_id = %s;"

                cur.execute(query, (game_id,))
                game_acess = cur.fetchone()[0]
                return game_acess

    except Exception:
        return False

# Function to remove a student from the database
def remove_student(user_id):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = "DELETE FROM user_ WHERE user_id = %s;"

                cur.execute(query, (user_id,))
         
                return True
            
    except Exception:
        return False

# Function to fetch student data from the database
def get_students_from_db():
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                
                query = """
                    SELECT u.user_id, u.email, u.group_id, u.academic_year, u.class, u.timestamp_user
                    FROM user_ AS u LEFT JOIN professor AS p 
                        ON u.user_id = p.user_id
                    WHERE p.user_id IS NULL;
                """
                cur.execute(query)
                
                # Fetch all results from the query
                rows = cur.fetchall()
                
                # If data exists, create a DataFrame
                if rows:
                    # Convert the result set into a pandas DataFrame
                    df = pd.DataFrame(rows, columns=["user_id", "email", "group_id", "academic_year", "class", "timestamp_user"])
                    return df
                else:
                    return pd.DataFrame(columns=["user_id", "email", "group_id", "academic_year", "class", "timestamp_user"])
    
    except Exception:
        return False

# Function to insert email and OTP into the user table
def insert_student_data(user_id, email, otp, group_id, academic_year, class_):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    INSERT INTO user_ (user_id, email, password, group_id, academic_year, class)
                    VALUES (%(param1)s, %(param2)s, %(param3)s, %(param4)s, %(param5)s, %(param6)s);
                """

                cur.execute(query, {
                    'param1': user_id, 
                    'param2': email, 
                    'param3': otp, 
                    'param4': group_id, 
                    'param5': academic_year,
                    'param6': class_
                })
         
                return True
            
    except Exception:
        return False

# Function to insert round data into the 'round' table
def insert_round_data(game_id, round_number, group1_id, group2_id, score_group1, score_group2):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = """
                    INSERT INTO round (game_id, round_number, group1_id, group2_id, score_group1, score_group2)
                    VALUES (%(param1)s, %(param2)s, %(param3)s, %(param4)s, %(param5)s, %(param6)s);
                """

                cur.execute(query, {
                    'param1': game_id, 
                    'param2': round_number, 
                    'param3': group1_id, 
                    'param4': group2_id, 
                    'param5': score_group1, 
                    'param6': score_group2,
                })
         
                return True
            
    except Exception:
        return False
    
# Function to get the round information of a specific group from a specific game
def get_round_data(game_id, group_id):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:

                query = "SELECT round_number, group1_id, group2_id FROM round WHERE (group1_id = %(param2)s OR group2_id = %(param2)s) AND game_id=%(param1)s;"

                cur.execute(query,{
                    'param1': game_id, 
                    'param2': group_id, 
                })
                round_data = cur.fetchall()

                return round_data

    except Exception:
        return False

# Function to get the ids of the groups that played a specific game
def get_group_ids_from_game_id(game_id): 
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                query = '''SELECT DISTINCT u.group_id
                        FROM user_ u
                        JOIN plays p ON u.user_id = p.user_id
                        WHERE p.game_id = %(param1)s;''' 

                cur.execute(query, {
                    'param1': game_id})
                
                group_ids = cur.fetchall()
                return [i[0] for i in group_ids]

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
                                    ON p.user_id = u.user_id
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
    
# Function to get user_id by email
def get_user_id_by_email(email):
    try:
        with psycopg2.connect(DB_CONNECTION_STRING) as conn:
            with conn.cursor() as cur:
                
                query = "SELECT user_id FROM user_ WHERE email = %s;"

                cur.execute(query, (email,))
                
                # Fetch the result
                user_id = cur.fetchone()[0]
                
                return user_id
            
    except Exception:
        return False
