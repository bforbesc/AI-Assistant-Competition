import streamlit as st
import hashlib
import time
from modules.database_handler import authenticate_user, is_professor

st.markdown("# Login")

# Username and Password Input
email = st.text_input("Email")
password = st.text_input("Password", type="password")
login_button = st.button("Login")

if login_button:
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if authenticate_user(email, hashed_password):  # Custom function to check against DB
        st.session_state['authenticated'] = True
        st.success("Login successful!")
        # Redirect to the Home page (but without query parameters)
        time.sleep(2)
        if is_professor(email):
            st.session_state['professor'] = True
        else:
            st.session_state['professor'] = False
        st.switch_page("0_Home.py")
    else:
        st.error("Invalid email or password")

# Sign-up Link
st.write("Not yet signed in? [Sign Up](../SignUp)")
