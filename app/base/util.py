# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
 
import hashlib, binascii, os
import smtplib 
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Inspiration -> https://www.vitoshacademy.com/hashing-passwords-in-python/

def hash_pass( password ):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash) # return bytes

def verify_pass(provided_password, stored_password):
    """Verify a stored password against one provided by user"""
    stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', 
                                  provided_password.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def send_email(subject,recipientemail):
    SENDER = 'falstoop@gmail.com' 
    SENDER_FROM = 'falstoop@gmail.com' 
    SENDERNAME = 'kaardio' 
    RECIPIENT = recipientemail 
    #CONFIGURATION_SET = "ConfigSet"
    USERNAME_SMTP = "AKIA2S6RSX5CLGX6AS4Q" 
    PASSWORD_SMTP = "BDkIWDCIaN3LCzo8W2VEa06alCrI5Hz7ZU/dgBnhchlg" 
    HOST = "email-smtp.us-east-1.amazonaws.com"
    PORT = "587"
    # The subject line of the email.
    SUBJECT = subject
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Email Test")

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
    msg['To'] = RECIPIENT
    # Comment or delete the next line if you are not using a configuration set
    #msg.add_header('X-SES-CONFIGURATION-SET',CONFIGURATION_SET)

    # Try to send the message.
    try:  
        server = smtplib.SMTP(HOST, PORT)
        server.ehlo()
        server.starttls()
        #stmplib docs recommend calling ehlo() before & after starttls()
        server.ehlo()
        server.login(USERNAME_SMTP, PASSWORD_SMTP)
        server.sendmail(SENDER, RECIPIENT, msg.as_string())
        server.close()
    # Display an error message if something goes wrong.
    except Exception as e:
        print ("Error: ", e)
    else:
        print ("Email sent!")
