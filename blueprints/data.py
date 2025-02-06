import datetime
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET
from typing import Tuple
from subprocess import PIPE
from flask import Blueprint, current_app, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
from utils import logfile_output, logfile_outerror, logfile_validation, logfile_output, subprocess_args, get_diskinfo
from dotenv import dotenv_values
from markupsafe import Markup
from dateutil import parser

data_bp = Blueprint('data', __name__)

config = dotenv_values(".env")
DATA_path = config['DATA_FOLDER']
SIP_path = config['SIP_FOLDER']
SERVER_ffmpeg = config['SERVER_FFMPEG']

@data_bp.route('/data')
@login_required
def data():
   files = sorted(os.listdir(DATA_path))
   diskinfo = get_diskinfo()
   if 'message' in session:
      pass
   else:
      session['message'] = ""
   ###
   try:
      with open(DATA_path+"validation.txt") as f:
         output = f.read()
   except:
      output = ""
   ###
   return render_template('data.html', files=files, diskinfo=diskinfo, output=output, DATA_path=DATA_path)


@data_bp.route('/data_premis_event_ffmpeg_ffv1')
@login_required
def data_premis_event_ffmpeg_ffv1(): # Matroska video FFMPEG normalization event
   redir = request.args.get('flag') # If you want to make own button for this function
   files = os.listdir(DATA_path)
   ###
   file = open("settings.json", "r")
   content = file.read()
   settings = json.loads(content)
   file.close()
   event_time = settings['prem_norm_date']
   agent_name = settings['prem_norm_agent']
   ###
   for file in files:
      filesplit = file.split('.')
      extension = filesplit[-1].lower()
      filepath = DATA_path + file
      if extension in ['mkv']: # Only for Matroska .mkv files!
         event_type = "normalization"
         #event_time = datetime.datetime.now()
         event_detail = "File conversion with FFMPEG program"
         event_outcome = "success"
         event_outcome_detail = "FFV1 video in Matroska container"
         #agent_name = "FFMPEG version git-2020-01-26-5e62100 / Windows 10"
         agent_type = "software"
         datetime_obj = parser.parse(event_time)
         CreateDate = datetime_obj.isoformat()
         subprocess_args('premis-event', event_type, CreateDate, '--event_detail', event_detail, '--event_outcome', event_outcome, '--event_outcome_detail', event_outcome_detail, '--workspace', SIP_path, '--agent_name', agent_name, '--agent_type', agent_type, '--event_target', filepath.replace("./",""))
   if redir == 'once':
      return redirect(url_for('sip.sip'))
   return True

#######################
### VIDEO FRAME CHECKSUM
#######################
@data_bp.route('/data_premis_event_frame_md') # Calculate video frame checksum
@login_required
def data_premis_event_frame_md():
   files = os.listdir(DATA_path)
   for file in files:
      filesplit = file.split('.')
      extension = filesplit[-1].lower()
      filepath = DATA_path + file
      if extension in ['mkv']: # Only for Matroska .mkv files!
         try: # Get MD5 video frame checksum from file
            cmd = 'ffmpeg -loglevel error -i ' + filepath + ' -map 0:v -f md5 -'
            out = subprocess.run(cmd, shell=True, executable='/bin/bash',stdout=PIPE, stderr=PIPE, universal_newlines=True)
            #logfile_output(cmd+"\n")
            #logfile_output(out.stdout+"\n")
            #logfile_outerror(out.stderr)
            session['message_md5'] = out.stdout
         except:
            logfile_outerror(out.stderr)
         CreateDate = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).isoformat()
         output_file = f"{file}.FrameMD5.txt"
         with open(os.path.join(DATA_path, output_file), "w", encoding="utf-8") as f:
            f.write(f"ffmpeg -loglevel error -i {file} -map 0:v -f md5 -\n")
            f.write(session['message_md5'])
   return redirect(url_for('data.data'))

