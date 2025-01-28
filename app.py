from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import dotenv_values
from extensions import init_extensions
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.data import data_bp
from blueprints.datanative import datanative_bp
from blueprints.metadata import metadata_bp
from blueprints.sip import sip_bp
from blueprints.download import download_bp
from blueprints.sftp import sftp_bp
from blueprints.rest import rest_bp
from blueprints.paslog import paslog_bp

def create_app():
   app = Flask(__name__)

   # Load configuration
   config = dotenv_values(".env")
   app.config['SECRET_KEY'] = config['SECRET_KEY']
   app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pas_db.db'

   # Add email configuration
   app.config.update(
       MAIL_SERVER=config['MAIL_SERVER'],
       MAIL_PORT=587,
       MAIL_USE_TLS=True,
       MAIL_USE_SSL=False,
       MAIL_USERNAME=config['MAIL_USERNAME'],
       MAIL_PASSWORD=config['MAIL_PASSWORD']
   )

   # Initialize extensions with the app
   init_extensions(app)

   # Apply ProxyFix
   app.wsgi_app = ProxyFix(
      app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
   )

   # Register blueprints
   app.register_blueprint(auth_bp, url_prefix='/auth')
   app.register_blueprint(main_bp)
   app.register_blueprint(data_bp)
   app.register_blueprint(datanative_bp)
   app.register_blueprint(metadata_bp)
   app.register_blueprint(sip_bp)
   app.register_blueprint(download_bp)
   app.register_blueprint(sftp_bp)
   app.register_blueprint(rest_bp)
   app.register_blueprint(paslog_bp)


   # Create database tables
   with app.app_context():
      from extensions import db
      db.create_all()

   return app

# Create an application instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)