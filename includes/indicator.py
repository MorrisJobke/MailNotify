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
import os
import gobject
import urllib2
import logging

# own imports
from includes.settings import Settings

# log
log = logging.getLogger('Log.Indicator')

class Indicator():
	def __init__(self, confFile, pluginDir):
		self.desktopFile 	= os.path.join(os.getcwd(),'data','mailnotify.desktop')
		self.server	= indicate.indicate_server_ref_default()
		self.server.set_type('message.mail')
		self.server.set_desktop_file(self.desktopFile)
		self.server.connect('server-display', self.click)
		self.server.show()
		
		self.loadConfig(confFile)
		self.config['refreshtimeout'] = int(self.config['refreshtimeout'])
		
		self.notifier = {}	
		self.loadAndStartPlugins(pluginDir)
		
		self.indicators = {}
		if self.config['plugins'] == {}:
			self.indicators['setup'] = SettingsIndicatorItem(
				'You have to setup a account'
			)
		if not len(self.config['plugins']) == len(self.notifier):		
			self.indicators['error'] = SettingsIndicatorItem(
				'One or more accounts are not supported'
			)
		self.refresh()
		
	def loadConfig(self, confFile):
		log.info('loading config ...')
		self.config = Settings(confFile).config
		
	def loadAndStartPlugins(self, pluginDir):
		p = []
		for i in self.config['plugins']:
			q = self.config['plugins'][i]
			if 'enableprefix' in q and 'plugin' in q and \
				'username' in q and 'password' in q:
				if not q['plugin'] in p:
					p.append(q['plugin'])			
		
		log.info('importing plugins ...')
		g = globals()
		l = locals()
		gs = []
		ls = []
		ns = []
	
		plugins = []
		notFoundPlugins = []
		for n in p:
			if os.path.isfile(os.path.join(pluginDir,n+'.py')):
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
	
		for i in self.config['plugins']:
			p = self.config['plugins'][i]
			if 'plugin' in p and not p['plugin'] in notFoundPlugins:
				self.notifier[i] = loadedPlugins[p['plugin']].Notifier(p)
		
	def click(self, server, something):
		log.info('TODO - open settings')
		
	def refresh(self):
		for n in self.notifier:
			try:
				self.notifier[n].check()
			except urllib2.HTTPError, e:
				if e.code == 401:
					log.info('Unauthorized - plugin: %s'%n)
					tmp = self.config['plugins'][n]
					tmp['password'] = '*****'
					log.debug(tmp)
					title = self.config['plugins'][n]['plugin']
					title += ' - Unauthorized Account: '
					title += self.config['plugins'][n]['username']
					
					
					if 'error' in self.indicators and \
						not self.indicators['error'].subject == title:
						self.indicators['error'].hide()
						del self.indicators['error']
					
					if 'error' not in self.indicators:
						self.indicators['error'] = SettingsIndicatorItem(
							title
						)
				else:
					log.error('An HTTPError occured ...')
					log.error(e)
					log.error('code: ' . e.code)
			except urllib2.URLError, e:
				if str(e.reason) == '[Errno -2] Name or service not known':
					log.info('Lost internet connection')
					
					title = 'May you haven\'t internet connection'
					
					if 'error' in self.indicators and \
						not self.indicators['error'].subject == title:
						self.indicators['error'].hide()
						del self.indicators['error']

					if 'error' not in self.indicators:
						self.indicators['error'] = SettingsIndicatorItem(
							title
						)
						self.indicators['error'].unstress()
				else:				
					log.error('An URLError occured ...')
					log.error(e)
					log.error('reason: ' . e.reason)
					
					if 'error' not in self.indicators:
						self.indicators['error'] = SettingsIndicatorItem(
							title
						)
						self.indicators['error'].unstress()
			except Exception, e:
				log.error('An error occured ...')
				log.error(e)
			else:
				if self.notifier[n].unread:
					self.notifier[n].unread.indicate()
					for u in self.notifier[n].unread.mails:
						u.notify()
		
		gobject.timeout_add_seconds(self.config['refreshtimeout'], self.refresh)
		
class SettingsIndicatorItem(indicate.Indicator):		
	def __init__(self, subject):
		'''
		indicator for error and setting items		
		'''
		indicate.Indicator.__init__(self)
		self.subject = subject
		self.set_property('name', subject)
		self.connect('user-display', self.click)
		self.stress()
		self.show()	
		
	def click(self, server, something):
		self.unstress()
		log.info('TODO - open settings')
		
	def stress(self):
		self.set_property('draw-attention', 'true')
		
	def unstress(self):
		self.set_property('draw-attention', 'false')
