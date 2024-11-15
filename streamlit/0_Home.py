import streamlit as st
import hashlib
import time
import jwt
import os
from modules.database_handler import authenticate_user, is_professor, update_password
from modules.email_service import valid_email, reset_password

# Initialize session state variables if they are not already defined
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'professor' not in st.session_state:
    st.session_state['professor'] = False

if 'reset_password' not in st.session_state:
    st.session_state['reset_password'] = False

if 'reset_email' not in st.session_state:
    st.session_state['reset_email'] = ""

if 'login_email' not in st.session_state:
    st.session_state['login_email'] = ""

if 'login_password' not in st.session_state:
    st.session_state['login_password'] = ""

if 'reset_link' not in st.session_state:
    st.session_state['reset_link'] = False

if 'login' not in st.session_state:
    st.session_state['login'] = False

if 'show_reset_form' not in st.session_state:
    st.session_state['show_reset_form'] = False

# Get query parameters (like ?reset=token)
query_params = st.query_params

# Check if 'show_reset_form' exists in query params and set session state to True
if 'show_reset_form' in query_params:
    st.session_state['show_reset_form'] = True

# Main login section if the user is not logged in
if not st.session_state.get('login'):
    st.markdown("# Login")
    
    # Input fields for email and password
    email = st.text_input("Email", key="login_email", value=st.session_state['login_email'])
    password = st.text_input("Password", type="password", key="login_password", value=st.session_state['login_password'])

    # Create columns to place the buttons
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Login button on the left
        login_button = st.button("Login", key="login_button")
    
    with col2:
        # Forgot password link that reloads the page with show_reset_form=true
        st.markdown(
            "<a href='?show_reset_form=true'>Forgot your password?</a>",
            unsafe_allow_html=True
        )

    # If login button is pressed
    if login_button:
        # Hash password before authentication
        hashed_password = hashlib.sha256(st.session_state['login_password'].encode()).hexdigest()
        
        # Authenticate user
        if authenticate_user(st.session_state['login_email'], hashed_password):
            st.session_state['authenticated'] = True
            st.success("Login successful!")
            time.sleep(2)
            # Check if user is a professor
            st.session_state['professor'] = is_professor(st.session_state['login_email'])
            st.session_state['login'] = True
            st.rerun()  # Rerun the page after successful login
        else:
            st.error("Invalid email or password")


    # Password reset section
    if st.session_state.get('show_reset_form'):
        # Show reset form when 'show_reset_form' is True
        st.markdown("# Reset Password")
        st.write("Please enter your email to reset your password.")
        reset_email = st.text_input("Enter your email address", key="reset_email", value=st.session_state['reset_email'])
        submit_reset = st.button("Reset the Password")

        # When reset password is submitted
        if submit_reset:
            if valid_email(st.session_state['reset_email']):
                if reset_password(st.session_state['reset_email']):
                    st.success("Password reset link has been sent to your email!")
                else:
                    st.error("Email not found. Please check your email and try again.")
            else:
                st.error("Please enter a valid email address.")


    # Handling password reset from the link
    SECRET_KEY = str(os.getenv("SECRET_KEY"))

    # Check if there's a reset token in query parameters
    if 'reset' in query_params:
        st.markdown("# New Password")
        token = query_params['reset']
        if token.startswith("b'") and token.endswith("'"):
            token = token[2:-1]  # Clean token format

        try:
            # Decode the JWT token
            decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            st.session_state['reset_email'] = decoded_payload.get('email', '')

            # Input fields for new password and confirmation
            new_password = st.text_input("Enter your new Password", type="password")
            confirm_password = st.text_input("Confirm your new Password", type="password")
            change_password_button = st.button("Change Password", key="change_password_button")

            # When the change password button is clicked
            if change_password_button:
                if new_password and confirm_password:
                    if new_password == confirm_password:
                        # Hash new password and update it
                        hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
                        if update_password(st.session_state['reset_email'], hashed_new_password):
                            st.success("Password successfully changed!")
                            time.sleep(2)
                            st.switch_page("0_Home.py")  # Redirect to home page
                        else:
                            st.error("An error occurred while updating the password.")
                    else:
                        st.error("Passwords do not match. Please try again.")
                else:
                    st.error("Please fill in both password fields.")
        except jwt.ExpiredSignatureError:
            st.error("The reset link has expired. Please request a new one.")
        except jwt.InvalidTokenError:
            st.error("Invalid reset link. Please check the link and try again.")

else:
    # If the user is logged in, we provide the following content
    st.write("""This is the home page of the app where we will briefly explain what it consists of.""")