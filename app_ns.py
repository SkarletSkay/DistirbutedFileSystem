import os
import shutil

import requests
from flask import Flask, request, jsonify

api = Flask(__name__)

CONFIGURE_PATH = './etc/'
DATANODES_IP = os.environ["STORAGE"].split(",")
working_nodes = []
down_nodes = []


@api.route('/', methods=['GET'])
def home():
    return f"Welcome to Super DFS! Here files in CONFIGURE_PATH: {os.listdir(CONFIGURE_PATH)}"


@api.route('/init', methods=['GET'])
def init():
    health_check()
    res = {}
    for node in working_nodes:
        res = requests.get('http://' + node + ':9000/init')
        if len(res.json()):
            working_nodes.remove(node)
            down_nodes.append(node)

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    if os.path.exists(CONFIGURE_PATH):
        shutil.rmtree(CONFIGURE_PATH)
    os.mkdir(CONFIGURE_PATH)
    return res.json()


@api.route('/createf', methods=["POST"])
def create_file():
    health_check()
    data = request.json()
    for node in working_nodes:
        res = requests.get('http://' + node + ':9000/CreateFile', json=data)
        if len(res.json()) == 0:
            working_nodes.remove(node)
            down_nodes.append(node)
        if res.json()['resp'] == 404:
            return jsonify(res)

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    if not os.path.exists(data['path']):
        return jsonify({'resp': 404})

    file = open(CONFIGURE_PATH + data['path'] + data['name'], 'w+')
    file.close()

    return jsonify({'resp': 201})


@api.route('/copyf', methods=['POST'])
def copy_file():
    health_check()
    data = request.json()
    path = CONFIGURE_PATH + data['path']
    file = data['name']
    if os.path.exists(path+file):
        i = 0
        parts = file.rsplit('.', maxsplit=1)
        name = parts[0] + str(i) + '.' + parts[1]
        while os.path.exists(path+name):
            i = i + 1
            name = parts[0] + str(i) + '.' + parts[1]
        jdata = {'path': path, 'source': file, 'destination': name}

        health_check()

        for node in working_nodes:
            res = requests.get('http://' + node + ':9000/copy', json=jdata)
            if len(res.json()) == 0:
                working_nodes.remove(node)
                down_nodes.append(node)
            if res.json()['resp'] == 404:
                return jsonify(res)

        if len(working_nodes) == 0:
            return jsonify({'resp': 500})
        shutil.copy(path+file, path+name)
        return jsonify({'resp': 201})
    else:
        return jsonify({'resp': 404})


@api.route('/mkdir', methods=['POST'])
def mkdir():
    data = request.json()
    for node in working_nodes:
        res = requests.get('http://' + node + ':9000/createDir', json=data)
        if len(res.json()) == 0:
            working_nodes.remove(node)
            down_nodes.append(node)
        if res.json()['resp'] == 404:
            return jsonify(res)

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    os.makedirs(CONFIGURE_PATH + data['path'])
    return jsonify({'resp': 201})


@api.route('/rmf', methods=["POST"])
def remove_file():
    health_check()
    data = request.json()
    for node in working_nodes:
        res = requests.get('http://' + node + ':9000/removeFile', json=data)
        if len(res.json()) == 0:
            working_nodes.remove(node)
            down_nodes.append(node)
        if res.json()['resp'] == 404:
            return jsonify(res)

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    if not os.path.exists(CONFIGURE_PATH + data['path']):
        return jsonify({'resp': 404})
    os.remove(CONFIGURE_PATH + data['path'])

    return jsonify({'resp': 200})


@api.route('/rmdir', methods=["POST"])
def remove_dir():
    health_check()
    data = request.json()
    for node in working_nodes:
        res = requests.get('http://' + node + ':9000/removeDir', json=data)
        if len(res.json()) == 0:
            working_nodes.remove(node)
            down_nodes.append(node)
        if res.json()['resp'] == 404:
            return jsonify(res)

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    if not os.path.exists(CONFIGURE_PATH + data['path']):
        return jsonify({'resp': 404})
    shutil.rmtree(CONFIGURE_PATH + data['path'])
    return jsonify({'resp': 200})


@api.route('/ls', methods=["POST"])
def ls():
    data = request.json()
    path = CONFIGURE_PATH + data['path']
    return jsonify({'resp': 200, 'list': os.listdir(path)})


@api.route('/mv', methods=["POST"])
def move():
    health_check()
    data = request.json()
    for node in working_nodes:
        res = requests.get('http://' + node + ':9000/move', json=data)
        if len(res.json()) == 0:
            working_nodes.remove(node)
            down_nodes.append(node)
        if res.json()['resp'] == 404:
            return jsonify(res)

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
    data = request.json()
    res = 0
    for node in working_nodes:
        res = requests.get('http://' + node + ':9000/info', json=data)
        if len(res.json()) == 0:
            working_nodes.remove(node)
            down_nodes.append(node)
        if res.json()['resp'] == 404:
            return jsonify(res)

    if len(working_nodes) == 0:
        return jsonify({'resp': 500})

    return res


@api.route('/access', methods=['GET'])
def access():
    health_check()
    if len(working_nodes) == 0:
        return jsonify({'resp': 500})
    return jsonify({'resp': 200, 'server': working_nodes[0]})


@api.route('/writeFile', methods=['GET'])
def write_file():
    health_check()
    data = request.json()
    res = access()
    if res.json()['resp'] == 200:
        file = open(CONFIGURE_PATH + data['path'], 'w+')
        file.close()
    return res


def health_check():
    for node in working_nodes:
        res = requests.get('http://' + node + ':9000/heartbeat')
        if res != 200:
            working_nodes.remove(node)
            down_nodes.append(node)
    for node in down_nodes:
        res = requests.get('http://' + node + ':9000/info')
        if res == 200:
            working_nodes.append(node)
            down_nodes.remove(node)


def update_data(node):
    unchecked = [CONFIGURE_PATH]
    files = []
    leaves = []

    while len(unchecked) > 0:
        tmp = unchecked.pop()
        listed = os.listdir(tmp)
        is_leaf = True
        for t in listed:
            if os.path.isdir(t):
                is_leaf = False
                unchecked.append(tmp + t + "/")
            else:
                files.append(tmp + t)
        if is_leaf:
            leaves.append(tmp)
    data = {'dirs': leaves, 'files': files, 'server': node}
    res = requests.get('http://' + node + ':9000/recovery', jsonify(data))
    return res


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True, port=5000)
