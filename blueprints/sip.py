import json
import os
import shutil
import datetime
import uuid
from flask import Blueprint, current_app, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
from modules import mp_metadata
from utils import logfile_output, logfile_outerror, logfile_datanative, subprocess_args, get_diskinfo
from dotenv import dotenv_values
from markupsafe import Markup
from mets_builder import METS, MetsProfile, StructuralMapDiv, StructuralMap
from mets_builder.metadata import DigitalProvenanceEventMetadata, DigitalProvenanceAgentMetadata, ImportedMetadata

from siptools_ng.file import File
from siptools_ng.sip import SIP

sip_bp = Blueprint('sip', __name__)

config = dotenv_values(".env")
SIGNATURE = config['SIGNATURE']
DATA_path = config['DATA_FOLDER']
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
   ###
   return render_template('sip.html', files=files, diskinfo=diskinfo, output=output, outerr=outerr, SIP_path=SIP_path)

@sip_bp.route('/sip_from_directory')
@login_required
def sip_from_directory():
   # Luodaan METS-olio dpres-mets-builderin avulla
   mets = METS(
      mets_profile=MetsProfile.RESEARCH_DATA,
      contract_id="urn:uuid:abcd1234-abcd-1234-5678-abcd1234abcd",
      creator_name="Sigmund Sipenthusiast",
      creator_type="INDIVIDUAL"
   )
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

      sip.finalize(
         output_filepath="static/SIP/example-automated-sip.tar",
         sign_key_filepath="signature/sip_sign_pas.pem"
      )
      # Onnistunut finalize
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
        
        # Tarkistetaan, että kyseessä on tiedosto (ei alihakemisto)
        if os.path.isfile(full_path):
            digital_object_path = f"DATA/{item}"
            static_path = f"static/{digital_object_path}"
            
            # Luodaan File-objekti
            file_obj = File(
                path=static_path,
                digital_object_path=digital_object_path
            )
            
            # Jos tiedosto on .mkv, liitetään automaattisesti metatietoa
            if item.lower().endswith('.mkv'):
                event = DigitalProvenanceEventMetadata(
                    event_type="creation",
                    datetime="2024-01-01",
                    outcome="success",
                    detail = "What the fuck?",
                    outcome_detail="The file was uploaded into the collection management system ArchiveStar"
                )
                agent = DigitalProvenanceAgentMetadata(
                    name="ArchiveStar",
                    agent_type="software",
                    version="1.2.0"
                )
                event.link_agent_metadata(
                    agent,
                    agent_role="executing program"
                )
                
                # Lisätään tapahtuma file_obj:iin
                file_obj.add_metadata([event])
            
            # Lisätään tiedosto listaan
            files.append(file_obj)
    
    return files
####################
@sip_bp.route('/sip_from_files')
@login_required
def sip_from_files():
   ###
   file = open("settings.json", "r")
   content = file.read()
   settings = json.loads(content)
   file.close()
   mets_createdate = settings['mets_createdate']
   date_obj = datetime.datetime.fromisoformat(mets_createdate)
   # Luodaan METS-olio dpres-mets-builderin avulla
   mets = METS(
      mets_profile=MetsProfile.RESEARCH_DATA,
      contract_id="urn:uuid:abcd1234-abcd-1234-5678-abcd1234abcd",
      creator_name="Sigmund Sipenthusiast",
      creator_type="INDIVIDUAL",
      create_date= date_obj,
      last_mod_date= datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3)))
   )
   try:
      files = read_all_files_mkv(DATA_path)
      sip = SIP.from_files(mets=mets, files=files)

      # Import descriptive metadata from an XML source, and add it to SIP
      descriptive_md = ImportedMetadata.from_path("static/METADATA/lido_description.xml")
      sip.add_metadata([descriptive_md])

      # Lisätään provenienssimetadata (DigitalProvenanceEventMetadata)
      provenance_md = DigitalProvenanceEventMetadata(
         event_type="creation",
         detail="This is a detail",
         outcome="success",
         outcome_detail="Another detail",
      )
      sip.add_metadata([provenance_md])

      # Tallennetaan SIP Flask-sovelluksen configiin
      # current_app.config["dpres_sip"] = sip

      sip.finalize(
         output_filepath="static/SIP/example-automated-sip.tar",
         sign_key_filepath="signature/sip_sign_pas.pem"
      )
      sip.mets.write(SIP_path+"mets.xml")
      # Onnistunut finalize
      flash("SIP created from files!", "success")
      return redirect(url_for('sip.sip'))
   except Exception as e:
      # Mikäli finalize() heittää poikkeuksen, siepataan virhe
      flash(f"Error creating SIP! : {str(e)}", "error")
      return redirect(url_for('sip.sip'))


