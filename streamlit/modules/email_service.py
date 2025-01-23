import streamlit as st
import smtplib
import re
import jwt
import os
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from modules.database_handler import exists_user

MAIL = st.secrets["mail"]
MAIL_API_PASS = st.secrets["mail_api"]
APP_LINK = st.secrets["app_link"]

# Validate email format (lowercase only)
def valid_email(email):
    if any(char.isupper() for char in email):
        return False
    email_pattern = r'^[a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+$'
    return bool(re.match(email_pattern, email))

# Initiate set password
def set_password(email):
    if exists_user(email):
        set_password_link = generate_set_password_link(email)
        send_set_password_email(email, set_password_link)
        return True
    return False

# Send email with set password link
def send_set_password_email(email, set_password_link):
    message = MIMEMultipart()
    message['Subject'] = "Set Password Request"
    message['From'] = MAIL
    message['To'] = email
    body = MIMEText(f"Click here to set your password: {set_password_link}", 'plain')
    message.attach(body)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(MAIL, MAIL_API_PASS)
            server.sendmail(MAIL, email, message.as_string())
            print("Set password email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

# Secret key for JWT
SECRET_KEY = str(os.getenv("SECRET_KEY"))

base_url = APP_LINK

# Generate set password link with JWT
def generate_set_password_link(email):
    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    payload = {'email': email, 'exp': expiration_time}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    set_password_url = f"{base_url}?set_password={token}"
    return set_password_url
