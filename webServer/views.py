# coding: utf8
from flask import Flask, render_template, url_for, redirect, request, flash, session
from threading import Thread

from cmdConsole import cmd_main
from utils.computeMd5 import compute_md5
from webServer.usersDb import UsersDb

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
	elif real_pword is None:
		flash("该用户不存在！")
	elif real_pword != pword:
		flash("用户名或密码错误！")
	return redirect(url_for('login'))

@app.route('/monitor/')
def monitor():
	if session.get('uname', None) is None:
		return redirect(url_for('login'))
	return render_template('monitor.html')

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
	if session.get('uname', None) is None:
		return redirect(url_for('login'))
	website_path = request.args.get('sitePath')
	backup_path = request.args.get('backupPath')
	mail_receivers = request.args.get('receivers').split()
	msg_interval = request.args.get('msgInterval') or 30
	auto_recover = request.args.get('autoRecover', False)
	if website_path and backup_path and mail_receivers:
		Thread( target=cmd_main, args=( website_path, backup_path, mail_receivers,
				int(msg_interval), auto_recover) ).start()
	return redirect(url_for('monitor'))