@sip_bp.route("/sip_make_all")
@login_required
def sip_make_all():
   sip_premis_event_created()
   sip_compile_structmap()
   sip_compile_mets()
   sip_sign_mets()
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

@sip_bp.route("/sip_compile_structmap")
@login_required
def sip_compile_structmap():
   redir = request.args.get('flag') # If you want to make own button for this function
   subprocess_args('compile-structmap', '--workspace', SIP_path)
   if redir == 'once':
      return redirect(url_for('sip.sip'))
   return True

@sip_bp.route("/sip_compile_mets")
@login_required
def sip_compile_mets():
   redir = request.args.get('flag') # If you want to make own button for this function
   if not session.get('mp_inv'):
      objid = str(uuid.uuid1())
   else:
      objid = session['mp_inv']
   subprocess_args('compile-mets','--workspace', SIP_path , 'ch', ORGANIZATION, CONTRACTID, '--objid',objid, '--copy_files', '--clean')
   if redir == 'once':
      return redirect(url_for('sip.sip'))
   return True

@sip_bp.route("/sip_compile_mets_update")
@login_required
def sip_compile_mets_update():
   redir = request.args.get('flag') # If you want to make own button for this function
   LastmodDate = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=3))).isoformat() 
   ###
   file = open("settings.json", "r")
   content = file.read()
   settings = json.loads(content)
   file.close()
   mets_createdate = settings['mets_createdate']
   ###
   if session['mp_inv']:
      objid = session['mp_inv']
   else:
      objid = str(uuid.uuid1())
   subprocess_args('compile-mets','--workspace', SIP_path , 'ch', ORGANIZATION, CONTRACTID, '--objid',objid, '--create_date', mets_createdate, '--last_moddate', LastmodDate, '--record_status', 'update', '--copy_files', '--clean')
   if redir == 'once':
      return redirect(url_for('sip.sip'))
   return True

@sip_bp.route("/sip_sign_mets")
@login_required
def sip_sign_mets():
   redir = request.args.get('flag') # If you want to make own button for this function
   #subprocess_args('./sign.sh', SIGNATURE, SIP_path)
   subprocess_args('sign-mets', SIGNATURE, '--workspace', SIP_path)
   if redir == 'once':
      return redirect(url_for('sip.sip'))
   return True

@sip_bp.route("/sip_make_tar")
@login_required
def sip_make_tar():
   redir = request.args.get('flag') # If you want to make own button for this function
   lido_inv, lido_id, lido_name, lido_created = mp_metadata.read_mets_lido_xml()
   if lido_id > "":
      sip_filename = lido_id + '.tar'
      message = "TAR package from mets.xml file: "+lido_name + ", Inv nro: " +lido_inv + ", MuseumPlus ID: " + lido_id
      msg_status = "success"
   else:
      sip_filename = str(uuid.uuid1()) + '.tar'
      message = "SOMETHING WENT WRONG! TAR package name is: " + sip_filename
      msg_status = "error"
   subprocess_args('compress', '--tar_filename',  sip_filename, SIP_path)
   if redir == 'once':
      flash( message,msg_status)
      return redirect(url_for('sip.sip'))
   return True


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