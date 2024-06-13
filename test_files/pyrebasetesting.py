import pyrebase
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'apiKey': os.getenv('APIKEY'),
    'authDomain': os.getenv('AUTHDOMAIN'),
    'projectId': os.getenv('PROJECT_ID'),
    'storageBucket': os.getenv('STORAGE_BUCKET'),
    'messagingSenderId': os.getenv('MESSAGING_SENDER_ID'),
    'appId': os.getenv('APP_ID'),
    'measurementId': os.getenv('MEASUREMENT_ID'),
    'databaseURL': os.getenv('DATABASE_URL')
}

firebase = pyrebase.initialize_app(config)

auth = firebase.auth()
database = firebase.database()
storage = firebase.storage()

user = auth.sign_in_with_email_and_password("test@gmail.com", "test123")
print(database.child('accounts').child("test").get().val())
# DOESNT WORK???? WHYY
# SCREW PYREBASE4