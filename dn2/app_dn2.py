import os
import shutil

import requests
from flask import Flask, request, abort, jsonify, send_from_directory

NAMESERVER_IP = 'http://3.135.19.135:5000'

CONFIGURE_PATH = './dn2_storage/'
api = Flask(__name__)


@api.route('/', methods=['GET'])
def home():
    return f"Welcome to Super DFS! Here files in CONFIGURE_PATH: {os.listdir(CONFIGURE_PATH)}"


@api.route('/init', methods=['GET'])
def init():
    if os.path.exists(CONFIGURE_PATH):
        shutil.rmtree(CONFIGURE_PATH)
        os.mkdir(CONFIGURE_PATH)

        total_storage, used_storage, free_storage = shutil.disk_usage('/')
        return str("Success recreation. You can use: %d GB" % (free_storage // (2 ** 30)))
    else:
        os.mkdir(CONFIGURE_PATH)

        total_storage, used_storage, free_storage = shutil.disk_usage('/')
        return str("Success creation. You can use: %d GB" % (free_storage // (2 ** 30)))


@api.route('/readf <file_name>', methods=['POST'])
def readf_file(file_name):
    file = open(f'{CONFIGURE_PATH}{file_name}', 'rb')
    bytes = file.read()
    file.close()

    return bytes


@api.route('/createf <dir_name>,<filename>', methods=["POST"])
def post_file(dir_name, filename):
    """Upload a file."""
    file = open(f'{CONFIGURE_PATH}{dir_name}@{filename}', 'wb')
    file.write(request.data)
    file.close()
    requests.post(f'{NAMESERVER_IP}/add_file {dir_name},{filename}')
    # Return 201 CREATED
    return "Successed uploaded"


@api.route('/find <filename>', methods=["POST"])
def find(filename):
    files = os.listdir(f'{CONFIGURE_PATH}')
    if filename in files:
        return '1'
    else:
        return '0'


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True, port=5000)
