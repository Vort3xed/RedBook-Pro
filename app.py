from flask import Flask, session, render_template, request, redirect, url_for, send_file, abort
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
from dotenv import load_dotenv
import pyrebase
import os
import io

app = Flask(__name__)

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

# init basic app
firebase = pyrebase.initialize_app(config)

auth = firebase.auth()

# DO NOT UNCOMMENT, "storage" variable should not be overwritten
# storage = firebase.storage()

# set credientials for firebase admin
cred = credentials.Certificate('redbook-910e9-firebase-adminsdk-hzs4e-a467f4cf29.json')

# setup firebase admin for image storage
firebase_admin.initialize_app(cred, {
    'storageBucket': 'redbook-910e9.appspot.com'
})

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
            return render_template('quiz.html', image_name='1007161b.png')
    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'])
def home():
    # sign in request
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # try to sign in using the credentials provided
            user = auth.sign_in_with_email_and_password(email, password)
            # if it works, set the session variables and go to dashboard
            session['is_logged_in'] = True
            session['email'] = user['email']
            session['uid'] = user['idToken']
            return redirect(url_for('dashboard'))
        except Exception as e:
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
    print("connected to bucket")
    blob = bucket.blob(image_name)
    print("retrieved blob")
    image_data = blob.download_as_bytes()
    return io.BytesIO(image_data)

@app.context_processor
def import_session():
	return dict(session=session)

if __name__ == '__main__':
    app.run(debug=True)