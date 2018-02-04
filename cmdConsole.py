# -*- coding: utf-8 -*-
import os.path
import shutil
import atexit

from core.monitor import Monitor, CONFIG
from core.fingerprintBuilder import build_fingerprint_lib

def init_path():
	path = os.path.dirname(__file__)
	os.chdir(path)
	
init_path()
CONFIG.read('config.ini')

@atexit.register
def empty_monitoring_sites():
	path = './snapshoot/monitoring'
	shutil.rmtree(path)
	os.mkdir(path)

def cmd_main(siteName):
	site_config = CONFIG[siteName]
	website_path = site_config['website_path']
	backup_path = site_config['web_backup_path']
	mail_receivers = site_config['mail_receivers'].split()
	monitor_pages = site_config['monitor_pages']
	page_suffix = site_config['monitor_suffix'].split()
	interval = site_config.getint('email_frequency')
	auto_cure = site_config.getboolean('auto_cure')
	
	history_file = "./snapshoot/history/%s" %siteName
	if not os.path.exists(history_file):
		build_fingerprint_lib(website_path, siteName)
		open(history_file, 'wb').close()
	web_monitor = Monitor( website_path, backup_path, mail_receivers,
						   page_suffix, interval, auto_cure )
	web_monitor.start_monitor()
	
if __name__ == "__main__":
	siteName = 'testWebsite'
	cmd_main(siteName)
