import streamlit as st
import re
import time 
from datetime import datetime as dt
from modules.database_handler import fetch_current_games_data_by_user_id, get_group_id_from_user_id, get_game_access, get_round_data
from modules.drive_file_manager import get_text_from_file, overwrite_text_file, get_text_from_file_without_timestamp

# ------------------------ SET THE DEFAULT SESSION STATE FOR THE PLAY SECTION ---------------------------- #

# Initialize session state for show password form
if "show_game_password_form" not in st.session_state:
    st.session_state.show_game_password_form = True

# -------------------------------------------------------------------------------------------------------- #

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
        games = fetch_current_games_data_by_user_id('<', st.session_state.user_id)
        if games != []:

                    # Streamlit sidebar selectbox for games
                    game_names = [game['game_name'] for game in games]
                    selected_game_name = st.sidebar.selectbox("Select Game", game_names)

                    st.markdown(f'## {selected_game_name}')

                    # Find the selected game
                    selected_game = next((game for game in games if game['game_name'] == selected_game_name), None)

                    with st.expander("Explanation"):

                        # Retrieve the ID, professor ID and timestamp of the game
                        game_id = selected_game['game_id']
                        professor_id = selected_game['created_by']
                        game_timestamp = selected_game['timestamp_game_creation']
    
                        # Get the Game explanation from Google Drive using the filename
                        game_explanation = get_text_from_file_aux(f'{professor_id}_{game_id}_{game_timestamp}')
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

                        group_id = get_group_id_from_user_id(st.session_state['user_id'])
                        
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

        past_games = fetch_current_games_data_by_user_id('<', st.session_state.user_id) #should be '>'

        # If there are past games (in which the student took part)
        if past_games != []:
            past_game_names = [past_game['game_name'] for past_game in past_games]
            selected_past_game_name = st.sidebar.selectbox("Select Game", past_game_names)
            selected_past_game = next((game for game in past_games if game['game_name'] == selected_past_game_name), None)
             
            st.header(selected_past_game_name)

            group_id = get_group_id_from_user_id(st.session_state['user_id'])

            game_id = selected_past_game['game_id']
            professor_id = selected_past_game['created_by']
            game_timestamp = selected_past_game['timestamp_game_creation']

            submission = get_text_from_file_without_timestamp_aux(f'Game{game_id}_Group{group_id}') 

            # If negotiation chats of the game are already available to students
            if get_game_access(selected_past_game['game_id'])==1:
                
                round_data=get_round_data(selected_past_game['game_id'], get_group_id_from_user_id(st.session_state['user_id']))
  
                files_names=[]
                for i in range(len(round_data)):
                    round = round_data[i][0] 
                    team_1, team_2 =  round_data[i][1], round_data[i][2] 
                    if team_1 == get_group_id_from_user_id(st.session_state['user_id']):
                        files_names.append([round, team_2])
                    else: files_names.append([round, team_1])

                options = ['Buyer', 'Seller']
                selection = st.sidebar.radio(label= 'Select Your Position', options=options, horizontal=True)

                options_chat = [f'Round {i[0]} (vs Group {i[1]})' for i in files_names]
                chat_selector = st.sidebar.selectbox('Select Negotiation Chat', options_chat)

                with st.expander("Explanation"):
                    game_explanation = get_text_from_file_aux(f'{professor_id}_{game_id}_{game_timestamp}')
                    if game_explanation:
                        st.write(f"{game_explanation}")
                    else:
                        st.write("No explanation found for this game.")

                with st.expander("See your prompts"):
                    st.write(submission)

                st.markdown(f'### {chat_selector}')

                round_and_group = re.findall(r'\d+', chat_selector)
                round_and_group = list(map(int, round_and_group))   

                if selection == 'Buyer':
                    chat = get_text_from_file_aux(f'Game{game_id}_Round{round_and_group[0]}_Group{group_id}_Group{round_and_group[1]}')
                    st.write(chat)

                elif selection == 'Seller':
                    chat = get_text_from_file_aux(f'Game{game_id}_Round{round_and_group[0]}_Group{round_and_group[1]}_Group{group_id}')
                    st.write(chat)
    
            # If negotiation chats of the game are not yet available to students
            else: 
                st.write('Negotiation Chats are not available yet.')
                with st.expander("Explanation"):
                    game_explanation = get_text_from_file_aux(f'{professor_id}_{game_id}_{game_timestamp}')
                    if game_explanation:
                        st.write(f"{game_explanation}")
                    else:
                        st.write("No explanation found for this game.")
                    
                with st.expander("See your prompts"):
                    st.write(submission)

        # If there are not any past games (in which the student took part)
        else: 
            st.write('No past games to show.') 
        
else:
    st.write('Please Login first')
