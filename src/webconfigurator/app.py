import os

from os import listdir
from os.path import isfile, join
from flask import Flask, render_template

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/delete_selected_photos/<images>',methods=['POST'])
def delete_selected_photos(images):
    print(request.data)
    #print(request.form['static/capture52.png'])
    images = []
    path  = 'static'
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for f in files:
        images.append(os.path.join(path, f))
    return render_template("test.html", images=images)

@app.route('/')
def show_index():
    images = []
    #path  = '/home/anthony/Pictures/capture'
    path  = 'static'
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for f in files:
        images.append(os.path.join(path, f))
    return render_template("test.html", images=images)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
