import re
import os
import time
import logging
import logging.handlers

from flask import Flask, render_template

class ConfigurationFile(object):

    @staticmethod
    def contents():
        return ("ip=0.0.0.0\nverbose=True\nemail_port=587\n"
        "logfile=/var/log/motiondetection.log\ndisable_email=False\n"
        "configfile=/etc/motiondetection/motiondetection.cfg"
        "cam_location=0\nfps=30\nemail=sshmonitorapp@gmail.com\n"
        "password=hkeyscwhgxjzafvj\ncamview_port=5000\ndelta_thresh_min=1500\n"
        "delta_thresh_max=10000\nburst_mode_opts=5\nmotion_thresh_min=500\nserver_port=50050")

class Logging(object):

    @staticmethod
    def log(level,message,verbose=True):
        comm = re.search("(WARN|INFO|ERROR)", str(level), re.M)
        try:
            handler = logging.handlers.WatchedFileHandler(
                os.environ.get("LOGFILE","/var/log/motiondetection.log")
            )
            formatter = logging.Formatter(logging.BASIC_FORMAT)
            handler.setFormatter(formatter)
            root = logging.getLogger()
            root.setLevel(os.environ.get("LOGLEVEL", str(level)))
            root.addHandler(handler)
            # Log all calls to this class in the logfile no matter what.
            if comm is None:
                print(str(level) + " is not a level. Use: WARN, ERROR, or INFO!")
                return
            elif comm.group() == 'ERROR':
                logging.error(str(time.asctime(time.localtime(time.time()))
                    + " - MotionDetection.webconfigurator - "
                    + str(message)))
            elif comm.group() == 'INFO':
                logging.info(str(time.asctime(time.localtime(time.time()))
                    + " - MotionDetection.webconfigurator - "
                    + str(message)))
            elif comm.group() == 'WARN':
                logging.warning(str(time.asctime(time.localtime(time.time()))
                    + " - MotionDetection.webconfigurator - "
                    + str(message)))
            if verbose or str(level) == 'ERROR':
                print("(" + str(level) + ") "
                    + str(time.asctime(time.localtime(time.time()))
                    + " - MotionDetection.webconfigurator - "
                    + str(message)))
        except IOError as eIOError:
            if re.search('\[Errno 13\] Permission denied:', str(eIOError), re.M | re.I):
                print("(ERROR) MotionDetection.webconfigurator - Must be sudo to run the webconfigurator!")
                sys.exit(0)
            print("(ERROR) MotionDetection.webconfigurator - IOError in Logging class => "
                + str(eIOError))
            logging.error(str(time.asctime(time.localtime(time.time()))
                + " - MotionDetection.webconfigurator - IOError => "
                + str(eIOError)))
        except Exception as eLogging:
            print("(ERROR) MotionDetection.webconfigurator - Exception in Logging class => "
                + str(eLogging))
            logging.error(str(time.asctime(time.localtime(time.time()))
                + " - MotionDetection.webconfigurator - Exception => "
                + str(eLogging)))
            pass
        return

class Configure(Flask):

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

    def run(self, **kwargs):
        super().run(**kwargs)

    def email(self,credentials):
        obj = str(credentials).split(",")
        if obj is not None:
            return obj[0]
        return str()
    
    def password(self,credentials):
        obj = str(credentials).split(",")
        if obj is not None:
            return obj[1]
        return str() 
    
    def validate_email(self, email):
        regex = '(\A[\w+\.\-]+)(@)(\w+)(\.)(\w+)\Z'
        addr  = re.search(regex, str(email), re.M | re.I)
        if addr is not None:
            return True
        return False 
    
    def validate_password(self, password):
        regex  = '\A\w+\Z'
        passwd = re.search(regex, str(password), re.M | re.I)
        if passwd is not None:
            return True
        return False
    
class FileOpts(object):

    def __init__(self,logfile='/var/log/motiondetection.log'):

        if not self.dir_exists(self.root_directory()):
            self.mkdir_p(self.root_directory())

        if not FileOpts.file_exists(logfile):
            FileOpts.create_file(logfile)

        if not FileOpts.file_exists("/etc/motiondetection/motiondetection.cfg"):
           FileOpts.create_file("/etc/motiondetection/motiondetection.cfg")
           self.populate_config_file(ConfigurationFile.contents())

    def root_directory(self):
        return "/etc/motiondetection"

    @staticmethod
    def file_exists(file_name):
        return os.path.isfile(file_name)

    @staticmethod
    def create_file(file_name):
        if FileOpts.file_exists(file_name):
            Logging.log("INFO", "(FileOpts.create_file) - File "
                + str(file_name)
                + " exists.")
            return
        Logging.log("INFO", "(FileOpts.create_file) - Creating file "
            + str(file_name)
            + ".")
        open(file_name, 'w')

    def dir_exists(self,dir_path):
        return os.path.isdir(dir_path)

    def mkdir_p(self,dir_path):
        try:
            Logging.log("INFO", "Creating directory " + str(dir_path))
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno == errno.EEXIST and self.dir_exists(dir_path):
                pass
            else:
                Logging.log("ERROR", "mkdir error: " + str(e))
                raise

    def populate_config_file(self,contents):
        Logging.log("WARN","(FileOpts.write_to_config_file) Populating configuration file with default options.")
        file_name = open('/etc/motiondetection/motiondetection.cfg', 'w')
        file_name.write(contents)
        file_name.close()

    def read_in_config_file(self):
        return open('/etc/motiondetection/motiondetection.cfg', 'r').read()

    def overwrite_config_options(self,**kwargs):
        content = self.read_in_config_file()
        new_content = content 
        for option,value in kwargs.items():
            new_content = re.sub("\n"+option+"=.*\n","\n"+option+"="+value+"\n",new_content)
            self.populate_config_file(new_content)

if __name__ == '__main__':

    configure = Configure(__name__, template_folder="templates")

    ConfigurationFile.contents()

    @configure.route('/')
    def index():
        return render_template('index.html')

    @configure.route('/about.html')
    def about():
        return render_template('about.html')

    @configure.route('/usage.html')
    def usage():
        return render_template('usage.html')

    @configure.route('/filler1.html')
    def filler1():
        return render_template('filler1.html')

    @configure.route('/filler2.html')
    def filler2():
        return render_template('filler2.html')

    @configure.route('/filler3.html')
    def filler3():
        return render_template('filler3.html')
    
    @configure.route('/reload')
    def reload_framework():
        Logging.log("INFO","(Configure.__main__) Reloading the MotionDetection framework!")
        return "Reloading the MotionDetection framework!"
    
    @configure.route('/configure/<credentials>')
    def update_credentials(credentials):

        fileOpts = FileOpts()

        addr     = configure.email(credentials)
        passwd   = configure.password(credentials)
        if configure.validate_email(addr) and configure.validate_password(passwd):
            Logging.log("INFO","(Configure.__main__) Using %s as the system email address with password: %s." % (addr, passwd))
            fileOpts.overwrite_config_options(email=addr,password=passwd)
            return "Using %s as the system email address with password: %s." % (addr, passwd)
        return render_template("invalid_credential_format.html")

    configure.run(debug=True, host='0.0.0.0')

    
