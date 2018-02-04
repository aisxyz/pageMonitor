# coding: utf8
import os
import time
import shutil
from configparser import ConfigParser

from core.dbHandler import DbHandler
from utils.computeMd5 import compute_md5
from utils.alarmMessage import send_alarm_mail
from utils.log import write_to_log

CONFIG = ConfigParser()

class Monitor:
	_NORMAL = 0		# Match fingerprint in db.
	_EXTRA = 1		# Should't exists such file.
	_TAMPERED = 2	        # File has been tampered.
	def __init__( self, website_path, backup_path, mail_receivers,
				  page_suffix_set=None, msg_interval=30, auto_cure=True ):
		self.website_path = website_path
		self.backup_path = backup_path
		self.__website_path_len = len(self.website_path)
		self.mail_receivers = mail_receivers
		self.msg_interval = msg_interval
		self.auto_cure = auto_cure
		self.tampered_page_cache = {}
		webname = os.path.basename(website_path)
		self.isolation_path = 'snapshoot/isolationArea/%s' %webname
		self.current_site = './snapshoot/monitoring/%s' %webname
		open(self.current_site, 'wb').close()
		if page_suffix_set is None:
			self.page_suffix_set = { '.html', '.htm', '.asp', '.jpg',
					'.png', '.gif', '.php', '.jsp' }
		else:
			self.page_suffix_set = {suffix.lower() for suffix in page_suffix_set}
		self.__db = DbHandler(webname)
		
	def get_tamper_num(self, filepath):
		mtime = os.path.getmtime(filepath)
		filename = filepath.replace('\\', '/')
		real_mtime, real_md5 = self.__db.find_fingerprint(filename)
		if real_mtime is None:
			return self._EXTRA
		if mtime != real_mtime:
			with open(filepath, 'rb') as fd:
				md5_value = compute_md5(fd.read())
			if md5_value == real_md5:
				return self._NORMAL
			relative_pos = filepath[self.__website_path_len: ].lstrip('/\\')
			backup_file = os.path.join(self.backup_path, relative_pos)
			with open(backup_file, 'rb') as fd:
				backup_md5 = compute_md5(fd.read())
			if md5_value != backup_md5:
				return self._TAMPERED
			self.__db.update_fingerprint( filepath, [mtime, md5_value] )
		return self._NORMAL
		
	def start_monitor(self):
		print("\n%s Monitoring %s..." %(time.asctime(), self.website_path))
		config = CONFIG[os.path.basename(self.website_path)]
		while True:
			if not os.path.exists(self.current_site):
				print("\n%s %s quit." %(time.asctime(), self.website_path))
				return
			pages = config['monitor_pages'].split()
			if pages:
				self._monitor_part_pages(pages)
			else:
				self._monitor_all_pages()
				
	def check_if_send(self, filepath):
		last_tampered_time = self.tampered_page_cache.setdefault(filepath, 0)
		now_time = time.time()
		if now_time - last_tampered_time > self.msg_interval*60:
			self.tampered_page_cache[filepath] = now_time
			return True
		return False
			
	def _monitor_part_pages(self, pages):
		for f in pages:
			filepath = os.path.normpath( self.website_path + f )
			self._handle_tamper_file(filepath)
	
	def _monitor_all_pages(self):
		for dirpath, dirnames, files in os.walk(self.website_path):
			for f in files:
				file_suffix = os.path.splitext(f)[1].lower()
				if file_suffix not in self.page_suffix_set:
					continue
				filepath = os.path.join(dirpath, f)
				self._handle_tamper_file(filepath)
				
	def _handle_tamper_file(self, filepath):
		relative_pos = filepath[self.__website_path_len: ].lstrip('/\\')
		backup_filepath = os.path.join(self.backup_path, relative_pos)
		tamper_num = self.get_tamper_num(filepath)
		if tamper_num != self._NORMAL:
			if tamper_num == self._EXTRA:
				content = " 警告：发现可疑文件%s！" %filepath
				# move to isolation area.
				filename = os.path.basename(filepath)
				if not os.path.exists(self.isolation_path):
					os.mkdir(self.isolation_path)
				try:
					os.replace(filepath, os.path.join(self.isolation_path, filename))
					content += '已隔离到%s' %self.isolation_path
				except:
					print('Isolate Error: %s is in use!' %filepath)
			else:
				content = " 警告：文件%s的内容发生变动！" %filepath
				if self.auto_cure:
					try:
						shutil.copy2(backup_filepath, filepath)
						content += "文件已恢复。"
					except Exception as err_msg:
						#Provisionally skip the file in use.
						content += '文件恢复失败：' + err_msg
			if self.check_if_send(filepath):
				try:
					subject = "页面篡改问题"
					send_alarm_mail(self.mail_receivers, subject, content)
				except Exception as err_msg:
					content += '发送告警邮件失败：' + err_msg
			write_to_log(content)
