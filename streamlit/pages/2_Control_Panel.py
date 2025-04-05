import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import random
import re
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
from modules.database_handler import populate_plays_table, insert_student_data, remove_student, store_game_in_db, update_game_in_db, update_num_rounds_game, update_access_to_chats, delete_from_round
from modules.database_handler import get_academic_year_class_combinations, get_game_by_id, fetch_games_data, get_next_game_id, get_students_from_db, get_group_ids_from_game_id, get_round_data, get_error_matchups, fetch_and_compute_scores_for_year, fetch_and_compute_scores_for_year_game
from modules.drive_file_manager import overwrite_text_file, get_text_from_file, upload_text_as_file, get_text_from_file_without_timestamp, find_and_delete 
from modules.negotiations import create_chats, create_all_error_chats

# ---------------------------- SET THE DEFAULT SESSION STATE FOR ALL CASES ------------------------------- #

# Initialize session state for action selection
if "action" not in st.session_state:
    st.session_state.action = "Select Option"

# Initialize session state for back button
if "back_button" not in st.session_state:
    st.session_state.back_button = False

# -------------------- SET THE DEFAULT SESSION STATE FOR STUDENT MANAGEMENT CASE ------------------------- #

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

# ----------------------- SET THE DEFAULT SESSION STATE FOR AVAILABLE GAMES CASE ------------------------- #

if "edit_game" not in st.session_state:
    st.session_state.edit_game = False
if "game_id" not in st.session_state:
    st.session_state.game_id = ""

# -------------------------------------------------------------------------------------------------------- #

st.set_page_config("Control Panel")

@st.cache_resource
def get_text_from_file_aux(name):
    text = get_text_from_file(f'{name}.txt')
    return text

@st.cache_resource
def get_text_from_file_without_timestamp_aux(name):
    text = get_text_from_file_without_timestamp(name)
    return text

