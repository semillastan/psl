import os
import sys
import site

sys.path.insert(0, '/srv/www/lotto/lotto-jackpot/jackpot')

site.addsitedir('/srv/www/lotto/lib/python2.7/site-packages')

sys.path.append('/srv/www/lotto')
sys.path.append('/srv/www/lotto/lotto-jackpot')
sys.path.append('/srv/www/lotto/lotto-jackpot/jackpot')

activate_this = '/srv/www/lotto/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from psl import app as application
