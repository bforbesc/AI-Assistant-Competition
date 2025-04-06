import streamlit as st
import pandas as pd
import hashlib
import time
from modules.database_handler import update_password, get_class_from_user_id, get_group_id_from_user_id
from modules.database_handler import fetch_games_data, fetch_and_compute_scores_for_year, get_academic_year_from_user_id, fetch_and_compute_scores_for_year_game

# Initialize session state for buttons if not set
if 'password_edit_mode' not in st.session_state:
    st.session_state['password_edit_mode'] = False

if 'show_password' not in st.session_state:
    st.session_state['show_password'] = False  # Track password visibility state

# Check if the user is logged in
if st.session_state['authenticated']:

    # Create a sign-out button
    _, _, col3 = st.columns([2, 8, 2])
    with col3:
        sign_out_btn = st.button("Sign Out", key="sign_out", use_container_width=True)

        if sign_out_btn:
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.cache_resource.clear()
            # time.sleep(2)
            st.switch_page("0_Home.py")  # Redirect to home page

    if st.session_state.professor == True:

        st.header("Profile")

        # Display email
        email = st.session_state['login_email']
        st.markdown(f"<h3 style='font-size: 24px;'>Email</h3>", unsafe_allow_html=True)
        st.write(f"{email}")

        # Display user_id
        user_id = st.session_state['user_id']
        st.markdown(f"<h3 style='font-size: 24px;'>User ID</h3>", unsafe_allow_html=True)
        st.write(f"{user_id}")

        # Display password with eye and edit pencil buttons
        st.markdown(f"<h3 style='font-size: 24px;'>Password</h3>", unsafe_allow_html=True)
        col1, col2, _, _, _, _, _ = st.columns([4, 1, 1, 1, 1, 1, 1])  # Same structure as the user_id for vertical alignment
        with col1:
            password = st.session_state.get('login_password', '')
            if st.session_state['show_password']:
                st.write(f"{password if password else 'Not defined'}")
            else:
                st.text('*******' if password else 'Not defined')

        with col2:
            # Align eye and pencil buttons within the same column
            col_eye, col_pencil = st.columns([6, 1])
            with col_eye:
                if st.session_state['show_password'] == True:
                    if st.button("🔒", key="toggle_password"):
                        st.session_state['show_password'] = not st.session_state['show_password']  # Toggle visibility state
                        st.rerun()
                else:
                    if st.button("👁️", key="toggle_password"):
                        st.session_state['show_password'] = not st.session_state['show_password']  # Toggle visibility state
                        st.rerun()   
            with col_pencil:
                if st.session_state['password_edit_mode'] == False:
                    if st.button("✏️", key="edit_password"):
                        st.session_state['password_edit_mode'] = True  # Set to True when clicked
                        st.rerun()
                if st.session_state['password_edit_mode'] == True:
                    if st.button("✏️", key="edit_password"):
                        st.session_state['password_edit_mode'] = False  # Set to True when clicked
                        st.rerun()

        # Show form for editing password if in edit mode
        if st.session_state['password_edit_mode']:
            with st.form(key="password_form"):
                new_password = st.text_input("**Enter new password**", type="password", key="new_password_input")
                confirm_password = st.text_input("**Confirm new password**", type="password", key="confirm_password_input")
                update_password_btn = st.form_submit_button("Update Password")

                if update_password_btn:
                    if new_password and confirm_password:
                        if new_password == confirm_password:
                            # Check if password is strong
                            if (len(new_password) >= 8 and
                                any(char.isupper() for char in new_password) and
                                any(char.islower() for char in new_password) and
                                any(char.isdigit() for char in new_password) and
                                any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?/`~' for char in new_password)):

                                # Hash and update password if strong
                                hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

                                if update_password(email, hashed_password):
                                    st.success("Password updated successfully!")
                                    st.session_state['login_password'] = new_password  # Update session state password
                                    st.session_state['password_edit_mode'] = False  # Reset edit mode
                                    # time.sleep(2)
                                    st.rerun()  # Rerun to reset the page
                                else:
                                    st.error("Failed to update password.")
                            else:
                                st.error("Password must be at least 8 characters long and include an uppercase letter, \
                                            a lowercase letter, a number, and a special character.")
                        else:
                            st.error("Passwords do not match.")
                    else:
                        error = st.error("Please fill in both password fields.")
                        # time.sleep(2)
                        error.empty()

    elif st.session_state.professor == False:
            
        ACADEMIC_YEAR = get_academic_year_from_user_id(st.session_state.user_id)
        CLASS = get_class_from_user_id(st.session_state['user_id'])
        GROUP_ID = get_group_id_from_user_id(st.session_state['user_id'])
        
        selection = st.sidebar.radio(label= '', options=['Leaderboard','Personal Data'], horizontal=True)

        if selection == 'Personal Data':

            st.header("Personal Data")

            # Display email
            email = st.session_state['login_email']
            st.markdown(f"<h3 style='font-size: 24px;'>Email</h3>", unsafe_allow_html=True)
            st.write(f"{email}")

            # Display user_id
            user_id = st.session_state['user_id']
            st.markdown(f"<h3 style='font-size: 24px;'>User ID</h3>", unsafe_allow_html=True)
            st.write(f"{user_id}")

            # Display password with eye and edit pencil buttons
            st.markdown(f"<h3 style='font-size: 24px;'>Password</h3>", unsafe_allow_html=True)
            col1, col2, _, _, _, _, _ = st.columns([4, 1, 1, 1, 1, 1, 1])  # Same structure as the user_id for vertical alignment
            with col1:
                password = st.session_state.get('login_password', '')
                if st.session_state['show_password']:
                    st.write(f"{password if password else 'Not defined'}")
                else:
                    st.text('*******' if password else 'Not defined')

            with col2:
                # Align eye and pencil buttons within the same column
                col_eye, col_pencil = st.columns([6, 1])
                with col_eye:
                    if st.session_state['show_password'] == True:
                        if st.button("🔒", key="toggle_password"):
                            st.session_state['show_password'] = not st.session_state['show_password']  # Toggle visibility state
                            st.rerun()
                    else:
                        if st.button("👁️", key="toggle_password"):
                            st.session_state['show_password'] = not st.session_state['show_password']  # Toggle visibility state
                            st.rerun()   
                with col_pencil:
                    if st.session_state['password_edit_mode'] == False:
                        if st.button("✏️", key="edit_password"):
                            st.session_state['password_edit_mode'] = True  # Set to True when clicked
                            st.rerun()
                    if st.session_state['password_edit_mode'] == True:
                        if st.button("✏️", key="edit_password"):
                            st.session_state['password_edit_mode'] = False  # Set to True when clicked
                            st.rerun()

            # Show form for editing password if in edit mode
            if st.session_state['password_edit_mode']:
                with st.form(key="password_form"):
                    new_password = st.text_input("**Enter new password**", type="password", key="new_password_input")
                    confirm_password = st.text_input("**Confirm new password**", type="password", key="confirm_password_input")
                    update_password_btn = st.form_submit_button("Update Password")

                    if update_password_btn:
                        if new_password and confirm_password:
                            if new_password == confirm_password:
                                # Check if password is strong
                                if (len(new_password) >= 8 and
                                    any(char.isupper() for char in new_password) and
                                    any(char.islower() for char in new_password) and
                                    any(char.isdigit() for char in new_password) and
                                    any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?/`~' for char in new_password)):

                                    # Hash and update password if strong
                                    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

                                    if update_password(email, hashed_password):
                                        st.success("Password updated successfully!")
                                        st.session_state['login_password'] = new_password  # Update session state password
                                        st.session_state['password_edit_mode'] = False  # Reset edit mode
                                        # time.sleep(2)
                                        st.rerun()  # Rerun to reset the page
                                    else:
                                        st.error("Failed to update password.")
                                else:
                                    st.error("Password must be at least 8 characters long and include an uppercase letter, \
                                                a lowercase letter, a number, and a special character.")
                            else:
                                st.error("Passwords do not match.")
                        else:
                            error = st.error("Please fill in both password fields.")
                            # time.sleep(2)
                            error.empty()

        if selection == 'Leaderboard':
            st.header("Leaderboard")

            games = fetch_games_data(academic_year=ACADEMIC_YEAR)

            if games != []:

                game_names_with_classes = [
                                f"{game['game_name']}{'' if game['game_class'] == '_' else (' - Class ' + game['game_class'])}"
                                for game in games
                            ]

                game_names_with_classes.insert(0, "All")

                selected_game_with_classes = st.sidebar.selectbox("Select Game", game_names_with_classes)

                def color_coding(row):
                        return ['background-color:rgba(0, 255, 0, 0.25'] * len(row) if row["Class"] == CLASS  and row["Group ID"] == GROUP_ID else [''] * len(row)

                if selected_game_with_classes == "All":

                    st.subheader(ACADEMIC_YEAR)

                    leaderboard = fetch_and_compute_scores_for_year(ACADEMIC_YEAR, student=True)

                    if leaderboard:
                                            
                        leaderboard_with_position = [
                            {
                                "Class": row["team_class"],
                                "Group ID": row["team_id"],
                                "Score": row["average_score"],
                                "Position (Minimizer Role)": row["position_name_roles_1"],
                                "Score (Minimizer Role)": row["score_name_roles_1"],
                                "Position (Maximizer Role)": row["position_name_roles_2"],
                                "Score (Maximizer Role)": row["score_name_roles_2"],
                            }
                            for row in leaderboard
                        ]
                        
                        leaderboard_df = pd.DataFrame(
                            leaderboard_with_position, 
                            columns=[
                                "Class", 
                                "Group ID", 
                                "Score", 
                                "Position (Minimizer Role)",
                                "Score (Minimizer Role)",
                                "Position (Maximizer Role)",
                                "Score (Maximizer Role)"
                            ]
                        )

                        leaderboard_df["Score"] = leaderboard_df["Score"].round(2)
                        leaderboard_df["Score (Minimizer Role)"] = leaderboard_df["Score (Minimizer Role)"].round(2)
                        leaderboard_df["Score (Maximizer Role)"] = leaderboard_df["Score (Maximizer Role)"].round(2)

                        leaderboard_df.index = leaderboard_df.index + 1

                        st.dataframe(leaderboard_df.style.apply(color_coding, axis=1).format(precision=2), use_container_width=True)

                    else: st.write("Leaderboard not available yet.") 

                else:

                    st.subheader(selected_game_with_classes)

                    index_ = game_names_with_classes.index(selected_game_with_classes)-1

                    if games[index_]['available'] == 1:
                        leaderboard = fetch_and_compute_scores_for_year_game(games[index_]['game_id'])

                        if leaderboard:                         

                            leaderboard_with_position = [
                                {
                                    "Class": row["team_class"],
                                    "Group ID": row["team_id"],
                                    "Score": row["average_score"],
                                    "Position (Minimizer Role)": row["position_name_roles_1"],
                                    "Score (Minimizer Role)": row["score_name_roles_1"],
                                    "Position (Maximizer Role)": row["position_name_roles_2"],
                                    "Score (Maximizer Role)": row["score_name_roles_2"],
                                }
                                for row in leaderboard
                            ]

                            leaderboard_df = pd.DataFrame(
                                leaderboard_with_position, 
                                columns=[
                                    "Class", 
                                    "Group ID", 
                                    "Score", 
                                    "Position (Minimizer Role)",
                                    "Score (Minimizer Role)",
                                    "Position (Maximizer Role)",
                                    "Score (Maximizer Role)"
                                ]
                            )

                            leaderboard_df["Score"] = leaderboard_df["Score"].round(2)
                            leaderboard_df["Score (Minimizer Role)"] = leaderboard_df["Score (Minimizer Role)"].round(2)
                            leaderboard_df["Score (Maximizer Role)"] = leaderboard_df["Score (Maximizer Role)"].round(2)

                            leaderboard_df.index = leaderboard_df.index + 1

                            st.dataframe(leaderboard_df.style.apply(color_coding, axis=1).format(precision=2), use_container_width=True)

                    elif games[index_]['available'] == 0: st.write("Leaderboard not available yet.") 

            else: st.write('No games played yet.')

else:
    st.header("Profile")
    st.write("Please Login first.")
