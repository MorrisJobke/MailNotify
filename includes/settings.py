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
import ConfigParser
import os

# own imports
from includes.keyring import Keyring

import logging
log = logging.getLogger('Log.Settings')

from pprint import pprint

class Settings:
	def __init__(self, file):
		log.info('loading settings ...')
		self.file 	= os.path.expanduser(file)
		self.c 		= ConfigParser.ConfigParser()
		if not os.path.exists(os.path.dirname(self.file)):
			os.mkdir(os.path.dirname(self.file))
		if not os.path.exists(self.file):
			self.c.readfp(open('data/default.conf'))
		self.c.read(self.file)
		
		self.config = {'plugins':{}}
		
		for s in self.c.sections():
			items = self.c.items(s)
			if s == 'Main':
				for p in items:
					self.config[p[0]] = self.convert(s, p[0])
			else:
				tmp = {}
				for p in items:					
					tmp[p[0]] = self.convert(s, p[0])
				self.config['plugins'][s] = tmp
	
		self.write()
		
		self.getCredentials()
		
	def convert(self, s, o):
		n = self.c.get(s, o)
		try:
			n = self.c.getint(s, o) 
		except Exception, e:
			try:
				n = self.c.getboolean(s, o)
			except Exception, e:
				pass
		return n
		
	def write(self):
		with open(self.file, 'wb') as configfile:
			self.c.write(configfile)
			
	def getCredentials(self):
		gkr = Keyring('MailNotify', 'login data')
		for p in self.config['plugins']:
			log.info('receiving credentials ...')
			username, password = gkr.getCredential(p)
			self.config['plugins'][p]['username'] = username
			self.config['plugins'][p]['password'] = password	
