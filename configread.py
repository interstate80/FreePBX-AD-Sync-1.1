#! /usr/bin/python
# -*- coding: utf8 -*-

import os, ConfigParser

def ConfigSectionMap(section):
    cfg_path = os.getcwd() + '/settings.cfg'
    Config = ConfigParser.ConfigParser()
    try:
        Config.read(cfg_path)
    except IOError as ioerr:
        print("%s: [ERROR] ConfigSectionMap(): Ошибка чтения конфигурации: %s." % (log_datetime(), ioerr))
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("%s: [DEBUG] Пропускаем: %s" % (log_datetime(), option))
        except:
            print("%s [ERROR] Считывание параметра %s!" % (log_datetime(), option))
            dict1[option] = None
    return dict1
	
if __name__ == '__main__':
    print("Not for run standalone.")