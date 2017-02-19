from pymongo import MongoClient

class DbHandler:
	def __init__(self, collection_name):
		db = MongoClient().file_fingerprint_lib
		# Can't do like: self.collection = db.collection_name
		exec_code = "self.collection = db.%s" %collection_name
		exec(exec_code)
		
	def insert_to_collection(self, documents):
		self.collection.insert_many(documents)
		
	def find_fingerprint(self, filepath):
		for doc in self.collection.find({'name': filepath}, limit=1):
			return doc['attr']
		return [None, None]
			
	def update_fingerprint(self, filepath, new_attr):
		self.collection.update_one( {'name': filepath}, 
									{'$set': {'attr': new_attr}} )
									
if __name__ == "__main__":
	dh = DbHandler('web_test')
	ds = [ {'name':'f1', 'attr': [123, 'abcd']}, 
			{'name':'f2', 'attr': [234, 'abcd']}]
	dh.insert_to_collection(ds)
	print(dh.find_fingerprint('f1'))
	dh.update_fingerprint('f1', [111, 'xyz'])
	print(dh.find_fingerprint('f1'))