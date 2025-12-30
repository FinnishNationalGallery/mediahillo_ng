import json
import os
import shutil
import datetime
import uuid
import tarfile
import glob
import gc
import traceback

from siptools_ng.file import File
from siptools_ng.sip import SIP
from mets_builder import METS, MetsProfile, StructuralMapDiv, StructuralMap
from mets_builder.metadata import DigitalProvenanceEventMetadata, DigitalProvenanceAgentMetadata, ImportedMetadata, MetadataType, MetadataFormat

from dateutil import parser
from flask import Blueprint, current_app, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
from modules import mp_metadata, pas_sftp_paramiko
from utils import logfile_output, logfile_outerror, logfile_datanative, subprocess_args, subprocess_args_simple, get_diskinfo
from dotenv import dotenv_values
from markupsafe import Markup
from subprocess import run, PIPE




sip_bp = Blueprint('sip', __name__)

config = dotenv_values(".env")
SIGNATURE = config['SIGNATURE']
DATA_path = config['DATA_FOLDER']
DATANATIVE_path = config['DATANATIVE_FOLDER']
SIP_path = config['SIP_FOLDER']
SIPLOG_path = config['SIPLOG_FOLDER']
ORGANIZATION = config['ORGANIZATION']
CONTRACTID = config['CONTRACTID']

@sip_bp.route("/sip")
@login_required
def sip():
   diskinfo = get_diskinfo()
   try:
      with open(SIPLOG_path+"output.txt") as f:
         output = f.read()
   except:
      output = ""
   try:   
      with open(SIPLOG_path+"outerror.txt") as f:
         outerr = f.read()
   except:
      outerr = ""
   files = sorted(os.listdir(SIP_path))
   data = mp_metadata.read_lido_xml()
   session['mp_inv'] = data.get("mp_inv", "No value")
   session['mp_id'] = data.get("mp_id", "No value")
   session['mp_name'] = data.get("mp_name", "No value")
   session['mp_created'] = data.get("mp_created", "No value")
   ###
   return render_template('sip.html', files=files, diskinfo=diskinfo, output=output, outerr=outerr, SIP_path=SIP_path)


def sip_name_detect():
   data = mp_metadata.read_lido_xml()
   lido_id = data.get("mp_id", "No value")
   if lido_id == "No value":
      sip_filename = str(uuid.uuid1()) + '.tar'
      flash("Error reading TAR package name!", "error")
      sip_filename = lido_id + '.tar'
   else:
      sip_filename = lido_id + '.tar'
   return sip_filename

#######################
### SIP FROM DIRECTORY
#######################
@sip_bp.route('/sip_from_directory')
@login_required
def sip_from_directory():
   update = request.args.get('update') 
   ###
   file = open("settings.json", "r")
   content = file.read()
   settings = json.loads(content)
   file.close()
   try:
      # Luodaan METS-olio dpres-mets-builderin avulla
      if update == "Yes":
         try:
            mets_createdate = settings['mets_createdate']
            #date_obj = datetime.datetime.fromisoformat(mets_createdate)
            date_obj = parser.isoparse(mets_createdate)
         except Exception as e:
            flash(f"Error creating METS! : Invalid original Createdate in Settings! : {str(e)}", "error")
            return redirect(url_for('sip.sip'))
         mets = METS(
            mets_profile=MetsProfile.CULTURAL_HERITAGE,
            contract_id=CONTRACTID,
            creator_name=ORGANIZATION,
            creator_type="ORGANIZATION",
            package_id=session['mp_inv'],
            content_id=session['mp_inv'],
            create_date= date_obj,
            last_mod_date= datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))),
            record_status="update"
         )
      else:
         mets = METS(
            mets_profile=MetsProfile.CULTURAL_HERITAGE,
            contract_id=CONTRACTID,
            creator_name=ORGANIZATION,
            creator_type="ORGANIZATION",
            package_id=session['mp_inv'],
            content_id=session['mp_inv']
         )
   except Exception as e:
      flash(f"Error creating METS! : {str(e)}", "error")
   try:
      # Generoidaan SIP hakemiston pohjalta
      sip = SIP.from_directory(
         directory_path="static/DATA",  # Mukauta polku
         mets=mets
      )
      # Lisätään provenienssimetadata (DigitalProvenanceEventMetadata)
      provenance_md = DigitalProvenanceEventMetadata(
         event_type="creation",
         detail="This is a detail",
         outcome="success",
         outcome_detail="Another detail",
      )
      sip.add_metadata([provenance_md])
      # Import descriptive metadata from an XML source, and add it to SIP
      descriptive_md = ImportedMetadata.from_path("static/METADATA/lido_description.xml")
      sip.add_metadata([descriptive_md])

      # Tallennetaan SIP Flask-sovelluksen configiin
      # current_app.config["dpres_sip"] = sip
      tar_name = sip_name_detect()
      sip.finalize(
         output_filepath="static/SIP/"+tar_name,
         sign_key_filepath=SIGNATURE
         #sign_key_filepath="signature/sip_sign_pas.pem"
      )
      sip.mets.write(SIP_path+"mets.xml")
      flash("SIP created from directory!", "success")
      return redirect(url_for('sip.sip'))
   except Exception as e:
      # Mikäli finalize() heittää poikkeuksen, siepataan virhe
      flash(f"Error creating SIP! : {str(e)}", "error")
      return redirect(url_for('sip.sip'))
