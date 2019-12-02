# DistirbutedFileSystem
* Svetlana Kabriova (SE-01)
* Alexander Gruk    (DS-02)
* Ilnur Mamedbakov  (DS-02)

## Installation
**Name Server + Storages:**
```
docker swarm init
```
<i>Use given command for joining datanodes</i>
```
docker node update --availability drain (node-1)
```
```
docker service create --name (name) --replicas (numOfDN) --host nameserver:(nameser_ip)  --publish 9000:9000 skab/dfs2_dn
```
```
docker run --env STORAGE="(storage_ip1),(storage_ip2)" -p 5000:5000 skab/dfs2_ns
```
**CLIENT:**
```
docker run --add-host nameserver:(nameser_ip) -it skab/dfs2_client
```

Architecture
![alt text](https://i.ibb.co/cNzxhVh/Untitled-Diagram-1.png)

**Client commands:**
```
init - Initialization
createf test.txt - Create file with name 'test.txt'
readf storage/home/Desktop test.txt - Download file 'test.txt' from server
writef test.txt - Upload file 'test.txt' to server
rmf test.txt - Delete file 'test.txt'
copyf test.txt storage/home - Copy 'test.txt'
infof test.txt - Get info about file 'test.txt'
mvf test.txt storage/home - Move file 'test.txt' to 'storage/home'
cd home - Open directory '/home'
cd.. - Open up directory 
cd - Open root directory 
mkdir home - Create directory '/home'
rmdir home - Delete directory '/home'
ls - list files in the directory
exit - Exit from program
```

**Nameserver:**
```
'/init'
'/mkdir <cur_path>,<dir_name>'
'/rmdir <cur_path>,<dir_name>'
'/ls <cur_path>'
'/cd <cur_path>'
'/createf <cur_path>,<file_name>', methods=["POST"])
'/rmf <cur_path>,<file_name>', methods=["POST"])
'/copyf <cur_path>,<file_name>,<file_copy_name>', methods=["POST"])
'/infof <cur_path>,<file_name>', methods=["POST"])
'/writef'
'/add_file <dir_name>,<file_name>'
'/rm_file <dir_name>,<file_name>'
'/access <dir_name>,<file_name>'
'/mv <source_path_dir>,<source_path_file>,<destination_path_dir>'
'/raiseup <ip>'
```

**Storage:**
```
'/'
'/init'
'/readf <file_name>'
'/ls'
'/createf <dir_name>,<filename>'
'/upload <filename>'
'/writef <dir_name>,<filename>'
'/find <filename>'
'/rm <dir_name>,<filename>'
'/info <filename>'
'/copy <filename_source>,<filename_copy>,<current_path>'
'/rename <old_name>,<new_name>'
```
