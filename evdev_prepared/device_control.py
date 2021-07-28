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
import collections
import time, threading
from evdev import list_devices
from .input_dev import AdhancedInputDevice, EvdevInputLooper, DefaultInputLooper
from evdev.ecodes import (EV_KEY, EV_ABS, EV_SYN, EV_MSC, KEY, BTN,
    EV_LED)


class DeviceUpdater:
    device_folder = "/dev/input"
    InputDevice_cls = AdhancedInputDevice
    
    def __init__(self, autoupdating=True, update_interval=5,
            print_dev_change=True, allow_collecting=True,
            use_distinct_looper=False):
        if allow_collecting:
            if use_distinct_looper:
                self.input_looper = EvdevInputLooper()
            else:
                self.input_looper = DefaultInputLooper
            self.InputDevice_cls = self.input_looper.DeviceClass
            assert issubclass(self.InputDevice_cls, self.__class__.InputDevice_cls)
        self.all_devs = []
        self._autoupdating = False
        self.update_interval = update_interval
        self.change_actions = []
        if print_dev_change: self.change_actions.append(self.print_dev_change)
        self.autoupdating = autoupdating
            # this will trigger self.update_devs if autoupdating is True
        
    
    # upon creation of an InputDevice for a path/device that has already been
    # created, the fileno alias fd can change, which might give problems.
    # I.e. we have two instances of InputDevice for the same path, but with
    # different fd. A typical problem: If one of them is grabbed, the other
    # instance is useless suddenly.
    # The problem is solved below by manually checking if such an InputDevice
    # was already found in the last run of update_devs and replace the new
    # with the old instance to keep the fd identic.
    # NOTE: if a device is disconnected for more than 5s (i.e. until the next
    # run of update_devs), it is "forgotten". so that when the device is
    # reconnected, a fresh instance of InputDevice is created (with possibly
    # new fd).
    
    
    
    def update_devs(self, run_change_action=True):
        remaining_devs = self.all_devs
        new_devs = []
        found_new = []
        for path in list_devices(self.device_folder):
            dev = self.InputDevice_cls(path)
            for old_dev in remaining_devs:
                if dev == old_dev:
                    # this compares info and path attributes, but not fd
                    dev = old_dev  # this makes sure fd is the same.
                    remaining_devs.remove(old_dev)
                    break
            else:
                found_new.append(dev)
            new_devs.append(dev)
        if not new_devs:
            msg = 'error: no input devices found (do you have rw permission ' \
                  'on %s/*?)'
            raise IOError(msg%self.device_folder)
        self.all_devs = new_devs
        #print("Update devs\n", "found_new\n",found_new,"\nremaining_devs\n",
        # remaining_devs)
        if run_change_action and (found_new or remaining_devs):
            for action in self.change_actions:
                action(found_new, remaining_devs)
    
    
    @staticmethod
    def print_dev_change(found_new, lost_devs):
        msg = ""
        if found_new:
            msg += "New devs found:\n"
            for dev in found_new: msg += str(dev) + "\n"
        if lost_devs:
            msg += "Following devs lost:\n"
            for dev in lost_devs: msg += str(dev) + "\n"
        print(msg)
    
    @property
    def autoupdating(self):
        return self._autoupdating
    
    @autoupdating.setter
    def autoupdating(self, state: bool):
        old = self._autoupdating
        self._autoupdating = state
        if not old and state:
            self.update_devs()
            threading.Thread(target=self.updater).start()
    
    def updater(self):
        while self._autoupdating:
            time.sleep(self.update_interval)
            self.update_devs()
            #self.input_looper.print_devices()




