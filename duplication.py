#! /usr/bin/python
# -*- coding: utf-8 -*-

import ldap, re, os, collections
from configread import ConfigSectionMap

# Считываем конфигурацию
# LDAP section
AD_URL = ConfigSectionMap('ldap')['adurl']
AD_USER = ConfigSectionMap('ldap')['aduser']
AD_PASSWORD = ConfigSectionMap('ldap')['adpassword']
BASE_DN = ConfigSectionMap('ldap')['basedn']
filterexp = ConfigSectionMap('misc')['extfilt']
adattr = ConfigSectionMap('misc')['adattr']
attrlist = ["displayName", "pager", adattr, "userAccountControl"]
scope = ldap.SCOPE_SUBTREE

print(attrlist)
AD = ldap.initialize(AD_URL)
AD.simple_bind_s(AD_USER, AD_PASSWORD)
results = AD.search_s(BASE_DN, scope, filterexp, attrlist)
for result in results:
    if 'userAccountControl' in result[1].keys():
        UAC = result[1]['userAccountControl'][0]
    if UAC == '66048' or UAC == '512':
        print("Учетная запись: %s включена." % result[1]['displayName'][0])

AD.unbind_s()