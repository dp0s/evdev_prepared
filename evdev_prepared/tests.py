#
#
# Copyright (c) 2020-2021 DPS, dps@my.mail.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#

uinput_instruction = """echo 'KERNEL=="uinput", TAG+="uaccess"' | sudo tee -a '/etc/udev/rules.d/50-uinput.rules'"""
input_instruction = "sudo usermod -a -G input $USER"
install_instructions = input_instruction + "\n" + uinput_instruction

def check_uinput():
    import evdev.uinput as ui
    try:
        ui.UInput()  # this will raise an error if /dev/uinput is not writable
    except ui.UInputError as e:
        msg ="Seems like there is no access to /dev/uninput. Please refer "\
             " to https://github.com/dp0s/evdev_prepared#writing-to-devuinput."
        raise OSError(msg)

# the following check is performed automatically if importing the
# evdev_preperation.input_dev module.
def check_evdev_input_devices(device_dir='/dev/input'):
    from evdev import list_devices, InputDevice
 
    devices = []
    for path in list_devices(device_dir):
        dev = InputDevice(path)
        if "uinput" in dev.name: continue
        devices.append(path)
        dev.close()

    if not devices:
        msg = f"No devices found in {device_dir}. Probably read/write " \
          f"permission is missing. \nPlease refer to " \
          f"https://github.com/dp0s/evdev_prepared#accessing-devinput"
        raise OSError(msg)
    return devices