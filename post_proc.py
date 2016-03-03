import subprocess
import logging

class PostProcessor:

	def __init__(self, script):
		self.script = script
		self.in_file = ''
		self.out_file = ''
		
	def execute_script(self):
		# check params are set
		if (self.in_file == '') or (self.out_file == ''):
			logging.warn('Params for the post processing script are missing - Skipping..')
			return False
		# execute the script
		subprocess.call([self.script, self.in_file, self.out_file])
		# handle error
		return
	
	def set_infile(self, filename):
		self.in_file = filename
	
	def set_outfile(self, filename):
		self.out_file = filename
		