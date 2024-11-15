import smtplib
import re
import jwt
import os
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from modules.database_handler import get_user_by_email

# Validate email format (lowercase only)
def valid_email(email):
    if any(char.isupper() for char in email):
        return False
    email_pattern = r'^[a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+$'
    return bool(re.match(email_pattern, email))

# Send OTP email
def send_otp_email(email, otp):
    subject = "Your One-Time Password (OTP)"
    body = f"Your OTP is {otp}. Please use this to complete your login or registration."
    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = "ricardo.almeida2210@gmail.com"
    message['To'] = email
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login("ricardo.almeida2210@gmail.com", "zbqv zxft zmub qtru")
            server.sendmail("ricardo.almeida2210@gmail.com", email, message.as_string())
        print("OTP email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")
    
    return otp

# Initiate password reset
def reset_password(email):
    if get_user_by_email(email):
        reset_link = generate_reset_link(email)
        send_reset_email(email, reset_link)
        return True
    return False

# Send reset email with reset link
def send_reset_email(email, reset_link):
    message = MIMEMultipart()
    message['Subject'] = "Password Reset Request"
    message['From'] = 'ricardo.almeida2210@gmail.com'
    message['To'] = email
    body = MIMEText(f"Click here to reset your password: {reset_link}", 'plain')
    message.attach(body)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login("ricardo.almeida2210@gmail.com", "zbqv zxft zmub qtru")
            server.sendmail("ricardo.almeida2210@gmail.com", email, message.as_string())
            print("Reset email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")

# Secret key for JWT
SECRET_KEY = str(os.getenv("SECRET_KEY"))

base_url = "http://localhost:8501"

# Generate password reset link with JWT
def generate_reset_link(email):
    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    payload = {'email': email, 'exp': expiration_time}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    reset_url = f"{base_url}?reset={token}"
    return reset_url