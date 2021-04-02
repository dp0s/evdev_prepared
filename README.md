This package provides classes that solve common tasks when using python evdev:

https://github.com/gvalkov/python-evdev

It is mainly intended as backend to the Dpowers project:

https://github.com/dp0s/Dpowers

But maybe it's useful for your project too.

Features
-

- Find a list of all input devices and keep them up to date (if new are 
  added / existign removed).
- Categorize the devices and select all devices with certain category.
- Loop over all input events of selected devices and call a function for each.
- Provide a global uinput object to handle sending events.





Writing to /dev/uinput
-

In order to run evdev_prepared.uinput module without root privilege, please add
`KERNEL=="uinput", TAG+="uaccess"` to `/etc/udev/rules.d/50-uinput.rules` 
file:
```
echo 'KERNEL=="uinput", TAG+="uaccess"' | sudo tee -a '/etc/udev/rules.d/50-uinput.rules'
```
Restart the system afterwards.


Accessing /dev/input
-
Evdev needs access to the /dev/input folder and its contents to receive 
events. In order to achieve this without root privilege, you can add the 
current user the the system's permission group "input":

`sudo usermod -a -G input <user>`