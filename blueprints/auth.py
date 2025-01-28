from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db, login_manager, mail
from flask_mail import Message
import uuid
from forms.form_login import *
from dotenv import dotenv_values

auth_bp = Blueprint('auth', __name__)

config = dotenv_values(".env")

# Configuration
APP_SERVER_ADDRESS = config['APP_SERVER_ADDRESS']


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/register/', methods=['POST', 'GET'])
def register():
   form = RegistrationForm()
   if form.validate_on_submit():
      try:
         user = User(username =form.username.data, email = form.email.data)
         user.set_password(form.password1.data)
         db.session.add(user)
         db.session.commit()
         return redirect(url_for('auth.login'))
      except Exception as e:
         flash("Error! "+ str(e))
   return render_template('login_registration.html', form=form)

@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
   form = LoginForm()
   if form.validate_on_submit():
      user = User.query.filter_by(email = form.email.data).first()
      if user is not None and user.check_password(form.password.data):
         if form.remember:
            login_user(user, remember=True)
         else:
            login_user(user)
         next = request.args.get("next")
         return redirect(next or url_for('main.index'))
      flash('Invalid email address or Password.')    
   return render_template('login.html', form=form)

@auth_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/login_reset_email/', methods=['POST', 'GET'])
def login_reset_email():
   form = LoginFormReset()
   if form.validate_on_submit():
      try:
         user = User.query.filter_by(email = form.email.data).first()
         mytoken = str(uuid.uuid4())
         user.set_token(mytoken)
         db.session.commit()
         msg = Message('PAS palvelimen käyttäjätunnuksen sähköpostiviesti!', sender = config['MAIL_USERNAME'], recipients = [form.email.data])
         msg.body = "Hei,\n\nOlet pyytänyt salasanan resetointia PAS-paketoinnin palvelussa!\n\nVaihda tunnuksen salasana tästä linkistä: \n\n" + APP_SERVER_ADDRESS + url_for('auth.register_reset', token=mytoken) +"\n\n"
         mail.send(msg)
         flash("Email send to : "+form.email.data+" \n\nRemember to check Junk Email folder!")
      except Exception as e:
         flash("Error! " + str(e))
   return render_template("login_reset_email.html", form=form)

@auth_bp.route('/register_reset/<string:token>', methods=['POST', 'GET'])
def register_reset(token):
   form = RegistrationFormReset()
   if form.validate_on_submit():
      try:
         user=User.query.filter_by(token=token).first()
         user.set_password(form.password1.data)
         mytoken = str(uuid.uuid4())
         user.set_token(mytoken)
         db.session.commit()
         flash("Password changed, you can login now!")
         
         return redirect(url_for('auth.login'))
      except Exception as e:
         flash("Error! User with given token not found!")
   try:
      user=User.query.filter_by(token=token).first()
      flash(user.email)
   except:
      flash("Reset link has expired!")
   return render_template('login_registration_reset.html', form=form, token=token)

@auth_bp.route('/list_users/')
@login_required
def login_list_registered_users():
    try:
        users = User.query.order_by(User.joined_at.desc()).all()
        return render_template('login_list_users.html', users=users)
    except Exception as e:
        flash("Error fetching users: " + str(e))
        return redirect(url_for('main.index'))
