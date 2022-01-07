# requires https://exiftool.org

import os
import pandas as pd
from scripts.disk_scripts import mount_disk_image, unmount_disk_image, get_partition_name_from_id


def exif_to_csv(data_dir_path: str, partition_id: str):
    img_filename = get_partition_name_from_id(data_dir_path, partition_id) + ".img"
    disk_image_path = os.path.join(data_dir_path, partition_id, img_filename)
    mount_disk_image(disk_image_path)

    output_csv_path = os.path.join(data_dir_path, partition_id, 'extracted_data_csv')
    if not os.path.isdir(output_csv_path):
        os.mkdir(output_csv_path)

    output_csv_fpath = os.path.join(output_csv_path, 'exif.csv')
    command = f"exiftool -exif:all -csv -r /mnt/mountpoint -ext png -ext jpg -ext jpeg -ext tiff -ext bmp -ext gif > {output_csv_fpath}"
    print(f"Saving exif data from {disk_image_path} to csv...")
    os.popen(command).read()
    remove_rows_with_no_data(output_csv_fpath)
    unmount_disk_image()


def remove_rows_with_no_data(df_path):
    df = pd.read_csv(df_path)
    print(df)
    mask = len(df.columns) - df.isnull().sum(axis=1) > 1
    df = df[mask]
    if len(df) > 0:
        df.to_csv(df_path, index=False)
    else:
        os.remove(df_path)

if __name__ == "__main__":
    #exif_to_csv('../disk_images', '98b59a39-03f5-494c-9a65-c80a3d608a0e')
    remove_rows_with_no_data('../disk_images/442bb4e5-7c00-4cde-a13b-b441ea7f31c5/extracted_data_csv/exif.csv')