####################

def read_all_files(DATA_path):
   files = []
   for item in os.listdir(DATA_path):
      full_path = os.path.join(DATA_path, item)
      
      # Tarkistetaan, että kyseessä on tiedosto (ei alihakemisto)
      if os.path.isfile(full_path):
         digital_object_path = f"DATA/{item}"
         static_path = f"static/{digital_object_path}"
         
         files.append(
               File(
                  path=static_path,
                  digital_object_path=digital_object_path
               )
         )
   return files

def read_all_files_mkv(DATA_path):
   files = []
   for item in os.listdir(DATA_path):
      full_path = os.path.join(DATA_path, item)
      file_append_flag = True
      # Check if is file and not folder
      if os.path.isfile(full_path):
         digital_object_path = f"DATA/{item}"
         static_path = f"static/{digital_object_path}"
         # Create file object
         file_obj = File(
               path=static_path,
               digital_object_path=digital_object_path
         )
         #
         # CHECK IF IS MATROSKA MKV FILE AND PROCEED
         #
         if item.lower().endswith('.mkv'):
            # Read settings file
            file = open("settings.json", "r")
            content = file.read()
            settings = json.loads(content)
            file.close()
            event_time = settings['prem_norm_date']
            agent_name = settings['prem_norm_agent']
            # Create Premis event
            datetime_obj = parser.parse(event_time)
            CreateDate = datetime_obj.isoformat()
            event = DigitalProvenanceEventMetadata(
               event_type="normalization",
               datetime=CreateDate,
               outcome="success",
               detail = "File conversion with software",
               outcome_detail="FFV1 video in Matroska container"
            )
            agent = DigitalProvenanceAgentMetadata(
               name=agent_name,
               agent_type="software",
               #version="1.2.0"
            )
            event.link_agent_metadata(
               agent,
               agent_role="executing program"
            )
            # Add Premis event to file object
            file_obj.add_metadata([event])
            # 
            # CHECK IF THERE IS VIDEO FRAME MD5 INFORMATION PER FILE
            #
            video_frame_file_path = os.path.join(DATA_path, f"{item}.FrameMD5.txt")
            try:
               with open(video_frame_file_path, "r", encoding="utf-8") as video_frame_file:
                     for line in video_frame_file:
                        if line.startswith("MD5="):
                           video_frame_md = line.strip()
               provenance_md = DigitalProvenanceEventMetadata(
                  event_type="message digest calculation",
                  detail=f"ffmpeg -loglevel error -i {item} -map 0:v -f md5 -",
                  outcome="success",
                  outcome_detail=video_frame_md,
               )
               file_obj.add_metadata([provenance_md])
            except FileNotFoundError:
               pass # We do not care if there is no information
            except Exception as e:
               flash(f"Error reading video frame MD5! : {str(e)}", "error")
            # 
            # CHECK IF THERE IS DATANATIVE FILES AND MAKE LINK FOR THEM
            #
            outcome_map = read_datanative_linkfile()
            if item in outcome_map:
               source_filename, outcome_filename = outcome_map[item]
               #print(f"Löytyi vastaavuus: Source: {source_filename} | Outcome: {outcome_filename}")
               source_file = File(
                  path="static/DATANATIVE/"+source_filename,
                  digital_object_path="DATANATIVE/"+source_filename
               )
               outcome_file = File(
                  path="static/DATA/"+outcome_filename,
                  digital_object_path="DATA/"+outcome_filename
               )
               file_obj_source, file_obj_outcome = make_datanative_premis(source_file, outcome_file)
               files.append(file_obj_source)
               files.append(file_obj_outcome)
               file_append_flag = False
               
         # Add file object to files list
         if file_append_flag is True:
            files.append(file_obj)

   return files

