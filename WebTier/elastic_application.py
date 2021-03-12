import imghdr
import os
import time
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import SubmitField, MultipleFileField
from upload_data import main, download
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
        start_time = time.time()
        files = os.listdir(app.config['RESULTS_PATH'])
        result = {}
        for file in files:
            os.remove(app.config["RESULTS_PATH"]+"/"+file)
        files = []
        for file in form.file.data:
            current_time = datetime.now()
            filename = str(time.time())+"_"+current_time.strftime('%m-%d-%Y')+"_"+secure_filename(file.filename)
            #filename = secure_filename(file.filename)
            if filename != '':
                file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
                files.append(filename)
        result = main()
        end_time = time.time()
        print("Total Process done. Time taken : " + str(end_time-start_time))
        files1 = []
        result1 = {}
        for file in files:
            file1 = file.split("2021_")[-1]
            files1.append(file1)
            result1[file1] = result[file]
        files = files1
        result = result1
        return render_template('index.html', files=files, form = form, result = result)

    # files = os.listdir(app.config['RESULTS_PATH'])
    files = []
    # result = {}
    # uploadKeys = []
    # # textFiles = []
    # for file in files:
    #     uploadKeys.append(file)

    # #     if ".txt" in file:
    # #         print("Exists  "+ file)
    # #         textFiles.append(file)

    # # for file in textFiles:
    # #     files.remove(file)

    # # for file in files:
    # #     new_file = file.split(".")[0]+".txt"
    # #     if new_file not in textFiles :
    # #         uploadKeys.append(file)
    # #     print(os.path.exists(app.config['RESULTS_PATH']+"/"+new_file))
    # #     if socket.gethostname() in file and os.path.exists(app.config['RESULTS_PATH']+"/"+new_file):
    # #         f = open(app.config['RESULTS_PATH']+"/"+new_file)
    # #         result[file] = str(f.read())
    # #     print(result)
    # # print("Upload Keys : " , uploadKeys)
    # # print("Files to Front End : " , files)
    result={}
    # result = download(uploadKeys)
    return render_template('index.html', files=files, form = form, result = result)

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['RESULTS_PATH'], filename)

if __name__=='__main__':
    print("Web Tier has Started...")
    # app.run(debug=True)
    serve(app, host="0.0.0.0", port=5000)
