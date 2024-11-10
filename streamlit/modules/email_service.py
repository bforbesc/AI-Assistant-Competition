import smtplib
from email.mime.text import MIMEText
import random
import string

# Send the OTP email
def send_otp_email(email, otp):
    # Define email content
    subject = "Your One-Time Password (OTP)"
    body = f"Your OTP is {otp}. Please use this to complete your login or registration."
    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = "ricardo.almeida2210@gmail.com"
    message['To'] = email
    
    try:
        # Set up the server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Enable TLS for security
            server.login("ricardo.almeida2210@gmail.com", "gfbjimqgcqlekigg")
            server.sendmail("ricardo.almeida2210@gmail.com", email, message.as_string())  # Send email
            
        print("OTP email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")
    
    return otp  # Return OTP to save in the database/session
