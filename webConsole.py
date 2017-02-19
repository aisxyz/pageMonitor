#coding: utf8
from utils.computeMd5 import compute_md5

def web_main():
	from webServer.views import app
	from webServer.usersDb import UsersDb
	db = UsersDb()
	if db.find_user('root') is None:		# Initial password.
		db.add_user('root', compute_md5(b'root123'))
	app.secret_key = 'chEb0a69cf(b19e6f282d501,g8b'
	app.run(debug=True)
	

if __name__ == "__main__":
	web_main()