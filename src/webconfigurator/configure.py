import re
from flask import Flask, render_template

config = Flask(__name__, template_folder="templates")

def write_config_file_into_hash():
    pass

def read_config_file_into_hash(hash=dict()):
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


def email(credentials):
    obj = str(credentials).split(",")
    if obj is not None:
        return obj[0]
    return str()

def password(credentials):
    obj = str(credentials).split(",")
    if obj is not None:
        return obj[1]
    return str() 

def validate_email(email):
    regex = '(\A[\w+\.\-]+)(@)(\w+)(\.)(\w+)\Z'
    addr  = re.search(regex, str(email), re.M | re.I)
    if addr is not None:
        return True
    return False 

def validate_password(password):
    regex  = '\A\w+\Z'
    passwd = re.search(regex, str(password), re.M | re.I)
    if passwd is not None:
        return True
    return False

@config.route('/reload')
def reload_framework():
    return "Reloading the MotionDetection framework!"

@config.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html',value=read_config_file_into_hash())

if __name__ == '__main__':
    config.run(debug=True, host='0.0.0.0')