## MAKE DATANATIVE PREMIS EVENT ##
def make_datanative_premis(source_file, outcome_file):
   source_file.generate_technical_metadata()
   outcome_file.generate_technical_metadata()
   source_file.digital_object.use = "fi-dpres-no-file-format-validation"
   event = DigitalProvenanceEventMetadata(
      event_type = "migration",
      detail = "Normalization of digital object.",
      outcome = "success",
      outcome_detail = ("Source file format has been normalized. Outcome "
                        "object has been created as a result."),
      datetime = "2024-08-14T15:22:00",
   )

   source_file_techmd = next(
      metadata for metadata in source_file.metadata
      if metadata.metadata_type.value == "technical"
      and metadata.metadata_format.value == "PREMIS:OBJECT"
   )
   event.link_object_metadata(
      source_file_techmd,
      object_role="source"
   )
   outcome_file_techmd = next(
      metadata for metadata in outcome_file.metadata
      if metadata.metadata_type.value == "technical"
      and metadata.metadata_format.value == "PREMIS:OBJECT"
   )
   event.link_object_metadata(
      outcome_file_techmd,
      object_role="outcome"
   )
   source_file.add_metadata([event])
   outcome_file.add_metadata([event])
   return source_file, outcome_file

## READ DATANATIVE LINK FILE AND MAKE LINKS ##
def read_datanative_linkfile():
   outcome_map = {}
   try:
      with open(SIPLOG_path+"datanative.txt", "r", encoding="utf-8") as f:
         for line in f:
               line = line.strip()
               if not line:
                  continue  # ohitetaan mahdolliset tyhjät rivit
               # Oletetaan, että rivi on muodossa:
               # Source:Telefunken.mov > Outcome:Telefunken_FFV1_FLAC.mkv
               parts = line.split('>')
               if len(parts) != 2:
                  # Jos rivi ei vastaa odotettua rakennetta, ohitetaan
                  continue
               source_part = parts[0].strip()   # esim. "Source:Telefunken.mov"
               outcome_part = parts[1].strip()  # esim. "Outcome:Telefunken_FFV1_FLAC.mkv"
               # Poimitaan varsinaiset tiedostonimet (poistetaan "Source:" ja "Outcome:")
               source_filename = source_part.replace("Source:", "").strip()
               #print(source_filename)
               outcome_filename = outcome_part.replace("Outcome:", "").strip()
               #print(outcome_filename)
               # Tallennetaan sanakirjaan siten, että avaimena on Outcome-tiedostonimi
               # ja arvona tupla (source_filename, outcome_filename)
               outcome_map[outcome_filename] = (source_filename, outcome_filename)
   except Exception as e:
      # Mikäli finalize() heittää poikkeuksen, siepataan virhe
      # flash(f"No DATANATIVE files : {str(e)}", "error")
      pass

   return outcome_map

