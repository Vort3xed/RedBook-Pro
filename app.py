from flask import Flask, session, render_template, request, redirect, url_for, send_file, abort, jsonify
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

# @app.route('/quiz', methods=['GET', 'POST'])
# def quiz():
#     if session['is_logged_in'] == True:
#         # return render_template('quiz.html', image_name='1007161b.png')
#         if session['quiz_params'] == None:
#             return redirect(url_for('dashboard'))
#         else:
#             # user_data = db.collection('accounts').where('field_name', '==', specific_string).stream()
#             # print(info)
#             uid = session['uid']
#             quiz_params = session['quiz_params']

#             # get the user's data from the database
#             doc = db.collection('accounts').document(uid).get()
#             user_data = doc.to_dict()

#             print(user_data)

#             return render_template('quiz.html', image_name='1007161b.png')
#     return redirect(url_for('home'))

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

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    return render_template('settings.html')

@app.route('/wipecompleted', methods=['GET', 'POST'])
def wipecompleted():
    if request.method == 'POST':
        if session['is_logged_in'] == True:
            uid = session['uid']
            db.collection('accounts').document(uid).update({
                'answered': []
            })
            db.collection('accounts').document(uid).update({
                'answeredCorrectly': []
            })
            db.collection('accounts').document(uid).update({
                'answeredIncorrectly': []
            })
    return redirect(url_for('settings'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if session['is_logged_in'] == True:
        if session['quiz_params'] == None:
            return redirect(url_for('dashboard'))
        else:
            uid = session['uid']
            quiz_params = session['quiz_params']

            test = quiz_params[0]
            difficulty = quiz_params[1]
            skill = quiz_params[2]

            return render_template('quiz2.html')
        
@app.route('/unreadAndQuit', methods=['GET', 'POST'])
def unreadAndQuit():
    if request.method == 'POST':
        if session['is_logged_in'] == True:
            data = request.json
            uid = session['uid']
            question_id = data.get('answered_question')
            print("question_id: {}", question_id)
            db.collection('accounts').document(uid).update({
                'answered': firestore.ArrayRemove([question_id])
            })

    return redirect(url_for('dashboard'))

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    if session['is_logged_in'] == True:
        return render_template('stats.html')
    return redirect(url_for('home'))

# @app.route('/get_stats', methods=['GET', 'POST'])
# def getstats():
#     if session['is_logged_in'] == True:
#         uid = session['uid']
#         answered = db.collection('accounts').document(uid).get().to_dict().get('answered')
#         answered_correctly = db.collection('accounts').document(uid).get().to_dict().get('answeredCorrectly')
#         answered_incorrectly = db.collection('accounts').document(uid).get().to_dict().get('answeredIncorrectly')

#         if len(answered) == 0:
#             return render_template('stats.html', total_accuracy=0, reading_skill_accuracy=[0,0,0,0,0,0,0,0,0], math_skill_accuracy=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
#         total_accuracy = len(answered_correctly) / len(answered) * 100
#         total_accuracy = round(total_accuracy, 2)

#         reading_skill_accuracy = []
#         math_skill_accuracy = []

#         all_reading_skills = ["Central Ideas and Details","Command of Evidence","Words in Context","Text Structure and Purpose","Cross-Text Connections","Rhetorical Synthesis","Transitions","Boundaries","Form, Structure, and Sense"]
#         all_math_skills = ["Linear equations in one variable", "Linear functions", "Linear equations in two variables", "Systems of two linear equations in two variables", "Linear inequalities in one or two variables", "Nonlinear functions", "Nonlinear equations in one variable and systems of equations in two variables", "Equivalent expressions", "Ratios, rates, proportional relationships, and units", "Percentages", "One-variable data: Distributions and measures of center and spread", "Two-variable data: Models and scatterplots", "Probability and conditional probability", "Inference from sample statistics and margin of error", "Evaluating statistical claims: Observational studies and experiments", "Area and volume", "Lines, angles, and triangles", "Right triangles and trigonometry", "Circles"]

#         print(len(all_reading_skills))
#         print(len(all_math_skills))

#         for skill in all_reading_skills:
#             all_questions = filter_by_skill(db.collection('accounts').document(uid).get().to_dict().get('answered'), skill, "reading")
#             answered_correctly = filter_by_skill(db.collection('accounts').document(uid).get().to_dict().get('answeredCorrectly'), skill, "reading")
#             if (len(all_questions) == 0):
#                 reading_skill_accuracy.append(0)
#             else:
#                 reading_skill_accuracy.append(len(answered_correctly) / len(all_questions) * 100)

#         for skill in all_math_skills:
#             all_questions = filter_by_skill(db.collection('accounts').document(uid).get().to_dict().get('answered'), skill, "math")
#             answered_correctly = filter_by_skill(db.collection('accounts').document(uid).get().to_dict().get('answeredCorrectly'), skill, "math")
#             if (len(all_questions) == 0):
#                 math_skill_accuracy.append(0)
#             else:
#                 math_skill_accuracy.append(len(answered_correctly) / len(all_questions) * 100)

#         print(total_accuracy)
#         print(reading_skill_accuracy)
#         print(math_skill_accuracy)
#         return jsonify({
#             'total_accuracy': total_accuracy,
#             'reading_skill_accuracy': reading_skill_accuracy,
#             'math_skill_accuracy': math_skill_accuracy
#         })

def filter_by_skill(questions, skill, type):
    filtered = []
    if type == "reading":
        for question in questions:
            
            if db.collection('reading_questions').document(question).get().to_dict() != None and db.collection('reading_questions').document(question).get().to_dict().get('skill') == skill:
                filtered.append(question)
    else:
        for question in questions:
            if db.collection('math_questions').document(question).get().to_dict() != None and db.collection('math_questions').document(question).get().to_dict().get('skill') == skill:
                filtered.append(question)

    print(filtered)
    return filtered


@app.route('/get_next_question', methods=['GET', 'POST'])
def get_next_question():
    data = request.json

    uid = session['uid']
    quiz_params = session['quiz_params']

    test = quiz_params[0]
    difficulty = quiz_params[1]
    skill = quiz_params[2]

    session['question_index'] = 0

    # current_index = data.get('current_index')
    selected_answer = data.get('selected_answer')
    answered_question = data.get('answered_question')
    handle_grading(answered_question, selected_answer)

    # query = db.collection('reading_questions').where('difficulty', '==', difficulty).where('skill', '==', skill)
    # query = db.collection('reading_questions').filter('difficulty', '==', difficulty).filter('skill', '==', skill)

    if (test == 'RD' and skill == 'Random' and difficulty == 'Random'):
        print("querying RD random skill random difficulty")
        query = db.collection('reading_questions')
    elif (test == 'RD' and skill == 'Random'):
        print("querying RD random skill specific difficulty")
        query = db.collection('reading_questions').where('difficulty', '==', difficulty)
    elif (test == 'RD' and difficulty == 'Random'):
        print("querying RD specific skill random difficulty")
        query = db.collection('reading_questions').where('skill', '==', skill)
    elif (test == 'RD'):
        print("querying RD specific skill specific difficulty")
        query = db.collection('reading_questions').where('difficulty', '==', difficulty).where('skill', '==', skill)

    if (test == 'MH' and skill == 'Random' and difficulty == 'Random'):
        print("querying MH random skill random difficulty")
        query = db.collection('math_questions')
    elif (test == 'MH' and skill == 'Random'):
        print("querying MH random skill specific difficulty")
        query = db.collection('math_questions').where('difficulty', '==', difficulty)
    elif (test == 'MH' and difficulty == 'Random'):
        print("querying MH specific skill random difficulty")
        query = db.collection('math_questions').where('skill', '==', skill)
    elif (test == 'MH'):
        print("querying MH specific skill specific difficulty")
        query = db.collection('math_questions').where('difficulty', '==', difficulty).where('skill', '==', skill)


    # query = db.collection('reading_questions').where('difficulty', '==', "Medium").where('skill', '==', "Command of Evidence")
    # query = db.collection('reading_questions').filter('difficulty', '==', "Medium").filter('skill', '==', "Command of Evidence")

    questions = [doc.to_dict() for doc in query.stream()]

    print(questions)

    if session['question_index'] < len(questions):
        answered = db.collection('accounts').document(uid).get().to_dict().get('answered')
        question = find_next_question(questions, answered)
        print(question)

        if question == None:
            return jsonify({'error': 'No more questions'}), 404

        question_id = question['sat_id']
        photo_type = question['photoType']
        is_free_response = True
        if question.get('freeResponse') is not None:
            is_free_response = question['freeResponse']

        print(question_id)

        document_ref = db.collection('accounts').document(uid)
        document_ref.update({
            'answered': firestore.ArrayUnion([question_id])
        })


        return jsonify({
            'question': question_id,
            'photoType': photo_type,
            'isFreeResponse': is_free_response
        })


    # if session['question_index'] < len(questions):
    #     question_data = questions[session['question_index']]

    #     print(question_data)
    #     image_name = question_data.get('image_name')
    #     question_data['image_url'] = url_for('get_image', image_name=image_name)

    #     session['question_index'] += 1
        
    #     # Optionally, you can store the selected answer in Firestore or process it as needed
        
    #     return jsonify({
    #         'question': question_data,
    #     })
    return jsonify({'error': 'No more questions'}), 404

@app.route('/incorrect', methods=['GET', 'POST'])
def incorrect():
    if session['is_logged_in'] == True:
        uid = session['uid']
        answered_incorrectly = db.collection('accounts').document(uid).get().to_dict().get('answeredIncorrectly')
        answered_incorrectly.reverse()
        return render_template('incorrect.html', answered_incorrectly=answered_incorrectly)

    
@app.route('/images/<image_name>')
def get_image(image_name):
    try:
        print("fetching image")
        image_stream = fetch_image(image_name)
        return send_file(image_stream, mimetype='image/jpeg')
    except Exception as e:
        print(e)
        abort(404)

def handle_grading(question_id, selected_answer):
    print("the selected answer: " + str(selected_answer))
    if db.collection('reading_questions').document(question_id).get().to_dict() == None:
        question = db.collection('math_questions').document(question_id).get().to_dict()
    else:
        question = db.collection('reading_questions').document(question_id).get().to_dict()
    print("grabbing question data of what was completed...")
    print(question)
    if question == None:
        return
    correct_answer = question['correctAnswer']
    uid = session['uid']
    if (selected_answer == correct_answer):
        db.collection('accounts').document(uid).update({
            'answeredCorrectly': firestore.ArrayUnion([question_id])
        })
    else:
        db.collection('accounts').document(uid).update({
            'answeredIncorrectly': firestore.ArrayUnion([question_id + "_" + selected_answer + "_" + correct_answer])
        })

def fetch_image(image_name):
    bucket = storage.bucket()
    blob = bucket.blob(image_name)
    image_data = blob.download_as_bytes()
    return io.BytesIO(image_data)

def find_next_question(questions, answered):
    for question in questions:
        if question['sat_id'] not in answered:
            return question
    return None

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