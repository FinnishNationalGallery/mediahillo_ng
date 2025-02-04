import json
import os
import shutil
import subprocess
from flask import Blueprint, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
from utils import logfile_output, logfile_outerror, logfile_datanative, subprocess_args, get_diskinfo
from dotenv import dotenv_values
from markupsafe import Markup
from dateutil import parser

datanative_bp = Blueprint('datanative', __name__)

config = dotenv_values(".env")
DATA_path = config['DATA_FOLDER']
DATANATIVE_path = config['DATANATIVE_FOLDER']
SIP_path = config['SIP_FOLDER']
SIPLOG_path = config['SIPLOG_FOLDER']
SERVER_ffmpeg = config['SERVER_FFMPEG']

@datanative_bp.route('/datanative')
@login_required
def datanative():
   files = sorted(os.listdir(DATANATIVE_path))
   files_outcome = sorted(os.listdir(DATA_path))
   diskinfo = get_diskinfo()
   try:
      with open(SIPLOG_path+"datanative.txt") as f:
         datanative = f.read()
   except:
      datanative = ""
   if 'message' in session:
      pass
   else:
      session['message'] = ""
   return render_template('datanative.html', files=files, files_outcome=files_outcome, diskinfo=diskinfo, datanative=datanative, DATANATIVE_path=DATANATIVE_path)

@datanative_bp.route('/datanative_import/', methods=['GET', 'POST'])
@login_required
def datanative_import():
   diskinfo = get_diskinfo()
   file = open("settings.json", "r")
   content = file.read()
   settings = json.loads(content)
   file.close()
   event_time = settings['prem_norm_date']
   agent_name = settings['prem_norm_agent']
   try:
      with open(SIPLOG_path+"datanative.txt") as f:
         datanative = f.read()
   except:
      datanative = ""
   if request.method == 'POST':
      file = request.form['file']
      outcome = request.form['outcome']
      datetime_obj = parser.parse(event_time)
      CreateDate = datetime_obj.isoformat()
      logfile_datanative("Source:"+file+" > "+"Outcome:"+outcome+"\n")   

   #return redirect(url_for('datanative.datanative'))
   return render_template('datanative.html', file=file, outcome=outcome, diskinfo=diskinfo, datanative=datanative)

@datanative_bp.route("/datanative_file_delete")
@login_required
def datanative_file_delete():
   path = request.args.get('path')
   file = request.args.get('name')
   view = request.args.get('page')
   path = DATANATIVE_path # This is dummy but secure
   deleteMessage = ""
   if os.path.isfile(path + file):
      try:
         os.remove(path + file)
      except:
         deleteMessage = "Cannot delete file!"
   elif os.path.isdir(path + file):
      try:
         shutil.rmtree(path + file)
      except:
         deleteMessage = "Cannot delete directory!"
   return redirect(url_for(view))

#######################
### FILE MEDIAINFO  ###
#######################
@datanative_bp.route("/mediainfo_datanative")
def mediainfo_datanative():
    # fullfilename voi olla esimerkiksi "tiedostonimi.xyz"
    # Erotetaan tiedostonimi ja pääte
    fullfilename = request.args.get('fullfilename')
    filename, extension = os.path.splitext(fullfilename)
    extension = extension.lstrip('.')  # Poistetaan piste laajennuksen edestä
    
    # Suoritetaan mediainfo-komento
    try:
        result = subprocess.run(["mediainfo", os.path.join(DATANATIVE_path, fullfilename)], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e), "output": e.output}), 400
    
    mediainfo_output = "MEDIAINFO -> " + fullfilename + "\n\n" + result.stdout
    
    # Kirjoitetaan tuloste tiedostoon filename-mediainfo.txt
    output_file = f"{filename}.{extension}.txt"
    with open(os.path.join(DATANATIVE_path, output_file), "w", encoding="utf-8") as f:
        f.write(mediainfo_output)
    
    return redirect(url_for('datanative.datanative'))
