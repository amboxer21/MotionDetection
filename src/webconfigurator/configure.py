import re
from flask import Flask, render_template

app = Flask(__name__, template_folder="templates")

@app.route('/reload')
def reload():
    return "Reloading the MotionDetection framework!"

def extract_email(credentials):
    obj = str(credentials).split(",")
    if obj is not None:
        return obj[0]
    return str()

def extract_password(credentials):
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

@app.route('/configure/<credentials>')
def change_credentials(credentials):
    email  = extract_email(credentials)
    passwd = extract_password(credentials)
    if validate_email(email) and validate_password(passwd):
        return "Using %s as the system email address with password: %s." % email % passwd
    return render_template("invalid_credential_format.html")

if __name__ == '__main__':
    app.run(debug = True,host='0.0.0.0')
