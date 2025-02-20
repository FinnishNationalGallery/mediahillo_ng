# AlmaLinux 9 and dpres-siptools dependencies

MediaJam needs dpres-siptools-ng to be installed with certain dependencies in AlmaLinux 9 server. 
Installation on Linux distributions is done by using the RPM Package Manager. 

Digital-Preservation-Finland has developed RPM packages to make installation easier.

> Install these as root user.

**INSTALL BASIC TOOLS**
```
dnf install git
dnf install tar
dnf install nano
dnf install python3-pip
```
**INSTALL RPM TOOLS**
```
rpm --import https://pas-jakelu.csc.fi/RPM-GPG-KEY-pas-support-el9 
dnf install dnf-plugins-core 
dnf config-manager --add-repo=https://pas-jakelu.csc.fi/pas-jakelu-csc-fi.repo
dnf config-manager --set-enabled crb
dnf install epel-release
dnf install --nogpgcheck https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-9.noarch.rpm
```
**INSTALL DPRES TOOLS**
```
dnf install python3-dpres-siptools-ng
dnf install python3-dpres-mets-builder
dnf install python3-file-scraper-full 
dnf update ImageMagick
```
**INSTALL EXTRA TOOLS**
```
dnf install mediainfo-gui mediainfo libmediainfo
dnf install ghostscript
