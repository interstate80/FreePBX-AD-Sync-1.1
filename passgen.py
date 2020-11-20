#! /usr/bin/python
# -*- coding: utf-8 -*-

import os, random, string

def gen_newpass(pleng):
    length = pleng
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))
    newpass = ''.join(random.choice(chars) for i in range(length))
    return newpass

if __name__ == '__main__':
    print(gen_newpass(11))