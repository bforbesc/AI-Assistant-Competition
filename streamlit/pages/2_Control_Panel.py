
# ----------------- IMPORTS ----------------- 

import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode
import pickle

# Check if the user is logged in
if st.session_state['authenticated']:

    # Create a sign-out button
    _, _, col3 = st.columns([2, 8, 2])
    with col3:
        sign_out_btn = st.button("Sign Out", key="sign_out", use_container_width=True)

        if sign_out_btn:
            st.session_state.update({'authenticated': False})
            st.session_state.update({'login_email': ""})
            st.session_state.update({'login_password': ""})
            time.sleep(2)
            st.switch_page("0_Home.py")  # Redirect to home page

    if st.session_state['professor']:

        # Markdown cheat sheet to help with formatting
        # https://www.markdownguide.org/basic-syntax/


        # ----------------- FUNCTIONS ----------------- 

        # Function to speed testing add a student (no inputs)
        def add_student():
            un = chr(ord(st.session_state.students["Username"].tolist()[-1])+1)
            input = pd.DataFrame({"User ID": [max(st.session_state.students["User ID"]) + 1],
                                    "Username": [un], 
                                    "Email": [un+"@student.com"],
                                    "Created at": [pd.Timestamp.now().strftime("%d-%m-%Y")]})
            st.session_state.students = pd.concat([st.session_state.students, input])
            st.session_state.add_student_button = False
            st.rerun()

        # function with inputs    
        # def add_student():
        #     st.write("Add Student")
        #     username = st.text_input("Enter Username")
        #     email = st.text_input("Enter Email")
        #     if st.button("Add"):
        #         input = pd.DataFrame({"User ID": [max(st.session_state.students["User ID"]) + 1], # Automatically generate User ID
        #                                 "Username": [username], # Get Username from input
        #                                 "Email": [email], # Get Email from input
        #                                 "Created at": [pd.Timestamp.now().strftime("%d-%m-%Y")]}) # Automatically generate Created at
        #         st.session_state.students = pd.concat([st.session_state.students, input])
        #         st.session_state.add_student_button = False
        #         st.rerun()
                
        def remove_student(user_id):
            st.session_state.students = st.session_state.students[st.session_state.students["User ID"] != user_id]
            st.rerun()

        def show_student_table():
            gb = GridOptionsBuilder.from_dataframe(st.session_state.students[["User ID", "Username", "Email", "Created at"]])
            gb.configure_selection(selection_mode="single", use_checkbox=True)
            gb.configure_column("User ID", "ID", width=50, resizable=False)
            gb.configure_column("Created at", width=75, resizable=False)
            gridOptions = gb.build()
            # save grid options in an external variable
            
            # with open("data.pkl", "wb") as f:
            #     pickle.dump(gridOptions, f)
            data = AgGrid(st.session_state.students[["User ID", "Username", "Email", "Created at"]],
                        gridOptions=gridOptions,
                        fit_columns_on_grid_load=True,
                        height=min(36+27*st.session_state.students.shape[0],300),
                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
            return data

        def show_student(selected_rows):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown("##### ID")
                st.markdown(f":orange[{selected_rows['User ID'].tolist()[0]}]")
            with col2:
                st.markdown("##### Name")
                st.markdown(f":orange[{selected_rows['Username'].tolist()[0]}]")
            with col3:
                st.markdown("##### Email")
                st.markdown(f":orange[{selected_rows['Email'].tolist()[0]}]")
            with col4:
                st.markdown("##### Created at")
                st.markdown(f":orange[{selected_rows['Created at'].tolist()[0]}]")

        # ------------- DEFINE VARIABLES ------------- 

        PROFESSOR_PASSWORD = "ProfessorRodrigo"

        button_1 = "Back to Options" # button name for back to options
        button_2 = "Back to Student Management" # button name for back to student management

        # ------- SET THE DEFAULT SESSION STATE ------- 

        if "action" not in st.session_state:
            st.session_state.action = "Student Management" # currently set to "Student Management" for speed testing (default is "Select Option")
        if "professor_authenticated" not in st.session_state:
            st.session_state.professor_authenticated = True # currently set to True for speed testing (default is False)
        if "add_student_button" not in st.session_state:
            st.session_state.add_student_button = False
        if "see_student" not in st.session_state:
            st.session_state.see_student = False
        if "selected_student" not in st.session_state:
            st.session_state.selected_student = None
        if "students" not in st.session_state:
            st.session_state.students = pd.DataFrame({"User ID": [1, 2], 
                                                    "Username": ["a", "b"], 
                                                    "Email": ["a@student.com", "b@student.com"], 
                                                    "Created at": ["01-10-2024", "02-10-2024"]
                                                    })

        # ----------------- PROFESSOR PAGE ----------------- 

        st.set_page_config(page_title='Control Panel')

        st.title("Professor Page")
        # Checks passwaord
        if not st.session_state.professor_authenticated:
            # Ask for password
            password = st.text_input("Enter Password", type="password")
            if st.button("Login"):
                if password == PROFESSOR_PASSWORD:
                    st.session_state.professor_authenticated = True
                    # st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid password!")
        else:
            # Allow professor to access the page if authenticated
            if st.session_state.action == "Select Option":
                st.header("Select Option")
                st.write("Welcome, Professor! Please select an option")
                # Allow professor to choose next action
                c1,_= st.columns([3,2])
                st.session_state.action = c1.selectbox("Select Option", ["Select Option", "Student Management", "Game Configuration", "Game Results", 
                                                        "Leaderboard and Performance", "Game Data Management", "Security", "Logout"])
                if st.button("Select"):
                    st.rerun()
            else:
                st.header(st.session_state.action)
                # Implement the selected action
                match st.session_state.action:
                    case "Student Management": # Allow professor to add students, assign students to games and track student activity
                        
                        if st.session_state.see_student:
                            st.write("Student Information")
                            show_student(st.session_state.selected_student)
                            if st.button(button_2): # Return to student management
                                st.session_state.see_student = False
                                st.rerun()
                        else:
                            data = show_student_table()
                            st.session_state.selected_student = data["selected_rows"]
                            c1, c2, c3 = st.columns([1,1,2])
                            if (c1.button("Add Student") or st.session_state.add_student_button):
                                st.session_state.add_student_button = True
                                st.session_state.remove_student_button = False
                                add_student()
                            if c2.button("Remove Student"):
                                if st.session_state.students.empty:
                                    st.error("No students found. Please add a student.")
                                else:
                                    if st.session_state.selected_student is not None:
                                        if len(st.session_state.selected_student) != 0:
                                            st.session_state.add_student_button = False
                                            remove_student(st.session_state.selected_student['User ID'].tolist()[0])
                                    else:
                                        st.warning("Please select a student to remove.")
                            if c3.button("See Student"):
                                if st.session_state.students.empty:
                                    st.error("No students found. Please add a student.")
                                else:
                                    if st.session_state.selected_student is not None:
                                        if len(st.session_state.selected_student) != 0:
                                            st.session_state.add_student_button = False
                                            st.session_state.see_student = True
                                            st.rerun()
                                    else:
                                        st.warning("Please select a student to see.")
                                
                        if st.button(button_1):
                            st.session_state.action = "Select Option"
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
                            
                        if st.button(button_1): # Return to options
                            st.session_state.action = "Select Option"
                            st.rerun()
                    case "Game Results":
                        st.write("To be implemented")
                        if st.button(button_1): # Return to options
                            st.session_state.action = "Select Option"
                            st.rerun()
                    case "Leaderboard and Performance":
                        st.write("To be implemented")
                        if st.button(button_1): # Return to options
                            st.session_state.action = "Select Option"
                            st.rerun()
                    case "Game Data Management":
                        st.write("To be implemented")
                        if st.button(button_1): # Return to options
                            st.session_state.action = "Select Option"
                            st.rerun()
                    case "Security":
                        st.write("To be implemented")
                        if st.button(button_1): # Return to options
                            st.session_state.action = "Select Option"
                            st.rerun()
                    case "Logout":
                        st.session_state.professor_authenticated = False
                        st.session_state.action = "Select Option"
                        # st.success("Logged out successfully!") 
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
