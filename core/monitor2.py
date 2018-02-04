# coding: utf8
import os
import time
import shutil
import filecmp
from subprocess import Popen, PIPE, TimeoutExpired
from configparser import ConfigParser

#from core.dbHandler import DbHandler
#from utils.computeMd5 import compute_md5
from utils.alarmMessage import send_alarm_mail
from utils.log import write_to_log

CONFIG = ConfigParser()

class Monitor:
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
		#self.__db = DbHandler(webname)
		
	def start_monitor(self):
		def clear_child_proc(proc):
			os.system("killall inotifywait")
			proc.kill()
			proc.communicate()
			
		print("\n%s Monitoring %s..." %(time.asctime(), self.website_path))
		config = CONFIG[os.path.basename(self.website_path)]
		while True:
			cmd = ['./core/webWatch.sh', config['monitor_pages'] or self.website_path]
			proc = Popen(cmd, stdout=PIPE, universal_newlines=True)
			if not os.path.exists(self.current_site):
				print("\n%s Stopped monitoring %s." %(time.asctime(), self.website_path))
				clear_child_proc(proc)
				del config
				return
			try:
				out, err = proc.communicate(timeout=15)
				filepath = out.split()[1]
				if not config['monitor_pages']:
					suffix = os.path.splitext(filepath)[1]
					if suffix not in self.page_suffix_set:
						continue
				self._handle_tamper_file(filepath)
			except TimeoutExpired:
				clear_child_proc(proc)
			
	def check_if_send(self, filepath):
		last_tampered_time = self.tampered_page_cache.setdefault(filepath, 0)
		now_time = time.time()
		if now_time - last_tampered_time > self.msg_interval*60:
			self.tampered_page_cache[filepath] = now_time
			return True
		return False
				
	def _handle_tamper_file(self, filepath):
		relative_pos = filepath[self.__website_path_len: ].lstrip('/')
		backup_filepath = os.path.join(self.backup_path, relative_pos)
		if not os.path.exists(backup_filepath):
			content = " 警告：发现可疑文件%s！" %filepath
			# move to isolation area.
			filename = os.path.basename(filepath)
			if not os.path.exists(self.isolation_path):
				os.mkdir(self.isolation_path)
			if self.auto_cure:
				try:
					os.replace(filepath, os.path.join(self.isolation_path, filename))
					content += '已隔离到%s' %self.isolation_path
				except:
					print('Isolate Error: %s is in use!' %filepath)
		else:
			if not os.path.exists(filepath):
				content = ' 警告：文件%s被删除！' %filepath
			else:
				if filecmp.cmp(filepath, backup_filepath):
					return
				content = " 警告：文件%s的内容发生变动！" %filepath
			if self.auto_cure:
				try:
					shutil.copy2(backup_filepath, filepath)
					content += "文件已恢复。"
				except Exception as err_msg:
					#Provisionally skip the file in use.
					content += '文件恢复失败：' + str(err_msg)
		
		if self.check_if_send(filepath):
			try:
				subject = "页面篡改问题"
				send_alarm_mail(self.mail_receivers, subject, content)
			except Exception as err_msg:
				content += '发送告警邮件失败：' + err_msg
		write_to_log(content)