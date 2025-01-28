import os
import shutil
import glob
from flask import Blueprint, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
from utils import logfile_output, logfile_outerror, logfile_datanative, subprocess_args, get_diskinfo
from dotenv import dotenv_values
from markupsafe import Markup
import modules.mp_metadata as mp_metadata
from forms.form_metadata import *

download_bp = Blueprint('download', __name__)

config = dotenv_values(".env")
DATA_path = config['DATA_FOLDER']
DOWNLOAD_path = config['DOWNLOAD_FOLDER']
SIP_path = config['SIP_FOLDER']
SERVER_ffmpeg = config['SERVER_FFMPEG']


@download_bp.route("/download")
@login_required
def download():
   #files = sorted(os.listdir(DOWNLOAD_path))
   files = list(filter(os.path.isfile, glob.glob(DOWNLOAD_path + "*")))
   files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
   idx = 0
   for item in files:
      if DOWNLOAD_path in item:
         item2 = item.replace(DOWNLOAD_path, "")
         files[idx] = item2
      idx = idx + 1
   return render_template('download.html', files=files, DOWNLOAD_path=DOWNLOAD_path)

@download_bp.route("/download_delete")
@login_required
def download_delete():
   delete_really = request.args.get('delete') 
   if delete_really == "True":
      try:
         shutil.rmtree(DOWNLOAD_path)
         os.mkdir(DOWNLOAD_path)
      except:
         message = "Could not delete folder!"
         flash(message, 'error')
   else:
      message = Markup("Do you really want to delete this folder? <a href=" + url_for('download.download_delete', delete="True") + "><button class=\"button is-danger\">Delete</button></a>"+" <a href=" + url_for('download.download') + "><button class=\"button is-dark\">Cancel</button> </a>")
      flash(message, 'error')
   return redirect(url_for('download.download'))

@download_bp.route("/download_file_delete")
@login_required
def download_file_delete():
   path = request.args.get('path')
   file = request.args.get('name')
   view = request.args.get('page')
   path = DOWNLOAD_path # This is dummy but secure
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