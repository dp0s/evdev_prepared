This package provides classes that solve common tasks when using python evdev:

https://github.com/gvalkov/python-evdev

Features:
- Find a list of all input devices and keep them up to date (if new are 
  added / existign removed).
- Categorize the devices and select all devices with certain category.
- Loop over all input events of selected devices and call a function for each.
- Provide a global uinput object to handle sending events.


evdev_prepared is mainly intended as a backend to the Dpowers project:

https://github.com/dp0s/Dpowers