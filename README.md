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
readf test.txt - Download file 'test.txt' from server
writef test.txt - Upload file 'test.txt' to server
rmf test.txt - Delete file 'test.txt'
copyf test.txt - Copy 'test.txt'
infof test.txt - Get info about file 'test.txt'
mvf t/test.txt /home/t.txt - Move file 't/test.txt' to 'home/t.txt'
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
'/ methods=['GET']'
'/init methods=['GET']'
'/mkdir <dir_name>  -> methods=["POST"]'
'/rmdir <dir_name> -> methods=["POST"]'
'/ls <path>  -> methods=["POST"]'
'/createf <file_name>' -> methods=["POST"])
'/rmf <file_name>' -> methods=["POST"])
'/copyf <file_name> -> methods=["POST"])
'/infof <file_name>'  -> methods=["POST"])
'/writeFile <file_name> -> methods=["POST"]'
'/rmf <file_name> -> methods=["POST"]'
'/access methods=['GET']'
'/mv <source_file>,<destination_path_dir>  -> methods=["POST"]'
```

**Storage:**
```
'/ methods=['GET']'
'/init methods=['GET']'
'/readf <file_path> -> methods=["POST"]'
'/ls <file_path> -> methods=["POST"]'
'/createf <dir_name>,<filename> -> methods=["POST"]'
'/writeFile <file_path> -> methods=["POST"]'
'/writef <dir_name>,<filename>' -> methods=["POST"]'
'/removeFile <file_path> ->  methods=["POST"]'
'/info <file_path> -> methods=["POST"]'
'/copy <filename_source>,<filename_copy>,<current_path>  -> methods=["POST"]'
'/heartbeat methods=['GET']
'/recovery <ip_server>, <dirs>, <file_names>  -> methods=['POST']
```
