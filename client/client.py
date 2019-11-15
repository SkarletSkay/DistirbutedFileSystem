import os
import requests

base_dir = 'storage' # TODO: replace ./storage on ~ when aws
sub_dir = ''
cur_path = base_dir
ns_ip = '0.0.0.0:5000' # TODO: change to real IP of name server

# Initialize the client storage on a new system, should remove any existing file in the dfs root directory and return
# available size.
def initialize(): # TODO: add returning of size of storage
    path = base_dir
    result = requests.get(ns_ip + '/init')
    print(result)
    return 1


# File create. Should allow to create a new empty file.
def file_create(file_name):
    # create(file_name)
    f = open(base_dir + sub_dir + "/" + file_name, "w+")
    f.close()
    print("File created", file_name)
    return 1


# File read. Should allow to read any file from DFS (download a file from the DFS to the Client side).
def file_read(file_name):
    # get(file_name)
    return 1


# File write. Should allow to put any file to DFS (upload a file from the Client side to the DFS)
def file_write(file):
    # send(file)
    return -1


# File delete. Should allow to delete any file from DFS
def file_delete(file_name):
    # delete(file_name)
    os.remove(base_dir + sub_dir + "/" + file_name)
    return 1


# File info. Should provide information about the file (any useful information - size, node id, etc.)
def file_info(file_name):
    # get_info(file_name)
    return 1


# File copy. Should allow to create a copy of file.
def file_copy(file_name):
    # copy(file_name)
    return 1


# File move. Should allow to move a file to the specified path.
def file_move(file_name, destination):
    # move(file_name, destination)
    return 1


# Open directory. Should allow to change directory
def open_directory(dir_name):
    # open_dir(dir_name)
    return 1


# Read directory. Should return list of files, which are stored in the directory.
def read_directory(dir_name):
    # read_dir(dir_name)
    return 1


# Make directory. Should allow to create a new directory.
def make_directory(dir_name):
    global cur_path
    result = requests.post(ns_ip + '/mkdir ' + cur_path + ',' + dir_name) # TODO: создать cur_path
    print(result)
    return 1


# Delete directory. Should allow to delete directory. If the directory contains files the system should ask for
# confirmation from the user before deletion.
def delete_directory(dir_name):
    global cur_path
    result = requests.post(ns_ip + '/rmdir ' + cur_path + ',' + dir_name) # TODO: создать cur_path
    print(result)
    return 1


def ls():
    global cur_path
    result = requests.post(ns_ip + '/ls ' + cur_path)
    print(result)
    return 1


def cd_dotdot():
    global cur_path
    if (cur_path == base_dir):
        return 1
    else:
        path_arr = cur_path.split('@')
        del path_arr[-1]
        cur_path = '@'.join(path_arr)
        return 1

def cd_empty():
    global cur_path
    cur_path = base_dir
    return 1


def cd_dir_name(dir_name):
    global cur_path
    result = requests.post(ns_ip + '/cd ' + cur_path + ',' + dir_name)
    print(result)
    if result == 200:
        cur_path = cur_path + '@' + dir_name
    return 1


def command_recognition(comm):
    if comm == "help":
        print("init - Initialization")
        print("createf fn.ext - Create file with name 'fn.ext'")
        print("readf fn.ext - Download file 'fn.ext' from server")
        print("writef fn.ext - Upload file 'fn.ext' to server")
        print("rmf fn.ext - Delete file 'fn.ext'")
        print("copyf fn.ext - Copy 'fn.ext'")
        print("infof fn.ext - Get info about file 'fn.ext'")
        print("mvf fn.ext ./dir1/ - Move file 'fn.ext' to './dir1/'")
        print("opendir ./dir1 - Open directory './dir1'")
        print("mkdir ./dir1 - Create directory './dir1'")
        print("rmdir ./dir1 - Delete directory './dir1'")
        print("ls - list files in the directory")
        print("exit - Exit from program")

        return 0
    if comm == "createf":
        return 0
    if comm == "init":
        if initialize() == 1:
            print("Successful!")
        else:
            print("Something goes wrong")
        return 0
    if comm == "ls":
        ls()
        return 0

    slt_comm = comm.split(" ")
    if slt_comm[0] == 'cd' and len(slt_comm) == 1 :
        cd_empty()
    elif slt_comm[0] == 'cd' and slt_comm[1] == '':
        cd_empty()
    elif slt_comm[0] == 'cd..':
        cd_dotdot()
    elif slt_comm[0] == 'cd' and len(slt_comm) > 1 :
        cd_dir_name(slt_comm[1])

    if slt_comm[0] == "createf":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            file_create(slt_comm[1])
        return 0

    if slt_comm[0] == "readf":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            res = file_read(slt_comm[1])
            if res == 1:
                print("Success")
            else:
                if res == 0:
                    print("File not found")
        return 0
    if slt_comm[0] == "writef":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            res = file_write(slt_comm[1])
            if res == 1:
                print("Success")
            else:
                if res == 0:
                    print("File not found")
        return 0
    if slt_comm[0] == "rmf":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            res = file_delete(slt_comm[1])
            if res == 1:
                print("Success")
            else:
                if res == 0:
                    print("File not found")
        return 0
    if slt_comm[0] == "infof":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            res = file_info(slt_comm[1])
            if res == 1:
                print("Success")
            else:
                if res == 0:
                    print("File not found")
        return 0
    if slt_comm[0] == "copyf":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            res = file_copy(slt_comm[1])
            if res == 1:
                print("Success")
            else:
                if res == 0:
                    print("File not found")
        return 0
    if slt_comm[0] == "mvf":
        if len(slt_comm) != 3:
            print("Wrong parameters")
        else:
            res = file_move(slt_comm[1], slt_comm[2])
            if res == 1:
                print("Success. File", slt_comm[1], "has moved to", slt_comm[2])
            else:
                if res == 0:
                    print("File not found")
        return 0
    if slt_comm[0] == "mkdir":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            res = make_directory(slt_comm[1])
            if res == 1:
                print("Success")
        return 0
    if slt_comm[0] == "opendir":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            res = open_directory(slt_comm[1])
            if res == 1:
                print("Success")
        return 0
    if slt_comm[0] == "rmdir":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            res = delete_directory(slt_comm[1])
            if res == 1:
                print("Success")
        return 0
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


print("Welcome to SuperDFS")
print("Type 'help' for more information")
control()
