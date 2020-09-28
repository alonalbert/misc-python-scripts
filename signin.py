#!/usr/bin/python3

import getpass
import sys

import pexpect

def print_str(value):
    print(value.decode('utf-8'))

if __name__ == '__main__':
    password = getpass.getpass('Password: ')

    gcert = pexpect.spawn('gcert -reuse_sso_cookie=true')
    i = gcert.expect([pexpect.EOF, r'SSO password for .*: '])

    if i == 0:
        print_str(gcert.before)
    else:
        gcert.sendline(password)
        gcert.expect(r'Please touch your security key.')
        print_str(gcert.after)
        gcert.expect(pexpect.EOF)
        print_str(gcert.before)
        
    prodaccess = pexpect.spawn('ssh -t work gcert --reuse_sso_cookie=true')
    i = prodaccess.expect([pexpect.EOF, r'SSO password for .*: '])
    if i == 0:
        print_str(prodaccess.before)
    else:
        prodaccess.sendline(password)
        prodaccess.expect(r'Please touch your security key.')
        print_str(prodaccess.after)
        prodaccess.expect(pexpect.EOF)
        print_str(prodaccess.before)




