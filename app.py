import os
from flask import Flask, render_template, request, redirect
from scripts.disk_scripts import get_disk_info, get_partition_size, create_disk_img, bulk_extractor

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('index.html', data=disks_info)

@app.route("/partition/<id>", methods=['GET', 'POST'])
def show_disk_info(id):
    partition_details = []
    partition_name = ''
    for disk in disks_info:
        for partitions in disk[1]:
            if partitions[0] == int(id):
                partition_name = partitions[1]
                partition_details.append(partition_name)
                partition_details.append(get_partition_size(partitions[1]))
    print(partition_details)
    if request.method == "POST":
        if request.form.get('submit-button'):
            # checked_boxes = request.form.getlist('types')
            create_disk_img(partition_path=partition_name, output_path='./disk_images')
            bulk_extractor(image_file_path=f'./disk_images/{os.path.basename(partition_name)}.img', output_directory='./extracted_data')
            return redirect("/")



    return render_template('partition_details.html', data=partition_details)

def extraction_btn_listener():
    if request.form.get('submit-button'):
        print('hello')

if __name__ == '__main__':
    disks_info = get_disk_info()
    app.run(debug=True)
