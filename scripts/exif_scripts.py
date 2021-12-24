# requires https://exiftool.org

import os
import json

def get_exif(img_path):
    command = f"exiftool {img_path} -a -exif:all"
    file_name = os.path.basename(img_path)
    if not file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        print('Not image file')
        return {}
    else:
        print(f'Extracting exif from {img_path}')
        output = os.popen(command).read()
        if output:
            print(output)
        else:
            print('No exif data found.')

if __name__ == "__main__":
    get_exif('zrybom.jpg')
