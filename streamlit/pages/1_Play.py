import streamlit as st
import time 
from datetime import datetime as dt
from modules.database_handler import fetch_current_games_data_by_userID, get_professor_id_from_game_id, get_group_id_from_game_id_and_user_id
from modules.drive_file_manager import get_text_from_file, overwrite_text_file

# ------------------------ SET THE DEFAULT SESSION STATE FOR THE PLAY SECTION ---------------------------- #

# Initialize session state for show password form
if "show_game_password_form" not in st.session_state:
    st.session_state.show_game_password_form = True

# -------------------------------------------------------------------------------------------------------- #

@st.cache_resource
def get_text_from_file_aux(professor_id, game_id, timestamp):
    text = get_text_from_file(f"{professor_id}_{game_id}_{timestamp}.txt")
    return text

# Check if the user is authenticated
if st.session_state['authenticated']:

    col1, _, col3 = st.columns([2, 8, 2])
    with col3:
        # Sign out button
        sign_out_btn = st.button("Sign Out", key="sign_out", use_container_width=True)

        if sign_out_btn:
            st.session_state.update({'authenticated': False})
            st.session_state.update({'login_email': ""})
            st.session_state.update({'login_password': ""})
            st.session_state.show_game_password_form = True
            time.sleep(2)
            st.switch_page("0_Home.py")  # Redirect to home page
    
    option = st.sidebar.radio("See:", ('Current Games', 'Past Games'),horizontal=True)

    # Fetch the list of games from the database
    if option == 'Current Games':
        games = fetch_current_games_data_by_userID('<', st.session_state.userID)
        if games != []:

                    # Streamlit sidebar selectbox for games
                    game_names = [game['game_name'] for game in games]
                    selected_game_name = st.sidebar.selectbox("Select Game", game_names)

                    st.markdown(f'## {selected_game_name}')

                    # Find the selected game
                    selected_game = next((game for game in games if game['game_name'] == selected_game_name), None)

                    with st.expander("Explanation"):

                        # Retrieve the game ID and professor ID of the game
                        game_id = selected_game['game_id']
                        professor_id = get_professor_id_from_game_id(game_id)
    
                        # Get the Game explanation from Google Drive using the filename
                        game_explanation = get_text_from_file_aux(professor_id, game_id, selected_game['timestamp_game_creation'])
                        if game_explanation:
                            st.write(f"{game_explanation}")
                        else:
                            st.write("No explanation found for this game.")

                    with st.expander("Submission Deadline"):
                        st.write(f"{selected_game['timestamp_submission_deadline']}")

                    if st.session_state.show_game_password_form == True:
                        with st.form("insert_password_form"):
                            st.write("Please introduce the Password to play this Game.")
                            password_input = st.text_input("Enter the Game Password", type="password", key="game_password_input")
                            
                            play_now_btn = st.form_submit_button("Play now!")

                            if play_now_btn:
                                if selected_game['password'] == password_input:
                                    st.success("Correct Password.")
                                    st.session_state.show_game_password_form = False
                                    time.sleep(2)
                                    st.rerun()

                                else:
                                    st.error("Incorrect Password. Please try again.")
                            
                    if st.session_state.show_game_password_form == False:

                        st.write('')

                        group_id = get_group_id_from_game_id_and_user_id(game_id, st.session_state['userID'])
                        
                        # Case where number of inputs is 1
                        if selected_game['num_inputs']==1:
                            with st.form(key='form_1_input'):
                                text_area = st.text_area('Your Prompt', help='A good prompt should be clear, specific, and provide enough context and detail about your position, interests, and desired outcomes.')
                                submit_button = st.form_submit_button('Submit')

                            if submit_button:
                                prompt = text_area
                                overwrite_text_file(prompt, f"Game{game_id}_Group{group_id}_{dt.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                success = st.success('Submission Successful')
                                time.sleep(3)
                                success.empty()

                        # Case where number of inputs is 2
                        if selected_game['num_inputs']==2:
                            text_inputs = []
                            
                            with st.form(key='form_2_inputs'):
                                text_area_1 = st.text_area('Buyer Prompt', help='A good prompt should be clear, specific, and provide enough context and detail about your position, interests, and desired outcomes.')
                                text_area_2 = st.text_area('Seller Prompt')
                                submit_button = st.form_submit_button('Submit')

                            roles = ['Buyer: ', 'Seller: ']

                            if submit_button:
                                text_inputs.extend([text_area_1, text_area_2])
                                prompts = ''
                                for i in range(2):
                                    prompts += roles[i] + text_inputs[i] + '\n\n'
                                overwrite_text_file(prompts, f"Game{game_id}_Group{group_id}_{dt.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                success = st.success('Submission Successful')
                                time.sleep(3)
                                success.empty()

        else:
            st.write("There are no available games.")

    if option == 'Past Games':
        st.header('Past Games')
        past_games = fetch_current_games_data_by_userID('>', st.session_state.userID)
        if past_games != []:
            past_game_names = [past_game['game_name'] for past_game in past_games]
            selected_past_game = st.sidebar.selectbox("Select Game", past_game_names)

        else: st.write('No past games to show.') 
        
else:
    st.write("""Please Login first""")
