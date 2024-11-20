import streamlit as st

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

    st.markdown("# Play")

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

else:
    st.write(
        """Please Login first"""
    )