#!/usr/bin/env python
import pretty_errors
import sys
import os

__shell_version__='0.1'

import manimlib.logger
import manimlib.utils.init_config

# change the path below to specify which script to debug
__scene_path__ = 'C:\\StarSky\\VideoCrafting\\MyProjects\\<project folder>\\src'

__manimhub_path__ = 'C:\\StarSky\\Programming\\MyProjects\\'
sys.path.append(__manimhub_path__)
import manimhub.extract_scene
import manimhub.config
from manimhub.constants import *

os.chdir(__scene_path__)
sys.path.append(__scene_path__)

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
	#                    |                                                   v
	#                    +--> config --------+--------> scene_config ----> scene
	#                                        |
	#                                        +--------> other usages

	args = manimlib.config.parse_cli()
	if args.version and args.file is None:
		return
	if args.log_level:
		manimlib.logger.log.setLevel(args.log_level)
	config = manimhub.config.get_configuration(args)

	window = None
	# module is reloaded everytime so that changes to src can be relected
	module = manimhub.extract_scene.get_module(args.file)
	scene_class_candidates = manimhub.extract_scene.get_scene_classes_from_module(module)
	scene_config = manimhub.extract_scene.get_scene_config(config)
	scene_class = manimhub.extract_scene.get_scene_class(scene_class_candidates, config)
	
	# AHA! Finally we get the Scene instance.
	scene = scene_class(window=window, **scene_config)

	# run the scene and try to handle exceptions
	try:
		ret = scene.run()
	except Exception as e:
		# use package `pretty_errors` to print more readable traceback info
		err_type, err_val, err_trb = sys.exc_info()
		pretty_errors.excepthook(err_type, err_val, err_trb)


if __name__ == "__main__":
	try:
		main()
	except Exception:
		err_type, err_val, err_trb = sys.exc_info()
		pretty_errors.excepthook(err_type, err_val, err_trb)
		os.system('pause')