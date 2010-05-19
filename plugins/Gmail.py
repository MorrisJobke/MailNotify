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
import base64
import urllib2
import time
import feedparser
import calendar
# own classes
from mail import Mail
from unreadmails import UnreadMails

import logging
log = logging.getLogger('Log.Gmail')

class Notifier():
	def __init__(self, config):
		self.config = config
		self.request = urllib2.Request('https://mail.google.com/mail/feed/atom/')
		self.request.add_header('Authorization', 'Basic %s'% \
			(base64.encodestring(
				'%s:%s'%(
					self.config['username'], 
					self.config['password']
				)
			)[:-1])
		)
		prefix = ''
		if self.config['enablePrefix']:
			prefix = self.config['prefix']
		self.unread = UnreadMails(
			'https://mail.google.com/mail/#search/label:%s',
			prefix,
			2
		)
		
	def check(self):
		log.info('checking Gmail ...')		
		try:
			data = feedparser.parse(urllib2.urlopen(self.request).read())
		except Exception, e:
			raise e
		else:
			mailboxUrl = data['feed']['link']
			if data['entries'] == []:
				self.unread.clear()
			else:
				mails = []
				for mail in data['entries']:
					mails.append(Mail(
						{
							'name': 'Inbox',
							'link': mailboxUrl
						},
						mail['title'],
						{	
							'name': mail['author_detail']['name'],
							'mail': mail['author_detail']['email']
						},
						mail['link'],
						time.mktime(time.localtime(calendar.timegm(time.strptime(mail['issued'].replace('T24', 'T00'),'%Y-%m-%dT%H:%M:%SZ')))))
					)	
				self.unread.add(mails)	