#######################
### FILE VALIDATION ###
#######################
def analyze_file_validation(file_path):
    # Suorita komentorivin komento ilman check-parametria ja tarkista paluukoodi
    result = subprocess.run(
        ["scraper", "scrape-file", file_path],
        text=True,
        capture_output=True,
        check=False  # Ei heitä poikkeusta, vaikka komento epäonnistuisi
    )
    
    # Jos komennon palautuskoodi ei ole 0, se tarkoittaa virhettä
    if result.returncode != 0:
        # Tarkista, onko virheilmoitus "Error: Proper scraper was not found"
        if "Error: Proper scraper was not found. The file was not analyzed." in result.stderr:
            return {
                "grade": "",
                "well-formed": "FALSE",
                "messages": "Error: Proper scraper was not found. The file was not analyzed."
            }
        else:
            return {
                "grade": "",
                "well-formed": "An error occurred during file analysis.",
                "messages": result.stderr if result.stderr else "Unknown error"
            }

    # Jatka JSON-parsintaan, jos tulostetta löytyy
    try:
        output_json = json.loads(result.stdout)
    except json.JSONDecodeError:
        # Jos tulostetta ei voi jäsentää JSON-muotoon, palautetaan virheviesti
        return {
            "grade": "",
            "well-formed": "Failed to parse JSON output.",
            "messages": result.stdout  # Palautetaan koko stdout-viesti
        }
    
    # Lue JSON-tulosteesta "grade" ja "well-formed" -arvot
    grade = output_json.get("grade", "")
    well_formed = output_json.get("well-formed", "")
    
    # Muuta well-formed boolean merkkijonoksi
    well_formed_str = "TRUE" if well_formed else "FALSE"
    
    # Hae kaikki virheilmoitukset riippumatta avaimesta
    errors = output_json.get("errors", {})
    error_messages = []
    for error_list in errors.values():
        if isinstance(error_list, list):
            error_messages.extend(error_list)
    
    # Tarkista, löytyykö XML-sisältöä
    xml_content = next((error for error in error_messages if "<?xml" in error), "")
    
    if xml_content:
        # Jos XML-sisältö löytyy, jäsennä se
        try:
            root = ET.fromstring(xml_content)
            namespaces = {'jhove': 'http://schema.openpreservation.org/ois/xml/ns/jhove'}
            # Tarkista, löytyykö <message>-elementtejä käyttäen nimiavaruuksia
            message_elements = root.findall(".//jhove:message", namespaces)
            messages = "\n".join(msg.text for msg in message_elements if msg.text)
        except ET.ParseError:
            # Jos XML-jäsennys epäonnistuu, anna virheilmoitus
            messages = "Invalid XML format in error messages."
    else:
        # Jos XML-sisältöä ei ole, yhdistä muut viestit merkkijonoksi
        messages = "\n".join(error_messages)

    # Palauta tiedot JSON-muodossa
    return {
        "grade": grade,
        "well-formed": well_formed_str,  # Käytä merkkijonoa
        "messages": messages              # Messages aina merkkijonona
    }

@data_bp.route("/analyze_file")
def analyze_file():
   filename = request.args.get('filename')
   path = DATA_path + filename
   file_analysis = analyze_file_validation(path)
   # Lue 'grade', 'well-formed' ja 'messages' -arvot
   grade = file_analysis.get("grade", "")
   well_formed = file_analysis.get("well-formed", "")
   messages = file_analysis.get("messages", "")
   logfile_validation(filename + " -> "+ well_formed + " -> " + messages + "\n")
   # logfile_validation(grade+"\n")
   logfile_validation("\n")
   return redirect(url_for('data.data'))

#######################
### FILE MEDIAINFO  ###
#######################
@data_bp.route("/mediainfo_data")
def mediainfo_data():
    # fullfilename voi olla esimerkiksi "tiedostonimi.xyz"
    # Erotetaan tiedostonimi ja pääte
    fullfilename = request.args.get('fullfilename')
    filename, extension = os.path.splitext(fullfilename)
    extension = extension.lstrip('.')  # Poistetaan piste laajennuksen edestä
    
    # Suoritetaan mediainfo-komento
    try:
        result = subprocess.run(["mediainfo", os.path.join(DATA_path, fullfilename)], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e), "output": e.output}), 400
    
    mediainfo_output = "MEDIAINFO -> " + fullfilename + "\n\n" + result.stdout
    
    # Kirjoitetaan tuloste tiedostoon filename-mediainfo.txt
    output_file = f"{filename}.{extension}-INFO.txt"
    with open(os.path.join(DATA_path, output_file), "w", encoding="utf-8") as f:
        f.write(mediainfo_output)
    
    return redirect(url_for('data.data'))

#######################
### FIX IMAGE MAGICK
#######################
@data_bp.route("/fix_image_magick")
@login_required
def fix_image_magick():
    filename = request.args.get('filename')
    view = request.args.get('page')
    
    # Allowed image extensions (case-insensitive)
    allowed_extensions = ['jpeg', 'jpg', 'tif', 'tiff', 'png']
    
    # Check if file has an allowed extension
    file_extension = filename.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        flash("File type not supported for fixing", 'error')
        return redirect(url_for(view))
    
    try:
        # Construct input and output file paths
        input_path = os.path.join(DATA_path, filename)
        base_name, ext = os.path.splitext(filename)
        output_filename = f"{base_name}-magick{ext}"
        output_path = os.path.join(DATA_path, output_filename)
        
        # Run ImageMagick conversion using subprocess
        result = subprocess.run(
            ['convert', input_path, output_path], 
            capture_output=True, 
            text=True, 
            check=True
        )

        # Flash success message
        message = Markup(f"Image fixed: {filename} -> {output_filename}")
        flash(message, 'success')
    except Exception as e:
        # Flash error message if conversion fails
        message = f"Error fixing image: {str(e)}"
        flash(message, 'error')
    
    return redirect(url_for(view))

