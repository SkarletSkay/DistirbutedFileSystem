import json
import os
import shutil

import requests
from flask import Flask, request, jsonify

api = Flask(__name__)

CONFIGURE_PATH = './etc/'
#DATANODES_IP = os.environ["STORAGE"].split(",")
DATANODES_IP = ['3.134.253.161','18.219.181.76','3.14.130.178']
working_nodes = DATANODES_IP

down_nodes = []


@api.route('/', methods=['GET'])
def home():
    return f"Welcome to Super DFS! Here files in CONFIGURE_PATH: {os.listdir(CONFIGURE_PATH)}"


@api.route('/init', methods=['GET'])
def init():
    health_check()
    res = {}
    for node in working_nodes:
        try:
            res = requests.get('http://' + node + ':9000/init')
        except requests.exceptions.ConnectionError:
            working_nodes.remove(node)
            down_nodes.append(node)
        else:
            if res.status_code == 500:
                working_nodes.remove(node)
                down_nodes.append(node)
            if res.json()['resp'] == 404:
                return jsonify({'resp': 404})
    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    if os.path.exists(CONFIGURE_PATH):
        shutil.rmtree(CONFIGURE_PATH)
    os.mkdir(CONFIGURE_PATH)

    return jsonify({'resp': 201, 'size': res.json()['size']})


@api.route('/createf', methods=["POST"])
def create_file():
    health_check()
    data = request.get_json()
    for node in working_nodes:
        try:
            res = requests.post('http://' + node + ':9000/createFile', json=data)
        except requests.exceptions.ConnectionError:
            working_nodes.remove(node)
            down_nodes.append(node)
        else:
            if res.status_code == 500:
                working_nodes.remove(node)
                down_nodes.append(node)
            if res.json()['resp'] == 404:
                return jsonify({'resp': 404})

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    if not os.path.exists(CONFIGURE_PATH + data['path']):
        return jsonify({'resp': 404})

    file = open(CONFIGURE_PATH + data['path'] + data['name'], 'w+')
    file.close()

    return jsonify({'resp': 201})


@api.route('/copyf', methods=['POST'])
def copy_file():
    health_check()
    data = request.get_json()
    path = data['path']
    file = data['name']
    if os.path.exists(CONFIGURE_PATH + path + file):
        i = 1
        parts = file.rsplit('.', maxsplit=1)
        name = parts[0] + str(i) + '.' + parts[1]
        while os.path.exists(CONFIGURE_PATH + path + name):
            i = i + 1
            name = parts[0] + str(i) + '.' + parts[1]
        jdata = {'path': path, 'source': file, 'destination': name}

        health_check()

        for node in working_nodes:
            res = requests.post('http://' + node + ':9000/copy', json=jdata)
            if res.status_code == 500:
                working_nodes.remove(node)
                down_nodes.append(node)
            if res.json()['resp'] == 404:
                return jsonify({'resp': 404})

        if len(working_nodes) == 0:
            return jsonify({'resp': 500})
        shutil.copy(CONFIGURE_PATH + path+file, CONFIGURE_PATH + path+name)
        return jsonify({'resp': 201})
    else:
        return jsonify({'resp': 404})


@api.route('/mkdir', methods=['POST'])
def mkdir():
    health_check()
    data = request.get_json()
    for node in working_nodes:
        try:
            res = requests.post('http://' + node + ':9000/createDir', json=data)
        except requests.exceptions.ConnectionError:
            working_nodes.remove(node)
            down_nodes.append(node)
        else:
            if res.status_code == 500:
                working_nodes.remove(node)
                down_nodes.append(node)
            if res.json()['resp'] == 404:
                return jsonify({'resp': 404})

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    os.makedirs(CONFIGURE_PATH + data['path'])
    return jsonify({'resp': 201})


@api.route('/rmf', methods=["POST"])
def remove_file():
    health_check()
    data = request.get_json()
    for node in working_nodes:
        try:
            res = requests.post('http://' + node + ':9000/removeFile', json=data)
        except requests.exceptions.ConnectionError:
            working_nodes.remove(node)
            down_nodes.append(node)
        else:
            if res.status_code == 500:
                working_nodes.remove(node)
                down_nodes.append(node)
            if res.json()['resp'] == 404:
                return jsonify({'resp': 404})

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    if not os.path.exists(CONFIGURE_PATH + data['path']):
        return jsonify({'resp': 404})
    os.remove(CONFIGURE_PATH + data['path'])

    return jsonify({'resp': 200})


