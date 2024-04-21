from flask import Flask, render_template, request, send_file, redirect, url_for, session
from moviepy.editor import VideoFileClip
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os

app = Flask(__name__)

app.secret_key = 'ae'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ae-users'

mysql = MySQL(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Logged in successfully !'
            return redirect(url_for('index'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message=message)


@app.route('/index')
def index():
    if 'loggedin' in session:
        name = session.get('name', 'Guest')
        return render_template('index.html', name=name)
    else:
        return redirect(url_for('login'))


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'fileInput' in request.files:
        video = request.files['fileInput']
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
        
        # Ensure the 'uploads' directory exists
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        
        try:
            video.save(video_path)
        except Exception as e:
            return f'Error saving file: {str(e)}'

        # Extract audio
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio.mp3')
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_path)

        # Clean up
        video_clip.close()
        audio_clip.close()

        return send_file(audio_path, as_attachment=True)
    else:
        return 'No file uploaded'

if __name__ == '__main__':
    app.run(debug=True)
