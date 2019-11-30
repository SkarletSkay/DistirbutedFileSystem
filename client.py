import json
import os
import shutil

import requests

base_dir = './storage/'
sub_dir = []
ns_ip = 'http://nameserver:5000'


def get_path():
    path = base_dir
    for s in sub_dir:
        path = path + s + '/'

    return path


# Initialize the client storage on a new system, should remove any existing file in the dfs root directory and return
# available size.
def initialize():
    path = base_dir
    sub_dir.clear()

    if os.path.exists(path):
        shutil.rmtree(path)
    try:
        os.mkdir(path)
    except OSError:
        print("Cannot create local storage file")
        return -3
    else:
        result = requests.get(ns_ip + '/init')
        if result.json()['resp'] == 200:
            print("Free space:" + str(result.json()['size']))
            return 1
        return -3


# File create. Should allow to create a new empty file.
def file_create(file_name):
    tmp = file_name.rsplit("/", maxsplit=1)
    data = {'path':  get_path() + tmp[0], 'name': tmp[1]}
    result = requests.post(ns_ip + '/init', json=json.dumps(data))
    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3
    return 1


# File read. Should allow to read any file from DFS (download a file from the DFS to the Client side).
def file_read(file_name):
    result = requests.post(ns_ip + '/access')
    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3

    server = result.json()['server']

    result = requests.post(str(server) + '/readFile', json=json.dumps({'path': get_path()+file_name}))
    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3
    os.makedirs(get_path()+file_name.rsplit("/", maxsplit=1)[0])
    file = open(get_path() + file_name, 'wb')
    file.write(result.json()['data'])
    file.close()
    return 1


# File write. Should allow to put any file to DFS (upload a file from the Client side to the DFS)
def file_write(file_name):
    if not os.path.exists(get_path()+file_name):
        print("File ", file_name, "Not Found")
        return -3
    file = open(get_path()+file_name, 'rb').read()

    result = requests.post(ns_ip + '/writeFile', json=json.dumps({'path': get_path() + file_name}))

    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3

    server = result.json()['server']

    result = requests.post(str(server) + '/writeFile', json=json.dumps({'path': get_path() + file_name,
                                                                        'data': file}))
    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3
    return 1


# File delete. Should allow to delete any file from DFS
def file_delete(file_name):
    path = get_path() + file_name
    result = requests.post(ns_ip + '/rmf', json=json.dumps({'path': path}))
    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3
    return 1


# File info. Should provide information about the file (any useful information - size, node id, etc.)
def file_info(file_name):
    path = get_path() + file_name
    result = requests.post(ns_ip + '/info', json=json.dumps({'path': path}))
    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3

    print("Size:" + str(result.content['size']))
    print("Last Access:" + str(result.content['access']))
    print("Last Modification:" + str(result.content['modified']))
    print("Last Change:" + str(result.content['change']))
    return 1


# File copy. Should allow to create a copy of file.
def file_copy(file_name):
    tmp = file_name.rsplit("/", maxsplit=1)
    data = {'path': get_path() + tmp[0], 'name': tmp[1]}
    result = requests.post(ns_ip + '/copyf', json=json.dumps(data))

    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3

    return 1


# File move. Should allow to move a file to the specified path.
def file_move(file_name, destination_path):
    destination_parts = destination_path.rsplit("/", maxsplit=1)
    data = {'source': get_path()+file_name, 'dir_destination': destination_parts[0],
            'destination': destination_parts[1]}
    result = requests.post(ns_ip + '/move', json=json.dumps(data))
    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3

    return 1


# Make directory. Should allow to create a new directory.
def make_directory(dir_name):
    path = get_path() + dir_name
    result = requests.post(ns_ip + '/mkdir', json=json.dumps({'path': path}))
    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3
    return 1


# Delete directory. Should allow to delete directory
def delete_directory(dir_name):
    path = get_path() + dir_name
    result = requests.post(ns_ip + '/rmdir', json=json.dumps({'path': path}))
    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3
    return 1


# ls. Should return list of files, which are stored in the directory.
def ls():
    path = get_path()
    result = requests.post(ns_ip + '/rmdir', json=json.dumps({'path': path}))
    if len(result.json()) == 0:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3
    print(result.json()['list'])
    return 1


def cd(dir_name):
    if dir_name == "":
        sub_dir.clear()
        return 1
    if dir_name == "..":
        sub_dir.pop()
        return 1
    sub_dir.extend(dir_name.split('/'))
    return 1


def command_recognition(comm):
    if comm == "":
        return 0

    if comm == "help":
        print("init - Initialization")
        print("createf test.txt - Create file with name 'test.txt'")
        print("readf storage/home/Desktop test.txt - Download file 'test.txt' from server")
        print("writef test.txt - Upload file 'test.txt' to server")
        print("rmf test.txt - Delete file 'test.txt'")
        print("copyf test.txt storage/home - Copy 'test.txt'")
        print("infof test.txt - Get info about file 'test.txt'")
        print("mvf test.txt storage/home - Move file 'test.txt' to 'storage/home'")
        print("cd home - Open directory '/home'")
        print("cd.. - Open up directory ")
        print("cd - Open root directory ")
        print("mkdir home - Create directory '/home'")
        print("rmdir home - Delete directory '/home'")
        print("ls - list files in the directory")
        print("exit - Exit from program")
        return 0

    if comm.replace(' ', '') == "init":
        initialize()
        return 0
    if comm.replace(' ', '') == "ls":
        ls()
        return 0

    slt_comm = comm.split()

    if slt_comm[0] == "cd":
        if len(slt_comm) > 2:
            return -2
        else:
            if len(slt_comm) == 1:
                return cd("")
            else:
                return cd(slt_comm[1])

    if slt_comm[0] == "createf":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            return file_create(slt_comm[1])

    if slt_comm[0] == "readf":
        if len(slt_comm) != 3:
            return -2
        else:
            return file_read(slt_comm[1])

    if slt_comm[0] == "writef":
        if len(slt_comm) != 2:
            return -2
        else:
            return file_write(slt_comm[1])

    if slt_comm[0] == "rmf":
        if len(slt_comm) != 2:
            return -2
        else:
            return file_delete(slt_comm[1])

    if slt_comm[0] == "infof":
        if len(slt_comm) != 2:
            return -2
        else:
            return file_info(slt_comm[1])

    if slt_comm[0] == "copyf":
        if len(slt_comm) != 3:
            return -2
        else:
            return file_copy(slt_comm[1])

    if slt_comm[0] == "mvf":
        if len(slt_comm) != 3:
            return -2
        else:
            return file_move(slt_comm[1], slt_comm[2])

    if slt_comm[0] == "mkdir":
        if len(slt_comm) != 2:
            return -2
        else:
            return make_directory(slt_comm[1])

    if slt_comm[0] == "rmdir":
        if len(slt_comm) != 2:
            return -2
        else:
            return delete_directory(slt_comm[1])

    return -1


def control():
    while True:
        comm = input()
        if comm == "exit":
            break
        res = command_recognition(comm)
        if res == -1:
            print("Unknown command:", comm)
            print("Type 'help' for more information")
        else:
            if res == -2:
                print("Wrong parameters")
            else:
                if res == -3:
                    print("Operation Failed")


print("Welcome to SuperDFS")
print("Type 'help' for more information")
control()