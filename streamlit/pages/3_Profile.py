import streamlit as st

# Check if the user is logged in
if st.session_state['authenticated']:

    st.markdown("# Profile")

    options = ['Agent History', 'Statistics', 'Personal Data']
    selection = st.segmented_control(label= 'a', options=options, selection_mode="single", label_visibility ='collapsed', default='Agent History')

else:
    st.write(
        """Please Login or Sign Up first"""
    )