#! /usr/bin/python
# -*- coding: utf-8 -*-

import ldap
import MySQLdb
import re, os
from datetime import datetime
from configread import ConfigSectionMap
from passgen import gen_newpass
from xmltpl import gen_newCfg

def log_timestamp():
	logDT = datetime.now()
	logtimestamp = logDT.strftime("%b %d %H:%M:%S")
	return logtimestamp

#
# Считываем конфигурацию settings.cfg
#
try:
	AD_URL = ConfigSectionMap('ldap')['adurl']
	AD_USER = ConfigSectionMap('ldap')['aduser']
	AD_PASSWORD = ConfigSectionMap('ldap')['adpassword']
	BASE_DN = ConfigSectionMap('ldap')['basedn']
	filterexp = ConfigSectionMap('misc')['extfilt']
	adattr = ConfigSectionMap('misc')['adattr']
	NTP_HOST = ConfigSectionMap('misc')['ntphost']
	DB_HOST = ConfigSectionMap('mysql')['dbhost']
	ASTERISK_HOST = ConfigSectionMap('mysql')['dbhost']
	DB_USER = ConfigSectionMap('mysql')['dbuser']
	DB_PASS = ConfigSectionMap('mysql')['dbpass']
	DB_NAME = ConfigSectionMap('mysql')['dbname']
except Exception as err:
	print("%s: [ERROR]: Ошибка считывания конфигурации: %s." % (log_timestamp(), err))

attrlist = ["displayName","sAMAccountName", "mail", "pager", adattr, "userAccountControl"]

#
# Проверка экстеншена на наличие
#
def check_ext(extnum, extname='', flag=1):
	try:
		DB = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME, charset='utf8')
	except Exception as err:
		print("%s: [ERROR]: check_ext(%s) Ошибка подключения к БД: %s." % (log_timestamp(), extnum, err))
	ch_cursor = DB.cursor()
	# print("%s: [NOTICE]: check_ext(%s) Проверка экстеншена %s на наличие." % (log_timestamp(), extnum, extnum))
	if flag == 1:
		sql_ch = "select extension, name from users where extension='%s';" % extnum
	elif flag == 2:
		sql_ch = "select extension, name from users where name='%s';" % extname
	ch_cursor.execute(sql_ch)
	ch_data = ch_cursor.fetchall()
	if ch_data:
		for ch_rec in ch_data:
			if not ch_rec:
				print("%s: [NOTICE]: check_ext(%s) Экстеншен %s не найден." % (log_timestamp(), extnum, extnum))
				return False
			elif flag == 2 and ch_rec[0] != extnum:
				print("%s: [NOTICE]: check_ext(%s) flag = %s. Возвращаю %s." % (log_timestamp(), extnum, flag, ch_rec[0]))
				return ch_rec[0]
			else:
				return True
	else:
		print("%s: [NOTICE]: check_ext(%s) Ничего не найдено. %s - %s." % (log_timestamp(), extnum, extnum, extname))
		return False
	ch_cursor.close()
	DB.close()

#
# Удаление экстеншена
#
def del_ext(extnum):
	del_sql = list()
	try:
		DB = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME, charset='utf8')
	except Exception as err:
		print("%s: [ERROR]: del_ext(%) Ошибка подключения к БД: %s." % (log_timestamp(), extnum, err))
	del_sql.append("delete from users where extension='%s';" % extnum)
	del_sql.append("delete from sip where id='%s';" % extnum)
	del_sql.append("delete from devices where id='%s';" % extnum)
	for sql in del_sql:
		try:
			del_cursor = DB.cursor()
			del_cursor.execute(sql)
			print("%s: [NOTICE]: del_ext(%s) Удаление экстеншена: %s." % (log_timestamp(), extnum, extnum))
			del_cursor.close()
		except Exception as err:
			print("%s: [ERROR]: del_ext(%s) Ошибка удаления: %s." % (log_timestamp(), extnum, err))
	DB.commit()
	DB.close()
	# удаляем запись из БД астериска
	try:
		res = os.system('/usr/sbin/rasterisk -x "database del CW %s"' % extnum)
		print("%s: [NOTICE]: del_ext(%s) Удаление экстеншена из БД: %s." % (log_timestamp(), extnum, res))
	except Exception as err:
		print("%s: [ERROR]: del_ext(%s) Ошибка удаления %s." % (log_timestamp(), extnum, err))

