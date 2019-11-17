import os

import requests
from flask import Flask, request, abort, jsonify, send_from_directory

UPLOAD_DIRECTORY = '.'
NAMESERVER_IP = 'http://3.135.19.135:5000'

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

api = Flask(__name__)


@api.route('/')
def hello_world():
    return 'Welcome to Super DFS!'


@api.route('/files')
def list_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify(files)


@api.route('/files/<path:path>')
def get_file(path):
    """Download a file."""
    try:
        return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)
    except FileNotFoundError:
        abort(404)


@api.route('/createf <dir_name>,<filename>', methods=["POST"])
def post_file(dir_name, filename):
    """Upload a file."""
    file = open(filename, 'wb')
    file.write(request.data)
    file.close()
    requests.post(f'{NAMESERVER_IP}/add_file {dir_name},{filename}')
    # Return 201 CREATED
    return "Successed uploaded"


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=False, port=5000)
