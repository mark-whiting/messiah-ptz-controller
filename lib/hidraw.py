# FIXME

import pathlib

sysfs_base = pathlib.Path('/', 'sys', 'class', 'hidraw')

def parse_vid_pid(uevent_data):
    try:
        for line in uevent_data.splitlines():
            if not line.startswith('HID_ID'):
                continue

            parts = line.split(':')
            if len(parts) != 3:
                continue

            vid = int(parts[1], 16)
            pid = int(parts[2], 16)
            return (vid, pid)
    except:
        pass

    return (0, 0)

def parse_instance(uevent_data):
    try:
        for line in uevent_data.splitlines():
            if not line.startswith('HID_PHYS'):
                continue

            parts = line.split('/')
            if len(parts) != 2:
                continue

            return parts[1]
    except:
        pass

    return ''

def match_device(path, vid, pid, instance):
    uevent_path = pathlib.Path(path, 'device', 'uevent')
    uevent_data = open(uevent_path, 'r').read()

    if (vid, pid) != parse_vid_pid(uevent_data):
        return False

    if instance != parse_instance(uevent_data):
        return False

    return True

def find_device(vid, pid, instance):
    for child in sysfs_base.iterdir():
        if child.is_dir() and match_device(child, vid, pid, instance):
            return pathlib.Path('/', 'dev', child.name)

class HIDException(Exception):
    pass

class Device(object):
    def __init__(self, vid=None, pid=None, serial=None, path=None):
        if vid and pid:
            self.hid_path = find_device(vid, pid, 'input1')
        else:
            raise HIDException('must specify vid/pid')

    def __enter__(self):
        return self

    def __exit__(self):
        pass

    def read(self, size, timeout=None):
        try:
            data = open(self.hid_path, 'rb').read(size)
        except:
            raise HIDException('error reading hid device')
        return data

