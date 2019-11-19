import os
import shutil

import requests
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
    for host in DATANODES_IP:
        hostname = host
        response = os.system("ping -c 1 " + hostname)
        # and then check the response...
        if response == 0:
            requests.get(f'http://{host}:9000/init')
            pingstatus = "Network Active"
        else:
            pingstatus = "Network Error"

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
        return f'Error: the folder {dir_name} already exists', 404

    file = open(f'{CONFIGURE_PATH}{cur_path}@{dir_name}.txt', 'w+')
    file.close()

    file = open(f'{CONFIGURE_PATH}{cur_path}.txt', 'a')
    file.write(dir_name + '\n')
    file.close()

    return str(f'Success directory creation /{cur_path}@{dir_name}'), 200


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
    return f'Here list of files in /{cur_path.replace("@", "/")}: ' + str(files[:len(files) - 1])


@api.route('/cd <cur_path>', methods=['POST'])
def cd(cur_path):
    dirs = os.listdir(CONFIGURE_PATH)
    if f'{cur_path}.txt' in dirs:
        cur_path_ = str(cur_path).replace('@', '/')
        return f'Now you are in /{cur_path_}', 200
    else:
        return 'No such file or directory', 404


@api.route('/createf <cur_path>,<file_name>', methods=["POST"])
def createf(cur_path, file_name):
    ds_ip_list_ = writef()
    ds_ip_list = ds_ip_list_.split(',')
    del ds_ip_list[-1]
    result = ""
    for i in range(len(ds_ip_list)):
        result = requests.post(ds_ip_list[i] + '/createf ' + cur_path + ',' + file_name)
    return result.content


@api.route('/rmf <cur_path>,<file_name>', methods=["POST"])
def rmf(cur_path, file_name):
    ds_ip_list_ = writef()
    ds_ip_list = ds_ip_list_.split(',')
    del ds_ip_list[-1]
    result = ""
    for i in range(len(ds_ip_list)):
        result = requests.post(ds_ip_list[i] + '/rm ' + cur_path + ',' + file_name)
    return result.content


@api.route('/copyf <cur_path>,<file_name>,<file_copy_name>', methods=["POST"])
def copyf(cur_path, file_name, file_copy_name):
    ds_ip_list = access(cur_path, file_name)
    ds_ip_list = ds_ip_list.split(',')
    del ds_ip_list[-1]
    file_copy_name = file_copy_name.replace('/', '@')
    for i in range(len(ds_ip_list)):
        result = requests.post(ds_ip_list[
                                   i] + '/copy ' + cur_path + '@' + file_name + ',' + file_copy_name + ',' + cur_path)
    return result.content


@api.route('/infof <cur_path>,<file_name>', methods=["POST"])
def info(cur_path, file_name):
    ds_ip_list_ = writef()
    ds_ip_list = ds_ip_list_.split(',')
    del ds_ip_list[-1]
    result = ""
    for i in range(len(ds_ip_list)):
        result = requests.post(ds_ip_list[i] + '/info ' + cur_path + '@' + file_name)
    return result.content


@api.route('/writef', methods=['GET'])
def writef():
    AVAILABLE_HOSTS = ''
    for host in DATANODES_IP:
        hostname = host
        response = os.system("ping -c 1 " + hostname)
        # and then check the response...
        if response == 0:
            AVAILABLE_HOSTS += (f'http://{host}:9000,')
            pingstatus = "Network Active"
        else:
            pingstatus = "Network Error"

    return AVAILABLE_HOSTS


@api.route('/add_file <dir_name>,<file_name>', methods=['POST'])
def add_file(dir_name, file_name):
    with open(f'{CONFIGURE_PATH}{dir_name}.txt') as f:
        lines = f.readlines()
    f.close()

    pattern = re.compile(re.escape(file_name))
    with open(f'{CONFIGURE_PATH}{dir_name}.txt', 'w') as f:
        for line in lines:
            result = pattern.search(line)
            if result is None:
                f.write(line)
    f.close()

    file = open(f'{CONFIGURE_PATH}{dir_name}.txt', 'a')
    file.write(file_name + '\n')
    file.close()
    return 'Success add file'


@api.route('/rm_file <dir_name>,<file_name>', methods=['POST'])
def rm_file(dir_name, file_name):
    with open(f'{CONFIGURE_PATH}{dir_name}.txt') as f:
        lines = f.readlines()
    f.close()

    pattern = re.compile(re.escape(file_name))
    with open(f'{CONFIGURE_PATH}{dir_name}.txt', 'w') as f:
        for line in lines:
            result = pattern.search(line)
            if result is None:
                f.write(line)
    f.close()


@api.route('/access <dir_name>,<file_name>', methods=['POST'])
def access(dir_name, file_name):
    full_file_name = f'{dir_name}@{file_name}'
    AVAILABLE_HOSTS_ = ''
    for host in DATANODES_IP:
        hostname = host
        response = os.system("ping -c 1 " + hostname)
        # and then check the response...
        if response == 0:
            AVAILABLE_HOSTS_ += (f'http://{host}:9000,')
            pingstatus = "Network Active"
        else:
            pingstatus = "Network Error"

    AVAILABLE_HOSTS = AVAILABLE_HOSTS_.split(',')
    del AVAILABLE_HOSTS[-1]

    HOSTS_TO_RETURN = ''
    for host in AVAILABLE_HOSTS:
        response = requests.post(f'{host}/find {full_file_name}').content
        if response == b'1':
            HOSTS_TO_RETURN += f'{host},'

    return HOSTS_TO_RETURN


@api.route('/mv <source_path_dir>,<source_path_file>,<destination_path_dir>', methods=['POST'])
def move(source_path_dir, source_path_file, destination_path_dir):
    dirs = os.listdir(CONFIGURE_PATH)
    if f'{destination_path_dir}.txt' in dirs:
        with open(f'{CONFIGURE_PATH}{source_path_dir}.txt') as f:
            lines = f.readlines()
        f.close()

        pattern = re.compile(re.escape(source_path_file))
        with open(f'{CONFIGURE_PATH}{source_path_dir}.txt', 'w') as f:
            for line in lines:
                result = pattern.search(line)
                if result is None:
                    f.write(line)
        f.close()

        file = open(f'{CONFIGURE_PATH}{destination_path_dir}.txt', 'a')
        file.write(source_path_file + '\n')
        file.close()
        return 'Success move file'
    else:
        return 'Error: No such destination directory', 404


if __name__ == "__main__":
    api.run(host='0.0.0.0', debug=True, port=5000)
