import os
import shutil

import requests
from flask import Flask, request, abort, jsonify, send_from_directory
import datetime
from shutil import copyfile

NAMESERVER_IP = 'http://3.135.19.135:5000'

CONFIGURE_PATH = './storage/'
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
def create_file(dir_name, filename):
    """"Create a file"""
    file = open(f'{CONFIGURE_PATH}{dir_name}@{filename}', 'w+')
    file.close
    requests.post(f'{NAMESERVER_IP}/add_file {dir_name},{filename}')
    return 'Successed created'


@api.route('/writef <dir_name>,<filename>', methods=["POST"])
def post_file(dir_name, filename):
    """Upload a file."""
    file = open(f'{CONFIGURE_PATH}{dir_name}@{filename}', 'wb')
    file.write(request.data)
    file.close()
    requests.post(f'{NAMESERVER_IP}/add_file {dir_name},{filename}')
    # Return 201 CREATED
    return "Successed uploaded"


@api.route('/find <filename>', methods=['POST'])
def find(filename):
    files = os.listdir(f'{CONFIGURE_PATH}')
    if filename in files:
        return '1'
    else:
        return '0'


@api.route('/rm <dir_name>,<filename>', methods=['POST'])
def remove_file(dir_name, filename):
    try:
        os.remove(f'{CONFIGURE_PATH}{dir_name}@{filename}')
        requests.post(f'{NAMESERVER_IP}/rm_file {dir_name},{filename}')
    except FileNotFoundError:
        return 'File not found', 404
    return 'Success remove file'


@api.route('/info <filename>', methods=['POST'])
def file_info(filename):
    info = os.stat(f'{CONFIGURE_PATH}{filename}')
    size = f'File size is {info[6]} bytes, '
    access_time = f'Access time {datetime.datetime.fromtimestamp(info[7]).strftime("%m/%d/%Y, %H:%M:%S")}, '
    modified_time = f'Modified time {datetime.datetime.fromtimestamp(info[8]).strftime("%m/%d/%Y, %H:%M:%S")}, '
    last_change_time = f'Last change time {datetime.datetime.fromtimestamp(info[9]).strftime("%m/%d/%Y, %H:%M:%S")}, '
    return f'{size}\n{access_time}\n{modified_time}\n{last_change_time}'

    return datetime.datetime.fromtimestamp(info[7]).strftime("%m/%d/%Y, %H:%M:%S")


@api.route('/copy <filename_source>,<filename_copy>,<current_path>', methods = ['POST'])
def copy(filename_source, filename_copy, current_path):
    try:
        f = open(CONFIGURE_PATH+filename_source)
        f.close()
    except FileNotFoundError:
        return 'File does not exist', 404

    try:
        copyfile(CONFIGURE_PATH+filename_source, CONFIGURE_PATH+current_path+'@'+filename_copy)
    except FileNotFoundError:
        return 'File not found', 404

    requests.post(f'{NAMESERVER_IP}/add_file {current_path},{filename_copy}')
    return 'Success copy', 200

if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True, port=5000)
