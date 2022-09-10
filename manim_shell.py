#!/usr/bin/env python
import pretty_errors
import sys
import os
import threading
import time

__shell_version__='0.1'
import manimlib.config

import manimlib.logger
import manimlib.utils.init_config

__manimhub_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__manimhub_path__)
import manimhub.extract_scene
from manimhub.constants import *

def main():
	print(f"ManimShell \033[32mv{__shell_version__}\033[0m")

	args = manimlib.config.parse_cli()
	if args.version and args.file is None:
		return
	if args.log_level:
		manimlib.logger.log.setLevel(args.log_level)

	if args.config:
		manimlib.utils.init_config.init_customization()
	else:
		first_run = False # TODO: get rid of this stuff
		window = None
		while True:
			config = manimlib.config.get_configuration(args)
			#scenes = manimlib.extract_scene.main(config)
			scene_class_candidates = manimhub.extract_scene.get_scene_classes_from_module(config['module'])
			scene_config = manimhub.extract_scene.get_scene_config(config)
			scene_class = manimhub.extract_scene.get_scene_class(scene_class_candidates, config)
			
			scene = scene_class(window=window, **scene_config)
			global daemon_should_stop 
			daemon_should_stop = False
			def daemon_thread_func():
				global daemon_should_stop
				filename = os.getcwd()+'\\factory.py' #TODO: remove this dependency
				prev_modtime = os.stat(filename).st_mtime

				while not daemon_should_stop:
					modtime = os.stat(filename).st_mtime
					if modtime != prev_modtime:
						scene._src_file_updated=True
						time.sleep(0.4)
						break
			daemon = threading.Thread(target=daemon_thread_func)
			daemon.start()
			
			ret = scene.run()
			daemon_should_stop = True
			daemon.join()
			if ret != RESTART_SCENE: 
				break
			if scene.is_window_closing():
				break

			# reuse window if possible
			# this will save a lot of time on window destroying and creating
			first_run = False
			window = scene.window
			window.clear()
			


if __name__ == "__main__":
	main()
