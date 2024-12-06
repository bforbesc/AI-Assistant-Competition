import streamlit as st
import time

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
            st.switch_page("0_Home.py")

    st.markdown("# About")
    st.write(
        """This is the about page of the app where we will provide deeper insights into how the app works,
        offer references, and share information about the authors."""
    )

else:
    st.write(
        """Please Login first"""
    )