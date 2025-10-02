from flask import Flask, request, jsonify, send_file
from flask_httpauth import HTTPBasicAuth
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
auth = HTTPBasicAuth()

# config
UPLOAD_FOLDER = '/home/brand/FileChain'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'zip', 'docx'}
USERNAME = 'username'
PASSWORD = 'password'
PORT = 3000 # Change to desired port

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def verify_password(username, password):
    return username == USERNAME and password == PASSWORD

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/ download/<filename>', methods=['GET'])
@auth.login_required
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/delete/<filename>', methods=['DELETE'])
@auth.login_required
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return jsonify({'message': f'File {filename} deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run (host='0.0.0.0', port=PORT, debug=True)


