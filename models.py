from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(150), unique=True, index=True)
    password_hash = db.Column(db.String(150))
    joined_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow, index=True)
    token = db.Column(db.String(50))

    def set_token(self, mytoken):
        self.token = mytoken

    def set_password(self, password):
        # https://werkzeug.palletsprojects.com/en/3.0.x/utils/#werkzeug.security.generate_password_hash
        # This is for Apple Mac with LibreSSL
        # self.password_hash = generate_password_hash(password, method='pbkdf2')
        # This is for Linux with OpenSSL, when method is by default scrypt
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class db_paslog_mp(db.Model):
    __tablename__ = 'db_paslog_mp'
    id = db.Column('paslog_id', db.Integer, primary_key=True)
    mp_id = db.Column(db.String(50))
    mp_name = db.Column(db.String(500))
    mp_paslog = db.Column(db.String(500))

class db_paslog_csc(db.Model):
    __tablename__ = 'db_paslog_csc'
    id = db.Column('paslog_id', db.Integer, primary_key=True)
    pas_mp_id = db.Column(db.String(50))
    pas_id = db.Column(db.String(500))
    pas_created = db.Column(db.String(50))
    pas_location = db.Column(db.String(500))
    mp_paslog = db.Column(db.String(500))