from flask import Flask, session, render_template, request, redirect, url_for, send_file, abort
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from dotenv import load_dotenv
import requests
import json
import os
import io

app = Flask(__name__)

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

# DO NOT UNCOMMENT, "storage" variable should not be overwritten
# storage = firebase.storage()

# set credientials for firebase admin
cred = credentials.Certificate(os.getenv('CERT_PATH'))

# setup firebase admin with acccess to the storage bucket
firebase_admin.initialize_app(cred, {
    'storageBucket': os.getenv('STORAGE_BUCKET_URL')
})

# setup firebase admin with access to the database
db = firestore.client()

# probably JWT token encryption
app.secret_key = os.getenv('DATABASE_SECRET')

@app.route('/dashboard')
def dashboard():
    if session['is_logged_in'] == True:
        return render_template('dashboard.html')
    return redirect(url_for('home'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if session['is_logged_in'] == True:
        # return render_template('quiz.html', image_name='1007161b.png')
        if session['quiz_params'] == None:
            return redirect(url_for('dashboard'))
        else:
            # user_data = db.collection('accounts').where('field_name', '==', specific_string).stream()
            # print(info)
            uid = session['uid']

            # get the user's data from the database
            doc = db.collection('accounts').document(uid).get()
            user_data = doc.to_dict()

            print(user_data)


            return render_template('quiz.html', image_name='1007161b.png')
    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'])
def home():
    # sign in request
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # try to sign in using the credentials provided (OLD METHOD WITH PYREBASE)
            # user = auth.sign_in_with_email_and_password(email, password)

            user = sign_in_with_email_password(email, password)
            # if it works, set the session variables and go to dashboard
            session['is_logged_in'] = True
            print("session is set to active")
            session['email'] = user['email']
            print("email is retrieved")
            session['uid'] = user['localId']
            print("uid is retrieved")

            print("success! uid -> " + str(session['uid']))
            return redirect(url_for('dashboard'))
        except Exception as e:
            print("this is the exception: " + str(e))
            # womp womp sign in failed or credentials are wrong
            return render_template('home.html')
    return render_template('home.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session['is_logged_in'] = False
        return redirect(url_for('home'))
    
@app.route('/setQuizParams', methods=['GET', 'POST'])
def setQuizParams():
    if request.method == 'POST':
        selectedTest = request.form["testselect"]
        selectedDiff = request.form["difficultyselect"]
        if selectedTest == 'RD':
            selectedSkill = request.form["readingskill"]
        else:
            selectedSkill = request.form["mathskill"]
        session['quiz_params'] = [selectedTest, selectedDiff, selectedSkill]
        print(session['quiz_params'])
    return redirect(url_for('quiz'))
    
@app.route('/images/<image_name>')
def get_image(image_name):
    try:
        print("fetching image")
        image_stream = fetch_image(image_name)
        return send_file(image_stream, mimetype='image/jpeg')
    except Exception as e:
        print(e)
        abort(404)

def fetch_image(image_name):
    bucket = storage.bucket()
    blob = bucket.blob(image_name)
    image_data = blob.download_as_bytes()
    return io.BytesIO(image_data)

def sign_up_with_email_password(email, password):
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

@app.context_processor
def import_session():
	return dict(session=session)

if __name__ == '__main__':
    app.run(debug=True)