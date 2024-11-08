import streamlit as st

col1, col2= st.columns([6,1])  
with col2:
    sign_out = st.button('Sign Out')

st.markdown("# Profile")
st.sidebar.header("Profile")

options = ['Agent History', 'Statistics', 'Personal Data']
selection = st.segmented_control(label= 'a', options=options, selection_mode="single", label_visibility ='collapsed', default='Agent History')