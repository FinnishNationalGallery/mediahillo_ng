from flask import Blueprint, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
import modules.pas_sftp_paramiko as pas_sftp

sftp_bp = Blueprint('sftp', __name__)

@sftp_bp.route("/pas_sftp_index")
@login_required
def pas_sftp_index():
   return render_template('pas_sftp_index.html', environment=pas_sftp.SFTP_ENV)

@sftp_bp.route("/pas_sftp_folder")
@login_required
def pas_sftp_folder():
   folder = request.args.get('folder')
   data, directories, files = pas_sftp.folder(folder)
   return render_template('pas_sftp_folder.html', folder=folder, data=data, directories=directories, files=files, environment=pas_sftp.SFTP_ENV)

@sftp_bp.route("/pas_sftp_file")
@login_required
def pas_sftp_file():
   folder = request.args.get('folder')
   file  = request.args.get('file')
   message = pas_sftp.file(folder, file)
   return render_template('pas_sftp_file.html', folder=folder, file=file, message=message, environment=pas_sftp.SFTP_ENV)