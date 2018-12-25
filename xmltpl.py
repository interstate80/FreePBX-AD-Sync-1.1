#! /usr/bin/python
# -*- coding: utf8 -*-

from string import Template

def gen_newCfg(telMAC, telExtention, telDisplayName, telPasswd, telAsteriskHost):
	# считываем шаблон
	TplFile = open('config.tmpl')
	SrcTmpl = Template(TplFile.read())
	ResultList = [telExtention, telDisplayName, telPasswd, telAsteriskHost]
	resultIn = {'telExtention':telExtention, 'telDisplayName':telDisplayName, 'telPasswd':telPasswd, 'telAsteriskHost':telAsteriskHost}
	ResultStr = SrcTmpl.substitute(resultIn)
	# сохраняем конфиг
	CfgFilePath = '/var/lib/tftpboot/SEP' + telMAC + '.cnf.xml'
	try:
		CfgFile = open(CfgFilePath, 'w')
		CfgFile.write(ResultStr)
		CfgFile.close
	except Exception as err:
		print("%s: [ERROR]: gen_newCfg(%s) %s. Путь к файлу: %s" % (log_timestamp(), telExtention, err, CfgFilePath))
	TplFile.close

if __name__ == '__main__':
	print("Not for run standalone!")