import firebase_admin
from firebase_admin import credentials, auth
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin SDK
cred = credentials.Certificate('redbook-910e9-firebase-adminsdk-hzs4e-a467f4cf29.json')
firebase_admin.initialize_app(cred)

def sign_up_with_email_password(email, password):
    """Create a new user with email and password."""
    try:
        user = auth.create_user(email=email, password=password)
        print('Successfully created new user:', user.uid)
        return user.uid
    except Exception as e:
        print('Error creating new user:', e)
        return None

def sign_in_with_email_password(email, password):
    """Sign in existing user with email and password."""
    url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + os.getenv('APIKEY')
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        # print('Successfully signed in user:', data['localId'])
        # print('ID Token:', data['idToken'])
        return data
    else:
        print('Failed to sign in:', response.json())
        return None

def verify_id_token(id_token):
    """Verify the ID token using Firebase Admin SDK."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        print('Successfully verified ID token for user:', uid)
        return decoded_token
    except Exception as e:
        print('Error verifying ID token:', e)
        return None

# Example usage
email = "test@gmail.com"
password = "test123"

# Sign up a new user
# user_id = sign_up_with_email_password(email, password)

# Sign in the user
sign_in_data = sign_in_with_email_password(email, password)


# print(os.getenv('DATABASE_SECRET'))
# print(sign_in_data['idToken'])
print(sign_in_data['localId'])
print(sign_in_data['email'])