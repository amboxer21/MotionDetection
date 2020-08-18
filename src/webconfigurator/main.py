import re
import os
import time
import fcntl
import select
import threading
import subprocess

from os import listdir
from os.path import isfile, join
from flask import Flask, render_template

from flask import Flask, render_template, request, redirect, url_for

main = Flask(__name__, template_folder="templates")

class MotionDetection(object):

    LINES = []
    COUNT = 0
    LOCK  = threading.Semaphore()

    @classmethod
    def images(cls):
        photos = []
        files  = [f for f in listdir('static') if isfile(join('static', f))]
        for f in files:
            if re.search('capture\d+.png',f, re.M | re.I) is not None:
                photos.append(os.path.join('static', f))
        return photos

    @staticmethod
    def threaded(proc,*args):
        try:
            t = threading.Thread(target=proc,args=args)
            t.daemon = True
            t.start()
        except Exception as exception:
            print('threaded Exception => '+str(exception))

    @classmethod
    def flatten(cls,array):
        return [a for b in array for a in b]

    @classmethod
    def get_logs(cls):
        MotionDetection.COUNT += 500
        return cls.LINES[MotionDetection.COUNT:MotionDetection.COUNT+500] 

    @classmethod
    def load_logs(cls):
        with open("/var/log/motiondetection.log", "r") as f:
            for line in f.read().splitlines():
                cls.LINES.append(line)
            if not cls.LINES:
                cls.LINES.append('Nothing to show here!')
        return cls.LINES

    @classmethod
    def write_config_file_into_hash(cls,hash=dict()):
        with open('/etc/motiondetection/motiondetection.cfg','w') as f:
            for key,value in hash.items():
                f.write(key+"="+value+"\n")

    # D.R.Y This methods needs tightening
    @classmethod
    def read_config_file_into_hash(cls,hash=dict()):
        with open('/etc/motiondetection/motiondetection.cfg','r') as line:
            for f in line.read().splitlines():
    
                ip = re.search('^ip=(.*)', f, re.M | re.I)
                if ip is not None:
                    hash['ip'] = ip.group(1)
                else:
                    try:
                        if not hash['ip']:
                            pass 
                    except KeyError:
                        hash['ip'] = 'IP Address...'
                        pass
    
                verbose = re.search('^verbose=(.*)', f, re.M | re.I)
                if verbose is not None:
                    hash['verbose'] = verbose.group(1)
                else:
                    try:
                        if not hash['verbose']:
                            pass
                    except KeyError:
                        hash['verbose'] = 'Verbose...'
                        pass
    
                email_port = re.search('^email_port=(.*$)',f, re.M | re.I)
                if email_port is not None:
                    hash['email_port'] = email_port.group(1)
                else:
                    try:
                        if not hash['email_port']:
                            pass
                    except KeyError:
                        hash['email_port'] = 'E-mail Address...'
                        pass
        
                logfile = re.search('^logfile=(.*$)', f, re.M | re.I)
                if logfile is not None:
                    hash['logfile'] = logfile.group(1)
                else:
                    try:
                        if not hash['logfile']:
                            pass
                    except KeyError:
                        hash['logfile'] = 'Log File Path...'
                        pass
        
                disable_email = re.search('^disable_email=(.*$)', f, re.M | re.I)
                if disable_email is not None:
                    hash['disable_email'] = disable_email.group(1)
                else:
                    try:
                        if not hash['disable_email']:
                            pass
                    except KeyError:
                        hash['disable_email'] = 'Disable E-mail...'
                        pass
        
                configfile = re.search('^configfile=(.*$)', f, re.M | re.I)
                if configfile is not None:
                    hash['configfile'] = configfile.group(1)
                else:
                    try:
                        if not hash['configfile']:
                            pass
                    except KeyError:
                        hash['configfile'] = 'Configuration File Path...'
                        pass
        
                cam_location = re.search('^cam_location=(.*$)', f, re.M | re.I)
                if cam_location is not None:
                    hash['cam_location'] = cam_location.group(1)
                else:
                    try:
                        if not hash['cam_location']:
                            pass
                    except KeyError:
                        hash['cam_location'] = 'Camera Location...'
                        pass
        
                fps = re.search('^fps=(.*$)', f, re.M | re.I)
                if fps is not None:
                    hash['fps'] = fps.group(1)
                else:
                    try:
                        if not hash['fps']:
                            pass
                    except KeyError:
                        hash['fps'] = 'Camera\'s Frames Per Second...'
                        pass
    
                email = re.search('^email=(.*$)',f, re.M | re.I)
                if email is not None:
                    hash['email'] = email.group(1)
                else:
                    try:
                        if not hash['email']:
                            pass
                    except KeyError:
                        hash['email'] = 'E-mail Address...'
                        pass
    
        
                password = re.search('^password=(.*$)', f, re.M | re.I)
                if password is not None:
                    hash['password'] = password.group(1)
                else:
                    try:
                        if not hash['password']:
                            pass
                    except KeyError:
                        hash['password'] = 'Password...'
                        pass
        
                camview_port = re.search('^camview_port=(.*$)', f, re.M | re.I)
                if camview_port is not None:
                    hash['camview_port'] = camview_port.group(1)
                else:
                    try:
                        if not hash['camview_port']:
                            pass
                    except KeyError:
                        hash['camview_port'] = 'SecureView Port...'
                        pass
        
                delta_thresh_min = re.search('^delta_thresh_min=(.*$)', f, re.M | re.I)
                if delta_thresh_min is not None:
                    hash['delta_thresh_min'] = delta_thresh_min.group(1)
                else:
                    try:
                        if not hash['delta_thresh_min']:
                            pass
                    except KeyError:
                        hash['delta_thresh_min'] = 'Delta Threshold Minimum...'
                        pass
        
                delta_thresh_max = re.search('^delta_thresh_max=(.*$)', f, re.M | re.I)
                if delta_thresh_max is not None:
                    hash['delta_thresh_max'] = delta_thresh_max.group(1)
                else:
                    try:
                        if not hash['delta_thresh_max']:
                            pass
                    except KeyError:
                        hash['delta_thresh_max'] = 'Delta Threshold Minimum...'
                        pass
        
                burst_mode_opts = re.search('^burst_mode_opts=(.*$)', f, re.M | re.I)
                if burst_mode_opts is not None:
                    hash['burst_mode_opts'] = burst_mode_opts.group(1)
                else:
                    try:
                        if not hash['burst_mode_opts']:
                            pass
                    except KeyError:
                        hash['burst_mode_opts'] = 'Burst Mode Count...'
                        pass
        
                motion_thresh_min = re.search('^motion_thresh_min=(.*$)', f, re.M | re.I)
                if motion_thresh_min is not None:
                    hash['motion_thresh_min'] = motion_thresh_min.group(1)
                else:
                    try:
                        if not hash['motion_thresh_min']:
                            pass
                    except KeyError:
                        hash['motion_thresh_min'] = 'Motion Threshold Minimum...'
                        pass
        
                server_port = re.search('^server_port=(.*$)', f, re.M | re.I)
                if server_port is not None:
                    hash['server_port'] = server_port.group(1)
                else:
                    hash['server_port'] = 'Server Port...'
                    
            return hash

    @classmethod
    def remove_photos(cls,paths=[]):
        [os.remove(path) for path in paths if '/capture' in path]

