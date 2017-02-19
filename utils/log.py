from time import strftime
'''
import logging

logging.basicConfig( filename="error.log", 
					 format='%(asctime)s %(message)s', 
					 datefmt='%m/%d/%Y %H:%M',
					 level=logging.WARNING )

def write_to_log(content):
	logging.warning(content)
'''
def write_to_log(content):
	with open('error.log', 'a') as fd:
		fd.write(strftime('%Y/%m/%d %H:%M:%S')+content+'\n')