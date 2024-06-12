import pyrebase
from firebase_admin import credentials, firestore, initialize_app
import firebase_admin
import json
import os

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


cred = credentials.Certificate('redbook-910e9-firebase-adminsdk-hzs4e-a467f4cf29.json')
firebase_admin.initialize_app(cred)
# firebase = pyrebase.initialize_app(config)



# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'redbook-910e9.appspot.com'
# })

# firebase_admin.initialize_app(cred, {
#     'databaseURL': "https:///redbook-910e9.web.app"
# })

# db = firebase.database()

# email = "test@gmail.com"
# password = "test123"

#user = auth.create_user_with_email_and_password(email, password)
#print(user)

# user = auth.sign_in_with_email_and_password(email, password)

# info = auth.get_account_info(user['idToken'])
# print(info)
db = firestore.client()

document_id = 'VaQIZzpBplPRuHV9KQzW8kJDJ2f2'
# document_id = 'test'

# Get the document with the specific ID from the accounts collection
doc = db.collection('accounts').document(document_id).get()
# doc = db.child('accounts').child(document_id).get()
#(document_id).get()
# doc.set("test")
# document_data_json = json.dumps(doc.val(), indent=4)
# print(f'Document Data (JSON):\n{document_data_json}')
print(doc.to_dict())


