import firebase_admin
from firebase_admin import credentials, firestore, initialize_app, storage, auth
from dotenv import load_dotenv
import requests
import json
import os
import io

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

cred = credentials.Certificate(str(os.getenv('CERT_PATH')))
firebase_admin.initialize_app(cred, {
    'storageBucket': 'redbook-910e9.appspot.com'
})
db = firestore.client()

def sign_up_with_email_password(email, password):
    """Create a new user with email and password."""
    try:
        user = auth.create_user(email=email, password=password)
        print('Successfully created new user:', user.uid)

        #create a new document in the accounts collection
        doc_ref = db.collection('accounts').document(user.uid)
        doc_ref.set({
            'answered': [],
            'answeredCorrectly': [],
            'answeredIncorrectly': []
        })

        return user.uid
    except Exception as e:
        print('Error creating new user:', e)
        return None
    
sign_up_with_email_password('user@redbook.com', 'password')