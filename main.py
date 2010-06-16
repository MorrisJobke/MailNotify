#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Morris Jobke 2010 <morris.jobke@googlemail.com>
# 
# MailNotify is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# MailNotify is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

# python imports
import gtk
import logging
import logging.handlers
import sys
import os

# own imports
from includes.indicator import Indicator

LOGFILE = '/tmp/mailnotify-log'
LOGFORMAT = '%(levelname)s\t%(name)-20s\t%(relativeCreated)d\t%(message)s'
PLUGINDIR = './plugins'
CONFIGFILE = '~/.config/mailnotify/settings.conf'

PLUGINDIR = os.path.join(
	sys.path[0],
	PLUGINDIR
)

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

if __name__ == '__main__':
	# initialize log	
	logging.basicConfig(filename=LOGFILE, filemode='w', format=LOGFORMAT)
	log = logging.getLogger('Log')
	level = logging.NOTSET
	level = logging.DEBUG # tmp
	if len(sys.argv) > 1:
		level = LEVELS.get(sys.argv[1], logging.NOTSET)
	log.setLevel(level)
	
	i = Indicator(CONFIGFILE, PLUGINDIR)
	gtk.main()
