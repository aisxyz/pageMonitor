#coding: utf8
from pymongo import MongoClient

class UsersDb:
	def __init__(self):
		db = MongoClient().file_fingerprint_lib
		self.coll = db.users
		
	def add_user(self, uname, pword):
		self.coll.insert_one({'uname': uname, 'pword': pword})
		
	def delete_user(self, uname):
		self.coll.delete_one({'uname': uname})
		
	def find_user(self, uname):
		for doc in self.coll.find({'uname': uname}, limit=1):
			return doc['pword']
		return None
		
	def update_user_pword(self, uname, pword):
		self.coll.update_one( {'uname': uname},
							  {'$set': {'pword': pword}} )