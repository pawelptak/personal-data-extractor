import os

sudoPassword = 'kali'

def get_disk_info():
    command =  'fdisk -l'
    print('Getting disk info')
    output = os.popen(f'echo {sudoPassword} | sudo -S %s'%(command)).read()
    # print(output)
    output = output.splitlines()
    disk_lines = []
    prefix = "Disk model: "
    for line_number, line in enumerate(output):
        if prefix in line:
            disk_lines.append(line_number)

    disk_info = []
    for i in range(len(disk_lines)):
        name_with_prefix = output[disk_lines[i]]
        disk_name = name_with_prefix[len(prefix):]
        start = disk_lines[i]
        if i < len(disk_lines) - 1:
            end = disk_lines[i+1] - 1
        else:
            end = len(output)
        partition_names = []
        for j in range(start, end):
            partition_index = output[j].find('/dev/')
            if partition_index >= 0:
                partition_name = output[j].split()[0]
                partition_names.append(partition_name)
        disk_info.append([disk_name, partition_names])
    print(disk_info)
    return disk_info

def create_disk_img(partition_path : str):
    file_name = os.path.basename(partition_path)
    command = f'dd if={partition_path} if={file_name}'
    output = os.popen('sudo -S %s' % (command)).read()

