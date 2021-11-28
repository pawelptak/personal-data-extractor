import os
import csv
sudoPassword = 'kali'
import pandas as pd
import numpy as np

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
    if files is None:
        # files = ['domain.txt', 'email.txt', 'ip.txt', 'telephone.txt', 'url.txt', 'ccn.txt']
        files = ['domain.txt', 'email.txt', 'ip.txt', 'url.txt', 'ccn.txt', 'telephone_histogram.txt']

    print(f"Converting {data_dir_path} to csv...")
    for file_name in os.listdir(data_dir_path):
        file_path = os.path.join(data_dir_path, file_name)
        if file_name in files:
            if os.path.getsize(file_path) > 0:
                extracted = []
                with open(file_path) as file:
                    for line in file:
                        if not line.startswith('#'):
                            parts = line.split()
                            if len(parts) > 1:
                                extracted.append(parts[1])

                output_dir_name = data_dir_path + '_csv'
                if not os.path.isdir(output_dir_name):
                    os.mkdir(output_dir_name)

                with open(os.path.join(output_dir_name, file_name.split('.')[0] + '.csv'), 'w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    unique_extracted = set(extracted)
                    for item in unique_extracted:
                        writer.writerow([item])

    print(f"Converting {data_dir_path} to csv - done.")


def get_partition_size(partition_path: str):
    command = f"fdisk -l {partition_path}"
    output = os.popen(f'echo {sudoPassword} | sudo -S %s' % (command)).read()
    output = output.splitlines()
    size = output[0][output[0].find(':') + 2:output[0].find(',')]
    return size


# get data from one partition
def get_bulk_partiton_data(data_dir_path: str):
    all_data = []
    for file_name in os.listdir(data_dir_path):
        file_path = os.path.join(data_dir_path, file_name)
        current_data = []
        with open(file_path, newline='') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                current_data.append(row[0])
        all_data.append([file_name.split('.')[0], current_data])
    print(all_data)
    return all_data


# get data from all partitions
def get_bulk_all_data(data_dir_path: str = '../extracted_data'):
    all_partition_data = []
    for i, dir_name in enumerate(os.listdir(data_dir_path)):
        if dir_name.endswith('_csv'):
            dir_path = os.path.join(data_dir_path, dir_name)
            all_partition_data.append([dir_name[:dir_name.find('_')], get_bulk_partiton_data(dir_path)])
    return all_partition_data


def remove_data(partition_name: str, data_dir_path: str = '../extracted_data', img_dir_path: str = '../disk_images'):
    for dir_name in os.listdir(data_dir_path):
        dir_path = os.path.join(data_dir_path, dir_name)
        if dir_name.startswith(partition_name):
            command = f"rm -r {dir_path}/*"
            print(f'Deleting all contents of {dir_path}')
            os.popen(f'echo {sudoPassword} | sudo -S %s' % (command))

            command = f"rm -d {dir_path}"
            os.popen(f'echo {sudoPassword} | sudo -S %s' % (command))

    for file_name in os.listdir(img_dir_path):
        file_path = os.path.join(img_dir_path, file_name)
        if file_name.startswith(partition_name):
            command = f"rm {file_path}"
            print(f'Deleting image {file_path}')
            os.popen(f'echo {sudoPassword} | sudo -S %s' % (command))

if __name__ == "__main__":
    # create_disk_img('/dev/sdb1')
    # bulk_extractor('../disk_images/sdb1.img')
    # bulk_extractor_data_to_csv('../extracted_data/sdb1')
    # get_bulk_csv_data('../extracted_data/sdb1_csv')
    # get_bulk_all_data()
    remove_data(partition_name='sdb1')
    pass