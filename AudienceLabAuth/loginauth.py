import streamlit as st
import math
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
import dashboard

# Function to create a SQLite database
def create_database():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    # Create a Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Function to send emails
def send_email(to_email, subject, message):
    # Replace these with your email server details
    smtp_server = 'smtp.elasticemail.com'
    smtp_port = 2525
    smtp_username = 'ilesanmijohn99@gmail.com'
    smtp_password = 'CDB725781506AC8E74F43EE5555404C2045E'

    # Create an SMTP connection
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
    except Exception as e:
        st.error(f"Failed to connect to the email server: {e}")
        return

    # Create the email
    msg = MIMEText(message)
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject

    # Send the email
    try:
        server.sendmail(smtp_username, to_email, msg.as_string())
        st.success(f"Email sent successfully to {to_email}")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

    # Close the SMTP connection
    server.quit()

# Streamlit App
def main():
    create_database()  # Create the SQLite database

    st.title("AudienceLab Partners")
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        
    if st.session_state.logged_in:
        dashboard.main()
        
    else:
        # Use st.sidebar to create a sidebar
        with st.sidebar:
            st.header("Sign Up")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.button("Sign Up"):
                # Store user data in the database
                conn = sqlite3.connect('user_data.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                           (first_name, last_name, email, password))
                conn.commit()
                conn.close()

                # Send welcome email
                welcome_subject = "Welcome!!!"
                welcome_message = f"Dear {first_name},\n\nYou are welcome to this platform.\n\n****PLEASE NOTE: DO NOT REPLY. THIS IS AN AUTO-GENERATED EMAIL****\n\nBest regards,\n\nIT Team"
                send_email(email, welcome_subject, welcome_message)
                st.success("Sign up successful. Welcome email sent!")

        # User login
        st.header("Login")
        login_email = st.text_input("Email", key="email_input")
        login_password = st.text_input("Password", type="password", key="password_input")
        if st.button("Login"):
            conn = sqlite3.connect('user_data.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE email = ? AND password = ?", (login_email, login_password))
            user = cursor.fetchone()
            conn.close()

            if user:
                st.success("Login successful")
                # Add your dashboard here  
                st.session_state.logged_in = True
            
                st.experimental_set_query_params(logged_in=True)
                dashboard.main()   
            else:
                st.error("Login failed. Please check your credentials.")

        # Forgot password functionality
        if st.button("Forgot Password"):
            forgot_email = st.text_input("Enter your email")
            reset_code = str(random.randint(1000, 9999))

            # Update the database with the reset code (you can use a separate table for this)
            conn = sqlite3.connect('user_data.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE Users SET reset_code = ? WHERE email = ?", (reset_code, forgot_email))
            conn.commit()
            conn.close()

            # Send reset email
            reset_subject = "Password Reset Code"
            reset_message = f"Your password reset code is: {reset_code}\n\nPlease use this code to reset your password."
            send_email(forgot_email, reset_subject, reset_message)
            st.success("Password reset code sent to your email.")

if __name__ == "__main__":
    st.markdown("<style>body {background-color: lightSkyBlue;}</style>", unsafe_allow_html=True)
    main()
