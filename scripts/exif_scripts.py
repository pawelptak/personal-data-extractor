# requires https://exiftool.org

import os

from scripts.disk_scripts import mount_disk_image, unmount_disk_image, get_partition_name_from_id


def exif_to_csv(data_dir_path: str, partition_id: str):
    img_filename = get_partition_name_from_id(data_dir_path, partition_id) + ".img"
    disk_image_path = os.path.join(data_dir_path, partition_id, img_filename)
    mount_disk_image(disk_image_path)

    output_csv_path = os.path.join(data_dir_path, partition_id, 'extracted_data_csv')
    if not os.path.isdir(output_csv_path):
        os.mkdir(output_csv_path)

    command = f"exiftool -exif:all -csv -r /mnt/mountpoint -ext png -ext jpg -ext jpeg -ext tiff -ext bmp -ext gif > {os.path.join(output_csv_path, 'exif.csv')}"
    print(f"Saving exif data from {disk_image_path} to csv...")
    os.popen(command).read()
    unmount_disk_image()


if __name__ == "__main__":
    exif_to_csv('../disk_images', '98b59a39-03f5-494c-9a65-c80a3d608a0e')