#!/bin/bash
# Pi 4 Dependency install script

# Intalling Dependencies
sudo pip3 install lsq-ellipse
sudo apt-get install libatlas-base-dev
sudo pip3 install imutils
sudo pip3 install opencv-python==4.1.0.25 # Pi 3 may need different version?
sudo apt install libjasper1
sudo apt-get --yes --force-yes install libatlas-base-dev
sudo apt-get install libqtgui4
sudo apt install libqt4-test
sudo pip3 install zmq
# pip3 install circle-fit # Not working due to scipy problems...
sudo apt-get install network-manager
# sudo nmcli dev wifi connect NETWORK_NAME password NETWORK_PASSWORD


# Install kernels for the wifi adapter
# https://www.raspberrypi.org/forums/viewtopic.php?f=91&t=54946&p=1427675#p1427675
# https://www.raspberrypi.org/forums/viewtopic.php?uid=81098&f=28&t=62371&start=0#p462982
sudo apt purge firmware-realtek
sudo wget http://downloads.fars-robotics.net/wifi-drivers/install-wifi -O /usr/bin/install-wifi
sudo chmod +x /usr/bin/install-wifi
sudo install-wifi

# make a rule for how to deal with assigning wifi adapter names
# https://www.raspberrypi.org/forums/viewtopic.php?t=198946
# ln -nfs /dev/null /etc/systemd/network/99-default.link
# sudo nano /etc/udev/rules.d/72-wlan-geo-dependent.rules

# Setting up accsess point
# https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md
# https://www.raspberrypi.org/forums/viewtopic.php?t=216288

#sudo apt install hostapd
#sudo systemctl unmask hostapd
#sudo systemctl enable hostapd
#sudo apt install dnsmasq
#sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent

# need to just have the file written I guess
#sudo nano /etc/dhcpcd.conf

#sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig

# need to just have the file written I guess
#sudo nano /etc/dnsmasq.conf

#sudo rfkill unblock wlan

# need to just have the file written I guess
#sudo nano /etc/hostapd/hostapd.conf