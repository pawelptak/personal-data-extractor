# requires https://github.com/openalpr/openalpr/wiki/Compilation-instructions-(Ubuntu-Linux)#the-easy-way
# (14.12.2021) only "The Easy Way" working

import json
import os

from disk_scripts import mount_disk_image, unmount_disk_image


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
        data['plate_numbers'] = plate_numbers
        return data


def find_image_files(path):
    command = 'find {disk_img_path} -type f -print0 | xargs -0 file --mime-type | grep -i image | cut -f 1 -d :'
    command = command.replace('{disk_img_path}', path)
    print(f'Searching for image files in {path}')
    output = os.popen(command).read().split()
    return output


if __name__ == "__main__":
    img_path = 'audi2.jpg'
    data = get_license_plates(img_path)
    print(data)

    mount_disk_image('../disk_images/sdb1.img')
    img_files = find_image_files('/mnt/mountpoint')
    for img_file in img_files:
        print(get_license_plates(img_file))
    unmount_disk_image()

