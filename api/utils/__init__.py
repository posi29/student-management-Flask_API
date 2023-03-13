from flask_sqlalchemy import SQLAlchemy
import string
import secrets





db = SQLAlchemy()




def random_char(length):
    """ Generate a random string 
    param:
        length : length of string to be generated"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))


password='evctrejhhdkghsmy'
sender_email='olujas1@gmail.com' 