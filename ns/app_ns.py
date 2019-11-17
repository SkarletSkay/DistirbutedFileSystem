import os
import shutil
from flask import Flask, request, abort, jsonify, send_from_directory
import re

api = Flask(__name__)

CONFIGURE_PATH = './etc/'
DATANODES_IP = ['3.134.253.161', '18.219.181.76']


@api.route('/', methods=['GET'])
def home():
    return f"Welcome to Super DFS! Here files in CONFIGURE_PATH: {os.listdir(CONFIGURE_PATH)}"


@api.route('/init', methods=['GET'])
def init():
    if os.path.exists(CONFIGURE_PATH):
        shutil.rmtree(CONFIGURE_PATH)
        os.mkdir(CONFIGURE_PATH)

        file = open(CONFIGURE_PATH + 'storage.txt', 'w+')
        file.close()
        total_storage, used_storage, free_storage = shutil.disk_usage('/')
        return str("Success recreation. You can use: %d GB" % (free_storage // (2 ** 30)))
    else:
        os.mkdir(CONFIGURE_PATH)

        file = open(CONFIGURE_PATH + "storage.txt", 'w+')
        file.close()
        total_storage, used_storage, free_storage = shutil.disk_usage('/')
        return str("Success creation. You can use: %d GB" % (free_storage // (2 ** 30)))


@api.route('/mkdir <cur_path>,<dir_name>', methods=['POST'])
def mkdir(cur_path, dir_name):
    dirs = os.listdir(CONFIGURE_PATH)

    if f'{cur_path}@{dir_name}.txt' in dirs:
        return 'Error: the folder already exists'

    file = open(f'{CONFIGURE_PATH}{cur_path}@{dir_name}.txt', 'w+')
    file.close()

    file = open(f'{CONFIGURE_PATH}{cur_path}.txt', 'a')
    file.write(dir_name + '\n')
    file.close()

    return str(f'Success directory creation {CONFIGURE_PATH}{cur_path}@{dir_name}.txt')


@api.route('/rmdir <cur_path>,<dir_name>', methods=['POST'])
def rmdir(cur_path, dir_name):
    dirs = os.listdir(CONFIGURE_PATH)
    subdirs = [dir for dir in dirs if f'{cur_path}@{dir_name}' in dir]

    if f'{cur_path}@{dir_name}.txt' in dirs:
        for subdir in subdirs:
            os.remove(f'{CONFIGURE_PATH}{subdir}')

        with open(f'{CONFIGURE_PATH}{cur_path}.txt') as f:
            lines = f.readlines()
        f.close()

        # TODO: make up how to do better
        pattern = re.compile(re.escape(dir_name))
        with open(f'{CONFIGURE_PATH}{cur_path}.txt', 'w') as f:
            for line in lines:
                result = pattern.search(line)
                if result is None:
                    f.write(line)
        f.close()

        return 'Success remove'
    else:
        return 'Error: no such directory'


@api.route('/ls <cur_path>', methods=['POST'])
def ls(cur_path):
    file = open(f'{CONFIGURE_PATH}{cur_path}.txt')
    files = file.read().split('\n')
    file.close()
    return str(files[:len(files) - 1])


@api.route('/cd <cur_path>', methods=['POST'])
def cd(cur_path):
    dirs = os.listdir(CONFIGURE_PATH)
    if cur_path in dirs:
        cur_path_ = str(cur_path).replace('@', '/')
        return f'Now you are in {cur_path_}'
    else:
        return 'No such file or directory'


@api.route('/ping', methods=['GET'])
def ping():
    AVAILABLE_HOSTS = []
    for host in DATANODES_IP:
        hostname = host
        response = os.system("ping -c 1 " + hostname)
        # and then check the response...
        if response == 0:
            AVAILABLE_HOSTS.append(f'http://{host}:5000')
            pingstatus = "Network Active"
        else:
            pingstatus = "Network Error"

    return str(AVAILABLE_HOSTS)


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True, port=5000)
