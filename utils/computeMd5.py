from hashlib import md5

def compute_md5(content):
	return md5(content).hexdigest()