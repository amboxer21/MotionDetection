import re
from flask import Flask, render_template

config = Flask(__name__, template_folder="templates")

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

@config.route('/configure/<credentials>',methods=['POST'])
def update_credentials(credentials):
    addr   = email(credentials)
    passwd = password(credentials)
    if validate_email(addr) and validate_password(passwd):
        return "Using %s as the system email address with password: %s." % (addr, passwd)
    return render_template("invalid_credential_format.html")

if __name__ == '__main__':
    config.run(debug=True, host='0.0.0.0')
