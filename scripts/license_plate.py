# requires https://github.com/openalpr/openalpr/wiki/Compilation-instructions-(Ubuntu-Linux)#the-easy-way
# As for 14.12.2021 only "The Easy Way" working

import json
import os
import csv
import time

from scripts.disk_scripts import mount_disk_image, unmount_disk_image, get_partition_name_from_id

def get_license_plates(img_path):
    command = f"alpr -c eu -j {img_path}"
    file_name = os.path.basename(img_path)
    if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        print('Not image file')
        return {}
    else:
        print(f'Searching for license plates in {img_path}')
        output = os.popen(command).read()
        json_output = json.loads(output)
        data = {}
        data['image_name'] = file_name
        plate_numbers = []
        for result in json_output["results"]:
            plate_number = result["plate"]
            confidence = result["confidence"]
            # print(plate_number, confidence)
            plate_numbers.append(plate_number)
        if plate_numbers:
            data['plate_numbers'] = plate_numbers
            return data
        else:
            return 0


def find_image_files(path):
    command = 'find {disk_img_path} -type f -print0 | xargs -0 file --mime-type | grep -i image | cut -f 1 -d :'
    command = command.replace('{disk_img_path}', path)
    print(f'Searching for image files in {path}')
    output = os.popen(command).read().split()
    return output


def license_plate_data_to_csv(data_dir_path: str, partition_id: str):
    img_filename = get_partition_name_from_id(data_dir_path, partition_id) + ".img"
    disk_image_path = os.path.join(data_dir_path, partition_id, img_filename)
    mount_disk_image(disk_image_path)
    img_files = find_image_files('/mnt/mountpoint')
    extracted_jsons = []
    for img_file in img_files:
        extracted_plates = get_license_plates(img_file)
        if extracted_plates != 0:
            extracted_jsons.append(extracted_plates)
    print(extracted_jsons)
    unmount_disk_image()

    output_csv_path = os.path.join(data_dir_path, partition_id, 'extracted_data_csv')
    if not os.path.isdir(output_csv_path):
        os.mkdir(output_csv_path)

    print(f"Saving license plate data from {disk_image_path} to csv...")
    with open(os.path.join(output_csv_path, 'license_plates.csv'), 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for js in extracted_jsons:
            writer.writerow([f"{js['plate_numbers']} ({js['image_name']})"])


if __name__ == "__main__":
    img_path = 'audi3.jpg'
    data = get_license_plates(img_path)
    print(data)
    #license_plate_data_to_csv(data_dir_path='../disk_images/', partition_id="25410c57-fd06-4ae9-b9f6-ec2bb237a0e5")
    #print(get_license_plates('nissan.jpg'))


