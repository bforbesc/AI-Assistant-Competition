import streamlit as st
import pandas as pd
import time
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
from modules.database_handler import remove_student, get_students_from_db, insert_student_data

# ---------------------------- SET THE DEFAULT SESSION STATE FOR ALL CASES ------------------------------- #

# Initialize session state for action selection
if "action" not in st.session_state:
    st.session_state.action = "Select Option"

# -------------------------------------------------------------------------------------------------------- #

# Check if the user is authenticated
if st.session_state['authenticated']:

    _, _, col3 = st.columns([2, 8, 2])
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

        # ----------------------------------------------------------- FUNCTIONS -------------------------------------------------------------- #

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

        # Handle different actions for the professor
        if st.session_state.action == "Select Option":
            st.header("Select Option")
            st.write("Welcome, Professor! Please select an option")

            # Action selection dropdown
            c1,_= st.columns([3,2])
            st.session_state.action = c1.selectbox("Select Option", ["Student Management", "Game Configuration", "Game Results", 
                                                    "Leaderboard and Performance", "Game Data Management", "Security"])
            if st.button("Select"):
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

                    # Display the student table
                    data = show_student_table()
                    st.session_state.selected_student = data["selected_rows"]

                    # Action buttons
                    col1, col2, col3, col4 = st.columns([1,1,1,2])

                    with col1:
                        if st.button("⬅ Back"):
                            st.session_state.action = "Select Option"
                            st.rerun()
                    with col2:
                        if st.button("Add Students", key="add_students_via_csv"):
                            st.session_state.add_students = True
                    with col3:
                        if st.button("Add Student", key="add_student_manually"):
                            st.session_state.add_student = True
                    with col4:
                        if st.button("Remove Student", key="remove_student_manually"):
                            st.session_state.remove_student = True

                    # Handle adding students via CSV
                    if st.session_state.add_students:
                        with st.form("add_students_form", clear_on_submit=True):
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
                        with st.form("add_student_form", clear_on_submit=True):
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

                case "Game Configuration": # Allow professor to choose a game and set the configurations

                    game_types = ["Select Game", "Ultimatum Game", "Prisoner's Dilemma", "Trust Game"]
                    game_type = st.selectbox("Select Game Type", game_types)
                    match game_type:
                        case "Ultimatum Game":
                            st.write("Ultimatum Game settings:")
                            rounds = st.number_input("Number of Rounds:", min_value=1, step=1)
                            # Save settings in session state
                            if st.button("Set Game Settings"):
                                st.session_state.game_settings = {
                                    "game_type": game_type,
                                    "rounds": rounds
                                }
                                st.success("Game settings updated!")
                        case "Prisoner's Dilemma":
                            st.write("Prisoner's Dilemma settings:")
                            rounds = st.number_input("Number of Rounds:", min_value=1, step=1)
                            # Save settings in session state
                            if st.button("Set Game Settings"):
                                st.session_state.game_settings = {
                                    "game_type": game_type,
                                    "rounds": rounds
                                }
                                st.success("Game settings updated!")
                        case "Trust Game":
                            st.write("Trust Game settings:")
                            rounds = st.number_input("Number of Rounds:", min_value=1, step=1)
                            # Save settings in session state
                            if st.button("Set Game Settings"):
                                st.session_state.game_settings = {
                                    "game_type": game_type,
                                    "rounds": rounds
                                }
                                st.success("Game settings updated!")
                        case _:
                            st.write("Select a game type")
                        
                    if st.button("⬅ Back"): # Return to options
                        st.session_state.action = "Select Option"
                        st.rerun()

                case "Game Results":
                    st.write("To be implemented")
                    if st.button("⬅ Back"): # Return to options
                        st.session_state.action = "Select Option"
                        st.rerun()

                case "Leaderboard and Performance":
                    st.write("To be implemented")
                    if st.button("⬅ Back"): # Return to options
                        st.session_state.action = "Select Option"
                        st.rerun()

                case "Game Data Management":
                    st.write("To be implemented")
                    if st.button("⬅ Back"): # Return to options
                        st.session_state.action = "Select Option"
                        st.rerun()

                case "Security":
                    st.write("To be implemented")
                    if st.button("⬅ Back"): # Return to options
                        st.session_state.action = "Select Option"
                        st.rerun()

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
