import streamlit as st
import pandas as pd
import hashlib
import time
from datetime import datetime
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
from modules.database_handler import get_game_by_id, update_game_in_db, fetch_games_data, get_next_game_id, store_game_in_db, remove_student, get_students_from_db, insert_student_data
from modules.drive_file_manager import overwrite_text_file, get_text_from_file, upload_text_as_file

# ---------------------------- SET THE DEFAULT SESSION STATE FOR ALL CASES ------------------------------- #

# Initialize session state for action selection
if "action" not in st.session_state:
    st.session_state.action = "Select Option"

# Initialize session state for back button
if "back_button" not in st.session_state:
    st.session_state.back_button = False

# -------------------------------------------------------------------------------------------------------- #

# Check if the user is authenticated
if st.session_state['authenticated']:

    col1, _, col3 = st.columns([2, 8, 2])
    with col1:
        if st.session_state.back_button:
            # Back button
            if st.button("⬅ Back"):
                st.session_state.back_button = False
                st.session_state.action = "Select Option"
                st.rerun()
    with col3:
        # Sign out button
        sign_out_btn = st.button("Sign Out", key="sign_out", use_container_width=True)

        if sign_out_btn:
            st.session_state.update({'authenticated': False})
            st.session_state.update({'login_email': ""})
            st.session_state.update({'login_password': ""})
            time.sleep(2)
            st.switch_page("0_Home.py")  # Redirect to home page

    # Check if the user is a professor
    if st.session_state['professor']: 

        # Handle different actions for the professor
        if st.session_state.action == "Select Option":
            st.header("Select Option")
            st.write("Welcome, Professor! Please select an option.")

            # Action selection dropdown
            c1, _ = st.columns([3, 2])
            selected_option = c1.selectbox("Select Option", ["Student Management", "Game Configuration", "Available Games", 
                                                            "Leaderboard and Performance", "Game Data Management", "Security"])

            if st.button("Select"):
                st.session_state.action = selected_option  # Update session state only when the button is clicked
                st.session_state.back_button = True
                st.rerun()
        else:
            # Render the selected action
            st.header(st.session_state.action)
            
            # Define behavior for "Student Management"
            match st.session_state.action:

                case "Student Management": # Allow professor to add students, assign students to games and track student activity
                    
                    # ---------------------------- SET THE DEFAULT SESSION STATE FOR STUDENT MANAGEMENT ------------------------------- #

                    if "add_students" not in st.session_state:
                        st.session_state.add_students = False
                    if "add_student" not in st.session_state:
                        st.session_state.add_student = False
                    if "remove_student" not in st.session_state:
                        st.session_state.remove_student = False
                    if "selected_student" not in st.session_state:
                        st.session_state.selected_student = None
                    if "students" not in st.session_state:
                        st.session_state.students = pd.DataFrame(columns=["User ID", "Email", "Academic Year", "Class", "Created at"])

                    # ----------------------------------------------------------------------------------------------------------------- #

                    # --------------------------------------------------- FUNCTIONS --------------------------------------------------- #

                    # Function to add students from a CSV file
                    def add_students_from_csv(file):
                        try:
                            # Read CSV with a semicolon delimiter
                            df = pd.read_csv(file, sep=';', dtype={'OTP': str, 'academic year': str})
                            
                            # Check if all required columns exist in the CSV
                            if 'userID' not in df.columns or 'email' not in df.columns or 'OTP' not in df.columns or 'academic year' \
                                not in df.columns or 'class' not in df.columns:
                                st.error("CSV must contain 'userID', 'email', 'OTP', 'academic year' and 'class' columns.")
                                return
                            
                            # Insert student data row by row
                            for _, row in df.iterrows():
                                userID = row['userID']
                                email = row['email']
                                otp = row['OTP']
                                academic_year = row['academic year']
                                class_ = row['class']

                                if insert_student_data(userID, email, otp, academic_year, class_):
                                    continue
                                else:
                                    return False
                            return True
                            
                        except Exception:
                            st.error("Error processing the CSV file. Please try again.")

                    # Function to display the student table with selectable rows
                    def show_student_table():
                        # Fetch data from the database
                        students_from_db = get_students_from_db()
                        
                        # Rename columns for display
                        students_display = students_from_db.rename(columns={
                            "userID": "User ID",
                            "email": "Email",
                            "academic_year": "Academic Year",
                            "class": "Class",
                            "timestamp_user": "Created at"
                        })
                        
                        # Update session state with the dataset
                        st.session_state.students = students_display

                        # Add a "Select" column for row checkboxes
                        students_display[""] = ""
                        
                        ## Configure grid options
                        gb = GridOptionsBuilder.from_dataframe(students_display[["", "User ID", "Email", "Academic Year", "Class", "Created at"]])
                    
                        gb.configure_column("", checkboxSelection=True, width=60)
                        gb.configure_column("User ID", width=120)
                        gb.configure_column("Email", width=200)
                        gb.configure_column("Academic Year", width=160)
                        gb.configure_column("Class", width=80)
                        gb.configure_column("Created at", width=150)
                        
                        gridOptions = gb.build()

                        # Display the table
                        data = AgGrid(students_display[["", "User ID", "Email", "Academic Year", "Class", "Created at"]],
                                    gridOptions=gridOptions,
                                    fit_columns_on_grid_load=True,
                                    height=min(36 + 27 * students_display.shape[0], 300),
                                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                                    columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
                        return data

                    # ------------------------------------------------------------------------------------------------------------------------------------ #

                    # Display the student table
                    data = show_student_table()
                    st.session_state.selected_student = data["selected_rows"]

                    # Action buttons
                    _, col1, col2, col3 = st.columns([1,1,1,2])

                    with col1:
                        if st.button("Add Students", key="add_students_via_csv"):
                            st.session_state.add_students = True
                    with col2:
                        if st.button("Add Student", key="add_student_manually"):
                            st.session_state.add_student = True
                    with col3:
                        if st.button("Remove Student", key="remove_student_manually"):
                            st.session_state.remove_student = True

                    # Handle adding students via CSV
                    if st.session_state.add_students:
                        with st.form("add_students_form"):
                            uploaded_file = st.file_uploader("Upload CSV with Email and OTP", type=["csv"])

                            submit_button = st.form_submit_button("Add Students")

                            if submit_button:
                                if uploaded_file is not None:
                                    if add_students_from_csv(uploaded_file):
                                        st.success("Students added successfully!")
                                    else:
                                        st.error("An error occurred when adding the students. Please try again.")
                                else:
                                    st.error("Please upload a valid CSV file.")
                                st.session_state.add_students = False
                                st.session_state.action = "Student Management"
                                time.sleep(2)
                                st.rerun()

                    # Handle manual student addition
                    if st.session_state.add_student:
                        with st.form("add_student_form"):
                            userID = st.text_input("Introduce User ID:")
                            email = st.text_input("Introduce Email:")
                            otp = st.text_input("Introduce OTP:")
                            academic_year = st.text_input("Introduce academic year:")
                            class_ = st.text_input("Introduce class:")

                            submit_button = st.form_submit_button("Add Student")

                            if submit_button:
                                if not userID or not email or not otp or not academic_year or not class_:
                                    st.error("Please fill in all fields.")
                                else:
                                    if insert_student_data(userID, email, otp, academic_year, class_):
                                        st.success("Student added successfully!")
                                    else:
                                        st.error("Failed to add student. Please try again.")
                                    st.session_state.add_student = False
                                    st.session_state.action = "Student Management"
                                    time.sleep(2)
                                    st.rerun()

                    # Handle student removal
                    if st.session_state.remove_student:
                        if st.session_state.students.empty:
                            st.warning("No students found. Please add a student.")
                        else:
                            if st.session_state.selected_student is not None:
                                if len(st.session_state.selected_student) != 0:
                                    userID = st.session_state.selected_student['User ID'].tolist()[0]
                                    if remove_student(userID):
                                        st.success("Student removed successfully!")
                                        st.session_state.students = st.session_state.students[st.session_state.students["User ID"] != userID]
                                    else:
                                        st.error("Failed to remove student. Please try again.")
                            else:
                                st.warning("Please select a student to remove.")
                        st.session_state.remove_student = False
                        st.session_state.action = "Student Management"
                        time.sleep(2)
                        st.rerun()

                case "Game Configuration": # Allow professor to create a game

                    # Handle manual game creation
                    with st.form("game_configuration_form"):
                        game_name = st.text_input("Game Name", max_chars=100, key="game_name")
                        game_explanation = st.text_area("Game Explanation", key="explanation")
                        number_of_rounds = st.number_input("Number of Rounds", min_value=1, step=1, key="number_of_rounds")
                        num_inputs = st.number_input("Number of Input Boxes", min_value=1, step=1, key="num_inputs")
                        password = st.text_input("Game Password (4-digit)", type="password", max_chars=4, key="password")
                        deadline_date = st.date_input("Submission Deadline Date", key="deadline_date")
                        deadline_time = st.time_input("Submission Deadline Time", key="deadline_time")

                        create_game_button = st.form_submit_button("Create Game")
                    
                        if create_game_button:
                            if game_name and game_explanation and number_of_rounds and num_inputs and password:
                                try:
                                    # Retrieve user ID from session state
                                    user_id = st.session_state.get('userID')

                                    # Get the next game ID from the database
                                    next_game_id = get_next_game_id()

                                    timestamp_game_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                    # Store the Game explanation in Google Drive
                                    upload_text_as_file(game_explanation, f"{user_id}_{next_game_id}_{timestamp_game_creation}")
                                    
                                    # Hash password before the creation of the game
                                    #hashed_password = hashlib.sha256(password.encode()).hexdigest()

                                    # Combine the date and time into a single datetime object
                                    submission_deadline = datetime.combine(deadline_date, deadline_time)

                                    # Store other details in the database
                                    store_game_in_db(user_id, game_name, number_of_rounds, num_inputs, password, 
                                                     timestamp_game_creation, submission_deadline)
                                    
                                    st.success("Game created successfully!")
                                    
                                except Exception:
                                    st.error(f"An error occurred. Please try again.")
                            else:
                                st.error("Please fill out all fields before submitting.")
                            st.session_state.action = "Game Configuration"
                            time.sleep(2)
                            st.rerun()

                case "Available Games": # Allow professor to see and edit the available games

                    # ------------------------- SET THE DEFAULT SESSION STATE FOR AVAILABLE GAMES ---------------------------- #

                    if "edit_game" not in st.session_state:
                        st.session_state.edit_game = False
                    if "game_id" not in st.session_state:
                        st.session_state.game_id = ""

                    # -------------------------------------------------------------------------------------------------------- #

                    # ------------------------------------------ FUNCTIONS --------------------------------------------------- #

                    # Function to put the game_edit state to True and save the game_id in the session state
                    def edit_game_state_and_save_game_id(game_id):
                        st.session_state.update({'game_id': game_id})
                        st.session_state.edit_game = True

                    # -------------------------------------------------------------------------------------------------------- #

                    if not st.session_state.edit_game:
                        # Fetch the list of games from the database
                        games = fetch_games_data()

                        if games != []:
                            # Streamlit sidebar selectbox for games
                            game_names = [game['game_name'] for game in games]
                            selected_game_name = st.sidebar.selectbox("Select a Game", game_names)

                            # Find the selected game
                            selected_game = next((game for game in games if game['game_name'] == selected_game_name), None)
                            
                            if selected_game:
                                st.subheader(f"Details for {selected_game['game_name']}")
                                st.write(f"**Game ID**: {selected_game['game_id']}")
                                st.write(f"**Created By**: {selected_game['created_by']}")
                                st.write(f"**Number of Rounds**: {selected_game['number_of_rounds']}")
                                st.write(f"**Number of Inputs**: {selected_game['num_inputs']}")
                                st.write(f"**Password**: {selected_game['password']}")
                                st.write(f"**Creation Time**: {selected_game['timestamp_game_creation']}")
                                st.write(f"**Submission Deadline**: {selected_game['timestamp_submission_deadline']}")

                                # Retrieve user ID from session state
                                user_id = st.session_state.get('userID')

                                # Get the Game explanation from Google Drive using the filename
                                game_explanation = get_text_from_file(f"{user_id}_{selected_game['game_id']}_{selected_game['timestamp_game_creation']}.txt")
                                if game_explanation:
                                    st.write(f"**Game Explanation**: {game_explanation}")
                                else:
                                    st.write("No explanation found for this game.")
                                
                                game_id = selected_game['game_id']
                                edit_game_button = st.button("Edit Game", on_click=edit_game_state_and_save_game_id(game_id))
                        else:
                            st.write("There are no available games.")
                    else:
                        # Handle manual game edit
                        with st.form("game_edit_form"):

                            game_id_edit = st.session_state.game_id
                            game_details = get_game_by_id(game_id_edit)

                            if game_details:
                                created_by_stored = game_details["created_by"]
                                game_name_stored = game_details["game_name"]
                                number_of_rounds_stored = game_details["number_of_rounds"]
                                num_inputs_stored = game_details["num_inputs"]
                                password_stored = game_details["password"]
                                timestamp_game_creation_stored = game_details["timestamp_game_creation"]
                                deadline_date_stored = game_details["timestamp_submission_deadline"].date()
                                deadline_time_stored = game_details["timestamp_submission_deadline"].time()

                                # Fetch Game explanation from Google Drive
                                game_explanation_stored = get_text_from_file(f"{created_by_stored}_{game_id_edit}_{timestamp_game_creation_stored}.txt")
                            else:
                                st.error("Game not found.")

                            game_name_edit = st.text_input("Game Name", max_chars=100, key="game_name_edit", value=game_name_stored)
                            game_explanation_edit = st.text_area("Game Explanation", key="explanation_edit", value=game_explanation_stored)
                            number_of_rounds_edit = st.number_input("Number of Rounds", min_value=1, step=1, key="number_of_rounds_edit", value=number_of_rounds_stored)
                            num_inputs_edit = st.number_input("Number of Input Boxes", min_value=1, step=1, key="num_inputs_edit", value=num_inputs_stored)
                            password_edit = st.text_input("Game Password (4-digit)", type="password", max_chars=4, key="password_edit", value=password_stored)
                            deadline_date_edit = st.date_input("Submission Deadline Date", key="deadline_date_edit", value=deadline_date_stored)
                            deadline_time_edit = st.time_input("Submission Deadline Time", key="deadline_time_edit", value=deadline_time_stored)

                            change_game_button = st.form_submit_button("Change Game")
                        
                            if change_game_button:
                                if game_name_edit and game_explanation_edit and number_of_rounds_edit and num_inputs_edit and password_edit:
                                    try:
                                        # Retrieve user ID from session state
                                        user_id = st.session_state.get('userID')

                                        game_id = st.session_state.game_id

                                        timestamp_game_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                        # Overwrite file in Google Drive
                                        overwrite_text_file(game_explanation_edit, f"{user_id}_{game_id}_{timestamp_game_creation}")
                                        
                                        # Hash password before the creation of the game
                                        #hashed_password = hashlib.sha256(password.encode()).hexdigest()

                                        # Combine the date and time into a single datetime object
                                        submission_deadline = datetime.combine(deadline_date_edit, deadline_time_edit)

                                        # Update other details in the database
                                        update_game_in_db(game_id, user_id, game_name_edit, number_of_rounds_edit, num_inputs_edit, password_edit, 
                                                        timestamp_game_creation, submission_deadline)
                                        
                                        st.success("Game changed successfully!")
                                        
                                    except Exception:
                                        st.error(f"An error occurred. Please try again.")
                                else:
                                    st.error("Please fill out all fields before submitting.")
                                st.session_state.edit_game = False
                                st.session_state.action = "Available Games"
                                time.sleep(2)
                                st.rerun()

                case "Game Results":
                    st.write("To be implemented")

                case "Leaderboard and Performance":
                    st.write("To be implemented")

                case _:
                    st.header("Select Option")

    else:
        st.write(
            """Page available only for Professors"""
        )

else:
    st.write(
        """Please Login first (Page available only for Professors)"""
    )