# Check if the user is authenticated
if st.session_state['authenticated']:

    col1, _, col3 = st.columns([2, 8, 2])
    with col1:
        if st.session_state.back_button:
            # Back button
            if st.button("⬅ Back"):
                if st.session_state.edit_game:
                    st.session_state.edit_game = False
                else:
                    st.session_state.back_button = False
                    st.session_state.add_student = False
                    st.session_state.add_students = False
                    st.session_state.remove_student = False
                    st.session_state.action = "Select Option"
                st.rerun()
    with col3:
        # Sign out button
        sign_out_btn = st.button("Sign Out", key="sign_out", use_container_width=True)

        if sign_out_btn:
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.cache_resource.clear()
            time.sleep(2)
            st.switch_page("0_Home.py")  # Redirect to home page

    # Check if the user is a professor
    if st.session_state['professor']: 

        # Handle different actions for the professor
        if st.session_state.action == "Select Option":
            st.header("Control Panel")
            st.write("Welcome, Professor!")

            # Action selection dropdown
            c1, _ = st.columns([3, 2])
            selected_option = c1.selectbox("Please select what you would like to do:", ["Student Management", "Create Game", "Available Games",
                                                                                        "Run Simulation" , "Game Data", "Leaderboard"])

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

                    # --------------------------------------------------- FUNCTIONS --------------------------------------------------- #

                    # Function to add students from a CSV file
                    def add_students_from_csv(file):
                        try:
                            # Read CSV with a semicolon delimiter
                            df = pd.read_csv(file, sep=';', dtype={'academic year': str})
                            
                            # Check if all required columns exist in the CSV
                            if 'userID' not in df.columns or 'email' not in df.columns or 'groupID' not in df.columns or 'academic year' \
                                not in df.columns or 'class' not in df.columns:
                                st.error("CSV must contain 'userID', 'email', 'groupID', 'academic year' and 'class' columns.")
                                return
                            
                            # Insert student data row by row
                            for _, row in df.iterrows():
                                user_id = row['userID']
                                email = row['email']
                                group_id = row['groupID']
                                academic_year = row['academic year']
                                class_ = row['class']

                                if insert_student_data(user_id, email, "Not defined", group_id, academic_year, class_):
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
                            "user_id": "User ID",
                            "email": "Email",
                            "group_id": "Group ID",
                            "academic_year": "Academic Year",
                            "class": "Class",
                            "timestamp_user": "Created at"
                        })
                        
                        # Update session state with the dataset
                        st.session_state.students = students_display

                        # Add a "Select" column for row checkboxes
                        students_display[""] = ""
                        
                        ## Configure grid options
                        gb = GridOptionsBuilder.from_dataframe(students_display[["", "User ID", "Email", "Group ID", "Academic Year", "Class", "Created at"]])
                    
                        gb.configure_column("", checkboxSelection=True, width=60)
                        gb.configure_column("User ID", width=120)
                        gb.configure_column("Email", width=140)
                        gb.configure_column("Group ID", width=120)
                        gb.configure_column("Academic Year", width=140)
                        gb.configure_column("Class", width=80)
                        gb.configure_column("Created at", width=130)
                        
                        gridOptions = gb.build()

                        # Display the table
                        data = AgGrid(students_display[["", "User ID", "Email", "Group ID", "Academic Year", "Class", "Created at"]],
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
                            st.session_state.add_student = False
                            st.session_state.remove_student = False
                    with col2:
                        if st.button("Add Student", key="add_student_manually"):
                            st.session_state.add_student = True
                            st.session_state.add_students = False
                            st.session_state.remove_student = False
                    with col3:
                        if st.button("Remove Student", key="remove_student_manually"):
                            st.session_state.remove_student = True
                            st.session_state.add_student = False
                            st.session_state.add_students = False

                    # Handle adding students via CSV
                    if st.session_state.add_students:
                        with st.form("add_students_form"):
                            uploaded_file = st.file_uploader("Upload CSV with all the Students", type=["csv"])

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
                            user_id = st.text_input("Introduce User ID:")
                            email = st.text_input("Introduce Email:")
                            group_id = st.text_input("Introduce the Group ID:")
                            academic_year = st.text_input("Introduce academic year:")
                            class_ = st.text_input("Introduce class:")

                            submit_button = st.form_submit_button("Add Student")

                            if submit_button:
                                if not user_id or not email or not group_id or not academic_year or not class_:
                                    st.error("Please fill in all fields.")
                                else:
                                    if insert_student_data(user_id, email, "Not defined", group_id, academic_year, class_):
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
                                    user_id = st.session_state.selected_student['User ID'].tolist()[0]
                                    if remove_student(user_id):
                                        st.success("Student removed successfully!")
                                        st.session_state.students = st.session_state.students[st.session_state.students["User ID"] != user_id]
                                    else:
                                        st.error("Failed to remove student. Please try again.")
                            else:
                                st.warning("Please select a student to remove.")
                        st.session_state.remove_student = False
                        st.session_state.action = "Student Management"
                        time.sleep(2)
                        st.rerun()

                case "Create Game":  # Allow professor to create a game
                    # Get academic year and class combinations
                    academic_year_class_combinations = get_academic_year_class_combinations()

                    # Create options list with both years and year-class combinations
                    combination_options = []
                    for year, classes in academic_year_class_combinations.items():
                        combination_options.append(f"{year}")  # Add the year itself
                        combination_options.extend([f"{year} - {cls}" for cls in classes])  # Add year-class combinations

                    # Form to handle game creation
                    with st.form("game_creation_form"):
                        # Game details
                        game_name = st.text_input("Game Name", max_chars=100, key="game_name")
                        game_explanation = st.text_area("Game Explanation", key="explanation")
                
                        col1, col2 = st.columns(2)
                        with col1: name_roles_1 = st.text_input("Name of Low-Value Role", value = 'Buyer')
                        with col2: name_roles_2 = st.text_input("Name of High-Value Role", value = 'Seller')

                        st.write('')
                        col1, col2, col3, col4 = st.columns(4)
                        with col1: param1 = st.number_input("Minimum Low-Value", min_value=0, step=1, value=9)
                        with col2: param2 = st.number_input("Maximum Low-Value", min_value=0, step=1, value=11)
                        with col3: param3 = st.number_input("Minimum High-Value", min_value=0, step=1, value=19)
                        with col4: param4 = st.number_input("Maximum High-Value", min_value=0, step=1, value=21,
                                                     help='All values are expressed in the unit mentioned in description.')

                        # Academic year and class selection
                        selected_combination = st.selectbox(
                            "Select Academic Year and Class",
                            options=combination_options,
                            key="academic_year_class_combination",
                        )

                        # Extract academic year and class from the selected combination
                        if "-" in selected_combination:
                            game_academic_year, game_class = selected_combination.replace(" ", "").split("-")
                        else:
                            game_academic_year = selected_combination
                            game_class = "_"  # No class selected

                        password = st.text_input("Game Password (4-digit)", type="password", max_chars=4, key="password")

                        # Calculate default date and time
                        default_date = datetime.today().date() + timedelta(weeks=1)
                        default_time = datetime.strptime("23:59", "%H:%M").time()

                        # Create Streamlit inputs with defaults
                        deadline_date = st.date_input("Submission Deadline Date", value=default_date, key="deadline_date")
                        deadline_time = st.time_input("Submission Deadline Time", value=default_time, key="deadline_time")

                        # Submit button for creating the game
                        submit_button = st.form_submit_button("Create Game")

                    # Submit button for creating the game
                    if submit_button:
                        #if create_game_button:
                        if game_name and game_explanation and name_roles_1 and name_roles_2 and selected_combination and \
                            param1 and param2 and param3 and param4 and password and deadline_date and deadline_time:
                            try:
                                # Retrieve user ID from session state
                                user_id = st.session_state.get('user_id')

                                # Get the next game ID from the database
                                next_game_id = get_next_game_id()

                                timestamp_game_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                # Store the Game explanation in Google Drive
                                upload_text_as_file(game_explanation, f"Explanation_{user_id}_{next_game_id}_{timestamp_game_creation}")

                                # Combine the date and time into a single datetime object
                                submission_deadline = datetime.combine(deadline_date, deadline_time)

                                # Concatenate both names of roles using a security pattern between them
                                name_roles = name_roles_1 + '#_;:)' + name_roles_2

                                # Store other details in the database
                                store_game_in_db(next_game_id, 0, user_id, game_name, -1, name_roles, game_academic_year,
                                                   game_class, password, timestamp_game_creation, submission_deadline)
                                
                                # Populate the 'plays' table with eligible students
                                if not populate_plays_table(next_game_id, game_academic_year, game_class):
                                    error = st.error("An error occurred while assigning students to the game.")
                                    time.sleep(2)
                                    error.empty()
                                
                                different_groups_classes = get_group_ids_from_game_id(next_game_id)
                                text = f'{param1},{param2},{param3},{param4}\n'
                                for i in different_groups_classes:
                                    buy_value = int(random.uniform(param1, param2))
                                    sell_value = int(random.uniform(param3, param4))
                                    text += f'{i[0]},{i[1]},{buy_value},{sell_value}\n'

                                upload_text_as_file(text, f"Values_{user_id}_{next_game_id}_{timestamp_game_creation}")

                                success = st.success("Game created successfully!")
                                time.sleep(2)
                                success.empty()

                            except Exception:
                                error = st.error("An error occurred. Please try again.")
                                time.sleep(2)
                                error.empty()

                        else:
                            warning = st.warning("Please fill out all fields before submitting.")
                            time.sleep(2)
                            warning.empty()
 
                case "Available Games": # Allow professor to see and edit the available games

                    if not st.session_state.edit_game:

                        # Fetch unique academic years
                        possible_years = fetch_games_data(get_academic_years=True)

                        # Sidebar selectbox for academic year selection
                        selected_year = st.sidebar.selectbox("Select Academic Year", possible_years)

                        # Fetch games for the selected academic year
                        games_for_selected_year = fetch_games_data(academic_year=selected_year)

                        if games_for_selected_year != []:
                            # Generate game names with class suffixes
                            game_names_with_classes = [
                                f"{game['game_name']}{'' if game['game_class'] == '_' else (' - Class ' + game['game_class'])}"
                                for game in games_for_selected_year
                            ]

                            # Sidebar selectbox for game selection
                            selected_game_with_classes = st.sidebar.selectbox("Select Game", game_names_with_classes)

                            # Extract game_name and game_class from selected_game_with_classes
                            if " - Class " in selected_game_with_classes:
                                selected_game_name, selected_game_class = selected_game_with_classes.split(" - Class ")
                            else:
                                selected_game_name = selected_game_with_classes
                                selected_game_class = "_"

                            # Find the selected game
                            selected_game = next(
                                (game for game in games_for_selected_year if game['game_name'] == selected_game_name and game['game_class'] == selected_game_class),
                                None
                            )

                            radio = st.sidebar.radio('See Game:', ['Details', 'Simulation Params'], horizontal=True)

                            if radio == 'Details':

                                if selected_game:

                                    values = get_text_from_file(f"Values_{selected_game['created_by']}_{selected_game['game_id']}_{selected_game['timestamp_game_creation']}.txt")
                                    if values: 
                                        values = values.split('\n')
                                        values = [item.split(',') for item in values if item]
                                        params = list(map(int, values[0]))

                                    st.subheader(f"Details of {selected_game['game_name']}")
                                    st.write(f"**Game ID**: {selected_game['game_id']}")
                                    st.write(f"**Available**: {selected_game['available']}")
                                    st.write(f"**Created By**: {selected_game['created_by']}")
                                    st.write(f"**Number of Rounds**: {selected_game['number_of_rounds'] if selected_game['number_of_rounds'] != -1 else 'TBD'}")
                                    st.write(f"**Academic Year**: {selected_game['game_academic_year']}")
                                    st.write(f"**Class**: {selected_game['game_class']}")
                                    st.write("")
                                    col1, col2 = st.columns(2)
                                    with col1: st.write(f"**Name of Low-Value Role**: {selected_game['name_roles'].split('#_;:)')[0]}")
                                    with col2: st.write(f"**Name of High-Value Role**: {selected_game['name_roles'].split('#_;:)')[1]}")
                                    col1, col2= st.columns(2)
                                    with col1: st.write(f"**Minimum Low-Value**: {params[0]}")
                                    with col2: st.write(f"**Minimum High-Value**: {params[2]}")
                                    col1, col2= st.columns(2)
                                    with col1: st.write(f"**Maximum Low-Value**: {params[1]}")
                                    with col2: st.write(f"**Maximum High-Value**: {params[3]}")
                                    st.write("")
                                    st.write(f"**Password**: {selected_game['password']}")
                                    st.write(f"**Creation Time**: {selected_game['timestamp_game_creation']}")
                                    st.write(f"**Submission Deadline**: {selected_game['timestamp_submission_deadline']}")

                                    # Retrieve user ID from session state
                                    user_id = st.session_state.get('user_id')

                                    # Get the Game explanation from Google Drive using the filename
                                    game_explanation = get_text_from_file(f"Explanation_{selected_game['created_by']}_{selected_game['game_id']}_{selected_game['timestamp_game_creation']}.txt")
                                    if game_explanation:
                                        st.write(f"**Game Explanation**: {game_explanation}")
                                    else:
                                        st.write("No explanation found for this game.")
                                    
                                    game_id = selected_game['game_id']
                                    edit_game_button = st.button("Edit Game")
                                    st.session_state.update({'game_id': game_id})

                                    if edit_game_button:
                                        st.session_state.edit_game = True
                                        st.rerun()

                            elif radio == 'Simulation Params':

                                st.subheader(f'Simulation Parameters of {selected_game_with_classes}')
                                simulation_params_names = ['Model', 'Conversation Starter', 'Starting Message', 'Number of Turns', 'Negotiation Termination Message', 'Negotiation Summary Prompt', 'Summary Termination Message']
                                
                                # here we do not save the result in cache on purpose
                                simulation_params = get_text_from_file_without_timestamp(f'Simulation_{selected_game["created_by"]}_{selected_game["game_id"]}')
                                if simulation_params:
                                    simulation_params = simulation_params.split('\n')                               
                                    name_roles = selected_game['name_roles'].split('#_;:)')
                                    name_roles_1, name_roles_2 = name_roles[0], name_roles[1]
                                    if simulation_params[1]=='same': simulation_params[1] = f'{name_roles_1} ➡ {name_roles_2}'
                                    else: simulation_params[1] = f'{name_roles_2} ➡ {name_roles_1}'
                                
                                    for i in range(len(simulation_params_names)):
                                        st.write(f'**{simulation_params_names[i]}**: {simulation_params[i]}')

                                else: st.write('No simulation run yet.')
                                    
                        else:
                            st.write("There are no available games.")
                    else:
                        # Handle manual game edit
                        game_id = st.session_state.game_id
                        game_details = get_game_by_id(game_id)

                        if game_details:
                            created_by_stored = game_details["created_by"]
                            game_name_stored = game_details["game_name"]
                            number_of_rounds_stored = game_details["number_of_rounds"]
                            name_roles_1_stored = game_details["name_roles"].split('#_;:)')[0]
                            name_roles_2_stored = game_details["name_roles"].split('#_;:)')[1]
                            game_academic_year_stored = game_details["game_academic_year"]
                            game_class_stored = game_details["game_class"]
                            password_stored = game_details["password"]
                            timestamp_game_creation_stored = game_details["timestamp_game_creation"]
                            deadline_date_stored = game_details["timestamp_submission_deadline"].date()
                            deadline_time_stored = game_details["timestamp_submission_deadline"].time()

                            values_stored = get_text_from_file(f'Values_{created_by_stored}_{game_id}_{timestamp_game_creation_stored}.txt')
                            if values_stored: 
                                values_stored = values_stored.split('\n')
                                values_stored = [item.split(',') for item in values_stored if item]
                                params_stored = list(map(int, values_stored[0]))

                            # Fetch Game explanation from Google Drive
                            game_explanation_stored = get_text_from_file(f"Explanation_{created_by_stored}_{game_id}_{timestamp_game_creation_stored}.txt")
                        else:
                            st.error("Game not found.")

                        # Get academic year and class combinations
                        academic_year_class_combinations = get_academic_year_class_combinations()

                        # Create options list with both years and year-class combinations
                        combination_options = []
                        for year, classes in academic_year_class_combinations.items():
                            combination_options.append(f"{year}")  # Add the year itself
                            combination_options.extend([f"{year} - {cls}" for cls in classes])  # Add year-class combinations

                        # Preselect the stored academic year-class combination
                        if game_class_stored != "_":
                            stored_combination = f"{game_academic_year_stored} - {game_class_stored}"
                        else: 
                            stored_combination = f"{game_academic_year_stored}"

                        with st.form("game_edit_form"):
                            # Game details
                            game_name_edit = st.text_input("Game Name", max_chars=100, key="game_name_edit", value=game_name_stored)
                            game_explanation_edit = st.text_area("Game Explanation", key="explanation_edit", value=game_explanation_stored)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                name_roles_1_edit = st.text_input("Name of Low-Value Role", key="name_roles_1_edit", value=name_roles_1_stored)
                            
                            with col2:
                                name_roles_2_edit = st.text_input("Name of High-Value Role", key="name_roles_2_edit", value=name_roles_2_stored)

                            st.write('')
                            col1, col2, col3, col4 = st.columns(4)
                            with col1: param1_edit = st.number_input("Minimum Low-Value", min_value=0, step=1, value=int(params_stored[0]/1000))
                            with col2: param2_edit = st.number_input("Maximum Low-Value", min_value=0, step=1, value=int(params_stored[1]/1000))
                            with col3: param3_edit = st.number_input("Minimum High-Value", min_value=0, step=1, value=int(params_stored[2]/1000))
                            with col4: param4_edit = st.number_input("Maximum High-Value", min_value=0, step=1, value=int(params_stored[3]/1000),
                                                     help='All values are expressed in thousands.')
                            
                            # Academic year-class combination selection
                            selected_combination_edit = st.selectbox(
                                "Select Academic Year and Class",
                                options=combination_options,
                                index=combination_options.index(stored_combination),
                                key="academic_year_class_combination_edit",
                            )

                            # Extract academic year and class from the selected combination
                            if "-" in selected_combination_edit:
                                game_academic_year_edit, game_class_edit = selected_combination_edit.replace(" ", "").split("-")
                            else:
                                game_academic_year_edit = selected_combination_edit
                                game_class_edit = "_"  # No class selected

                            password_edit = st.text_input("Game Password (4-digit)", type="password", max_chars=4, key="password_edit", value=password_stored)
                            deadline_date_edit = st.date_input("Submission Deadline Date", key="deadline_date_edit", value=deadline_date_stored)
                            deadline_time_edit = st.time_input("Submission Deadline Time", key="deadline_time_edit", value=deadline_time_stored)

                            # Submit button
                            submit_button = st.form_submit_button("Change Game")

                        # Handle form submission
                        if submit_button:
                            if  game_name_edit and game_explanation_edit and name_roles_1_edit and name_roles_2_edit and \
                                selected_combination_edit and password_edit and deadline_date_edit and deadline_time_edit:
                                try:
                                    # Overwrite file in Google Drive
                                    overwrite_text_file(game_explanation_edit, f"Explanation_{created_by_stored}_{game_id}_{timestamp_game_creation_stored}")
 
                                    # Combine the date and time into a single datetime object
                                    submission_deadline = datetime.combine(deadline_date_edit, deadline_time_edit)
 
                                    # Concatenate both names of roles using a security pattern between them
                                    name_roles_edit = name_roles_1_edit + '#_;:)' + name_roles_2_edit

                                    # Update other details in the database
                                    update_game_in_db(game_id, created_by_stored, game_name_edit, -1, name_roles_edit, game_academic_year_edit,
                                                        game_class_edit, password_edit, timestamp_game_creation_stored, submission_deadline)
                                    
                                    # Populate the 'plays' table with eligible students (after update)
                                    if not populate_plays_table(game_id, game_academic_year_edit, game_class_edit):
                                        st.error("An error occurred while assigning students to the game.")

                                    # Handling Values.txt
                                    different_groups_classes = get_group_ids_from_game_id(game_id)
                                    if game_class_stored == game_class_edit and str(game_academic_year_stored) == game_academic_year_edit:
                                        if params_stored[0]==param1_edit*1000 and params_stored[1]==param2_edit*1000 and params_stored[2]==param3_edit*1000 and params_stored[3]==param4_edit*1000:
                                            pass
                                        else:
                                            text = f'{param1_edit*1000},{param2_edit*1000},{param3_edit*1000},{param4_edit*1000}\n'
                                            for i in different_groups_classes:
                                                buy_value = int(round(random.uniform(param1_edit*1000, param2_edit*1000), -2))
                                                sell_value = int(round(random.uniform(param3_edit*1000, param4_edit*1000), -2))
                                                text += f'{i[0]},{i[1]},{buy_value},{sell_value}\n'
                                            overwrite_text_file(text, f'Values_{created_by_stored}_{game_id}_{timestamp_game_creation_stored}')
                                            
                                    else: 
                                        text = f'{param1_edit*1000},{param2_edit*1000},{param3_edit*1000},{param4_edit*1000}\n'
                                        for i in different_groups_classes:
                                            buy_value = int(round(random.uniform(param1_edit*1000, param2_edit*1000), -2))
                                            sell_value = int(round(random.uniform(param3_edit*1000, param4_edit*1000), -2))
                                            text += f'{i[0]},{i[1]},{buy_value},{sell_value}\n'
                                        overwrite_text_file(text, f'Values_{created_by_stored}_{game_id}_{timestamp_game_creation_stored}')

                                    st.success("Game changed successfully!")
                                    
                                except Exception:
                                    st.error(f"An error occurred. Please try again.")
                            else:
                                warning = st.warning("Please fill out all fields before submitting.")
                                time.sleep(2)
                                warning.empty()

                case "Run Simulation":

                    # Fetch unique academic years
                    possible_years = fetch_games_data(get_academic_years=True)

                    # Sidebar selectbox for academic year selection
                    selected_year = st.sidebar.selectbox("Select Academic Year", possible_years)

                    # Fetch games for the selected academic year
                    games_for_selected_year = fetch_games_data(academic_year=selected_year)

                    if games_for_selected_year != []:
                        # Generate game names with class suffixes
                        game_names_with_classes = [
                            f"{game['game_name']}{'' if game['game_class'] == '_' else (' - Class ' + game['game_class'])}"
                            for game in games_for_selected_year
                        ]

                        # Sidebar selectbox for game selection
                        selected_game_with_classes = st.sidebar.selectbox("Select Game", game_names_with_classes)

                        # Extract game_name and game_class from selected_game_with_classes
                        if " - Class " in selected_game_with_classes:
                            selected_game_name, selected_game_class = selected_game_with_classes.split(" - Class ")
                        else:
                            selected_game_name = selected_game_with_classes
                            selected_game_class = "_"

                        # Find the selected game
                        selected_game = next(
                            (game for game in games_for_selected_year if game['game_name'] == selected_game_name and game['game_class'] == selected_game_class),
                            None
                        )
                        
                        game_id = selected_game['game_id']
                        created_by = selected_game['created_by']
                        timestamp_game_creation = selected_game['timestamp_game_creation']
                        name_roles = selected_game['name_roles'].split('#_;:)')
                        name_roles_1, name_roles_2 = name_roles[0], name_roles[1]

                        values = get_text_from_file(f'Values_{created_by}_{game_id}_{timestamp_game_creation}.txt')
                        if values:
                            values = values.split('\n')
                            values = [item.split(',') for item in values if item]

                        radio = st.sidebar.radio('Run:', ['Simulation', 'Error Chats'], horizontal=True)

                        if radio == 'Simulation':

                            teams = get_group_ids_from_game_id(game_id)
                            
                            missing_submissions = ''
                            to_remove = []
                            for i in teams:
                                prompts = get_text_from_file_without_timestamp_aux(f'Game{game_id}_Class{i[0]}_Group{i[1]}')
                                if not prompts: 
                                    to_remove.append(i) 
                                    missing_submissions += f' Class{i[0]}-Group{i[1]},'
                            
                            if len(missing_submissions) > 0:
                                missing_submissions = missing_submissions[:-1]
                                st.warning(f'''Attention: Not all groups have submitted their prompts yet.\n
                                            Missing submissions from:{missing_submissions}.''')
                            
                            for i in to_remove:
                                teams.remove(i)
                                
                            if (len(teams)>=2):
                                st.warning('''Attention:  Running a new simulation will erase all previous data related to the game. 
                                           This includes all group chats and all group scores.''')
                                with st.form(key='my_form'):
                                    api_key = st.text_input('API Key')
                                    model = st.selectbox('OpenAI Model', ['gpt-4o-mini', 'gpt-4o'])
                                    num_rounds =  st.number_input('Number of Rounds', step=1, min_value=1, value=1, max_value=len(teams)-1)
                                    conversation_starter = st.radio('Conversation Starter', [f'{name_roles_1} ➡ {name_roles_2}', f'{name_roles_2} ➡ {name_roles_1}'], horizontal=True)
                                    starting_message =  st.text_input('Starting Messsage', value='I want to buy this car.')
                                    num_turns =  st.number_input('Maximum Number of Turns', step=1, min_value=1, value=15)
                                    negotiation_termination_message = st.text_input('Negotiation Termination Message', value='Pleasure doing business with you')
                                    summary_prompt = st.text_input('Negotiation Summary Prompt', value='For how much was the car sold?')
                                    summary_termination_message = st.text_input('Summary Termination Message', value='The value agreed was')

                                    submit_button = st.form_submit_button(label='Run')

                                if submit_button:

                                    if api_key and model and num_rounds and conversation_starter and starting_message and num_turns and negotiation_termination_message and summary_prompt and summary_termination_message:
                                        
                                        round_data = get_round_data(game_id)
                                        for i in round_data:
                                            find_and_delete(f'Game{game_id}_Round{i[0]}_Class{i[1]}_Group{i[2]}_Class{i[3]}_Group{i[4]}.txt')
                                            find_and_delete(f'Game{game_id}_Round{i[0]}_Class{i[3]}_Group{i[4]}_Class{i[1]}_Group{i[2]}.txt')
                                        delete_from_round(game_id)
                                        
                                        order = 'same' if conversation_starter.split(' ➡ ') == name_roles else 'opposite'
                                        simulation_content = model + '\n' + order + '\n' + starting_message + '\n' + str(num_turns) + '\n' + negotiation_termination_message + '\n' + summary_prompt + '\n' + summary_termination_message
                                        overwrite_text_file(simulation_content, f"Simulation_{created_by}_{game_id}_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                  
                                        update_num_rounds_game(num_rounds, game_id)  

                                        config_list = {"config_list" : [{"model": model, "api_key": api_key}], "temperature": 0.3, "top_p": 0.5}
                                        
                                        outcome_simulation = create_chats(game_id, config_list, name_roles, order, teams, values, num_rounds, starting_message, num_turns, negotiation_termination_message, summary_prompt, summary_termination_message)
                                        if outcome_simulation == "All negotiations were completed successfully!":
                                            success = st.success(outcome_simulation)
                                            time.sleep(2)
                                            success.empty()
                                        else: 
                                            warning = st.warning(outcome_simulation)

                                    else:
                                        warning = st.warning("Please fill out all fields before submitting.")
                                        time.sleep(2)
                                        warning.empty()
                            else: 
                                st.write('There must be at least two submissions in order to run a simulation.')

                        elif radio == 'Error Chats':

                            st.subheader('Error Chats')
                            
                            if get_error_matchups(game_id):
                                error_message = "The following negotiations were unsuccessful:\n\n"
                                for match in get_error_matchups(game_id):
                                    if match[3]==1:
                                        error_message += f"- Round {match[0]} - Class{match[1][0]}_Group{match[1][1]} ({name_roles_1}) vs Class{match[2][0]}_Group{match[2][1]} ({name_roles_2});\n"
                                    if match[4]==1:
                                        error_message += f"- Round {match[0]} - Class{match[2][0]}_Group{match[2][1]} ({name_roles_1}) vs Class{match[1][0]}_Group{match[1][1]} ({name_roles_2});\n"
                                st.warning(error_message)

                                with st.form(key='my_form2'):
                                    api_key = st.text_input('API Key')
                                    model = st.selectbox('OpenAI Model', ['gpt-4o-mini', 'gpt-4o'])
                                    submit_button = st.form_submit_button(label='Run')

                                if submit_button:
                                    if api_key and model:                            
                                        simulation_params = get_text_from_file_without_timestamp(f'Simulation_{created_by}_{game_id}')
                                        simulation_params = simulation_params.split('\n')    
                                        simulation_params[3] = int(simulation_params[3])     
                                        
                                        config_list = {"config_list" : [{"model": model, "api_key": api_key}], "temperature": 0.3, "top_p": 0.5}

                                        outcome_errors_simulation = create_all_error_chats(game_id, config_list, name_roles, simulation_params[1], values, simulation_params[2], simulation_params[3], simulation_params[4], simulation_params[5], simulation_params[6])                 
                                        if outcome_errors_simulation == "All negotiations were completed successfully!":
                                            success = st.success(outcome_errors_simulation)
                                            time.sleep(2)
                                            success.empty()
                                            st.rerun()
                                        else: 
                                            warning = st.warning(outcome_errors_simulation)
                                            time.sleep(2)
                                            warning.empty()
                                            st.rerun()

                                    else:
                                        warning = st.warning("Please fill out all fields before submitting.")
                                        time.sleep(2)
                                        warning.empty()

                            else: st.write('No error chats found.')
                    else:
                        st.write('There are no available games.')

                case "Game Data":

                    # Fetch unique academic years
                    possible_years = fetch_games_data(get_academic_years=True)

                    # Sidebar selectbox for academic year selection
                    selected_year = st.sidebar.selectbox("Select Academic Year", possible_years)

                    # Fetch games for the selected academic year
                    games_for_selected_year = fetch_games_data(academic_year=selected_year)
                    
                    if games_for_selected_year != []:
                        # Generate game names with class suffixes
                        game_names_with_classes = [
                            f"{game['game_name']}{'' if game['game_class'] == '_' else (' - Class ' + game['game_class'])}"
                            for game in games_for_selected_year
                        ]

                        # Sidebar selectbox for game selection
                        selected_game_with_classes = st.sidebar.selectbox("Select Game", game_names_with_classes)

                        # Extract game_name and game_class from selected_game_with_classes
                        if " - Class " in selected_game_with_classes:
                            selected_game_name, selected_game_class = selected_game_with_classes.split(" - Class ")
                        else:
                            selected_game_name = selected_game_with_classes
                            selected_game_class = "_"

                        # Find the selected game
                        selected_game = next(
                            (game for game in games_for_selected_year if game['game_name'] == selected_game_name and game['game_class'] == selected_game_class),
                            None
                        )

                        game_id = selected_game['game_id']
                        professor_id = selected_game['created_by']
                        num_rounds = selected_game['number_of_rounds']
                        game_timestamp = selected_game['timestamp_game_creation'] 
                        name_roles = selected_game['name_roles'].split('#_;:)')
                        name_roles_1, name_roles_2 = name_roles[0], name_roles[1]

                        teams = get_group_ids_from_game_id(game_id)

                        options = ['View Prompts', 'View Chats']
                        selection = st.sidebar.radio(label= 'Select an option', options=options, horizontal=True)

                        st.header(f"{selected_game_name}")

                        with st.expander("**Explanation**"):
                            # Get the Game explanation from Google Drive using the filename
                            game_explanation = get_text_from_file(f'Explanation_{professor_id}_{game_id}_{game_timestamp}.txt')
                            if game_explanation:
                                st.write(f"{game_explanation}")
                            else:
                                st.write("No explanation found for this game.")

                        if selection == 'View Prompts':

                            if teams:
                                for i in teams: 
                                    class_ = i[0]
                                    group_id = i[1]
                                    prompts = get_text_from_file_without_timestamp_aux(f'Game{game_id}_Class{class_}_Group{group_id}')

                                    # Display group header
                                    st.write(f"### Class {class_} - Group {group_id}")

                                    # Expandable section for viewing prompts
                                    if prompts:
                                        with st.expander("**View Prompts**"):
                                            prompts = prompts.split('#_;:)')
                                            st.write(f'**{name_roles_1}:** {prompts[0].strip()}')
                                            st.write(f'**{name_roles_2}:** {prompts[1].strip()}')
                                    else:
                                        st.write(f"No submission found.")

                        elif selection == 'View Chats':

                            # Check if the game is currently enabled
                            round_data = get_round_data(game_id)

                            if round_data:

                                is_enabled = selected_game['available']

                                if is_enabled:
                                    access_disabled = st.button('Disable Student Access to these Negotiation Chats and Leaderboard')

                                    if access_disabled: 
                                        update_access_to_chats(0, selected_game['game_id'])
                                        success = st.success('Student Access successfully disabled.')
                                        time.sleep(2)
                                        success.empty()
                                        st.rerun()
                                
                                else:
                                    access_enabled = st.button('Enable Student Access to Negotiation Chats and Leaderboard')

                                    if access_enabled: 
                                        update_access_to_chats(1, selected_game['game_id'])
                                        success = st.success('Student Access successfully enabled.')
                                        time.sleep(2)
                                        success.empty()
                                        st.rerun()

                                # Extract unique round numbers
                                unique_rounds = sorted(set(round_ for round_, _, _, _, _, _, _, _, _ in round_data))

                                round_options = [f"Round {round_}" for round_ in unique_rounds]
                                selected_round_label = st.sidebar.selectbox("Select Round", round_options)

                                # Extract the selected round number from the label
                                selected_round_number = int(re.search(r'\d+', selected_round_label).group())

                                st.markdown(f"### Round {selected_round_number}")

                                # Ensure unique round-teams combinations
                                unique_round_teams = [(class_1, team_1, class_2, team_2) for round_, class_1, team_1, class_2, team_2, _, _, _, _ in round_data if round_ == selected_round_number]  

                                for class_1, team_1, class_2, team_2 in unique_round_teams:

                                    # Fetch the chat data before creating the expander
                                    chat_buyer = get_text_from_file_aux(f'Game{game_id}_Round{selected_round_number}_Class{class_1}_Group{team_1}_Class{class_2}_Group{team_2}')
                                    chat_seller = get_text_from_file_aux(f'Game{game_id}_Round{selected_round_number}_Class{class_2}_Group{team_2}_Class{class_1}_Group{team_1}')

                                    # Create an expander only if the chat exists
                                    
                                    with st.expander(f"**Class {class_1} - Group {team_1} ({name_roles_1}) vs Class {class_2} - Group {team_2} ({name_roles_2})**"):
                                        if chat_buyer: st.write(chat_buyer.replace('$', '\\$'))
                                        else: st.write('Chat not found.')                                            

                                    with st.expander(f"**Class {class_1} - Group {team_1} ({name_roles_2}) vs Class {class_2} - Group {team_2} ({name_roles_1})**"):
                                        if chat_seller: st.write(chat_seller.replace('$', '\\$'))
                                        else: st.write('Chat not found.') 

                            else: 
                                st.write('No chats found.')                                           

                    else: 
                        st.write('There are no available games.')    

                case "Leaderboard":
                    
                    # Fetch unique academic years
                    possible_years = fetch_games_data(get_academic_years=True)

                    # Sidebar selectbox for academic year selection
                    selected_year = st.sidebar.selectbox("Select Academic Year", possible_years)

                    if selected_year:
                        # Fetch games for the selected academic year
                        games_for_selected_year = fetch_games_data(academic_year=selected_year)

                        if games_for_selected_year != []:
                            # Generate game names with class suffixes
                            game_names_with_classes = [
                                f"{game['game_name']}{'' if game['game_class'] == '_' else (' - Class ' + game['game_class'])}"
                                for game in games_for_selected_year
                            ]

                            # "All" as the default option
                            game_names_with_classes.insert(0, "All")

                            # Sidebar selectbox for game selection
                            selected_game_with_classes = st.sidebar.selectbox("Select Game", game_names_with_classes)

                            # If no game is selected, use fetch_and_compute_scores_for_year (based on year only)
                            if selected_game_with_classes == "All":
                                leaderboard = fetch_and_compute_scores_for_year(selected_year)
                                
                                if leaderboard and leaderboard != False: # Check for valid leaderboard data
                                    
                                    # Prepare the leaderboard data with all columns
                                    leaderboard_with_position = [
                                        {
                                            "Class": row["team_class"],
                                            "Group ID": row["team_id"],
                                            "Score": row["average_score"],
                                            "Position (Low-Value Role)": row["position_name_roles_1"],
                                            "Score (Low-Value Role)": row["score_name_roles_1"],
                                            "Position (High-Value Role)": row["position_name_roles_2"],
                                            "Score (High-Value Role)": row["score_name_roles_2"],
                                        }
                                        for row in leaderboard
                                    ]
                                    
                                    # Convert to a DataFrame for display
                                    leaderboard_df = pd.DataFrame(
                                        leaderboard_with_position, 
                                        columns=[
                                            "Class", 
                                            "Group ID", 
                                            "Score", 
                                            "Position (Low-Value Role)",
                                            "Score (Low-Value Role)",
                                            "Position (High-Value Role)",
                                            "Score (High-Value Role)"
                                        ]
                                    )

                                    # Round the numerical columns to two decimal places
                                    leaderboard_df["Score"] = leaderboard_df["Score"].round(2)
                                    leaderboard_df["Score (Low-Value Role)"] = leaderboard_df["Score (Low-Value Role)"].round(2)
                                    leaderboard_df["Score (High-Value Role)"] = leaderboard_df["Score (High-Value Role)"].round(2)

                                    # Adjust the index to start from 1
                                    leaderboard_df.index = leaderboard_df.index + 1

                                    st.dataframe(leaderboard_df.style.format(precision=2), use_container_width=True)
                                else:
                                    st.write("No leaderboard available.")
                            else:
                                index_ = game_names_with_classes.index(selected_game_with_classes)-1

                                # Fetch and compute the leaderboard for the selected year, game, and class
                                leaderboard = fetch_and_compute_scores_for_year_game(games_for_selected_year[index_]['game_id'])

                                if leaderboard and leaderboard != False:  # Check for valid leaderboard data
                                    
                                    # Prepare the leaderboard data with all columns
                                    leaderboard_with_position = [
                                        {
                                            "Class": row["team_class"],
                                            "Group ID": row["team_id"],
                                            "Score": row["average_score"],
                                            "Position (Low-Value Role)": row["position_name_roles_1"],
                                            "Score (Low-Value Role)": row["score_name_roles_1"],
                                            "Position (High-Value Role)": row["position_name_roles_2"],
                                            "Score (High-Value Role)": row["score_name_roles_2"],
                                        }
                                        for row in leaderboard
                                    ]

                                    # Convert to a DataFrame for display
                                    leaderboard_df = pd.DataFrame(
                                        leaderboard_with_position, 
                                        columns=[
                                            "Class", 
                                            "Group ID", 
                                            "Score", 
                                            "Position (Low-Value Role)",
                                            "Score (Low-Value Role)",
                                            "Position (High-Value Role)",
                                            "Score (High-Value Role)"
                                        ]
                                    )

                                    # Round the numerical columns to two decimal places
                                    leaderboard_df["Score"] = leaderboard_df["Score"].round(2)
                                    leaderboard_df["Score (Low-Value Role)"] = leaderboard_df["Score (Low-Value Role)"].round(2)
                                    leaderboard_df["Score (High-Value Role)"] = leaderboard_df["Score (High-Value Role)"].round(2)

                                    # Adjust the index to start from 1
                                    leaderboard_df.index = leaderboard_df.index + 1

                                    st.dataframe(leaderboard_df.style.format(precision=2), use_container_width=True)
                                else:
                                    st.write("No leaderboard available.")
                        else:
                            st.write("There are no available games for the selected academic year.")
                    
    else:
        st.header("Control Panel")
        st.write('Page accessible only to Professors.')

else:
    st.header("Control Panel")
    st.write('Please Login first. (Page accessible only to Professors)')
