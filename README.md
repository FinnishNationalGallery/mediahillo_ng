# MediaJam NG / Mediahillo NG

MediaJam (Mediahillo) is a long term preservation **packaging tool interface**, developed in FInnish National Gallery.
MediaJam is a Flask application working in Python 3 environment.

MediaJam uses [dpres-siptools-ng](https://github.com/Digital-Preservation-Finland/dpres-siptools-ng) commands for packaging files. Therefore [dpres-siptools-ng](https://github.com/Digital-Preservation-Finland/dpres-siptools-ng) MUST be installed to the same server. Installation on Linux distributions is done by using the RPM Package Manager. 

MediaJam can get descriptive metadata from [MuseumPlus](https://www.zetcom.com/en/kookos-collection-management-services-to-be-transferred-to-zetcom-nordics/) collection management system through API-interface.

Application is tested with AlmaLinux 9 server. Flask application was installed as a reverse-proxy installation with [Gunicorn](https://gunicorn.org/) and [NGINX](https://www.nginx.com/) www-servers.

## Installation
As user root:
First read [AlmaLinux instructions](README_AlmaLinux.md) and install dpres-siptools-ng
``````
Then add user for MediaJam:
adduser pasisti
passwd pasisti
``````
Install MediaJam as user pasisti (virtualenv not used):
``````
cd /home/pasisti
git clone https://github.com/FinnishNationalGallery/mediahillo_ng.git mediahillo_ng
cd mediahillo_ng
pip install -r requirements-flask3.txt
``````
Install and configure NGINX as user root:
``````
dnf install nginx -y
systemctl enable nginx
systemctl start nginx
# Configure nginx using gunicorn reverse proxy installation
nano /etc/nginx/nginx.conf
# Add this configuration to nginx.conf file for http server (and https server if needed)
        location / {
        proxy_read_timeout 28800;
        proxy_connect_timeout 28800;        
        proxy_send_timeout 28800;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Prefix /;
        # upstream sent too big header while reading response header from upstream
        proxy_busy_buffers_size   512k;
        proxy_buffers   4 512k;
        proxy_buffer_size   256k;
        }
# 
systemctl restart nginx
``````
## Start Flask application with gunicorn www-server as user pasisti:
``````
cd /home/pasisti/mediahillo_ng
# Configure .env file from env.txt 
nano env.txt
cp env.txt .env
# Start gunicorn www-server as reverse proxy
gunicorn -w 1 --timeout 28800 'app:app'
# Now you can go to servers home page and see MediaJam in action
``````
### Other commands for gunicorn management:
``````
# Start gunicorn to background and use access and error logfiles
gunicorn -w 1 --timeout 28800 'app:app' --access-logfile gunicorn-access.txt --error-logfile gunicorn-error.txt &
# Check if gunicorn processes are in progress
ps -aux | grep "gunicorn"
# Kill gunicorn processes so that you can restart application
kill -9 #process number
``````