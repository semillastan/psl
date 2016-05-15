import os
import sys
import site

VENV_PATH = "/srv/www/psl"
REPO_PATH = "{0}/provincial-state-lottery".format(VENV_PATH)
APP_PATH = "{0}/psl".format(REPO_PATH)

sys.path.insert(0, VENV_PATH)

site.addsitedir('{0}/lib/python2.7/site-packages'.format(VENV_PATH))

sys.path.append(VENV_PATH)
sys.path.append(REPO_PATH)
sys.path.append(APP_PATH)

activate_this = '{0}/bin/activate_this.py'.format(VENV_PATH)
execfile(activate_this, dict(__file__=activate_this))

from psl import app as application
