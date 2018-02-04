# coding: utf8
from flask import Flask, render_template, url_for, redirect, request, flash, session
from threading import Thread
import os.path

from cmdConsole import cmd_main, CONFIG
from utils.computeMd5 import compute_md5
from utils.treeFolder import treeview_folder
from webServer.usersDb import UsersDb

SITE = None

app = Flask(__name__)

@app.route('/')
@app.route('/index/')
@app.route('/login/')
def login():
	return render_template('login.html')
	
@app.route('/auth/', methods=['POST'])
def user_auth():
	uname = request.form['uname']
	pword = request.form['pword']
	pword = compute_md5(pword.encode())
	real_pword = UsersDb().find_user(uname)
	if real_pword == pword:
		session['uname'] = uname
		return redirect(url_for('monitor'))
	else:
		flash("用户名或密码错误！")
	return redirect(url_for('login'))

def make_tree_code(tree_folders):
	code = ''
	pages = CONFIG[SITE]['monitor_pages'].split()
	suffixes = CONFIG[SITE]['monitor_suffix'].split()
	checkbox = "%s &nbsp;<input type='checkbox' name='%s' {0}>"
	def recursive_tree(tree, indent):
		nonlocal code
		s = '\t'*indent
		for f in tree:
			fname = checkbox %(os.path.basename(f), f)
			if tree[f] == 0:
				suffix = os.path.splitext(f)[1].lower()
				if not pages and suffix in suffixes or f in pages:
					fname = fname.format('checked')
				code += '%s<li><span class="file">%s</span></li>\n' %(s, fname)
			else:
				fname = fname.format("onclick='choose(this)'")
				code += ('%s<li class="closed">\n'
						 '%s<span class="folder">%s</span>\n'
						 '%s<ul>\n' %(s, '\t'+s, fname, '\t'+s) )
				recursive_tree(tree[f], indent+2)
				code += '%s</ul>\n%s</li>\n' %('\t'+s, s)
	recursive_tree(tree_folders, 6)	# just better to display the html code.
	return code

@app.route('/monitor/')
def monitor():
	if session.get('uname', None) is None:
		return redirect(url_for('login'))
	folders = treeview_folder( CONFIG[SITE]['website_path'] ) if SITE else {}
	code = make_tree_code(folders) if SITE else ''
	return render_template('monitor.html', site=SITE, folders=code)

@app.route('/logout/')
def logout():
	session.pop('uname', None)
	return redirect(url_for('login'))
	
@app.route('/password/', methods=['POST'])
def modifyPword():
	new_pword = request.form['newPword']
	new_pword = compute_md5(new_pword.encode())
	uname = session['uname']
	UsersDb().update_user_pword(uname, new_pword)
	return redirect(url_for('monitor'))
	
@app.route('/config/')
def monitorConfig():
	global SITE
	if session.get('uname', None) is None:
		return redirect(url_for('login'))
	website_path = request.args.get('sitePath')
	SITE = os.path.basename(website_path)
	CONFIG[SITE] = {}
	section = CONFIG[SITE]
	section['website_path'] = website_path
	section['web_backup_path'] = request.args.get('backupPath')
	suffix_str = request.args.get('suffixType')
	if suffix_str:
		section['monitor_suffix'] = suffix_str.lower()
	section['mail_receivers'] = request.args.get('receivers')
	section['email_frequency'] = request.args.get('msgInterval') or '30'
	section['auto_recover'] = request.args.get('autoRecover', 'yes')
	Thread( target=cmd_main, args=(SITE,) ).start()
	return redirect(url_for('monitor'))
	
@app.route('/monitorPage/')
def monitorPage():
	if session.get('uname', None) is None:
		return redirect(url_for('login'))
	if request.args.get('exit'):
		global SITE
		os.remove(r'./snapshoot/monitoring/%s' %SITE)
		#del CONFIG[SITE]
		SITE = None
	else:
		pages = set(request.args.keys())
		pages.discard(SITE)
		site_path = CONFIG[SITE]['website_path']
		pages = set([site_path+f for f in pages])
		for f in tuple(pages):
			if os.path.isdir(site_path+f):
				pages.remove(f)
		CONFIG[SITE]['monitor_pages'] = ' '.join(pages)
	return redirect(url_for('monitor'))