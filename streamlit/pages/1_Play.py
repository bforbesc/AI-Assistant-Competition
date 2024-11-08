import streamlit as st

#import autogen

col1, col2= st.columns([6,1])  
with col2:
    sign_out = st.button('Sign Out')

st.markdown("# Play")
st.sidebar.header("Play")

if 'click' not in st.session_state:
    st.session_state.click = False

if 'start' not in st.session_state:
    st.session_state.start = False

def onClickFunction():
    st.session_state.click = True

def onStartFunction():
    st.session_state.start = True
def offClickFunction():
    st.session_state.click = False
    st.session_state.start = False

game_mode = st.sidebar.radio(
    "Choose you game mode",
    ['In class', 'Out of class'],
    captions=['Professor required to initialize game', 'Professor **not** required to initialize game'],
    horizontal=False
)

if game_mode == 'Out of class':
    option = st.sidebar.selectbox(
        "Which negotiation game would you like to play?",
        ("Ultimatum Game", "Prisoner’s Dilemma"),
    )

    st.markdown(f'## {option}')
    with st.expander("Explanation"):
        st.write(f'Here an explanation of {option} will be provided.')

    start = st.button('Start', on_click=onStartFunction, disabled= st.session_state.start)

    if st.session_state.start:

        txt = st.text_area('Input', label_visibility='collapsed', disabled = st.session_state.click)

        submit = st.button('Submit', disabled = len(txt)==0 or st.session_state.click, on_click = onClickFunction) 
    
        if txt and st.session_state.click:
            choice = st.checkbox('Save Chat')
            finish = st.button('Finish', on_click = offClickFunction, disabled = not st.session_state.click)
