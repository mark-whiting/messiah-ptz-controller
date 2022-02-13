#!/bin/sh
PASSWD='Messiah'

HOSTNAME='messiah-ptz-ctl'

LOCALE='en_US.UTF-8'
LAYOUT='us'
TIMEZONE='America/Chicago'

# Change user 'pi' password
sudo sh -c 'echo 'pi:${PASSWD}' | chpasswd'

# General system updates
sudo apt-get -y update
sudo apt-get -y upgrade

# Install OS dependencies
sudo apt-get -y install aptitude
sudo apt-get -y install python3 python3-cffi python3-pip
sudo apt-get -y install supervisor rdate
#sudo apt-get -y install isc-dhcp-server

# Install python dependencies
sudo python -m pip install -r requirements.txt

# Configure the raspberry pi locale
sudo raspi-config nonint do_change_locale ${LOCALE}
sudo raspi-config nonint do_change_timezone ${TIMEZONE}
sudo raspi-config nonint do_configure_keyboard ${LAYOUT}

# Set the system date/time
sudo rdate -n -4 time.nist.gov

# Configure networking
#sudo cp -af config/dhcpd.conf /etc/dhcp/dhcpd.conf
#sudo cp -af config/interfaces /etc/network/interfaces
#sudo sed -i 's/INTERFACESv4=".*"/INTERFACESv4="eth0"/g' /etc/default/isc-dhcp-server

# Install custom udev rules
sudo cp -af config/51-axis-t8311.rules /usr/lib/udev/rules.d

# Set messiah-ptz-controller.py to run at boot
sudo cp -af config/messiah-ptz-controller.conf /etc/supervisor/conf.d

# Enable SSH access and set hostname
sudo raspi-config nonint do_ssh 0
sudo raspi-config nonint do_hostname ${HOSTNAME}

reboot
