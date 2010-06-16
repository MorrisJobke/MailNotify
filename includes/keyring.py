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
import gnomekeyring
import gconf

class Keyring:
	def __init__(self, appName, appDesc, separator=' '):
		self.keyring 	= gnomekeyring.get_default_keyring_sync()
		self.appName 	= appName
		self.appDesc	= appDesc
		self.separator 	= separator
		self.gconfkey 	= '/apps/mailnotify/keyring_auth_token'

	def getCredential(self, appDesc=None):
		if appDesc == None:
			appDesc = self.appDesc
		authToken = gconf.client_get_default().get_int(self.gconfkey + '_' + appDesc)
		if authToken > 0:
			try:
				secret = gnomekeyring.item_get_info_sync(
						self.keyring, 
						authToken
					).get_secret()
			except gnomekeyring.DeniedError:
				username = None
				password = None
			else:
				try:
					username, password = secret.split(self.separator)
				except:
					username = None
					password = None
		else:
			username = None
			password = None
		
		return username, password
		
	def setCredential(self, username, password, appDesc=None):
		if appDesc == None:
			appDesc = self.appDesc
		appName = '%s, %s'%(self.appName, appDesc)
		authToken = gnomekeyring.item_create_sync(
			self.keyring,
			gnomekeyring.ITEM_GENERIC_SECRET,
			appName,
			dict(appname=appName),
			self.separator.join((username, password)), 
			True
		)
		gconf.client_get_default().set_int(self.gconfkey + '_' + appDesc, authToken)
