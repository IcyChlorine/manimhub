#!/usr/bin/env python
import pretty_errors
import sys
import os
import threading
import time

__shell_version__='0.1'

import manimlib.logger
import manimlib.utils.init_config

__manimhub_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__manimhub_path__)
import manimhub.extract_scene
import manimhub.config
from manimhub.constants import *

class FileModifiedDaemon(threading.Thread):
	'''A thread that checks whether a file has been modified
	by continuously quering the latest mod time of the file
	Upon file modification detected, action_func() will be called
	and the thread will stop.
	Not a genuine daemon though.'''
	def __init__(self, filename, action_func, wait_time=0.4):
		super().__init__()
		self.should_stop=False
		self.filename=filename
		self.action_func=action_func
		self.wait_time=wait_time

	def run(self):
		self.prev_modtime = os.stat(self.filename).st_mtime
		while not self.should_stop:
			modtime = os.stat(self.filename).st_mtime
			if modtime !=self. prev_modtime:
				self.action_func()
				self.should_stop=True	
				break
			time.sleep(self.wait_time)
			
	def stop(self):
		# this is supposed to be called from another thread
		# otherwise deadlock may occur (I'm not sure about this, 
		# but better not do this)
		self.should_stop=True
		self.join()

def query_yn(prompt, default_val=True) -> bool:
	assert(type(default_val)==bool)
	prompt = prompt + '' + ('[y]/n' if default_val else 'y/[n]') + ' '
	opt=''
	while not (opt in ['y','n']): 
		opt = input(prompt)
		if opt=='': opt = 'y' if default_val else 'n'
		if opt in (['y','n']): break

	return opt=='y'


def main():
	print(f"ManimShell \033[32mv{__shell_version__}\033[0m")

	# The pipeline here is:
	# <args> ---> args --+--> filename ---> module ---> scene_classes ---> scene_class
	#                    |                                                      v
	#                    +--> config --------+--------> scene_config ----> [[ scene ]]
	#                                        |
	#                                        +--------> other usages

	args = manimlib.config.parse_cli()
	if args.version and args.file is None:
		return
	if args.log_level:
		manimlib.logger.log.setLevel(args.log_level)
	config = manimhub.config.get_configuration(args)

	first_run = False # TODO: get rid of this stuff
	window = None
	daemon = None
	while True:
		try:
			# module is reloaded everytime so that changes to src can be reflected
			module        = manimhub.extract_scene.get_module(args.file)
			sc_candidates = manimhub.extract_scene.get_scene_classes_from_module(module)
			scene_config  = manimhub.extract_scene.get_scene_config(config)
			scene_class   = manimhub.extract_scene.get_scene_class(sc_candidates, config)
		except Exception:
			# use package `pretty_errors` to print more readable traceback info
			err_type, err_val, err_trb = sys.exc_info()
			pretty_errors.excepthook(err_type, err_val, err_trb)

			print('') # new line
			opt = query_yn('An exception has occurred during importing. Restart or not?')
			if opt: continue
			else: break

		# AHA! Finally we get the Scene instance.
		scene = scene_class(window=window, **scene_config)

		# init daemon thread that checks for changes in src file
		def inject_func():
			scene._src_file_updated=True
		
		daemon = FileModifiedDaemon(os.getcwd()+os.sep+args.file, inject_func)
		daemon.start()
		
		# run the scene and try to handle exceptions
		try:
			ret = scene.run()
		except Exception as e:
			# use package `pretty_errors` to print more readable traceback info
			err_type, err_val, err_trb = sys.exc_info()
			pretty_errors.excepthook(err_type, err_val, err_trb)

			print('') # new line
			opt = query_yn('An exception has occurred. Restart the scene or not?')
			if opt==False: 
				if not daemon is None: daemon.stop()
				break
			else: ret = RESTART_SCENE

		# aftermath
		daemon.stop()
		if ret != RESTART_SCENE: 
			break
		if scene.is_window_closing():
			break

		# reuse window if possible
		# this will save a lot of time on window destroying and creating
		first_run = False
		window = scene.window
		window.clear()

		# known issues: some subtle issue with keyboard quit(q or esc) and embed().
		# not unbearable, but still annoying though.


if __name__ == "__main__":
	main()
