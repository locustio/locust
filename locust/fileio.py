import logging
import os
import events
import werkzeug

logger = logging.getLogger(__name__)

def read(uploaded_file_path):
    try:
        with open(os_path()+uploaded_file_path, "r") as data_file:
            data = data_file.read()
    except IOError as err:
        logger.info("error read: " + err.strerror) 
        data = None
    return data

def write(file_path, file_content):
    try:
        with open(os_path()+file_path, "w") as data_file:
            data_file.write(file_content)
            status = True
            message = 'File has been saved'
    except IOError as err:
        logger.info("error write: " + err.strerror )
        status = False
        message = "Can't overwrite protected file. Please rename your test file. i.e : home_production_dilan.py"
    return status, message

def os_path():
    return os.environ['PYTHONPATH'].split(os.pathsep)[-1]+os.sep
