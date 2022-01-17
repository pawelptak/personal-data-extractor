import os
import csv
import time
import uuid
import json
from datetime import datetime
from settings_development import sudoPassword
import pandas as pd
from fpdf import FPDF
import hashlib
import subprocess


def get_disk_info():
    command = 'fdisk -l'
    print('Getting disk info')
    output = os.popen(f'echo {sudoPassword} | sudo -S %s' % (command)).read()
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
            end = disk_lines[i + 1] - 1
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


def create_disk_img(partition_path: str, output_path: str = '../disk_images'):
    unmount_disk_image()
    partition_id = str(uuid.uuid4())
    output_path = os.path.join(output_path, partition_id)
    if not os.path.isdir(output_path):
        os.mkdir(output_path)
    file_name = os.path.basename(partition_path)
    command = f"dd if={partition_path} of={output_path}/{file_name}.img"
    print(f'Creating image of partition {file_name}...')
    output = os.popen(f'echo {sudoPassword} | sudo -S %s' % (command)).read()
    print('Image created.')
    curr_datetime = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    f_path = os.path.join(output_path, f'{curr_datetime}_date')
    with open(f_path, 'w') as f:
        pass
    return partition_id


def bulk_extractor(images_dir: str, partition_id: str):
    img_dir = os.path.join(images_dir, partition_id)
    img_fname = [x for x in os.listdir(img_dir) if x.endswith('img')][0]
    image_path = os.path.join(img_dir, img_fname)
    output_dir = os.path.join(img_dir, 'extracted_data')
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    command = f"bulk_extractor -R -o {output_dir} {image_path}"
    sudo_command = f'echo {sudoPassword} | sudo -S %s' % (command)
    print(f'Bulk-extractor: extracting data from {image_path}')
    p = subprocess.Popen(sudo_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
        # returns None while subprocess is running
        retcode = p.poll()
        line = p.stdout.readline().replace(b'\n', b'').decode('UTF-8')
        yield line
        if retcode is not None:
            break


def bulk_extractor_data_to_csv(images_dir: str, partition_id: str, files=None):
    img_dir = os.path.join(images_dir, partition_id)
    data_dir_path = os.path.join(img_dir, 'extracted_data')
    if files is None:
        files = ['domain_histogram.txt', 'email_histogram.txt', 'ip.txt', 'url_histogram.txt', 'ccn_histogram.txt',
                 'telephone_histogram.txt']

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
                            if len(parts) > 1 and '\x00' not in parts[1]:
                                extracted.append(parts[1])

                output_dir_name = data_dir_path + '_csv'
                if not os.path.isdir(output_dir_name):
                    os.mkdir(output_dir_name)

                output_filename = file_name[:file_name.find('_')] + '.csv'
                with open(os.path.join(output_dir_name, output_filename), 'w', newline='') as csv_file:
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
def get_partiton_csv_data(images_dir: str, partition_id: str):
    all_data = {}
    img_dir = os.path.join(images_dir, partition_id, 'extracted_data_csv')
    for file_name in os.listdir(img_dir):
        file_path = os.path.join(img_dir, file_name)
        current_data = []
        if 'exif.csv' not in file_name:
            with open(file_path, newline='') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    current_data.append(row[0])
            all_data[file_name.split('.')[0]] = current_data
        else:
            df = pd.read_csv(file_path)
            js = df.to_json(orient='records')
            parsed = json.loads(js)
            all_data['exif'] = parsed
    print(all_data)
    return all_data


# get data from all partitions
def get_all_csv_data(data_dir_path: str = '../disk_images'):
    all_partition_data = {}
    for id_dir in os.listdir(data_dir_path):
        id_dir_path = os.path.join(data_dir_path, id_dir)
        if os.path.isdir(id_dir_path):
            partition_id = os.path.basename(id_dir_path)
            creation_date = [fname[:fname.rfind('_')] for fname in os.listdir(id_dir_path) if fname.endswith('_date')]
            if creation_date:
                creation_date = creation_date[0].split('-')
                creation_date = f'{creation_date[0]}.{creation_date[1]}.{creation_date[2]} {creation_date[3]}:{creation_date[4]}:{creation_date[5]}'
            else:
                creation_date = 'N/A'
            for file in os.listdir(id_dir_path):
                if file.endswith('_csv'):
                    all_partition_data.update({partition_id: {"creation_date": creation_date,
                                                              "name": get_partition_name_from_id(data_dir_path,
                                                                                                 partition_id),
                                                              "data": get_partiton_csv_data(data_dir_path,
                                                                                            partition_id)}})
                    # all_partition_data["id"].update({partition_id: get_partiton_csv_data(dir_path)})
    print(all_partition_data)
    return all_partition_data


def mount_disk_image(disk_img_path):
    if not os.path.exists('/mnt/mountpoint'):
        command = "mkdir /mnt/mountpoint"
        os.popen(f'echo {sudoPassword} | sudo -S %s' % (command))

    if os.listdir('/mnt/mountpoint'):
        print('Image already mounted')
        return
    else:
        command = f"mount {disk_img_path} /mnt/mountpoint -o loop,ro"
        print(f'Mounting disk image {disk_img_path}')
        os.popen(f'echo {sudoPassword} | sudo -S %s' % (command))
        while not os.listdir('/mnt/mountpoint'):
            time.sleep(.5)
        print('Mounting done')


def unmount_disk_image():
    if not os.path.exists('/mnt/mountpoint'):
        command = "mkdir /mnt/mountpoint"
        os.popen(f'echo {sudoPassword} | sudo -S %s' % (command))

    if not os.listdir('/mnt/mountpoint'):
        print('Image already unmounted')
        return
    else:
        command = "umount /mnt/mountpoint"
        print('Unmounting disk image')
        os.popen(f'echo {sudoPassword} | sudo -S %s' % (command))
        while os.listdir('/mnt/mountpoint'):
            time.sleep(.5)
        print('Unmounting done')


def get_partition_name_from_id(data_dir_path: str, partition_id: str):
    partition_name = ""
    for id_dir in os.listdir(data_dir_path):
        id_dir_path = os.path.join(data_dir_path, id_dir)
        if os.path.isdir(id_dir_path):
            part_id = os.path.basename(id_dir_path)
            if part_id == partition_id:
                partition_file_name = [x for x in os.listdir(id_dir_path) if x.endswith('.img')][0]
                partition_name = partition_file_name[:partition_file_name.find('.')]
    return partition_name


def remove_data(data_dir_path: str, partition_id: str):
    folder = '/path/to/folder'

    for id_dir in os.listdir(data_dir_path):
        id_dir_path = os.path.join(data_dir_path, id_dir)
        if os.path.isdir(id_dir_path):
            part_id = os.path.basename(id_dir_path)
            if part_id == partition_id:
                # for filename in os.listdir(id_dir_path):
                #     file_path = os.path.join(folder, filename)
                #     command = f'rm -rf {file_path}'
                #     os.popen(f'echo {sudoPassword} | sudo -S %s' % (command))
                #     try:
                #         if os.path.isfile(file_path) or os.path.islink(file_path):
                #             print(f'Deleting file {file_path}')
                #             os.unlink(file_path)
                #         elif os.path.isdir(file_path):
                #             print(f'Deleting directory {file_path}')
                #             shutil.rmtree(file_path)
                #     except Exception as e:
                #         print('Failed to delete %s. Reason: %s' % (file_path, e))
                print(f'Deleting directory {id_dir_path}')
                command = f'rm -rf {id_dir_path}'
                os.popen(f'echo {sudoPassword} | sudo -S %s' % (command))
                while os.path.isdir(id_dir_path):
                    time.sleep(.5)
                # shutil.rmtree(id_dir_path)


def make_hash(filename):
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    # open file for reading in binary mode
    with open(filename, 'rb') as file:
        # loop till the end of the file
        chunk = 0
        while chunk != b'':
            # read only 1024 bytes at a time
            chunk = file.read(1024)
            sha1.update(chunk)
            md5.update(chunk)

    # return the hex representation of digest
    return sha1.hexdigest(), md5.hexdigest()


def save_hash_sum(output, hash, hashname):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, hash, 0, 1)
    pdf.output(os.path.join(output, f'{hashname}.pdf'))


