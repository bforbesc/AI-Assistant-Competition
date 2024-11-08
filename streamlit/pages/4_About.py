import streamlit as st

col1, col2= st.columns([6,1])  
with col2:
    sign_out = st.button('Sign Out')

st.markdown("# About")
st.sidebar.header("About")
st.write(
    """This is the about page of the app where we will provide deeper insights into how the app works,
     offer references, and share information about the authors."""
)