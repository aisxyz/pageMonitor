# coding: utf8
import os
import time
import shutil

from core.dbHandler import DbHandler
from utils.computeMd5 import compute_md5
from utils.alarmMessage import send_alarm_mail
from utils.log import write_to_log

class Monitor:
	_NORMAL = 0		# Match fingerprint in db.
	_NOFILE = 1		# No such file in db.
	_TAMPERED = 2	# File has been tampered.
	def __init__( self, website_path, website_name, backup_path, mail_receivers,
				  page_suffix_set=None, msg_interval=30, auto_cure=True ):
		self.website_path = website_path
		self.backup_path = backup_path
		self.mail_receivers = mail_receivers
		self.msg_interval = msg_interval
		self.auto_cure = auto_cure
		if page_suffix_set is None:
			self.page_suffix_set = { '.html', '.htm', '.asp', '.jpg', '.png',
									 '.gif', '.xml', '.php', '.jsp', '.js' }
		else:
			self.page_suffix_set = {suffix.lower() for suffix in page_suffix_set}
		self.db = DbHandler(website_name)
		
	def get_tamper_num(self, filepath):
		mtime = os.path.getmtime(filepath)
		real_mtime, real_md5 = self.db.find_fingerprint(filepath)
		if real_mtime is None:
			return self._NOFILE
		if mtime != real_mtime:
			with open(filepath, 'rb') as fd:
				md5_value = compute_md5(fd.read())
			if md5_value != real_md5:
				return self._TAMPERED
			self.db.update_fingerprint( filepath, [mtime, real_md5] )
		return self._NORMAL
		
	def start_monitor(self):
		tampered_page_cache = {}
		
		def check_if_send(filepath):
			last_tampered_time = tampered_page_cache.setdefault(filepath, 0)
			now_time = time.time()
			if now_time - last_tampered_time > self.msg_interval*60:
				tampered_page_cache[filepath] = now_time
				return True
			return False

		subject = "页面篡改问题"
		web_path_len = len(self.website_path)
		print("\n%s Monitoring %s..." %(time.asctime(), self.website_path))
		while True:
			for dirpath, dirnames, files in os.walk(self.website_path):
				for f in files:
					filepath = os.path.join(dirpath, f)
					file_suffix = os.path.splitext(filepath)[1].lower()
					if file_suffix not in self.page_suffix_set:
						continue
					tamper_num = self.get_tamper_num(filepath)
					if tamper_num != self._NORMAL:
						if tamper_num == self._NOFILE:
							content = "警告：多了可疑文件%s！" %filepath
							if self.auto_cure:
								try:
									os.remove(filepath)
									content += "已删除。"
								except Exception as err_msg:
									write_to_log(err_msg)	# Skip the file in use.
						else:
							content = "警告：文件%s的内容发生变动！" %filepath
							if self.auto_cure:
								relative_pos = filepath[web_path_len:].lstrip('/\\')
								src_file = os.path.join(self.backup_path, relative_pos)
								try:
									shutil.copy2(src_file, filepath)
									content += "文件已恢复。"
								except Exception as err_msg:
									write_to_log(err_msg)	# File is in use or no backup.
						write_to_log(content)
						if check_if_send(filepath):
							try:
								send_alarm_mail(self.mail_receivers, subject, content)
							except Exception as err_msg:
								write_to_log(err_msg)