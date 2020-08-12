import re
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
        if re.search('capture\d+.png',f, re.M | re.I) is not None:
            photos.append(os.path.join('static', f))
    return photos

@app.route('/delete_selected_photos',methods=['POST'])
def delete_selected_photos():

    image  = request.form['image']

    img    = re.sub('static/', '', image)

    p_dir  = '/home/pi/.motiondetection' 
    p_path = os.path.join(p_dir, img)

    l_dir  = 'static' 
    l_path = os.path.join(l_dir, img)

    try:
        os.remove(p_path)
        os.remove(l_path)
    except Exception as exception:
        pass

    return render_template("test.html", images=images())

@app.route('/')
def show_index():
    return render_template("test.html", images=images())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
