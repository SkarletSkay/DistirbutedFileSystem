import os
import shutil
from flask import Flask, request, abort, jsonify, send_from_directory

api = Flask(__name__)

CONFIGURE_PATH = './etc/'


@api.route("/init", methods=['GET'])
def init():
    if os.path.exists(CONFIGURE_PATH):
        shutil.rmtree(CONFIGURE_PATH)
        os.mkdir(CONFIGURE_PATH)

        file = open(CONFIGURE_PATH + 'storage.txt', 'w+')
        file.close()

        return 'Success recreation'
    else:
        os.mkdir(CONFIGURE_PATH)

        file = open(CONFIGURE_PATH + "storage.txt", 'w+')
        file.close()

        return 'Success creation'


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
        return 'Success remove'
    else:
        return 'Error: no such directory'


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True, port=5000)