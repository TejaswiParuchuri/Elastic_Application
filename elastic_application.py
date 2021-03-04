import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField, MultipleFileField
from upload_data import main
import socket
from waitress import serve
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'd79cddc52783fe71bcbee0deb14061d0'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_PATH'] = 'uploads'
app.config['RESULTS_PATH'] = 'results'

class FileUploadForm(FlaskForm):
    file = MultipleFileField("Upload Files")
    submit = SubmitField('Upload')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = FileUploadForm()
    if form.validate_on_submit():
        for file in form.file.data:
            current_time = datetime.now()
            filename = socket.gethostname()+"_"+current_time.strftime('%m-%d-%Y')+"_"+secure_filename(file.filename)
            if filename != '':
                file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        main()
        return redirect(url_for('index'))

    files = os.listdir(app.config['RESULTS_PATH'])
    result = []
    return render_template('index.html', files=files, form = form, result = result)

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['RESULTS_PATH'], filename)

if __name__=='__main__':
    #app.run(debug=True)
    serve(app, host="0.0.0.0", port=5000)
