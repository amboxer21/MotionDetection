import re
from flask import Flask, render_template

app = Flask(__name__, template_folder="templates")

def extract_email(credentials):
    obj = str(credentials).split(",")
    if obj is not None:
        return obj[0]
    return credentials

def extract_password(credentials):
    obj = str(credentials).split(",")
    if obj is not None:
        return obj[1]
    return credentials 

def validate_email(email):
    addr = re.search('(\A[\w+\.\-]+)(@)(\w+)(\.)(\w+)\Z', str(email), re.M | re.I)
    if addr is not None:
        return True
    return False 

def validate_password(password):
    passwd = re.search('\A\w+\Z', str(password), re.M | re.I)
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
    app.run(debug = True)
