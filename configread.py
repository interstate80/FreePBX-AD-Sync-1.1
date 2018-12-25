#! /usr/bin/python
# -*- coding: utf8 -*-

import os, ConfigParser

def ConfigSectionMap(section):
    cfg_path = os.getcwd() + '/settings.cfg'
    Config = ConfigParser.ConfigParser()
    try:
        Config.read(cfg_path)
    except IOError as ioerr:
        print("Ошибка чтения конфигурации: %s." % ioerr)
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1