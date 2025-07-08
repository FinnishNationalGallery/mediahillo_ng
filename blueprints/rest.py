
from flask import Blueprint, render_template, request, url_for, flash, redirect, send_file, session, jsonify
from flask_login import login_required, current_user
import modules.pas_rest as pas_rest

rest_bp = Blueprint('rest', __name__)

@rest_bp.route("/pas_rest_index")
@login_required
def pas_rest_index():
   message = "Choose function from left panel"
   return render_template('pas_rest_index.html', environment=pas_rest.REST_ENV, message=message)

@rest_bp.route("/pas_rest_status")
@login_required
def pas_rest_status():
   message = pas_rest.get_status()
   return render_template('pas_rest_status.html', environment=pas_rest.REST_ENV, message=message)

@rest_bp.route("/pas_rest_accepted_created", methods=['GET', 'POST'])
@login_required
def pas_rest_accepted_created():
   message = ""
   counter = 0
   error = ""
   value = ""
   created = ""
   if request.method == 'POST':
      created = "\"" + request.form['created'] + "\""
      if request.form['created'] == "":
         created = "/.*/"
      if request.form['created'] == "*":
         created = "/.*/"
      value = request.form['created']
      try:
         message, counter, error = pas_rest.get_accepted_created(created)
      except:
         message = {'status': 'fail', 'data': {'message': 'Error with REST command!'}}
         counter = ""
         error = ""
         value = ""
   return render_template('pas_rest_accepted_created.html', environment=pas_rest.REST_ENV, message=message, counter=counter, error=error, value=value)

@rest_bp.route("/pas_rest_accepted_mpid", methods=['GET', 'POST'])
@login_required
def pas_rest_accepted_mpid():
   message = ""
   counter = 0
   error = ""
   value = ""
   mpid = ""
   if request.method == 'POST':
      mpid = request.form['mpid'] + "*"
      if request.form['mpid'] == "":
         mpid = "/.*/"
      if request.form['mpid'] == "*":
         mpid = "/.*/"
      value = request.form['mpid']
      try:
         message, counter, error = pas_rest.get_accepted_mpid(mpid)
      except:
         message = {'status': 'fail', 'data': {'message': 'Error with REST command!'}}
         counter = ""
         error = ""
         value = ""
   return render_template('pas_rest_accepted_mpid.html', environment=pas_rest.REST_ENV, message=message, counter=counter, error=error, value=value)

@rest_bp.route("/pas_rest_accepted_mpinv", methods=['GET', 'POST'])
@login_required
def pas_rest_accepted_mpinv():
   message = ""
   counter = 0
   error = ""
   value = ""
   mpinv = ""
   if request.method == 'POST':
      mpinv = request.form['mpinv']
      if request.form['mpinv'] == "":
         mpinv = "/.*/"
      if request.form['mpinv'] == "*":
         mpinv = "/.*/"
      value = request.form['mpinv']
      try:
         message, counter, error = pas_rest.get_accepted_mpinv(mpinv)
      except:
         message = {'status': 'fail', 'data': {'message': 'Error with REST command!'}}
         counter = ""
         error = ""
         value = ""
   return render_template('pas_rest_accepted_mpinv.html', environment=pas_rest.REST_ENV, message=message, counter=counter, error=error, value=value)

@rest_bp.route("/pas_rest_accepted_img_desc", methods=['GET', 'POST'])
@login_required
def pas_rest_accepted_img_desc():
   message = ""
   counter = 0
   error = ""
   value = ""
   description = ""
   if request.method == 'POST':
      description = request.form['description']
      if request.form['description'] == "":
         description = "/.*/"
      if request.form['description'] == "*":
         description = "/.*/"
      value = request.form['description']
      try:
         message, counter, error = pas_rest.get_accepted_img_desc(description)
      except:
         message = {'status': 'fail', 'data': {'message': 'Error with REST command!'}}
         counter = ""
         error = ""
         value = ""
   return render_template('pas_rest_accepted_description.html', environment=pas_rest.REST_ENV, message=message, counter=counter, error=error, value=value)

@rest_bp.route("/pas_rest_disseminate_aip", methods=['GET', 'POST'])
@login_required
def pas_rest_disseminate_aip():
   message = ""
   if request.method == 'POST':
      aipid = request.form['aipid']
      message, error = pas_rest.disseminate_aip(aipid)
   return render_template('pas_rest_disseminate_aip.html', environment=pas_rest.REST_ENV, message=message, error=error)