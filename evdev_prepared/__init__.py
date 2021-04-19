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
__version__ = "0.2.2"


from . import tests

install_instructions = tests.install_instructions

def permission_test(path = "/dev/input"):
    try:
        tests.check_uinput()
        tests.check_evdev_input_devices(path)
    except OSError as e:
        raise OSError("There seems to be a permission error. Refer to "
          "https://github.com/dp0s/evdev_prepared\n Usually the "\
          "following lines fix the permission problems. \n\n"
                      + install_instructions+ "\n\n Restart afterwards.") from e
    else:
        print("Permissions seem to be ok.")


if __name__ == "__main__":
    permission_test()