import os
import shutil
import datetime
from flask import Blueprint, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
from utils import logfile_output, logfile_outerror, logfile_datanative, subprocess_args, get_diskinfo
from dotenv import dotenv_values
from markupsafe import Markup
import modules.mp_metadata as mp_metadata
from forms.form_metadata import *
import xml.etree.ElementTree as ET

metadata_bp = Blueprint('metadata', __name__)

config = dotenv_values(".env")
ORGANIZATION = config['ORGANIZATION']
DATA_path = config['DATA_FOLDER']
METADATA_path = config['METADATA_FOLDER']
SIP_path = config['SIP_FOLDER']
SERVER_ffmpeg = config['SERVER_FFMPEG']

@metadata_bp.route("/metadata")
@login_required
def metadata():
   files = sorted(os.listdir(METADATA_path))
   data = mp_metadata.read_lido_xml()
   session['mp_inv'] = data.get("mp_inv", "No value")
   session['mp_id'] = data.get("mp_id", "No value")
   session['mp_name'] = data.get("mp_name", "No value")
   session['mp_created'] = data.get("mp_created", "No value")
   return render_template('metadata.html', files=files, environment=mp_metadata.MP_ENV, METADATA_path=METADATA_path)

@metadata_bp.route("/metadata_get")
@login_required
def metadata_get():
   return render_template('index.html')

@metadata_bp.route("/metadata_save_object_by_id")
@login_required
def metadata_save_object_by_id():
   objectid = request.args.get('objectid')
   #object_id = request.vars.object_id
   message = mp_metadata.save_object_by_id(objectid)
   if len(message) > 1:
      flash("Something went wrong when saving object XML file. ERROR MESSAGE: " + message, 'error')
   else:
      message = Markup("<a href=" + url_for('metadata.metadata_object_by_id', objectid=objectid) + "><button class=\"button is-dark\">Back</button></a>" + " File is saved to this folder! And you can go Back to MuseumPlus Object")
      flash(message, 'success')
   return redirect(url_for('data.data'))

@metadata_bp.route("/metadata_create_lido_xml")
@login_required
def metadata_create_lido_xml():
   objectid = request.args.get('objectid')
   session['mp_inv'] = ""
   session['mp_id'] = ""
   session['mp_name'] = ""
   #object_id = request.vars.object_id
   message = mp_metadata.create_lido_xml(objectid)
   if len(message) > 1:
          flash("Something went wrong when creating Lido XML file. ERROR MESSAGE: " + message, 'error')
   else:
      message = Markup("<a href=" + url_for('metadata.metadata_object_by_id', objectid=objectid) + "><button class=\"button is-dark\">Back</button></a>" + " File is saved to this folder! And you can go Back to MuseumPlus Object")
      flash(message, 'success')
   return redirect(url_for('metadata.metadata'))

@metadata_bp.route("/metadata_load_attachment")
@login_required
def metadata_load_attachment():
   objectid = request.args.get('objectid')
   objectname = request.args.get('objectname')
   object_id = request.args.get('img_id')
   object_name = request.args.get('img_name')
   try:
      input = mp_metadata.load_attachment(object_id)
      with open(DATA_path+object_name,'wb') as f:
         shutil.copyfileobj(input, f)
      message = Markup("<a href=" + url_for('metadata.metadata_object_by_id', objectid=objectid) + "><button class=\"button is-dark\">Back</button></a>" + " File is saved to this folder! And you can go Back to MuseumPlus Object")
      flash(message, 'success')
   except:
      flash("Something went wrong when downloading attachment file!", 'error' )
   return redirect(url_for('data.data'))

@metadata_bp.route("/metadata_read_lido_xml")
@login_required
def metadata_read_lido_xml():
   data = mp_metadata.read_lido_xml()
   session['mp_inv'] = data.get("mp_inv", "No value")
   session['mp_id'] = data.get("mp_id", "No value")
   session['mp_name'] = data.get("mp_name", "No value")
   session['mp_created'] = data.get("mp_created", "No value")
   files = os.listdir(METADATA_path)
   return render_template('metadata.html', files=files, environment=mp_metadata.MP_ENV, METADATA_path=METADATA_path)
   #return render_template('metadata_read_lido.html', mp_inv=mp_inv, mp_id=mp_id, mp_created=mp_created)

@metadata_bp.route('/metadata_import_description')
@login_required
def metadata_import_description():
   subprocess_args('import-description', METADATA_path+'lido_description.xml', '--workspace', SIP_path)
   message = Markup("Descriptive metadata file is imported to SIP folder")
   flash(message, 'success')
   return redirect(url_for('sip.sip'))


