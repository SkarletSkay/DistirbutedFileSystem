import codecs
import json
import os
import shutil
import requests
import datetime
base_dir = './storage/'
sub_dir = []
ns_ip = 'http://3.135.19.135:5000'

def get_path():
    path = ""
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
        if result.status_code == 500:
            return -3
        if result.json()['resp'] == 200:
            print("Free space:" + str(result.json()['size']))
            return 1
        return -3


# File create. Should allow to create a new empty file.
def file_create(file_name):
    tmp = file_name.rsplit("/", maxsplit=1)
    path = get_path()
    if len(tmp) > 1:
        path = path + tmp[0]
        name = tmp[1]
    else:
        name = tmp[0]
    data = {'path':  path+"/", 'name': name}
    result = requests.post(ns_ip + '/createf', json=json.loads(json.dumps(data)))
    if result.status_code == 500:
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
    result = requests.get(ns_ip + '/access')
    if result.status_code == 500:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3

    server = result.json()['server']

    result = requests.post("http://" + str(server) + ':9000/readFile',
                           json=json.loads(json.dumps({'path': get_path()+file_name})))
    if result.status_code == 500:
        return -3
    if result.status_code == 404:
        print("Not Found")
        return -3
    p = file_name.rsplit("/", maxsplit=1)
    if len(p) > 1:
        os.makedirs(base_dir+p[0])
    file = open(base_dir + file_name, 'wb')
    file.write(result.content)
    file.close()
    return 1


# File write. Should allow to put any file to DFS (upload a file from the Client side to the DFS)
def file_write(file_name):
    if not os.path.exists(base_dir + get_path()+file_name):
        print("File", file_name, "Not Found")
        return -3
    file = open(base_dir + get_path()+file_name, 'rb').read()
    cont = codecs.latin_1_decode(file)
    result = requests.post(ns_ip + '/writeFile', json=json.loads(json.dumps({'path': get_path() + file_name,
                                                                             'cont': cont[0]})))

    if result.status_code == 500:
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
    result = requests.post(ns_ip + '/rmf', json=json.loads(json.dumps({'path': path})))
    if result.status_code == 500:
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
    result = requests.post(ns_ip + '/info', json=json.loads(json.dumps({'path': path})))
    if result.status_code == 500:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3

    access_time = f'Access time ' \
                  f'{datetime.datetime.fromtimestamp(result.json()["access"]).strftime("%m/%d/%Y, %H:%M:%S")}, '
    modified_time = f'Modified time ' \
                    f'{datetime.datetime.fromtimestamp(result.json()["modified"]).strftime("%m/%d/%Y, %H:%M:%S")}, '
    last_change_time = f'Last change time ' \
                       f'{datetime.datetime.fromtimestamp(result.json()["change"]).strftime("%m/%d/%Y, %H:%M:%S")}, '
    print("Size:" + str(result.json()['size']))
    print(access_time)
    print(modified_time)
    print(last_change_time)
    return 1


# File copy. Should allow to create a copy of file.
def file_copy(file_name):
    tmp = file_name.rsplit("/", maxsplit=1)
    if len(tmp) > 1:
        data = {'path': get_path() + tmp[0] + "/", 'name': tmp[1]}
    else:
        data = {'path': get_path(), 'name': tmp[0]}
    result = requests.post(ns_ip + '/copyf', json=json.loads(json.dumps(data)))

    if result.status_code == 500:
        return -3
    if result.json()['resp'] == 404:
        print("Not Found")
        return -3
    if result.json()['resp'] == 4044:
        print("Not Found1")
        return -3
    if result.json()['resp'] == 500:
        print("Server error")
        return -3

    return 1


# File move. Should allow to move a file to the specified path.
def file_move(file_name, destination_path):
    destination_parts = destination_path.rsplit("/", maxsplit=1)
    if len(destination_parts) > 1:
        data = {'source': get_path()+file_name, 'dir_destination': destination_parts[0] + "/",
                'destination': destination_parts[1]}
    else:
        data = {'source': get_path() + file_name, 'dir_destination': "",
                'destination': destination_parts[0]}
    result = requests.post(ns_ip + '/mv', json=json.loads(json.dumps(data)))
    if result.status_code == 500:
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
    result = requests.post(ns_ip + '/mkdir', json=json.loads(json.dumps({'path': path})))
    if result.status_code == 500:
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
    result = requests.post(ns_ip + '/rmdir', json=json.loads(json.dumps({'path': path})))
    if result.status_code == 500:
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
    result = requests.post(ns_ip + '/ls', json=json.loads(json.dumps({'path': path})))
    if result.status_code == 500:
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
        print("copyf test.txt - Copy 'test.txt'")
        print("infof test.txt - Get info about file 'test.txt'")
        print("mvf test.txt storage/home - Move file 'test.txt' to 'storage/home'")
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
        if len(slt_comm) != 2:
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
        if len(slt_comm) != 2:
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