#######################
### SIP FROM FILES
#######################
@sip_bp.route('/sip_from_files')
@login_required
def sip_from_files():
   update = request.args.get('update') 
   sip = None
   files = None
   ###
   file = open("settings.json", "r")
   content = file.read()
   settings = json.loads(content)
   file.close()
   try:
      # Luodaan METS-olio dpres-mets-builderin avulla
      if update == "Yes":
         try:
            mets_createdate = settings['mets_createdate']
            #date_obj = datetime.datetime.fromisoformat(mets_createdate)
            date_obj = parser.isoparse(mets_createdate)
         except Exception as e:
            flash(f"Error creating METS! : Invalid original Createdate in Settings! : {str(e)}", "error")
            return redirect(url_for('sip.sip'))
         mets = METS(
            mets_profile=MetsProfile.CULTURAL_HERITAGE,
            contract_id=CONTRACTID,
            creator_name=ORGANIZATION,
            creator_type="ORGANIZATION",
            package_id=session['mp_inv'],
            content_id=session['mp_inv'],
            create_date= date_obj,
            last_mod_date= datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))),
            record_status="update"
         )
      else:
         mets = METS(
            mets_profile=MetsProfile.CULTURAL_HERITAGE,
            contract_id=CONTRACTID,
            creator_name=ORGANIZATION,
            creator_type="ORGANIZATION",
            package_id=session['mp_inv'],
            content_id=session['mp_inv']
         )
   except Exception as e:
      flash(f"Error creating METS! : {str(e)}", "error")
   try:
      files = read_all_files_mkv(DATA_path) # <---------
      sip = SIP.from_files(mets=mets, files=files)
      # Import descriptive metadata from an XML source, and add it to SIP
      descriptive_md = ImportedMetadata.from_path("static/METADATA/lido_description.xml")
      sip.add_metadata([descriptive_md])
      # Add provenance metadata (DigitalProvenanceEventMetadata)
      provenance_md = DigitalProvenanceEventMetadata(
         event_type="creation",
         detail="This is a detail",
         outcome="success",
         outcome_detail="Another detail",
      )
      sip.add_metadata([provenance_md])
      tar_name = sip_name_detect()
      sip.finalize(
         output_filepath="static/SIP/"+tar_name,
         sign_key_filepath=SIGNATURE
         #sign_key_filepath="signature/sip_sign_pas.pem"
      )
      sip.mets.write(SIP_path+"mets.xml")
      flash("SIP created from files!", "success")
      #return redirect(url_for('sip.sip'))
   except Exception as e:
      flash(f"Error creating SIP! : {str(e)}", "error")
      os.makedirs(SIPLOG_path, exist_ok=True)
      error_file = os.path.join(SIPLOG_path, "sip_error.txt")
      with open(error_file, "a", encoding="utf-8") as f:
         f.write("\n" + "=" * 80 + "\n")
         f.write(f"Timestamp: {datetime.datetime.now().isoformat(timespec='seconds')}\n")
         f.write(f"Exception: {type(e).__name__}: {e}\n")
         f.write(f"Request: {request.method} {request.full_path}\n")
         f.write(f"Remote: {request.remote_addr}\n")
         f.write("\nTraceback:\n")
         f.write(traceback.format_exc())
      siplog_error_file = os.path.join(SIPLOG_path, "output.txt")
      with open(siplog_error_file, "a", encoding="utf-8") as f:
         f.write("\n" + "=" * 80 + "\n")
         f.write(f"Timestamp: {datetime.datetime.now().isoformat(timespec='seconds')}\n")
         f.write(f"Exception: {type(e).__name__}: {e}\n")
         f.write(f"Request: {request.method} {request.full_path}\n")
         f.write(f"Remote: {request.remote_addr}\n")
         f.write("\nTraceback:\n")
         f.write(traceback.format_exc())
         #return redirect(url_for('sip.sip'))
   finally:
      sip = None
      files = None
      gc.collect()
      return redirect(url_for('sip.sip'))

@sip_bp.route("/sip_premis_event_created") # MuseumPlus digital object creation
@login_required
def sip_premis_event_created():
   redir = request.args.get('flag') # If you want to make own button for this function
   event_type = "creation"
   event_detail = "MuseumPlus object creation"
   event_outcome = "success"
   event_outcome_detail = "MuseumPlus object creation premis-event succeeded"
   agent_name = "MuseumPlus"
   agent_type = "software"
   if not session.get('mp_created'): # Try get date from MuseumPlus Lido read
      session['mp_created'] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).isoformat()
      #session['mp_created'] = "2018-04-12T14:09:00.233"
   subprocess_args('premis-event', event_type, session['mp_created'], '--event_detail', event_detail, '--event_outcome', event_outcome, '--event_outcome_detail', event_outcome_detail, '--workspace', SIP_path, '--agent_name', agent_name, '--agent_type', agent_type)
   if redir == 'once':
      return redirect(url_for('sip.sip'))
   return True

#######################
### MAKE DIRECTORY TREE FROM TAR
#######################
def build_tree(tar):
    tree = {}
    for member in tar.getmembers():
        parts = member.name.strip("/").split("/")
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        if member.isdir():
            node.setdefault(parts[-1], {})
        else:
            node[parts[-1]] = None
    return tree

