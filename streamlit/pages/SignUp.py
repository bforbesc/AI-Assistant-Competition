import streamlit as st
import random
import hashlib
import time
from modules.email_service import send_otp_email
from modules.database_handler import update_professor, is_valid_professor_email

st.markdown("# Sign Up")

# Email Verification Step
email = st.text_input("Enter your Professor Email")
username = st.text_input("Enter your Username")
request_otp = st.button("Request OTP")

if request_otp:
    if is_valid_professor_email(email):
        otp = str(random.randint(100000, 999999))
        st.session_state['otp'] = otp
        st.session_state['email'] = email
        send_otp_email(email, otp)
        st.success("OTP sent! Please check your email.")
    else:
        st.error("Invalid email! Only registered professor emails are allowed.")

# OTP and New Password Input
otp_input = st.text_input("Enter OTP")
new_password = st.text_input("Enter New Password", type="password")
confirm_password = st.text_input("Confirm New Password", type="password")
submit_button = st.button("Submit")

if submit_button:
    if otp_input == st.session_state.get('otp') and new_password == confirm_password:
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        if update_professor(username, email, hashed_password):
            # Display success message and countdown before redirect
            st.success("Registration successful! Redirecting to Login page")
            del st.session_state['otp']
            del st.session_state['email']
            time.sleep(2)
            
            st.switch_page("pages/Login.py")
        else:
            st.error("Registration failed. Please try again.")
    else:
        st.error("Invalid OTP or passwords do not match.")
