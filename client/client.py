import os
import requests

base_dir = 'storage'
sub_dir = ''
cur_path = base_dir
ns_ip = 'http://3.135.19.135:5000'

# Initialize the client storage on a new system, should remove any existing file in the dfs root directory and return
# available size.
def initialize():
    path = base_dir
    result = requests.get(ns_ip + '/init')
    print(result.content.decode('utf-8'))
    return 1


# File create. Should allow to create a new empty file.
def file_create(file_name):
    global cur_path
    ds_ip_list_ = requests.get(ns_ip + '/writef').content.decode('utf-8')
    ds_ip_list = ds_ip_list_.split(',')
    #print(ds_ip_list)
    del ds_ip_list[-1]
    #print(ds_ip_list)
    for i in range(len(ds_ip_list)):
        result = requests.post(ds_ip_list[i] + '/createf ' + cur_path + ',' + file_name).content.decode('utf-8')
        print(result)
    return 1


# File read. Should allow to read any file from DFS (download a file from the DFS to the Client side).
# Example: $readf image.jpg
# Request example: http://3.135.19.135:5000/access storage@home,image.jpg
def file_read(file_path, file_name):
    global cur_path
    ds_ip_list_ = requests.post(ns_ip + '/access ' + cur_path + ',' + file_name).content.decode('utf-8')
    ds_ip_list = ds_ip_list_.split(',') #TODO: добавить проверку на наличие вообще файла
    del ds_ip_list[-1]
    #print(ds_ip_list)
    result = requests.post(ds_ip_list[0] + '/readf ' + cur_path + '@' + file_name)
    file = open(file_path + '/' + file_name, 'wb')
    file.write(result.content)
    file.close()

    return 1


# File write. Should allow to put any file to DFS (upload a file from the Client side to the DFS)
# Example: $writef /home/alex/Pictures/test.jpg
def file_write(file_name):
    global cur_path
    byte_file = open(file_name, 'rb').read()
    file_name = file_name.split('/')[-1]
    ds_ip_list_ = requests.get(ns_ip + '/writef').content.decode('utf-8')
    ds_ip_list = ds_ip_list_.split(',')
    #print(ds_ip_list)
    del ds_ip_list[-1]
    #print(ds_ip_list)
    for i in range(len(ds_ip_list)):
        result = requests.post(ds_ip_list[i] + '/writef ' + cur_path + ',' + file_name, byte_file)
        print(result)
    return 1


# File delete. Should allow to delete any file from DFS
# Example: $rmf image.png
def file_delete(file_name):
    global cur_path
    ds_ip_list = requests.post(ns_ip + '/access ' + cur_path + ',' + file_name).content.decode('utf-8')
    ds_ip_list = ds_ip_list.split(',')
    del ds_ip_list[-1]
    for i in range(len(ds_ip_list)):
        result = requests.post(ds_ip_list[i] + '/rm ' + cur_path + ',' + file_name).content.decode('utf-8')
        print(result)
    return 1


# File info. Should provide information about the file (any useful information - size, node id, etc.)
# Example: $infof image.png
def file_info(file_name):
    global cur_path
    ds_ip_list = requests.post(ns_ip + '/access ' + cur_path + ',' + file_name).content.decode('utf-8')
    ds_ip_list = ds_ip_list.split(',')
    del ds_ip_list[-1]
    result = requests.post(ds_ip_list[0] + '/info ' + cur_path + '@' + file_name).content.decode('utf-8')
    print(result)
    return 1


# File copy. Should allow to create a copy of file.
# Example: $copyf image.png storage/lol
def file_copy(file_name, dest_path):
    global cur_path
    dest_path = dest_path.replace('/', '@')
    result = requests.post(ns_ip + '/copyf ' + cur_path + ',' + file_name + ',' + dest_path)
    print(result.content.decode('utf-8'))

    return 1


# File move. Should allow to move a file to the specified path.
# Example: $mvf image.png storage/lol/kek
def file_move(file_name, dest_path):
    global cur_path
    dest_path = dest_path.replace('/', '@')
    requests.post(ns_ip + '/mv ' + cur_path + ',' + file_name + ',' + dest_path)

    return 1


