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
import subprocess
import sys

# own imports
from includes.settings import Settings

# log
log = logging.getLogger('Log.Indicator')

class Indicator():
	def __init__(self, confFile, pluginDir):
		self.desktopFile 	= os.path.join(
			os.getcwd(),
			'data',
			'mailnotify.desktop'
		)
		self.confFile = confFile
		self.pluginDir = pluginDir
#		self.desktopFile 	= os.path.join(
#			os.path.dirname(sys.argv[0]),
#			'data',
#			'mailnotify.desktop'
#		)
		self.server	= indicate.indicate_server_ref_default()
		self.server.set_type('message.mail')
		self.server.set_desktop_file(self.desktopFile)
		self.server.connect('server-display', self.click)
		self.server.show()
		
		self.to = 0
		
		self.start(True)
		
	def start(self, init=False):
		'''
			wrapper method for all (re)loading tasks
		
			load config, load plugins, (re)initialize notifiers and indicators
		'''
		self.loadConfig()
		self.config['refreshtimeout'] = int(self.config['refreshtimeout'])
		
		self.config['refreshtimeout'] = 10
		
		if not init:
			for i in self.notifier:
				self.notifier[i].unread.clear()
		self.notifier = {}	
		self.loadAndStartPlugins()
		
		if not init:
			for i in self.indicators:
				self.indicators[i].hide()
				
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
		
	def loadConfig(self):
		'''
			receive config
		'''
		log.info('loading config ...')
		self.config = Settings(self.confFile).config
		
	def loadAndStartPlugins(self):
		'''
			check plugins and import available and needed ones
		'''
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
			if os.path.isfile(os.path.join(self.pluginDir,n+'.py')):
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
		
	def click(self, server=None, something=None):
		'''
			called on click: main item or error item
		'''
		log.info('open settings')
		subprocess.call([SETTINGSAPP])
		self.start()
		self.to += 1
		self.refresh(True)	
		
	def refresh(self, new=False):
		'''
			main functionality - checks for new mails :)
		'''
		if not new and self.to > 0:
			self.to -= 1
			return
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
							title,
							self.click
						)
				else:
					log.error('An HTTPError occured ...')
					log.error(e)
					log.error('code: ' . e.code)
					
			except urllib2.URLError, e:
				if str(e.reason) == '[Errno -2] Name or service not known':
					log.info('Network disabled')
					
					title = 'May you haven\'t network enabled'
					
					if 'error' in self.indicators and \
						not self.indicators['error'].subject == title:
						self.indicators['error'].hide()
						del self.indicators['error']

					if 'error' not in self.indicators:
						self.indicators['error'] = SettingsIndicatorItem(
							title,
							self.click
						)
						self.indicators['error'].unstress()
				elif str(e.reason) == '[Errno 101] Network is unreachable':
					log.info('Lost internet connection')
					title = 'May you haven\'t internet connection'
					
					if 'error' in self.indicators and \
						not self.indicators['error'].subject == title:
						self.indicators['error'].hide()
						del self.indicators['error']

					if 'error' not in self.indicators:
						self.indicators['error'] = SettingsIndicatorItem(
							title,
							self.click
						)
						self.indicators['error'].unstress()
				else:				
					log.error('An URLError occured ...')
					log.error(e)
					log.error('reason: ' + str(e.reason) )
					
			except Exception, e:
				log.error('An error occured ...')
				log.error(e)
			else:
				#if 'error' in self.indicators:
				#	self.indicators['error'].hide()
				#	del self.indicators['error']
					
				if self.notifier[n].unread:
					self.notifier[n].unread.indicate()
					for u in self.notifier[n].unread.mails:
						u.notify()
		
		gobject.timeout_add_seconds(self.config['refreshtimeout'], self.refresh)
		
class SettingsIndicatorItem(indicate.Indicator):		
	def __init__(self, subject, callback):
		'''
			indicator for error and setting items		
		'''
		indicate.Indicator.__init__(self)
		self.callback = callback
		self.subject = subject
		self.set_property('name', subject)
		self.connect('user-display', self.click)
		self.stress()
		self.show()	
		
	def click(self, server, something):
		self.unstress()		
		self.callback()
		
	def stress(self):
		self.set_property('draw-attention', 'true')
		
	def unstress(self):
		self.set_property('draw-attention', 'false')
