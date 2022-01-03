#!/bin/bash
PASSWD='Messiah'

HOSTNAME='messiah-ptz-ctl'

LOCALE='en_US.UTF-8'
LAYOUT='us'
TIMEZONE='America/Chicago'

# Change user 'pi' password
sudo sh -c 'echo pi:${PASSWD} | chpasswd'

# General system updates
sudo apt-get -y update
sudo apt-get -y upgrade

# Install OS dependencies
sudo apt-get -y install libhidapi-hidraw0 libhidapi-libusb0
sudo apt-get -y install python3 python3-pip
sudo apt-get -y install rdate isc-dhcp-server

# Install python dependencies
sudo python -m pip install -r requirements.txt

# Configure the raspberry pi
sudo raspi-config nonint do_hostname ${HOSTNAME}
sudo raspi-config nonint do_change_locale ${LOCALE}
sudo raspi-config nonint do_change_timezone ${TIMEZONE}
sudo raspi-config nonint do_configure_keyaboard ${LAYOUT}
sudo raspi-config nonint do_ssh 0

# Set the system date/time
sudo rdate -n -4 time.nist.gov

# Configure networking
sudo cp -af config/dhcpd.conf /etc/dhcp/dhcpd.conf
sudo cp -af config/interfaces /etc/network/interfaces
sudo sed -i 's/INTERFACESv4=".*"/INTERFACESv4="eth0"/g' /etc/default/isc-dhcp-server

# Set messiah-ptz-controller.py to run at boot
# TODO / FIXME

reboot