class DeviceSelector:
    
    _used_updaters = []
    
    allowed_attributes = {"category": "exact", "name": "substring", "path":
        "substring"}
    
    def __init__(self, devupdater=None, exclude_uinput = True,
            selection_func=None, **selection_kwargs):
        if selection_func and selection_kwargs: raise ValueError
        if not selection_func and not selection_kwargs: raise ValueError
        self.selection_func = selection_func
        self.included = dict()
        self.excluded = dict()
        for key, val in selection_kwargs.items():
            excl = True
            if key.startswith("exclude_"): key = key[8:]
            elif key.startswith("excl_"): key = key[5:]
            else:
                excl = False
            assert key in self.allowed_attributes
            if not isinstance(val,(list,tuple)): val = [val]
            if excl:
                self.excluded[key] = val
            else:
                self.included[key] = val
        if exclude_uinput:
            if "uinput" not in self.included.get("category", ()):
                l = list(self.excluded.get("category",[]))
                if "uinput" not in l: l.append("uinput")
                self.excluded["category"] = l
        if devupdater is None:
            if self._used_updaters:
                for old_updater in self._used_updaters:
                    if old_updater.autoupdating: devupdater = old_updater
            else:
                devupdater = DeviceUpdater()
        self.devupdater = devupdater
        if devupdater not in self._used_updaters:
            self._used_updaters.append(devupdater)
        devupdater.change_actions.append(self.dev_change_action)
    
    def properties(self):
        return self.included, self.excluded, self.selection_func
    
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.properties() == other.properties()
        return NotImplemented
    
    def dev_is_selected(self, dev):
        if self.selection_func is not None:
            return self.selection_func(dev)
        if self._compare_vals(dev, self.excluded): return False
        if not self.included: return True
        if self._compare_vals(dev, self.included): return True
        return False
    
    def _compare_vals(self, dev, dic):
        for key, values in dic.items():
            matching_behavior = self.allowed_attributes[key]
            dev_attribute_val = getattr(dev, key)
            for val in values:
                if matching_behavior == "exact":
                    if val == dev_attribute_val: return True
                elif matching_behavior == "substring":
                    if val in dev_attribute_val: return True
    
    
    def matching_devs(self):
        return list(dev for dev in self.devupdater.all_devs if
                self.dev_is_selected(dev))
    
    def dev_change_action(self, found_new, lost_devs):
        pass



class DeviceHandler(DeviceSelector):
    
    
    def __init__(self, devupdater=None, **selection_kwargs):
        DeviceSelector.__init__(self, devupdater=devupdater, **selection_kwargs)
        self.devupdater.change_actions.append(self._check_on_change)
        self.collect_active = False
        self.collected_devs = []
        self.grab_active = False
        self.grabbed_devs = []
    
    def _check_on_change(self, found_new, lost_devs):
        # this way, the EvdevHandler will automatically register newly
        # appearing devs and release disappearing devs
        for dev in lost_devs:
            if self.collect_active and dev in self.collected_devs:
                self.uncollect_dev(dev)
                self.collected_devs.remove(dev)
            if self.grab_active and dev in self.grabbed_devs:
                self.ungrab_dev(dev)
                self.grabbed_devs.remove(dev)
        for dev in found_new:
            if self.dev_is_selected(dev):
                if self.collect_active:
                    if dev in self.collected_devs: raise ValueError
                    self.collect_dev(dev)
                    self.collected_devs.append(dev)
                if self.grab_active:
                    if dev in self.grabbed_devs: raise ValueError
                    self.grab_dev(dev)
                    self.grabbed_devs.append(dev)
    
    def start_collecting(self):
        self.collect_active = True
        self.collected_devs = self.matching_devs()
        for dev in self.collected_devs: self.collect_dev(dev)
        
    def start_grabbing(self):
        self.grab_active = True
        self.grabbed_devs = self.matching_devs()
        for dev in self.grabbed_devs: self.grab_dev(dev)
    
    def stop_collecting(self):
        self.collect_active = False
        for dev in self.collected_devs: self.uncollect_dev(dev)
        self.collected_devs = []
        
    def stop_grabbing(self):
        self.grab_active = False
        for dev in self.grabbed_devs: self.ungrab_dev(dev)
        self.grabbed_devs = []

    def collect_dev(self, dev):
        dev.collect(collector=self)

    def uncollect_dev(self, dev):
        dev.uncollect(collector=self)
    
    def grab_dev(self, dev):
        dev.grab(grabber=self)
    
    def ungrab_dev(self, dev):
        dev.ungrab(grabber=self)

    def process_event(self, ty, co, val, dev):
        raise NotImplementedError

    
    #compatibility with Dpowers naming convention:
    start_capturing = start_grabbing
    stop_capturing = stop_grabbing