@metadata_bp.route('/metadata_search/', methods=['GET', 'POST'])
@login_required
def metadata_search():
   form = SearchMuseumPlus()
   if form.validate_on_submit():
      objectid = form.objectid.data
      invnumber = form.inventorynumber.data
      title = form.title.data
      message = objectid + invnumber + title
      if len(objectid) > 3:
         return redirect(url_for('metadata.metadata_object_by_id', objectid=objectid))
      elif len(invnumber) > 3:
         return redirect(url_for('metadata.get_object_by_inv', invnumber=invnumber))
      elif len(title) > 3:
         return redirect(url_for('metadata.get_object_by_title', title=title))
      else:
         flash('Minimum length for search field is 3 characters!', 'error')
         return render_template('metadata_search.html', form=form, message=message)
   message = ""
   return render_template('metadata_search.html', form=form, message=message, environment=mp_metadata.MP_ENV)

@metadata_bp.route('/metadata_object_by_id/', methods=['GET', 'POST'])
@login_required
def metadata_object_by_id():
   back = request.referrer
   objectid = request.args.get('objectid')
   xml_data, thumb_status = mp_metadata.get_object_by_id(objectid)
   return render_template('metadata_object_by_id.html', xml_data=xml_data, thumb_status=thumb_status, objectid=objectid, back=back)

@metadata_bp.route('/get_object_by_inv/', methods=['GET', 'POST'])
@login_required
def get_object_by_inv():
   back = request.referrer
   invnumber = request.args.get('invnumber')
   totalSize, mylist, xml = mp_metadata.get_object_by_number(invnumber)
   return render_template('metadata_object_by_inv.html', totalSize=totalSize, objects=mylist, xml=xml, back=back)

@metadata_bp.route('/get_object_by_title/', methods=['GET', 'POST'])
@login_required
def get_object_by_title():
   back = request.referrer
   title = request.args.get('title')
   totalSize, mylist, xml = mp_metadata.get_object_by_title(title)
   return render_template('metadata_object_by_title.html', title=title, totalSize=totalSize, objects=mylist, xml=xml, back=back)

#######################
### MAKE LIDO XML   ###
#######################
@metadata_bp.route('/metadata_lido_save', methods=['GET', 'POST'])
def metadata_lido_save():
   form = LidoSave()
   form.mp_created.data = datetime.datetime.now().isoformat()
   if form.validate_on_submit():
      data = form.data
      del data['submit']  # Poista submit-kenttä datasta
      del data['csrf_token']  # Poista csrf-token datasta
      #print("Request form data:", request.form)
      generate_lido_xml(data)
      return redirect(url_for('metadata.metadata'))
   return render_template('metadata_lido_save.html', form=form)

@metadata_bp.route('/metadata_lido_edit', methods=['GET', 'POST'])
def metadata_lido_edit():
   data2 = mp_metadata.read_lido_xml()
   form = LidoSave(data=data2)
   if form.validate_on_submit():
      data = form.data
      del data['submit']  # Poista submit-kenttä datasta
      del data['csrf_token']  # Poista csrf-token datasta
      #print("Request form data:", request.form)
      generate_lido_xml(data)
      return redirect(url_for('metadata.metadata'))
   return render_template('metadata_lido_save.html', form=form)

