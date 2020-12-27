#!/usr/bin/env python3
"""
A simple test server that returns a random number when sent the text "temp" via Bluetooth serial.
"""
import configparser
import bluetooth
import dbus
import os
# import qrcode

from cryptography.fernet import Fernet

name = 'Test'
uuid = '94f39d29-7d6d-437d-973b-fba39e49d4ee'


class Bpv:
    CONFIG_SECTION = 'main'
    CONFIG_FILE = os.path.expanduser('~/.bpv')

    def __init__(self):
        self.bus = dbus.SystemBus()
        self.manager = dbus.Interface(
            self.bus.get_object('org.bluez', "/"),
            "org.freedesktop.DBus.ObjectManager")
        self.config = configparser.ConfigParser()
        self.config.read(self.CONFIG_FILE)

        self.key = self.get_config('key')
        if self.key is None:
            self.key = Fernet.generate_key()
            self.set_config('key', self.key)

    def find_devices(self):
        devices = []
        objects = self.manager.GetManagedObjects()
        for path in objects.keys():
            interfaces = objects[path]
            device = interfaces.get('org.bluez.Device1')
            if device is not None:
                devices.append({"name": str(device['Name']), "address": str(device["Address"])})

        return devices

    def get_self(self):
        objects = self.manager.GetManagedObjects()
        for path in objects.keys():
            interfaces = objects[path]
            adapter = interfaces.get('org.bluez.Adapter1')
            if adapter is not None:
                return {'name': str(adapter['Name']), 'address': str(adapter['Address'])}

        return None

    def find_service(self, address=None):
        if address is None:
            for device in self.find_devices():
                services = bluetooth.find_service(uuid=uuid, address=device['address'])
                if len(services) > 0:
                    return services[0]
        else:
            services = bluetooth.find_service(uuid=uuid, address=address)
            if len(services) > 0:
                return services[0]
        return None

    def get_config(self, key):
        if self.config.has_section(self.CONFIG_SECTION):
            if self.config.has_option(self.CONFIG_SECTION, key):
                return self.config.get(self.CONFIG_SECTION, key)
        return None

    def set_config(self, key, value):
        if not self.config.has_section(self.CONFIG_SECTION):
            self.config.add_section(self.CONFIG_SECTION)
        self.config.set(self.CONFIG_SECTION, key, value)
        with open(self.CONFIG_FILE, 'wb') as f:
            self.config.write(f)

    def run(self):
        self.get_self()
        address = self.get_config('device_address')
        service = self.find_service(address)
        if address is None:
            address = service['host']
            self.set_config('device_address', address)

        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((address, (service['port'])))
        sock.send("Corp")
        response = sock.recv(1024)
        sock.close()

        # os.system('xte "str %s" "usleep 100000" "key Return"' % response)
        print(response.decode('utf-8'))

if __name__ == '__main__':
    Bpv().run()

    #
    # service = services[0]
    # port = service['port']
    #
    # sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    # sock.connect((addr, port))
    # sock.send("Hello!")
    # response = sock.recv(1024)
    # sock.close()
    #
    # print(response)
    # # os.system('xte "str %s" "usleep 100000" "key Return"' % response)