@main.route('/get_logs_wrapper')
def get_logs_wrapper():
    buffer = []
    for line in MotionDetection.get_logs():
        buffer.append(str(line)+'<br>') 
    return str(buffer[:-1])

@main.route('/delete_selected_photos',methods=['POST'])
def delete_selected_photos():

    img    = request.form['image']

    image  = re.sub('static/', '', img)

    p_dir  = '/home/pi/.motiondetection' 
    p_path = os.path.join(p_dir, image)

    l_dir  = 'static' 
    l_path = os.path.join(l_dir, image)

    try:
        MotionDetection.threaded(MotionDetection.remove_photos,[p_path, l_path])
    except Exception as exception:
        pass

    return render_template("photos.html", images=MotionDetection.images())

@main.route('/photos')
def photos():
    return render_template("photos.html", images=MotionDetection.images())

@main.route('/clear_logs',methods=['POST'])
def clear_logs():
    with open("/var/log/motiondetection.log", "w") as f:
        f.write("")
    return render_template("logs.html",lines=MotionDetection.get_logs())

@main.route('/logs')
def logs():
    return render_template("logs.html",lines=MotionDetection.get_logs())

@main.route('/reload',methods=['POST'])
def reload_framework(hash=dict()):
    hash['ip']                = request.form['ip']
    hash['fps']               = request.form['fps']
    hash['verbose']           = request.form['verbose']
    hash['email_port']        = request.form['email_port']
    hash['logfile']           = request.form['logfile']
    hash['disable_email']     = request.form['disable_email']
    hash['configfile']        = request.form['configfile']
    hash['cam_location']      = request.form['cam_location']
    hash['email']             = request.form['email']
    hash['password']          = request.form['password']
    hash['camview_port']      = request.form['camview_port']
    hash['delta_thresh_min']  = request.form['delta_thresh_min']
    hash['delta_thresh_max']  = request.form['delta_thresh_max']
    hash['burst_mode_opts']   = request.form['burst_mode_opts']
    hash['motion_thresh_min'] = request.form['motion_thresh_min']
    hash['server_port']       = request.form['server_port']
    MotionDetection.write_config_file_into_hash(hash)
    return render_template('configure.html',value=MotionDetection.read_config_file_into_hash())

@main.route('/configure', methods=['GET', 'POST'])
def configure():
    return render_template('configure.html',value=MotionDetection.read_config_file_into_hash())


@main.route('/')
def index():
    return render_template("main.html")

if __name__ == '__main__':
    MotionDetection.threaded(MotionDetection.load_logs)
    time.sleep(5)
    main.run(debug=True, host='0.0.0.0',port=80)