# Make directory. Should allow to create a new directory.
# Example: $mkdir lol
def make_directory(dir_name):
    global cur_path
    result = requests.post(ns_ip + '/mkdir ' + cur_path + ',' + dir_name)
    print(result.content.decode('utf-8')) #TODO надо пичинить вывод, а то там собаки вылезают вместо тэгов
    return 1


# Delete directory. Should allow to delete directory. If the directory contains files the system should ask for
# confirmation from the user before deletion.
# Example: $rmdir lol
def delete_directory(dir_name):
    global cur_path
    result = requests.post(ns_ip + '/rmdir ' + cur_path + ',' + dir_name)
    print(result.content.decode('utf-8'))
    return 1

# ls. Should return list of files, which are stored in the directory.
# Example: $ls
def ls():
    global cur_path
    result = requests.post(ns_ip + '/ls ' + cur_path)
    print(result.content.decode('utf-8'))
    return 1

# Example: $cd..
def cd_dotdot():
    global cur_path
    if (cur_path == base_dir):
        print('You are in storage')
        return 1
    else:
        path_arr = cur_path.split('@')
        del path_arr[-1]
        cur_path = '@'.join(path_arr)
        print('You are in ' + cur_path.replace('@', '/'))
        return 1

# Example: $cd
def cd_empty():
    global cur_path
    cur_path = base_dir
    print('You are in storage')
    return 1

# Example: $cd lol
def cd_dir_name(dir_name):
    global cur_path
    result = requests.post(ns_ip + '/cd ' + cur_path + '@' + dir_name + '.txt')
    if result.content != 'No such file or directory':
        cur_path = cur_path + '@' + dir_name
    print(result.content.decode('utf-8'))
    return 1


def command_recognition(comm):

    if comm == "help":
        print("init - Initialization")
        print("createf fn.ext - Create file with name 'fn.ext'")
        print("readf fn.ext - Download file 'fn.ext' from server")
        print("writef fn.ext - Upload file 'fn.ext' to server")
        print("rmf fn.ext - Delete file 'fn.ext'")
        print("copyf fn.ext storage/home - Copy 'fn.ext'")
        print("infof fn.ext - Get info about file 'fn.ext'")
        print("mvf fn.ext storage/home - Move file 'fn.ext' to 'storage/home'")
        print("cd home - Open directory '/home'")
        print("cd.. - Open up directory ")
        print("cd - Open root directory ")
        print("mkdir home - Create directory '/home'")
        print("rmdir home - Delete directory '/home'")
        print("ls - list files in the directory")
        print("exit - Exit from program")

        return 0

    if comm == "init":
        initialize()
        return 0
    if comm == "ls":
        ls()
        return 0

    slt_comm = comm.split(" ")
    if slt_comm[0] == 'cd' and len(slt_comm) == 1 :
        cd_empty()
        return 0
    elif slt_comm[0] == 'cd' and slt_comm[1] == '':
        cd_empty()
        return 0
    elif slt_comm[0] == 'cd..':
        cd_dotdot()
        return 0
    elif slt_comm[0] == 'cd' and len(slt_comm) > 1 :
        cd_dir_name(slt_comm[1])
        return 0

    if slt_comm[0] == "createf":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            file_create(slt_comm[1])
        return 0

    if slt_comm[0] == "readf":
        if len(slt_comm) != 3:
            print("Wrong parameters")
        else:
            file_read(slt_comm[1], slt_comm[2])
        return 0

    if slt_comm[0] == "writef":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            res = file_write(slt_comm[1])
        return 0

    if slt_comm[0] == "rmf":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            file_delete(slt_comm[1])
        return 0

    if slt_comm[0] == "infof":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            file_info(slt_comm[1])
        return 0

    if slt_comm[0] == "copyf":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            file_copy(slt_comm[1])
        return 0

    if slt_comm[0] == "mvf":
        if len(slt_comm) != 3:
            print("Wrong parameters")
        else:
            res = file_move(slt_comm[1], slt_comm[2])
            if res == 1:
                print("File", slt_comm[1], "has moved to", slt_comm[2])
            else:
                if res == 0:
                    print("File not found")
        return 0

    if slt_comm[0] == "mkdir":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            make_directory(slt_comm[1])
        return 0


    if slt_comm[0] == "rmdir":
        if len(slt_comm) != 2:
            print("Wrong parameters")
        else:
            delete_directory(slt_comm[1])
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
