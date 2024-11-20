import streamlit as st
import hashlib
import time
from modules.database_handler import update_password, get_userID_by_email

# Initialize session state for buttons if not set
if 'password_edit_mode' not in st.session_state:
    st.session_state['password_edit_mode'] = False

if 'userID' not in st.session_state:
    st.session_state['userID'] = ""

if 'show_password' not in st.session_state:
    st.session_state['show_password'] = False  # Track password visibility state

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
            st.switch_page("0_Home.py")  # Redirect to home page

    st.markdown("# Profile")

    options = ['Agent History', 'Statistics', 'Personal Data']
    selection = st.selectbox('Select an option', options)

    if selection == 'Personal Data':
        # Display email
        email = st.session_state['login_email']
        
        st.markdown(f"<h3 style='font-size: 24px;'>Email</h3>", unsafe_allow_html=True)
        st.write(f"{email}")
        # Display userID
        st.markdown(f"<h3 style='font-size: 24px;'>userID</h3>", unsafe_allow_html=True)
        # col1, col2, _, _, _, _, _ = st.columns([4, 1, 1, 1, 1, 1, 1])  # Adjusted to align with password layout
        # with col1:
        userID = get_userID_by_email(email)  # Default to empty if no userID is found

        # Display password with eye and edit pencil buttons
        st.markdown(f"<h3 style='font-size: 24px;'>Password</h3>", unsafe_allow_html=True)
        col1, col2, _, _, _, _, _ = st.columns([4, 1, 1, 1, 1, 1, 1])  # Same structure as the userID for vertical alignment
        with col1:
            password = st.session_state.get('login_password', '')
            if st.session_state['show_password']:
                st.write(f"{password if password else 'Not defined'}")
            else:
                st.text('*******' if password else 'Not defined')

        with col2:
            # Align eye and pencil buttons within the same column
            col_eye, col_pencil = st.columns([6, 1])
            with col_eye:
                if st.button("👁️", key="toggle_password"):
                    st.session_state['show_password'] = not st.session_state['show_password']  # Toggle visibility state
            with col_pencil:
                if st.button("✏️", key="edit_password"):
                    st.session_state['password_edit_mode'] = True  # Set to True when clicked

        # Show form for editing password if in edit mode
        if st.session_state['password_edit_mode']:
            with st.form(key="password_form"):
                new_password = st.text_input("Enter new password", type="password", key="new_password_input")
                confirm_password = st.text_input("Confirm new password", type="password", key="confirm_password_input")
                update_password_btn = st.form_submit_button("Update Password")

                if update_password_btn:
                    if new_password and confirm_password:
                        if new_password == confirm_password:
                            # Check if password is strong
                            if (len(new_password) >= 8 and
                                any(char.isupper() for char in new_password) and
                                any(char.islower() for char in new_password) and
                                any(char.isdigit() for char in new_password) and
                                any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?/`~' for char in new_password)):

                                # Hash and update password if strong
                                hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

                                if update_password(userID, hashed_password):
                                    st.success("Password updated successfully!")
                                    st.session_state['login_password'] = new_password  # Update session state password
                                    st.session_state['password_edit_mode'] = False  # Reset edit mode
                                    time.sleep(2)
                                    st.rerun()  # Rerun to reset the page
                                else:
                                    st.error("Failed to update password.")
                            else:
                                st.error("Password must be at least 8 characters long and include an uppercase letter, \
                                         a lowercase letter, a number, and a special character.")
                        else:
                            st.error("Passwords do not match.")
                    else:
                        st.error("Please fill in both password fields.")

else:
    st.write("Please Login first.")
