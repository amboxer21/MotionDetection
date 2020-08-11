import os

from os import listdir
from os.path import isfile, join
from flask import Flask, render_template

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def images(photos=[]):
    photos.clear()
    files = [f for f in listdir('static') if isfile(join('static', f))]
    for f in files:
        photos.append(os.path.join('static', f))
    return photos

@app.route('/delete_selected_photos',methods=['POST'])
def delete_selected_photos():

    cwd  = os.getcwd()
    img  = request.form['image']
    path = os.path.join(cwd, img)

    print(img)
    if os.path.isfile(path) or os.path.islink(path):
        os.remove(path)
    return render_template("test.html", images=images())

@app.route('/')
def show_index():
    return render_template("test.html", images=images())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
