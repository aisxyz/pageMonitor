import os
from time import asctime

from core.dbHandler import DbHandler
from utils.computeMd5 import compute_md5
#from config import WEBSITE_PATH, WEBSITE_NAME

def build_fingerprint_lib(website_path, website_name):
	save_data_to_db = DbHandler(website_name).insert_to_collection
	print("%s Creating fingerprint database ..." %asctime())
	for dirpath, dirnames, filenames in os.walk(website_path):
		documents = []
		for f in filenames:
			filepath = os.path.join(dirpath, f)
			mtime = os.path.getmtime(filepath)
			with open(filepath, 'rb') as fd:
				md5_value = compute_md5(fd.read())
			doc = {'name': filepath, 'attr': [mtime, md5_value]}
			documents.append(doc)
		if documents:		# Each may be a director under the current director.
			save_data_to_db(documents)
	print("%s Successful create fingerprint database." %asctime())