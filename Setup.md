# Setup Instructions

#### Updating Wifi Adapter
```
sudo apt purge firmware-realtek
sudo wget http://downloads.fars-robotics.net/wifi-drivers/install-wifi -O /usr/bin/install-wifi
sudo chmod +x /usr/bin/install-wifi
sudo install-wifi
```
---------------------

#### Custom Wifi Names

```
sudo ln -nfs /dev/null /etc/systemd/network/99-default.link
sudo nano /etc/udev/rules.d/72-wlan-geo-dependent.rules
```
Type this into the file:

```
ACTION=="add", SUBSYSTEM=="net", DRIVERS=="brcmfmac", NAME="wlan1"
```
---------------------
#### Custom USB Naming for Lidar

```
sudo nano /etc/udev/rules.d/10-usb-serial.rules
```

Type this into the file:

```
SUBSYSTEM=="tty", ATTRS{product}=="LIDAR", ATTRS{idVendor}=="10c4", SYMLINK+="turtle/USB_lidar"
SUBSYSTEM=="tty", ATTRS{product}=="CP2102 USB to UART Bridge Controller", ATTRS{idVendor}=="10c4", SYMLINK+="turtle/USB_micro"
```

Then trigger the update and check that it worked
```
sudo udevadm trigger
ls -l /dev/turtle/USB
```

---------------------
### Setting Up WiFi Accsess point
https://www.raspberrypi.org/documentation/configuration/wireless/access-point-routed.md