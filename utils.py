import subprocess
from subprocess import PIPE
import os
from dotenv import dotenv_values

# Load configuration
config = dotenv_values(".env")
DATA_path = config['DATA_FOLDER']
SIPLOG_path = config['SIPLOG_FOLDER']
APP_FOLDER = config['APP_FOLDER']

def logfile_output(line):
   file = open(os.path.join(SIPLOG_path, "output.txt"), "a")
   file.write(line)
   file.close()

def logfile_outerror(line):
   file = open(os.path.join(SIPLOG_path, "outerror.txt"), "a")
   file.write(line)
   file.close()

def logfile_datanative(line):
   file = open(os.path.join(SIPLOG_path, "datanative.txt"), "a")
   file.write(line)
   file.close()

def logfile_validation(line):
   file = open(os.path.join(DATA_path, "validation.txt"), "a")
   file.write(line)
   file.close()

def subprocess_args(*args):
   listToStrCmd = '\' \''.join(map(str, list(args)))
   commandStr = '\'' + listToStrCmd + '\''
   cmd = commandStr  # No need to activate venv
   out = subprocess.run(cmd, shell=True, executable='/bin/bash', stdout=PIPE, stderr=PIPE, universal_newlines=True)
   logfile_output(commandStr+"\n")
   logfile_output(out.stdout+"\n")
   logfile_outerror(out.stderr)

def get_diskinfo():
   cmd = 'df -h ' + APP_FOLDER
   out = subprocess.run(cmd, shell=True, executable='/bin/bash', stdout=PIPE, stderr=PIPE, universal_newlines=True)
   dioutput = out.stdout
   dioutput = dioutput.split("\n")
   diskinfo = dioutput[1]
   diskinfo = diskinfo.split()
   return diskinfo