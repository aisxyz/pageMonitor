# coding: utf-8
import os.path

def treeview_folder(site):
	siteName = os.path.basename(site)
	d = {siteName: {}}
	root_len = len(site) + 1	# strip '/' at the end of 'site'.
	for dirpath, dirnames, files in os.walk(site):
		relapath = dirpath[root_len:].replace('\\', '/')
		keys = relapath.split('/') if relapath else []
		temp_d = d[siteName]
		root = ''
		for k in keys:
			root = root+'/'+k if root else '/'+k
			temp_d = temp_d[root]
		relapath = '/' + relapath
		if relapath != '/':
			relapath += '/'
		for f in files:
			temp_d[ relapath+f ] = 0
		for folder in dirnames:
			temp_d[ relapath+folder ] = {}
	return d