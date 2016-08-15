import sys
import os
import paramiko


file_name = "RF_Driver.py"
# file_name = "Test2.py"
path_to_upload = "Weiyi/gumgum"
overwrite = False
download = False
download_file = "KBest_Select.npy"
download_aws = "/home/ubuntu/Weiyi"
download_local = "/home/wlu/Desktop"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname="174.129.176.95", port=22, username="ubuntu", key_filename="/home/wlu/Desktop/rips")

if overwrite:
    upload_name = file_name
else:
    upload_name = "tmp.py"
sftp = client.open_sftp()
sftp.put(file_name, os.path.join("/home/ubuntu", path_to_upload, upload_name))

cmd = "cd {};/home/ubuntu/anaconda2/bin/python2.7 {}".format(path_to_upload, upload_name)
stdin, stdout, stderr = client.exec_command(cmd)
while True:
    output = stdout.readline()
    if output == '':
        break
    if output:
        sys.stdout.write(output)
        sys.stdout.flush()

err = False
for line in stderr:
    err = True
    sys.stdout.write(line)
    sys.stdout.flush()

if (download) and (not err):
    path_aws = os.path.join(download_aws, download_file)
    path_local = os.path.join(download_local, download_file)
    sftp.get(path_aws, path_local)

if not overwrite:
    cmd = "cd {};rm {}".format(path_to_upload, upload_name)

sftp.close()
client.close()
