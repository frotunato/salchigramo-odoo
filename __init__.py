# -*- coding: utf-8 -*-

try:
	import twitter, pyfacebook
except ImportError:
	import sys
	import subprocess
	subprocess.check_call(['pip3', 'install', 'requests', 'requests-oauthlib', 'python-twitter', 'python-facebook-api', '--upgrade'])
from . import controllers
from . import models