#######################
### FIX IMAGE EXIFTOOL
#######################
@data_bp.route("/fix_image_exiftool")
@login_required
def fix_image_exiftool():
    filename = request.args.get('filename')
    view = request.args.get('page')
    
    # Allowed image extensions (case-insensitive)
    allowed_extensions = ['jpeg', 'jpg', 'tif', 'tiff', 'png']
    
    # Check if file has an allowed extension
    file_extension = filename.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        flash("File type not supported for fixing", 'error')
        return redirect(url_for(view))
    
    try:
        # Construct input and output file paths
        input_path = os.path.join(DATA_path, filename)
        base_name, ext = os.path.splitext(filename)
        output_filename = f"{base_name}-exiftool{ext}"
        output_path = os.path.join(DATA_path, output_filename)
        
        # Run Exiftool conversion using subprocess
        result = subprocess.run(
            #['exiftool','-overwrite_original','-TagsFromFile','@','-all:all',input_path], 
            ['exiftool','-TagsFromFile','@','-all:all',input_path], 
            capture_output=True, 
            text=True, 
            check=True
        ) 
        # exiftool -overwrite_original -all= -tagsfromfile @ -all:all UUSI.tif

        # Change filename using subprocess
        result = subprocess.run(
            ['mv',input_path,output_path], 
            capture_output=True, 
            text=True, 
            check=True
        ) 

        logfile_validation(filename + " exiftool -> "+ result.stdout + result.stderr + "\n")

        # Change original filename using subprocess
        fixed_path = f"{DATA_path}{base_name}{ext}_original"
        original_path = f"{DATA_path}{base_name}{ext}"
        result = subprocess.run(
            ['mv',fixed_path,original_path], 
            capture_output=True, 
            text=True, 
            check=True
        ) 
        # Flash success message
        message = Markup(f"Image fixed: {filename} -> {output_filename}")
        flash(message, 'success')
    except Exception as e:
        # Flash error message if conversion fails
        message = f"Error fixing image: {str(e)}"
        flash(message, 'error')
    
    return redirect(url_for(view))

#######################
### FIX PDF GHOSTSCRIPT
#######################
@data_bp.route("/fix_pdf_ghostscript")
@login_required
def fix_pdf_ghostscript():
    filename = request.args.get('filename')
    view = request.args.get('page')
    
    # Allowed image extensions (case-insensitive)
    allowed_extensions = ['pdf']
    
    # Check if file has an allowed extension
    file_extension = filename.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        flash("File type not supported for fixing", 'error')
        return redirect(url_for(view))
    
    try:
        # Construct input and output file paths
        input_path = os.path.join(DATA_path, filename)
        base_name, ext = os.path.splitext(filename)
        output_filename = f"{base_name}-ghostscript{ext}"
        output_path = os.path.join(DATA_path, output_filename)
        
        # Run Exiftool conversion using subprocess
        result = subprocess.run(
            ['gs','-o',output_path,'-sDEVICE=pdfwrite','-dPDFSETTINGS=/prepress','-dNOPAUSE','-dBATCH',input_path], 
            capture_output=True, 
            text=True, 
            check=True
        ) 
        # gs -o korjattu.pdf -sDEVICE=pdfwrite -dPDFSETTINGS=/prepress -dNOPAUSE -dBATCH epavalidi.pdf

        logfile_validation(filename + " chostscript -> "+ result.stdout + result.stderr + "\n")

        # remove original using subprocess
        #result = subprocess.run(
        #    ['rm',input_path], 
        #    capture_output=True, 
        #    text=True, 
        #    check=True
        #) 

        # Flash success message
        message = Markup(f"Image fixed: {filename} -> {output_filename}")
        flash(message, 'success')
    except Exception as e:
        # Flash error message if conversion fails
        message = f"Error fixing image: {str(e)}"
        flash(message, 'error')
    
    return redirect(url_for(view))

#######################
### DELETE FUNCTIONS
#######################
@data_bp.route("/data_delete")
@login_required
def data_delete():
   delete_really = request.args.get('delete') 
   if delete_really == "True":
      try:
         shutil.rmtree(DATA_path)
         os.mkdir(DATA_path)
         session['mp_inv'] = ""
         session['mp_id'] = ""
         session['mp_name'] = ""
         session['mp_created'] = ""
      except:
         message = "Could not delete folder!"
         flash(message, 'error')
   else:
      message = Markup("Do you really want to delete this folder? <a href=" + url_for('data.data_delete', delete="True") + "><button class=\"button is-danger\">Delete</button></a> "+" <a href=" + url_for('data.data') + "><button class=\"button is-dark\">Cancel</button> </a>")
      flash(message, 'error')
   return redirect(url_for('data.data'))

@data_bp.route("/file_delete")
@login_required
def file_delete():
   path = request.args.get('path')
   file = request.args.get('name')
   view = request.args.get('page')
   path = DATA_path # This is dummy but secure
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