def generate_report_pdf(partition_id, images_dir, out_dir):
    img_dir = os.path.join(images_dir, partition_id)
    partition_name = get_partition_name_from_id(images_dir, partition_id)
    creation_date = [fname[:fname.rfind('_')] for fname in os.listdir(img_dir) if fname.endswith('_date')][0]
    creation_date = creation_date.split('-')
    creation_date = f'{creation_date[0]}.{creation_date[1]}.{creation_date[2]} {creation_date[3]}:{creation_date[4]}:{creation_date[5]}'

    img_path = os.path.join(img_dir, f'{partition_name}.img')
    img_size = os.path.getsize(img_path)
    json_data = get_partiton_csv_data(images_dir=images_dir, partition_id=partition_id)

    val_sum = 0
    for k, v in json_data.items():
        for _ in v:
            val_sum += 1

    report_creation_date = datetime.today()

    out_dir = os.path.join(out_dir, partition_id)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_file = os.path.join(out_dir, 'report.pdf')

    print(f'Generating report for ID: {partition_id}')
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 10, txt=f'Report date: {report_creation_date.strftime("%d.%m.%Y %H:%M:%S")}', ln=1, align='C')
    pdf.cell(0, 10, txt=f'Partition: {partition_name}', ln=2, align='L')
    pdf.cell(0, 10, txt=f'Size: {img_size} B', ln=2, align='L')
    pdf.cell(0, 10, txt=f'Image created on: {creation_date}', ln=2, align='L')
    pdf.cell(0, 10, txt=f'Data found: {val_sum}', ln=2, align='L')

    for k, v in json_data.items():
        pdf.cell(0, 10, 20 * '_', 0, 1)
        pdf.set_font("Arial", "B", size=10)
        pdf.cell(0, 10, f'{k.upper()}: {len(v)}', 0, 1)
        pdf.set_font("Arial", size=10)

        for item in v:
            if 'exif' in k:
                for exif_name, exif_value in item.items():
                    if exif_value:
                        pdf.cell(0, 10, f'{exif_name}: {exif_value}', 0, 1)
                pdf.cell(0, 10, '', 0, 1)
            else:
                pdf.cell(0, 10, f'{item}', 0, 1)

    # save the pdf with name .pdf
    pdf.output(out_file)

    os.system(f'xdg-open {os.path.abspath(out_dir)}')

    sha1, md5 = make_hash(out_file)
    save_hash_sum(out_dir, sha1, "sha1")
    save_hash_sum(out_dir, md5, "md5")


if __name__ == "__main__":
    # get_disk_info()
    # img_id = create_disk_img('/dev/sdd1')
    # bulk_extractor(images_dir='../disk_images', partition_id=img_id)
    # bulk_extractor_data_to_csv(images_dir='../disk_images', partition_id=img_id)
    # get_all_csv_data()
    # js = get_partiton_csv_data(images_dir='../disk_images/', partition_id="d5ab6ff5-152e-42e9-9505-1459f685f09a")

    #generate_report_pdf("d5ab6ff5-152e-42e9-9505-1459f685f09a", '../disk_images', '../reports')
    # name = get_partition_name_from_id(data_dir_path='../disk_images', partition_id="22e6d54c-d5b6-4e36-8536-83c996eeeba3")
    # print(name)

    # remove_data(data_dir_path='../disk_images', partition_id="e2136eb0-59a6-4b77-9f5d-835d5c1812ed")

    #output = run(ful_cmd, capture_output=True).stdout


    pass
