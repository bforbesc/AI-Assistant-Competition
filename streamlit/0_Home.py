import streamlit as st
#import streamlit_authenticator as stauth

col1, col2= st.columns([6,1])  
with col2:
    sign_out = st.button('Sign Out')

st.markdown("# AI Assistant Competition")
st.sidebar.header("AI Assistant Competition")
st.write(
    """This is the home page of the app where we will briefly explain what is consists of."""
)
