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
import indicate
import subprocess
import os
import gobject
import urllib2

import logging
log = logging.getLogger('Log.Indicator')

class Indicator():
	def __init__(self, config, loadedPlugins, notifier):
		self.desktopFile 	= os.path.join(os.getcwd(),'mailnotify.desktop')
		self.server	= indicate.indicate_server_ref_default()
		self.server.set_type('message.mail')
		self.server.set_desktop_file(self.desktopFile)
		self.server.connect('server-display', self.click)
		self.server.show()

		self.notifier = notifier
		self.config = config
		self.loadedPlugins = loadedPlugins
		
		self.indicators = {}
		
		self.refresh()
		
	def click(self, server, something):
		log.info('TODO - open settings')
		
	def refresh(self):
		for n in self.notifier:
			try:
				self.notifier[n].check()
			except urllib2.HTTPError, e:
				if e.code == 401:
					log.error('ERROR: Unauthorized - plugin: %s'%n)
					tmp = self.config['plugins'][n]
					tmp['password'] = '*****'
					log.debug(tmp)
					if 'error' in self.indicators:
						self.indicators['error'].hide()
					title = self.config['plugins'][n]['plugin']
					title += ' - Unauthorized Account: '
					title += self.config['plugins'][n]['username']
					self.indicators['error'] = SettingsIndicatorItem(
						title
					)
					
			except Exception, e:
				log.error('An error occured ...')
				log.error(e)
			else:
				if self.notifier[n].unread:
					self.notifier[n].unread.indicate()
					for u in self.notifier[n].unread.mails:
						u.notify()
		
		gobject.timeout_add_seconds(self.config['refreshTimeout'], self.refresh)
		
class SettingsIndicatorItem(indicate.Indicator):		
	def __init__(self, subject):
		'''
		indicator for error and setting items		
		'''
		indicate.Indicator.__init__(self)
		self.subject = subject
		self.set_property('name', subject)
		self.connect('user-display', self.click)
		self.set_property('draw-attention', 'true')
		self.show()
		
	def click(self, server, something):
		server.set_property('draw-attention', 'false')
		log.info('TODO - open settings')
