import codecs
import json
import os
import shutil

import requests
from flask import Flask, request, jsonify
NAMESERVER_IP = 'http://nameserver:5000'

CONFIGURE_PATH = './storage/'
api = Flask(__name__)


@api.route('/', methods=['GET'])
def home():
    return f"Welcome to Super DFS! Here files in STORAGE_PATH: {os.listdir(CONFIGURE_PATH)}", 200


@api.route('/init', methods=['GET'])
def init():
    if os.path.exists(CONFIGURE_PATH):
        shutil.rmtree(CONFIGURE_PATH)
    os.mkdir(CONFIGURE_PATH)
    total_storage, used_storage, free_storage = shutil.disk_usage('/')
    resp = {'resp': 200, 'size': free_storage // (2 ** 30)}
    return jsonify(resp)


@api.route('/createFile', methods=["POST"])
def create_file():
    data = request.get_json()
    dir_name = data['path']
    filename = data['name']
    if os.path.exists(CONFIGURE_PATH + dir_name):
        file = open(CONFIGURE_PATH+dir_name+filename, 'w+')
        file.close()
        return jsonify({'resp': 200})
    else:
        return jsonify({'resp': 404})


@api.route('/createDir', methods=["POST"])
def create_dir():
    data = request.get_json()
    path = data['path']
    os.makedirs(CONFIGURE_PATH + path)
    return jsonify({'resp': 201})


@api.route('/move', methods=['POST'])
def move_file():
    data = request.get_json()
    source = CONFIGURE_PATH + data['source']
    dir_destination = CONFIGURE_PATH + data['dir_destination']
    destination = data['destination']
    if os.path.exists(dir_destination) or os.path.exists(source):
        os.rename(source, dir_destination+destination)
        return jsonify({'resp': 200})
    else:
        return jsonify({'resp': 404})


@api.route('/readFile', methods=['POST'])
def read_file():
    data = request.get_json()
    path = data['path']
    if not os.path.exists(CONFIGURE_PATH+path):
        return jsonify({'resp': 404})
    file = open(CONFIGURE_PATH + path, 'rb')
    b = file.read()
    file.close()
    return b


@api.route('/writeFile', methods=['POST'])
def write_file():
    info = request.get_json()
    path = info['path']
    file = open(CONFIGURE_PATH + path, 'wb')

    file.write(codecs.latin_1_decode(info['cont'])[0])
    file.close()
    return jsonify({'resp': 201})


@api.route('/heartbeat', methods=['GET'])
def heartbeat():
    return jsonify({'resp': 200})


@api.route('/info', methods=['POST'])
def file_info():
    data = request.get_json()
    path = data['path']

    if os.path.exists(CONFIGURE_PATH + path):
        info = os.stat(CONFIGURE_PATH + path)
        response = {'resp': 200,
                    'size': info[6],
                    'access': info[7],
                    'modified': info[8],
                    'change': info[9]}
        return jsonify(response)
    else:
        return jsonify({'resp': 404})


@api.route('/list', methods=['POST'])
def ls():
    data = request.get_json()
    path = data['path']
    if os.path.exists(CONFIGURE_PATH+path):
        response = os.listdir(CONFIGURE_PATH+path)
        return jsonify({'resp': 200, 'list': response})
    else:
        return jsonify({'resp': 404})


@api.route('/removeFile', methods=['POST'])
def remove_file():
    data = request.get_json()
    path = CONFIGURE_PATH + data['path']
    if os.path.exists(path):
        os.remove(path)
        return jsonify({'resp': 200})
    else:
        return jsonify({'resp': 404})


@api.route('/removeDir', methods=['POST'])
def remove_dir():
    data = request.get_json()
    path = CONFIGURE_PATH + data['path']
    if os.path.exists(path):
        shutil.rmtree(path)
        return jsonify({'resp': 200})
    else:
        return jsonify({'resp': 404})


def dir_create(path):
    os.makedirs(CONFIGURE_PATH + path)


def recover_file(file_path, data):
    file = open(CONFIGURE_PATH + file_path, 'wb')
    file.write(data)
    file.close()


@api.route('/recovery', methods=['POST'])
def recovery():
    init()
    data = request.get_json()
    server = data['server']
    dirs = data['dirs']
    files = data['files']
    for d in dirs:
        dir_create(d)
    for f in files:
        data = requests.get('http://' + server + ':9000/readFile', json=json.loads(json.dumps({'path': f})))
        recover_file(f, data.content)
    return jsonify({'resp': 201})


@api.route('/copy', methods=['POST'])
def copy():
    data = request.get_json()
    path = CONFIGURE_PATH + data['path']
    source = data['source']
    destination = data['destination']

    if os.path.exists(path + source):
        shutil.copy(path + source, path + destination)
        return jsonify({'resp': 201})
    else:
        return jsonify({'resp': 404})


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True, port=9000)
