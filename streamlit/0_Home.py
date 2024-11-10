import streamlit as st

# Initialize authenticated state if not already in session
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False  # Default to False (not logged in)

# Initialize professor state if not already in session
if 'professor' not in st.session_state:
    st.session_state['professor'] = False

st.markdown("# AI Assistant Competition")
st.sidebar.header("AI Assistant Competition")
st.write(
    """This is the home page of the app where we will briefly explain what is consists of."""
)
