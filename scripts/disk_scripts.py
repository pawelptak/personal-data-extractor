import os
import csv
sudoPassword = 'kali'


def get_disk_info():
    command = 'fdisk -l'
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
    partition_id = 0
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
                partition_names.append([partition_id, partition_name])
                partition_id += 1
        disk_info.append([disk_name, partition_names])
    print(disk_info)
    return disk_info


def create_disk_img(partition_path : str, output_path: str = '../disk_images'):
    file_name = os.path.basename(partition_path)
    command = f"dd if={partition_path} of={output_path}/{file_name}.img"
    print(f'Creating image of partition {file_name}...')
    output = os.popen(f'echo {sudoPassword} | sudo -S %s' % (command)).read()
    print('Image created.')
    return output


def bulk_extractor(image_file_path: str, output_directory: str = '../extracted_data'):
    file_name = os.path.basename(image_file_path).split('.')[0]
    command = f"bulk_extractor -R -o {output_directory}/{file_name} {image_file_path}"
    print(f'Bulk-extractor: extracting data from {image_file_path}')
    output = os.popen(f'echo {sudoPassword} | sudo -S %s' % (command)).read()
    print('Bulk-extractor: Data extracted.')

def bulk_extractor_data_to_csv(data_dir_path: str, files=None):
    dir_name = os.path.basename(data_dir_path).split('.')[0]

    if files is None:
        # files = ['domain.txt', 'email.txt', 'ip.txt', 'telephone.txt', 'url.txt', 'ccn.txt']
        files = ['domain.txt', 'email.txt', 'ip.txt', 'url.txt', 'ccn.txt']

    for file_name in os.listdir(data_dir_path):
        file_path = os.path.join(data_dir_path, file_name)
        if file_name in files:
            extracted = []
            if os.path.getsize(file_path) > 0:
                with open(file_path) as file:
                    for line in file:
                        if not line.startswith('#'):
                            parts = line.split()
                            if len(parts) > 1:
                                extracted.append(parts[1])

                output_dir_name = '../extracted_data/' + dir_name + '_csv'
                if not os.path.isdir(output_dir_name):
                    os.mkdir(output_dir_name)
                with open(os.path.join(output_dir_name, file_name.split('.')[0] + '.csv'), 'w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    unique_extracted = set(extracted)
                    for item in unique_extracted:
                        writer.writerow([item])

def get_partition_size(partition_path: str):
    command = f"fdisk -l {partition_path}"
    print(f"{partition_path}: getting partition info...")
    output = os.popen(f'echo {sudoPassword} | sudo -S %s' % (command)).read()
    output = output.splitlines()
    size = output[0][output[0].find(':') + 2:output[0].find(',')]
    return size

if __name__ == "__main__":
    # create_disk_img('/dev/sdb1')
    #bulk_extractor_data_to_csv('../extracted_data/sdb1')
    pass