def write_tree(tree, file, indent=0):
    for name in sorted(tree.keys()):
        if tree[name] is None:
            file.write(" " * indent + "- " + name + "\n")
        else:
            file.write(" " * indent + "+ " + name + "\n")
            write_tree(tree[name], file, indent + 4)

@sip_bp.route("/sip_tar_tree")
@login_required
def sip_tar_tree():
    directory_path = SIP_path
    tar_files = glob.glob(os.path.join(directory_path, "*.tar"))
    
    if not tar_files:
        flash("Folder '{}' does not have .tar files".format(directory_path), "error")
        return redirect(url_for('sip.sip'))
    else:
      tar_files.sort()
      tar_filename = tar_files[0]      
      try:
         with tarfile.open(tar_filename, "r") as tar:
               tree = build_tree(tar)
      except Exception as e:
         flash(f"Error opening tar-file: {str(e)}", "error")
         return redirect(url_for('sip.sip'))
    
    with open(SIPLOG_path+"output.txt", "w", encoding="utf-8") as f:
        write_tree(tree, f)
    return redirect(url_for('sip.sip'))

#######################
### SEND TAR WITH SFTP PROTOCOL
#######################
@sip_bp.route("/sip_send_transfer")
@login_required
def sip_send_transfer():
   send_really = request.args.get('send') 
   filename  = request.args.get('file')
   if send_really == "True":
      try:
         message = pas_sftp_paramiko.send_transfer(filename)
         flash(message, 'success')
      except Exception as e:
         flash(f"Error sending TAR-file! : {str(e)}", "error")
   else:
      message = Markup("Do you really want to send "+ filename +" TAR-file to CSC with SFTP protocol? <a href=" + url_for('sip.sip_send_transfer', send="True", file=filename) + "><button class=\"button is-success\">YES</button></a>"+" <a href=" + url_for('sip.sip') + "><button class=\"button is-dark\">Cancel</button> </a>")
      flash(message, 'success')         
   return redirect(url_for('sip.sip'))


#######################
### DELETE FUNCTIONS
#######################
@sip_bp.route("/sip_delete")
@login_required
def sip_delete():
   delete_really = request.args.get('delete') 
   if delete_really == "True":
      try:
         try:
            os.remove(SIPLOG_path+"output.txt")
         except:
            pass
         try:
            os.remove(SIPLOG_path+"outerror.txt")
         except:
            pass
         try:
            os.remove(SIPLOG_path+"datanative.txt")
         except:
            pass
         shutil.rmtree(SIP_path)
         os.mkdir(SIP_path)
         session['mp_inv'] = ""
         session['mp_id'] = ""
         session['mp_name'] = ""
         session['mp_created'] = ""
      except:
         message = "Could not delete folder!"
         flash(message, 'error')
   else:
      message = Markup("Do you really want to delete this folder? <a href=" + url_for('sip.sip_delete', delete="True") + "><button class=\"button is-danger\">Delete</button></a>"+" <a href=" + url_for('sip.sip') + "><button class=\"button is-dark\">Cancel</button> </a>")
      flash(message, 'error')
   return redirect(url_for('sip.sip'))

@sip_bp.route("/sip_file_delete")
@login_required
def sip_file_delete():
   path = request.args.get('path')
   file = request.args.get('name')
   view = request.args.get('page')
   path = SIP_path # This is dummy but secure
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


@sip_bp.route("/restart_gunicorn", methods=["GET", "POST"])
def restart_gunicorn():
    """
    Restart Gunicorn www-server and reset sip-instance.
    """
    if request.method == "POST":
        try:
         #subprocess_args_simple('/home/pasisti/restart_gunicorn.sh')

         env = os.environ.copy()
         env['PATH'] = '/usr/local/bin:/usr/bin:/bin:/home/pasisti/.local/bin'
         env['LANG'] = 'en_US.UTF-8'
         env['LC_ALL'] = 'en_US.UTF-8'

         # Run script
         result = run(
            '/home/pasisti/restart_gunicorn.sh',
            shell=True,
            executable='/bin/bash',
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True,
            env=env  
         )
            
        except Exception as e:
            flash(f'Validation error: {str(e)}', 'danger')
        
        return redirect(url_for("sip.restart_gunicorn"))
    
    # GET -> Show SIP folder
    return redirect(url_for('sip.sip'))