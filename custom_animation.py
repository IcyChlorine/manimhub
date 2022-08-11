from manimlib import *

from manimhub.constants import *
from manimhub.custom_rate_func import *

# alias
Create = ShowCreation
class Popup(GrowFromCenter):
	CONFIG = {
		'rate_func': braking_end,
		'clip_alpha': False
	}