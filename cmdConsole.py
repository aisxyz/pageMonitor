import os.path

from core.monitor import Monitor

def cmd_main( website_path, backup_path, mail_receivers, msg_interval=30,
			  auto_cure=True, page_suffix_set=None ):
	website_name = os.path.split(website_path)[1]
	history_file = "history/%s" %website_name
	if not os.path.exists(history_file):
		from core.fingerprintBuilder import build_fingerprint_lib
		build_fingerprint_lib(website_path, website_name)
		open(history_file, 'wb').close()
	web_monitor = Monitor( website_path, website_name, backup_path, mail_receivers,
						   page_suffix_set, msg_interval, auto_cure )
	web_monitor.start_monitor()
	
if __name__ == "__main__":
	from config import WEBSITE_PATH, WEB_BACKUP_PATH, MAIL_RECEIVERS
	cmd_main(WEBSITE_PATH, WEB_BACKUP_PATH, MAIL_RECEIVERS)