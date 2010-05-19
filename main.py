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
import os
import gtk
import time
import logging
import logging.handlers
import sys
# own imports
from indicator import Indicator

PLUGINDIR = './plugins'
LOGFILE = './log'
LOGFORMAT = '%(levelname)s\t%(name)s\t%(relativeCreated)d\t%(message)s'

import sys

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


if __name__ == '__main__':	
	logging.basicConfig(filename=LOGFILE, filemode='w', format=LOGFORMAT)
	log = logging.getLogger('Log')
	level = logging.NOTSET
	if len(sys.argv) > 1:
		level_name = sys.argv[1]
		level = LEVELS.get(level_name, logging.NOTSET)
	log.setLevel(level)

	log.info('loading config ...')
	config = {}
	config['refreshTimeout'] = 5
	config['plugins'] = {
		'Gmail-1': {'plugin': 'Gmail', 'username': 'huhu', 'password': 'dsafsd', 'labels': 'inbox,friends', 'prefix': 'Gmail - ', 'enablePrefix': True},
		'Gmail2-1': {'plugin': 'Gmail2', 'username': 'huhu2', 'password': 'moin', 'labels': 'inbox', 'prefix': 'Gmail2 - ', 'enablePrefix': True},
#		'Webde-1': {'plugin': 'Webde', 'username': 'huhu2', 'password': 'moin', 'labels': 'inbox', 'prefix': 'Webde - ', 'enablePrefix': True}
	}
	# needed plugins
	p = []
	for i in config['plugins']:
		q = config['plugins'][i]
		if not q['plugin'] in p:
			p.append(q['plugin'])			
		
	log.info('importing plugins ...')
	plugins = []
	g = globals()
	l = locals()
	gs = []
	ls = []
	ns = []
	
	notFoundPlugins = []
	for n in p:
		if os.path.isfile(os.path.join(PLUGINDIR,n+'.py')):
			log.info('plugin %s ... \tfound'%n)
			plugins.append('.'.join(['plugins',n]))
			gs.append(g)
			ls.append(l)
			ns.append('Notifier')
		else:
			log.warning('plugin %s ... \tnot found'%n)
			notFoundPlugins.append(n)
			
		
	modules = map(__import__, plugins, gs, ls, ns)

	log.info('starting plugins ...')
	loadedPlugins = {}
	for m in modules:
		loadedPlugins[m.__name__[8:]] = m
	
	notifier = {}	
	for i in config['plugins']:
		p = config['plugins'][i]
		if not p['plugin'] in notFoundPlugins:
			notifier[i] = loadedPlugins[p['plugin']].Notifier(p)
	
	i = Indicator(config, loadedPlugins, notifier)
	
	gtk.main()
