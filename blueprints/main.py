from flask import Blueprint, render_template, request, url_for, flash, redirect, send_file, jsonify
from flask_login import login_required, current_user
from models import db_paslog_mp, db_paslog_csc
from extensions import db
from utils import logfile_output, logfile_outerror, logfile_datanative, subprocess_args, get_diskinfo
from dotenv import dotenv_values
from forms.form_metadata import *
import json
from markupsafe import Markup

main_bp = Blueprint('main', __name__)

config = dotenv_values(".env")
# ... load your configuration variables ...

@main_bp.route("/")
def index():
    return render_template('index.html')

@main_bp.route("/ffmpeg")
def ffmpeg():
   return render_template('ffmpeg_info.html')

@main_bp.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
   form = Settings()
   if form.validate_on_submit():
      normalization_date = form.premis_video_normalization_date.data
      normalization_date_str = normalization_date.strftime('%Y-%m-%dT%H:%M')
      normalization_agent = form.premis_video_normalization_agent.data
      mets_createdate = form.mets_createdate.data
      settings = {
        "prem_norm_date": normalization_date_str,
        "prem_norm_agent": normalization_agent,
        "mets_createdate": mets_createdate}
      json_obj = json.dumps(settings, indent=4)
      try:
         file = open("settings.json", "w")
         file.write(json_obj)
         file.close()
         message = Markup("Settings saved succesfully!")
         flash(message, 'success')
      except:
         message = Markup("Error saving settings file!")
         flash(message, 'error')
   else:
      try:
         file = open("settings.json", "r")
         content = file.read()
         settings = json.loads(content)
         file.close()
      except:
         settings = {
         "prem_norm_date": "",
         "prem_norm_agent": "",
         "mets_createdate": ""}
         json_obj = json.dumps(settings, indent=4)
         file = open("settings.json", "w")
         file.write(json_obj)
         file.close()
   return render_template('settings.html', form=form, settings=settings)