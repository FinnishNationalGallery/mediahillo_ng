import paramiko
import os
import stat
from dotenv import dotenv_values

config = dotenv_values(".env")
KEY_PATH = config['PRIVATE_KEY_PATH']
KEY_PASS = config['PRIVATE_KEY_PASS']
DOWNLOAD_FOLDER = config['DOWNLOAD_FOLDER']
SIP_FOLDER = config['SIP_FOLDER']
SFTP_USER = config['SFTP_USER']
if "Production" in config['CONF_SFTP']:
    SFTP_HOST = config['SFTP_HOST_PROD']
    SFTP_ENV = 'PAS PRODUCTION ENVIRONMENT'
else:
    SFTP_HOST = config['SFTP_HOST_TEST']
    SFTP_ENV = 'PAS TESTING ENVIRONMENT'

def create_ssh_client():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    private_key = paramiko.RSAKey.from_private_key_file(KEY_PATH, password=KEY_PASS)
    ssh.connect(hostname=SFTP_HOST, username=SFTP_USER, pkey=private_key)
    return ssh

def folder(folderpath):
    try:
        ssh = create_ssh_client()
        sftp = ssh.open_sftp()
        
        sftp.chdir(folderpath)
        data = sftp.listdir()
        
        directories = []
        files = []
        for item in data:
            try:
                file_attr = sftp.stat(os.path.join(folderpath, item))
                if stat.S_ISDIR(file_attr.st_mode):
                    directories.append(item)
                elif stat.S_ISREG(file_attr.st_mode):
                    files.append(item)
            except IOError:
                # Jos emme voi määrittää onko se tiedosto vai hakemisto, ohitamme sen
                pass
        
        sftp.close()
        ssh.close()
        
        return data, directories, files
    except Exception as e:
        return str(e), [" *** Error connecting SFTP-server *** "], []

def file(folderpath, filename):
    try:
        ssh = create_ssh_client()
        sftp = ssh.open_sftp()
        
        sftp.chdir(folderpath)
        local_path = os.path.join(DOWNLOAD_FOLDER, filename)
        sftp.get(filename, local_path)
        
        sftp.close()
        ssh.close()
        
        return "OK"
    except Exception as e:
        return str(e)
    
def send_transfer(filename):
    try:
        ssh = create_ssh_client()
        sftp = ssh.open_sftp()
        #sftp.chdir("/transfer/")
        local_path = os.path.join(SIP_FOLDER, filename)
        print(local_path)
        sftp.put(local_path, "/transfer/")
        
        sftp.close()
        ssh.close()
        
        return "OK"
    except Exception as e:
        return str(e)

# Käyttöesimerkki
if __name__ == "__main__":
    # Listaa tiedostot ja hakemistot
    data, directories, files = folder("/some/remote/path")
    print("Kaikki kohteet:", data)
    print("Hakemistot:", directories)
    print("Tiedostot:", files)

    # Lataa tiedosto
    result = file("/some/remote/path", "example.txt")
    print("Latauksen tulos:", result)

