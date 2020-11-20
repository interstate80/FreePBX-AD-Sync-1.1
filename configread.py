#! /usr/bin/python
# -*- coding: utf8 -*-

import os, configparser
from users_adv import log_timestamp

def ConfigSectionMap(section):
    cfg_path = os.getcwd() + '/settings.cfg'
    Config = configparser.ConfigParser()
    try:
        Config.read(cfg_path)
    except IOError as ioerr:
        print("%s: [ERROR] ConfigSectionMap(): Ошибка чтения конфигурации: %s." % (log_timestamp(), ioerr))
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("%s: [DEBUG] Пропускаем: %s" % (log_timestamp(), option))
        except:
            print("%s [ERROR] Считывание параметра %s!" % (log_timestamp(), option))
            dict1[option] = None
    return dict1
	
if __name__ == '__main__':
    print("Not for run standalone.")