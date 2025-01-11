import streamlit as st
import hashlib
import time
import jwt
import os
from modules.database_handler import authenticate_user, is_professor, update_password, get_user_id_by_email
from modules.email_service import valid_email, set_password

# Initialize session state variables if they are not already defined
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if 'professor' not in st.session_state:
    st.session_state['professor'] = False

if 'set_password_email' not in st.session_state:
    st.session_state['set_password_email'] = ""

if 'login_email' not in st.session_state:
    st.session_state['login_email'] = ""

if 'login_password' not in st.session_state:
    st.session_state['login_password'] = ""

if 'show_set_password_form' not in st.session_state:
    st.session_state['show_set_password_form'] = False

if 'user_id' not in st.session_state:
    st.session_state['user_id'] = ""

# Get query parameters (like ?set_password=token)
query_params = st.query_params

# Check if 'set_password' exists in query params and set session state to True
if 'show_set_password_form' in query_params:
    st.session_state['show_set_password_form'] = True

# Main login section if the user is not logged in
if not st.session_state['authenticated']:

    # Set session state value for email if not already set
    if 'login_email' not in st.session_state:
        st.session_state['login_email'] = ''  # or some default value

    st.markdown("# Login")
    
    # Input fields for email and password
    email = st.text_input("Email", value=st.session_state['login_email'])
    password = st.text_input("Password", type="password", value=st.session_state['login_password'])

    # Create columns to place the buttons
    col1, col2 = st.columns([5, 1])
    
    with col1:
        # Login button on the left
        login_button = st.button("Login", key="login_button")
    
    with col2:
        # Set password link that reloads the page with show_set_password_form=true
        st.markdown(
            "<a href='?show_set_password_form=true'>Set Password</a>",
            unsafe_allow_html=True
        )

    # If login button is pressed
    if login_button:
        # Hash password before authentication
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Authenticate user
        if authenticate_user(email, hashed_password):
            st.session_state['login_email'] = email
            st.session_state['login_password'] = password
            st.success("Login successful!")
            time.sleep(2)
            # Check if user is a professor
            st.session_state['professor'] = is_professor(email)
            st.session_state['authenticated'] = True
            user_id = get_user_id_by_email(email)  # Default to empty if no user_id is found
            st.session_state.update({'user_id': user_id})
            st.rerun()  # Rerun the page after successful login
        else:
            st.error("Invalid email or password")

    # Set password section
    if st.session_state.get('show_set_password_form'):
        st.markdown("# Set Password")

        set_password_email = st.text_input("Enter your email address", key="set_password_email", value=st.session_state['set_password_email'])

        set_password_button = st.button("Set the Password")

        if set_password_button:
            if valid_email(st.session_state['set_password_email']):
                if set_password(st.session_state['set_password_email']):
                    st.success("Set password link has been sent to your email!")
                else:
                    st.error("Email not found. Please check your email and try again.")
            else:
                st.error("Please enter a valid email address.")


    # Handling set password from the link
    SECRET_KEY = str(os.getenv("SECRET_KEY"))

    # Check if there's a set_password token in query parameters
    if 'set_password' in query_params:
        st.markdown("# Set Password")
        token = query_params['set_password']
        if token.startswith("b'") and token.endswith("'"):
            token = token[2:-1]  # Clean token format

        try:
            # Decode the JWT token
            decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            st.session_state['set_password_email'] = decoded_payload.get('email', '')

            # Input fields for new password and confirmation
            password = st.text_input("Enter Password", type="password")
            confirm_password = st.text_input("Confirm your Password", type="password")
            set_password_button = st.button("Set Password", key="set_password_button")

            # When the set password button is clicked
            if set_password_button:
                if password and confirm_password:
                    if password == confirm_password:
                        # Check if password is strong
                        if (len(password) >= 8 and
                            any(char.isupper() for char in password) and
                            any(char.islower() for char in password) and
                            any(char.isdigit() for char in password) and
                            any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?/`~' for char in password)):

                            # Hash and update password if strong
                            hashed_password = hashlib.sha256(password.encode()).hexdigest()
                            if update_password(st.session_state['set_password_email'], hashed_password):
                                st.success("Password successfully set!")
                                time.sleep(2)
                                st.switch_page("0_Home.py")
                            else:
                                st.error("Failed to set password.")
                        else:
                            st.error("Password must be at least 8 characters long and include an uppercase letter, \
                                     a lowercase letter, a number, and a special character.")
                    else:
                        st.error("Passwords do not match. Please try again.")
                else:
                    st.error("Please fill in both password fields.")
        except jwt.ExpiredSignatureError:
            st.error("The set password link has expired. Please request a new one.")
        except jwt.InvalidTokenError:
            st.error("Invalid set password link. Please check the link and try again.")

else:
    # If the user is logged in, we provide the following content

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

    st.write("""This is the home page of the app where we will briefly explain what it consists of.""")