#
# Создание нового экстеншена
#
def add_ext(cextnum, cextname, flag, upass=''):
	sql_sip_add = ""
	try:
		DB = MySQLdb.connect(DB_HOST, DB_USER, DB_PASS, DB_NAME, charset='utf8')
	except Exception as err:
		print("%s: [ERROR]: add_ext(%s) Ошибка подключения к БД: %s." % (log_timestamp(), cextnum, err))
	add_cursor = DB.cursor()
	if flag == 3:
		sql_sip_add += """insert into sip(id, keyword, data, flags) values ('%(cextnum)s', 'secret', '%(upass)s', 2),"""%{"cextnum":cextnum, "upass":upass}
		sql_sip_add += """('%(cextnum)s', 'dtmfmode', 'rfc2833', 3),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'canreinvite', 'no', 4),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'context', 'from-internal', 5),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'host', 'dynamic', 6),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'defaultuser', '', 7),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'trustrpid', 'yes', 8),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'sendrpid', 'yes', 9),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'type', 'friend', 10),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'sessiontimers', 'accept', 11),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'nat', 'no', 12),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'port', '5060', 13),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'qualify', 'yes', 14),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'qualifyfreq', '60', 15),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'transport', 'udp', 16),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'avpf', 'no', 17),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'force_avp', 'no', 18),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'icesupport', 'no', 19),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'encryption', 'no', 20),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'videosupport', 'inherit', 21),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'namedcallgroup', '', 22),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'namedpickupgroup', '', 23),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'disallow', 'all', 24),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'allow', 'ulaw&alaw', 25),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'dial', 'SIP/%(cextnum)s', 26),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'accountcode', '', 27),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'deny', '0.0.0.0/0.0.0.0', 28),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'permit', '0.0.0.0/0.0.0.0', 29),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'secret_origional', '', 30),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'sipdriver', 'chan_sip', 31),"""%{"cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'account', '%(cextnum)s', 32),"""%{"cextnum":cextnum, "cextnum":cextnum}
		sql_sip_add += """('%(cextnum)s', 'callerid', 'device <%(cextnum)s>', 33);\n"""%{"cextnum":cextnum, "cextnum":cextnum}
		print("%s: [NOTICE]: add_ext(%s) Добавление пира: %s." % (log_timestamp(), cextnum, cextnum))
	elif flag == 1:    
		sql_sip_add += """insert into users(extension, name, voicemail, ringtimer, password, noanswer, recording, outboundcid, sipname) values ('%(cextnum)s', '%(cextname)s', 'novm', 0, '', '', '', '', '');"""%{"cextnum":cextnum, "cextname":cextname}
		print("%s: [NOTICE]: add_ext(%s) Добавление пользователя: %s." % (log_timestamp(), cextnum, cextname))
	elif flag == 2:
		sql_sip_add += """insert into devices(id, tech, dial, devicetype, user, description, emergency_cid) values ('%(cextnum)s', 'sip', 'SIP/%(cextnum)s', 'fixed', '%(cextnum)s', '%(cextname)s', '');"""%{"cextnum":cextnum, "cextnum":cextnum, "cextnum":cextnum, "cextname":cextname}
		print("%s: [NOTICE]: add_ext(%s) Добавление устройства для %s." % (log_timestamp(), cextnum, cextnum))
	try:
		add_cursor.execute(sql_sip_add)
		DB.commit()
		add_cursor.close()
		DB.close()
	except Exception as err:
		print("%s: [ERROR]: add_ext(%s) Ошибка добавления в БД (шаг: %s): %s." % (log_timestamp(), cextnum, flag, err))

#
# Поиск файла конфигурации для телефона
#
def find_cfg(ttel):
	try:
		strToFind = '<name>' + ttel + '</name>'
		print("%s: [NOTICE]: find_cfg(%s) Ищем конфигурацию для %s." % (log_timestamp(), ttel, ttel))
		out = os.popen('grep -R %s /var/lib/tftpboot/' % ttel)
		st = out.readline()
		out.close()
		if st and st.find('Binary') == -1:
			print("%s: [NOTICE]: find_cfg(%s) Конфигурация для %s найдена." % (log_timestamp(), ttel,ttel))
			spatt = '(SEP+[0-9A-Z]+\.cnf.xml)'
			b = re.search(spatt, st)
			ChmC = b.group(0).replace('.cnf.xml', '')
			ChmE = ChmC.replace('SEP', '')
			return ChmE
		else:
			print("%s: [NOTICE]: find_cfg(%s) Конфигурация для %s не обнаружена." % (log_timestamp(), ttel, ttel))
			return False
	except Exception as err:
		print("%s: [ERROR]: find_cfg(%s) %s." % (log_timestamp(), ttel, err))
		
#
# Запись конфигурационного файла для телефона
#
def write_cfg(imac, cfgstr):
	path = '/var/lib/tftpboot/' + imac + '.cfg'
	f = open(path, 'w')
	f.write(cfgstr)
	f.close
	print("%s: Файл конфигурации сохранен: %s" % (log_timestamp(), path))

#
# Добавление записей в БД Астериска
#
def AST_DB_ADD(ext_num):
	hintstr = '/usr/sbin/rasterisk -x "database put AMPUSER %s/hint SIP/%s,CustomPresence:%s"' % (ext_num,ext_num,ext_num)
	cidstr = '/usr/sbin/rasterisk -x "database put AMPUSER %s/cidnum %s"' % (ext_num,ext_num)
	devstr = '/usr/sbin/rasterisk -x "database put AMPUSER %s/device %s"' % (ext_num,ext_num)
	ddstr = '/usr/sbin/rasterisk -x "database put DEVICE %s/dial SIP/%s"' % (ext_num,ext_num)
	cwstr = '/usr/sbin/rasterisk -x "database put CW %s ENABLED"' % ext_num
	print("%s: [NOTICE]: AST_DB_ADD(%s) Добавление записей для %s в БД Астериска." % (log_timestamp(), ext_num, ext_num))
	try:
		os.system(hintstr)
		os.system(cidstr)
		os.system(devstr)
		os.system(ddstr)
		os.system(cwstr)
	except Exception as err:
		print("%s: [ERROR] AST_DB_ADD(%s) Ошибка добавления %s в БД: %s." % (log_timestamp(), ext_num, ext_num, err))

#
# Тело
#
try:
	AD = ldap.initialize(AD_URL)
	AD.simple_bind_s(AD_USER, AD_PASSWORD)
	# Список атрибутов объекта
	results = AD.search_s(BASE_DN, ldap.SCOPE_SUBTREE, filterexp, attrlist)
	for result in results:
		if 'userAccountControl' in result[1].keys():
			UAC = result[1]['userAccountControl'][0]
		if UAC == '66050':
			continue
		tel = result[1][adattr][0]
		disname = result[1]['displayName'][0]
		modext = check_ext(tel, disname, flag=2)
		modmac = find_cfg(tel)
		if 'pager' in result[1].keys():
			newmac = result[1]['pager'][0].upper()
		else:
			newmac = ''
		if  modmac and len(newmac) == 12 and modmac != newmac:
			print("%s: [NOTICE]: Изменился мак-адрес у %s... %s->%s" % (log_timestamp(), disname, modmac, newmac))
			try:
				cmdstr = "mv -f /var/lib/tftpboot/SEP%s.cnf.xml /var/lib/tftpboot/SEP%s.cnf.xml" % (modmac, newmac)
				print("%s: [NOTICE]: %s" % (log_timestamp(), cmdstr))
				out = os.popen(cmdstr)
				lnout = out.readline()
				out.close()
			except Exception as err:
				print("%s: [ERROR]: Ошибка перемещения файла конфигурации: %s." % (log_timestamp(), err))
		elif check_ext(tel):
			continue
		# MAC-адрес не задан
		elif not 'pager' in result[1].keys():
			mac_addr = ''
			print("%s: [NOTICE]: МАС-адрес не задан: %s" % (log_timestamp(), disname))
			continue
		# ошибка в MAC-адресе
		elif len(result[1]['pager'][0]) != 12:
			print("%s: [ERROR]: Ошибка в MAC-адресе у %s." % (log_timestamp(), disname))
			print("%s: [ERROR]: В %s количество символов - %s. Должно быть 12." % (log_timestamp(), result[1]['pager'][0], len(result[1]['pager'][0])))
			continue
		elif modext > 0:
			newpass = gen_newpass(11)
			del_ext(modext)
			mac_addr = result[1]['pager'][0].upper()
			add_ext(tel, disname, 1)
			add_ext(tel, disname, 2)
			add_ext(tel, disname, 3, newpass)
			# Генерируем конфиг для телефона
			gen_newCfg(mac_addr, tel, disname, newpass, ASTERISK_HOST)
			# добавляем запись CallWaiting в БД астериска
			AST_DB_ADD(tel)
		else:
			mac_addr = result[1]['pager'][0].upper()
			print("%s: [NOTICE]: Нет экстеншена: %s -> %s. Добавляем..." % (log_timestamp(), disname, tel))
			# Генерируем новый 11-символьный пароль
			userpass = gen_newpass(11)
			add_ext(tel, disname, 1)
			add_ext(tel, disname, 2)
			add_ext(tel, disname, 3, userpass)
			# Генерируем конфиг для телефона
			gen_newCfg(mac_addr, tel, disname, userpass, ASTERISK_HOST)
			# добавляем запись CallWaiting в БД астериска
			AST_DB_ADD(tel)
	AD.unbind_s()
except Exception as err:
		print("%s: [ERROR]: Main Fault! Критическая ошибка: %s." % (log_timestamp(), err))