

# Initialize the client storage on a new system, should remove any existing file in the dfs root directory and return
# available size.
def initialize():
    # Get files and directories
    # Delete it all
    return 1


# File create. Should allow to create a new empty file.
def file_create(file_name):
    # create(file_name)
    print("File created", file_name)
    return -1


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
    return -1


# File info. Should provide information about the file (any useful information - size, node id, etc.)
def file_info(file_name):
    # get_info(file_name)
    return -1


# File copy. Should allow to create a copy of file.
def file_copy(file_name):
    # copy(file_name)
    return -1


# File move. Should allow to move a file to the specified path.
def file_move(file_name, destination):
    # move(file_name, destination)
    return -1


# Open directory. Should allow to change directory
def open_directory(dir_name):
    # open_dir(dir_name)
    return -1


# Read directory. Should return list of files, which are stored in the directory.
def read_directory(dir_name):
    # read_dir(dir_name)
    return -1


# Make directory. Should allow to create a new directory.
def make_directory(dir_name):
    # make_dir(dir_name)
    return -1


# Delete directory. Should allow to delete directory. If the directory contains files the system should ask for
# confirmation from the user before deletion.
def delete_directory(dir_name):
    # delete(dir_name)
    return -1


def command_recognition(comm):
    if comm == "help":
        return 0
    if comm == "createf":
        return 0
    slt_comm = comm.split(" ")
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