def generate_lido_xml(data):
   # Luodaan XML-rakenne samalla tavalla kuin aiemmin
   lidoWrap = ET.Element("lido:lidoWrap", {
      "xmlns:lido": "http://www.lido-schema.org",
      "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
      "xsi:schemaLocation": "http://www.lido-schema.org http://www.lido-schema.org/schema/v1.0/lido-v1.0.xsd"
   })
   lido = ET.SubElement(lidoWrap, "lido:lido")
   ET.SubElement(lido, "lido:lidoRecID", {
      "lido:source": ORGANIZATION,
      "lido:type": "ITEM"
   }).text = data['mp_inv']

   # Descriptive Metadata
   descriptiveMetadata = ET.SubElement(lido, "lido:descriptiveMetadata", {"xml:lang": "fi"})

   objectClassificationWrap = ET.SubElement(descriptiveMetadata, "lido:objectClassificationWrap")
   objectWorkTypeWrap = ET.SubElement(objectClassificationWrap, "lido:objectWorkTypeWrap")
   objectWorkType = ET.SubElement(objectWorkTypeWrap, "lido:objectWorkType")
   ET.SubElement(objectWorkType, "lido:term").text = "artwork"

   classificationWrap = ET.SubElement(objectClassificationWrap, "lido:classificationWrap")

   classificationAineistotyyppi = ET.SubElement(classificationWrap, "lido:classification", {"lido:type": "aineistotyyppi"})
   ET.SubElement(classificationAineistotyyppi, "lido:term", {"lido:label": "aineistotyyppi"}).text = data['classification1']

   classificationPaaluokka = ET.SubElement(classificationWrap, "lido:classification", {"lido:type": "luokitus"})
   ET.SubElement(classificationPaaluokka, "lido:term", {"lido:label": "pääluokka"}).text = data['classification2']

   if len(data['classification3']) > 1:
      classificationErikoisluokka = ET.SubElement(classificationWrap, "lido:classification", {"lido:type": "luokitus"})
      ET.SubElement(classificationErikoisluokka, "lido:term", {"lido:label": "erikoisluokka"}).text = data['classification3']

   # Title
   objectIdentificationWrap = ET.SubElement(descriptiveMetadata, "lido:objectIdentificationWrap")
   titleWrap = ET.SubElement(objectIdentificationWrap, "lido:titleWrap")
   titleSet = ET.SubElement(titleWrap, "lido:titleSet", {"lido:type": "nimi"})
   ET.SubElement(titleSet, "lido:appellationValue", {"xml:lang": "fi"}).text = data['mp_name']

   # Repository Wrap
   repositoryWrap = ET.SubElement(objectIdentificationWrap, "lido:repositoryWrap")
   repositorySet = ET.SubElement(repositoryWrap, "lido:repositorySet", {"lido:type": "haltija"})
   repositoryName = ET.SubElement(repositorySet, "lido:repositoryName")
   legalBodyName = ET.SubElement(repositoryName, "lido:legalBodyName")
   ET.SubElement(legalBodyName, "lido:appellationValue").text = data['mp_repository']
   ET.SubElement(repositorySet, "lido:workID", {"lido:type": "inventaarionumero"}).text = data['mp_inv']

   # Event
   eventWrap = ET.SubElement(descriptiveMetadata, "lido:eventWrap")
   eventSet = ET.SubElement(eventWrap, "lido:eventSet")
   event = ET.SubElement(eventSet, "lido:event")

   eventType= ET.SubElement(event, "lido:eventType")
   ET.SubElement(eventType, "lido:term").text = "valmistus"
   eventActor = ET.SubElement(event, "lido:eventActor")
   actorInRole = ET.SubElement(eventActor, "lido:actorInRole")
   actor = ET.SubElement(actorInRole, "lido:actor")
   nameActorSet = ET.SubElement(actor, "lido:nameActorSet")
   ET.SubElement(nameActorSet, "lido:appellationValue").text = data['mp_actor']

   eventDateElement = ET.SubElement(event, "lido:eventDate")
   ET.SubElement(eventDateElement, "lido:displayDate").text = data['mp_creation']

   # Administrative Metadata
   administrativeMetadata = ET.SubElement(lido, "lido:administrativeMetadata", {"xml:lang": "fi"})
   recordWrap = ET.SubElement(administrativeMetadata, "lido:recordWrap")
   ET.SubElement(recordWrap, "lido:recordID", {"lido:type": "ObjectId"}).text = data['mp_id']
   recordType= ET.SubElement(event, "lido:recordType")
   ET.SubElement(recordType, "lido:term").text = "objekti"   

   recordSource = ET.SubElement(recordWrap, "lido:recordSource")
   legalBodyName = ET.SubElement(recordSource, "lido:legalBodyName")
   ET.SubElement(legalBodyName, "lido:appellationValue").text = data['mp_owner']

   recordInfoSet = ET.SubElement(recordWrap, "lido:recordInfoSet")
   ET.SubElement(recordInfoSet, "lido:recordMetadataDate").text = data['mp_created']

   # Tallenna XML-tiedosto
   tree = ET.ElementTree(lidoWrap)
   output_file = METADATA_path + 'lido_description.xml'
   tree.write(output_file, encoding='utf-8', xml_declaration=True)

   return redirect(url_for('metadata.metadata'))

#######################
### DELETE FILES    ###
#######################
@metadata_bp.route("/metadata_delete")
@login_required
def metadata_delete():
   delete_really = request.args.get('delete') 
   if delete_really == "True":
      try:
         shutil.rmtree(METADATA_path)
         os.mkdir(METADATA_path)
         session['mp_inv'] = ""
         session['mp_id'] = ""
         session['mp_name'] = ""
         session['mp_created'] = ""
      except:
         message = "Could not delete folder!"
         flash(message, 'error')
   else:
      message = Markup("Do you really want to delete this folder? <a href=" + url_for('metadata.metadata_delete', delete="True") + "><button class=\"button is-danger\">Delete</button></a>"+" <a href=" + url_for('metadata.metadata') + "><button class=\"button is-dark\">Cancel</button> </a>")
      flash(message, 'error')
   return redirect(url_for('metadata.metadata'))

@metadata_bp.route("/metadata_file_delete")
@login_required
def metadata_file_delete():
   path = request.args.get('path')
   file = request.args.get('name')
   view = request.args.get('page')
   path = METADATA_path # This is dummy but secure
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
