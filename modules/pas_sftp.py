import pysftp
import os
from dotenv import dotenv_values

config = dotenv_values(".env") 
KEY_PATH = config['PRIVATE_KEY_PATH']
KEY_PASS = config['PRIVATE_KEY_PASS']
DOWNLOAD_FOLDER = config['DOWNLOAD_FOLDER']
SFTP_USER = config['SFTP_USER']
if "Production" in config['CONF_SFTP']:
    SFTP_HOST = config['SFTP_HOST_PROD']
    SFTP_ENV = 'PAS PRODUCTION ENVIRONMENT'
else:
    SFTP_HOST = config['SFTP_HOST_TEST']
    SFTP_ENV = 'PAS TESTING ENVIRONMENT'

def folder(folderpath):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    try:
        srv = pysftp.Connection(host=SFTP_HOST, username=SFTP_USER, default_path='/', private_key_pass=KEY_PASS,  private_key=KEY_PATH, cnopts=cnopts)
        srv.cwd(folderpath)
        data = srv.listdir()
        directories =[]
        files =[]
        for item in data:
            if (srv.isdir(item)):
                directories.append(item)
            if (srv.isfile(item)):
                files.append(item)
    except Exception as e: 
        directories = [" *** Error connecting SFTP-server *** "]
        files = []
        data = str(e)
    return data, directories,files

def file(folderpath, filename):
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    try:
        srv = pysftp.Connection(host=SFTP_HOST, username=SFTP_USER, default_path='/', private_key_pass=KEY_PASS,  private_key=KEY_PATH, cnopts=cnopts)
        srv.cwd(folderpath)
        #os.chdir(SIP_path)
        pathdata = os.listdir('./')
        #srv.get_d(folderpath, SIP_path)
        srv.get(filename, DOWNLOAD_FOLDER+filename)
        message = "OK"
    except Exception as e: 
        directories = [" *** Error connecting SFTP-server *** "]
        files = []
        message = str(e)
    return message