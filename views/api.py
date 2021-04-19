import os
from flask import (Flask, flash, request, redirect, 
                  url_for, Blueprint, send_from_directory, jsonify)
from werkzeug.utils import secure_filename
from util.func_util import log_api

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'MOV', 'zip', 'jar'}
UPLOAD_FOLDER = './data'

api = Blueprint('api', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route('/upload', methods=['GET', 'POST'])
@log_api
def upload_file():
    '''
    API to accept the uploaded file.
    Receives the file as a part of POST form data.

    Returns a 200, with a Succcess or failure message.
    '''
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return f'Successful uploading {filename}'

    return 'Could not upload file'

@api.route("/files", methods=['GET'])
@log_api
def list_files():
    '''
    API to list the uploaded files for the user
    Parameters: user_id as a get parameter
    Returns : The list of files uploaded by the user and the metadata.
    '''
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)


@api.route("/download/<path:path>")
@log_api
def download_file(path):
    '''
    API to download the specified file
    Parameters: file_name, which indicates the file to be downloaded
    Returns : The file the user had requested for download
    '''
    return send_from_directory(UPLOAD_FOLDER, path)