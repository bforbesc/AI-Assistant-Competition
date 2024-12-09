import streamlit as st
import time
from modules.database_handler import fetch_games_data
from modules.drive_file_manager import get_text_from_file

# ------------------------ SET THE DEFAULT SESSION STATE FOR THE PLAY SECTION ---------------------------- #

# Initialize session state for game selection
if "game_selection" not in st.session_state:
    st.session_state.game_selection = "Select a Game"

# Initialize session state for show game
if "show_game" not in st.session_state:
    st.session_state.show_game = 0

# Initialize session state for back button
if "back_button" not in st.session_state:
    st.session_state.back_button = False

# Initialize session state for show password form
if "show_password_form" not in st.session_state:
    st.session_state.show_password_form = False

# -------------------------------------------------------------------------------------------------------- #

# Check if the user is authenticated
if st.session_state['authenticated']:

    col1, _, col3 = st.columns([2, 8, 2])
    with col1:
        if st.session_state.back_button:
            # Back button
            if st.button("⬅ Back"):
                if st.session_state.show_game:
                    st.session_state.show_password_form = False
                    st.session_state.show_game = False
                else:
                    st.session_state.back_button = False
                    st.session_state.game_selection = "Select a Game"
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

    # Fetch the list of games from the database
    games = fetch_games_data()

    if games != []:
        if not st.session_state.show_game:
            if st.session_state.game_selection == "Select a Game":

                st.header("Select a Game")

                # Streamlit sidebar selectbox for games
                game_names = [game['game_name'] for game in games]
                # Action selection dropdown
                c1, _ = st.columns([3, 2])
                selected_game_name = c1.selectbox("Select a Game", game_names)

                if st.button("Show"):
                    st.session_state.back_button = True
                    st.session_state.game_selection = selected_game_name
                    st.rerun()
            else:
                st.markdown(f'## {st.session_state.game_selection}')
                with st.expander("Explanation"):
                    #st.write(f'Here an explanation of {selected_game_name} will be provided.')

                    # Find the selected game
                    selected_game = next((game for game in games if game['game_name'] == st.session_state.game_selection), None)

                    # Retrieve user ID from session state
                    user_id = st.session_state.get('userID')

                    # Get the Game explanation from Google Drive using the filename
                    game_explanation = get_text_from_file(f"{user_id}_{selected_game['game_id']}_{selected_game['timestamp_game_creation']}.txt")
                    if game_explanation:
                        st.write(f"{game_explanation}")
                    else:
                        st.write("No explanation found for this game.")
                with st.expander("Game details"):
                    st.write(f"**Number of Rounds**: {selected_game['number_of_rounds']}")
                    st.write(f"**Number of Inputs**: {selected_game['num_inputs']}")

                with st.expander("Submission Deadline"):
                    st.write(f"{selected_game['timestamp_submission_deadline']}")

                if st.button("Play"):
                    st.session_state.show_password_form = True

                if st.session_state.show_password_form:
                    with st.form("insert_password_form"):
                        st.write("Please introduce the Password to play this Game.")
                        password_input = st.text_input("Enter the Game Password", type="password", key="game_password_input")
                        
                        play_now_btn = st.form_submit_button("Play now!")

                        if play_now_btn:
                            if selected_game['password'] == password_input:
                                st.success("Correct Password.")
                                st.session_state.show_game = selected_game['game_id']
                                st.session_state.back_button = True

                            else:
                                st.error("Incorrect Password. Please try again.")
                            time.sleep(2)
                            st.rerun()
        else:
            st.write("Show game :)")
    else:
        st.write("There are no available games.")

else:
    st.write(
        """Please Login first"""
    )