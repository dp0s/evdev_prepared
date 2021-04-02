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


from setuptools import setup, find_packages
from time import sleep
import multiprocessing, os, subprocess, warnings, shutil, sys

dirname = os.path.dirname(os.path.realpath(__file__))
os.chdir(dirname)


#with open("README.md", "r") as fh: long_description = fh.read()

try:
    subprocess.run(["licenseheaders", "-t", "licenseheader.txt", "-E", ".py"])
except FileNotFoundError as e:
    warnings.warn(str(e))

shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)

sys.path.insert(0, dirname)
#this way we will import from this folder not from pip
import evdev_prepared

def my_setup(name, **kwargs):
    if "version" not in kwargs: raise ValueError
    shutil.rmtree(f"{name}.egg-info", ignore_errors=True)
    print()
    print()
    print(f"------------------------  Package {name} ----------------------------")
    print()
    sleep(1)
    # for creating wheels using bdist_wheel it is somehow necessary to run
    # the setup command inside a seperate process.
    sub_process = multiprocessing.Process(target=setup_process, args=(name,),
            kwargs=kwargs)
    sub_process.start()
    sub_process.join()

def setup_process(name, **kwargs):
    setup(**kwargs,
        name=name,
        packages=find_packages(),
        include_package_data=False,
        ####must stay disabled to allow package_data option !!!
        python_requires=">=3.6", # metadata to display on PyPI
        author="DPS", author_email="dps@my.mail.de",
        url="https://github.com/dp0s/evdev_prepared",
        classifiers=["Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
         )


my_setup("evdev_prepared",
    version = evdev_prepared.__version__,
    install_requires=["setuptools >= 45","evdev>=1.4.0"],
    description="Useful classes to make usage of python evdev easier"
    )


print()
print("DONE")