@api.route('/rmdir', methods=["POST"])
def remove_dir():
    health_check()
    data = request.get_json()
    for node in working_nodes:
        try:
            res = requests.post('http://' + node + ':9000/removeDir', json=data)
        except requests.exceptions.ConnectionError:
            working_nodes.remove(node)
            down_nodes.append(node)
        else:
            if res.status_code == 500:
                working_nodes.remove(node)
                down_nodes.append(node)
            if res.json()['resp'] == 404:
                return jsonify({'resp': 404})

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    if not os.path.exists(CONFIGURE_PATH + data['path']):
        return jsonify({'resp': 404})
    shutil.rmtree(CONFIGURE_PATH + data['path'])
    return jsonify({'resp': 200})


@api.route('/ls', methods=["POST"])
def ls():
    data = request.get_json()
    path = CONFIGURE_PATH + data['path']
    return jsonify({'resp': 200, 'list': os.listdir(path)})


@api.route('/mv', methods=["POST"])
def move():
    health_check()
    data = request.get_json()
    for node in working_nodes:
        try:
            res = requests.post('http://' + node + ':9000/move', json=data)
        except requests.exceptions.ConnectionError:
            working_nodes.remove(node)
            down_nodes.append(node)
        else:
            if res.status_code == 500:
                working_nodes.remove(node)
                down_nodes.append(node)
            if res.json()['resp'] == 404:
                return jsonify({'resp': 404})

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})
    source = CONFIGURE_PATH + data['source']
    dir_destination = CONFIGURE_PATH + data['dir_destination']
    destination = data['destination']
    if os.path.exists(dir_destination) or os.path.exists(source):
        os.rename(source, dir_destination+destination)
        return jsonify({'resp': 200})
    else:
        return jsonify({'resp': 404})


@api.route('/info', methods=["POST"])
def info():
    health_check()
    data = request.get_json()
    res = 0
    for node in working_nodes:
        try:
            res = requests.post('http://' + node + ':9000/info', json=data)
        except requests.exceptions.ConnectionError:
            working_nodes.remove(node)
            down_nodes.append(node)
        else:
            if res.status_code == 500:
                working_nodes.remove(node)
                down_nodes.append(node)
            if res.json()['resp'] == 404:
                return jsonify({'resp': 404})

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    response = {'resp': 200,
                'size': res.json()['size'],
                'access': res.json()['access'],
                'modified': res.json()['modified'],
                'change': res.json()['change']}
    return jsonify(response)


@api.route('/access', methods=['GET'])
def access():
    health_check()
    if len(working_nodes) == 0:
        return jsonify({'resp': 500})
    return jsonify({'resp': 200, 'server': working_nodes[0]})


@api.route('/writeFile', methods=['POST'])
def write_file():
    health_check()
    data = request.get_json()
    for node in working_nodes:
        try:
            res = requests.post('http://' + node + ':9000/writeFile', json=data)
        except requests.exceptions.ConnectionError:
            working_nodes.remove(node)
            down_nodes.append(node)
        else:
            if res.status_code == 500:
                working_nodes.remove(node)
                down_nodes.append(node)
            else:
                if res.json()['resp'] == 404:
                    return jsonify({'resp': 404})

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    path = data['path'].rsplit('/', maxsplit=1)
    p = ""
    if len(path) > 1:
        p = path[0]
        os.makedirs(CONFIGURE_PATH + p)
    if not os.path.exists(CONFIGURE_PATH + p):
        return jsonify({'resp': 404})

    file = open(CONFIGURE_PATH + data['path'], 'w+')
    file.close()

    return jsonify({'resp': 201})


def health_check():
    for node in working_nodes:
        try:
            res = requests.get('http://' + node + ':9000/heartbeat')
        except requests.exceptions.ConnectionError:
            working_nodes.remove(node)
            down_nodes.append(node)
            return 500
        else:
            if res.status_code != 200:
                working_nodes.remove(node)
                down_nodes.append(node)
    for node in down_nodes:
        try:
            res = requests.get('http://' + node + ':9000/heartbeat')
        except requests.exceptions.ConnectionError:
            pass
        else:
            if res.status_code == 200:
                working_nodes.append(node)
                down_nodes.remove(node)
                update_data(node)


def update_data(node):
    unchecked = []
    files = []
    leaves = []

    unchecked.extend(os.listdir(CONFIGURE_PATH))
    while len(unchecked) > 0:
        tmp = unchecked.pop()
        if os.path.isdir(CONFIGURE_PATH + tmp):
            listed = os.listdir(CONFIGURE_PATH + tmp)
            is_leaf = True
            for t in listed:
                if os.path.isdir(CONFIGURE_PATH + tmp + "/" + t):
                    is_leaf = False
                    unchecked.append(tmp + "/" + t)
                else:
                    files.append(tmp + "/" + t)
            if is_leaf:
                leaves.append(tmp)
        else:
            files.append(tmp)
    d = {'dirs': leaves, 'files': files, 'server': working_nodes[0]}
    res = requests.post('http://' + node + ':9000/recovery', json=json.loads(json.dumps(d)))
    return res


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True, port=5000)
