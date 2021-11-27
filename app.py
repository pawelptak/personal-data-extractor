from flask import Flask, render_template
from scripts.get_disk_info import get_disk_info

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('index.html', data=get_disk_info())


if __name__ == '__main__':
    app.run(debug=True)
