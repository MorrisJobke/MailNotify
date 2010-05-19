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
# own imports

import logging
log = logging.getLogger('Log.UnreadMails')

class UnreadMails:
	def __init__(self, link, prefix='', style=1):
		log.debug('new UnreadMails ...')
		self.link 		= link
		self.style 		= style
		self.prefix 	= prefix
		self.mails		= []
		self.mailboxes 	= {}
		self.indicators = {}
				
	def add(self, mails):
		mailboxes = {}
		for mail in mails:
			if mail.mailbox['name'] not in mailboxes:
				mailboxes[mail.mailbox['name']] = {'count': 0, 'link': mail.mailbox['link']}
			mailboxes[mail.mailbox['name']]['count'] += 1
			if mail.subject not in [m.subject for m in self.mails]:
				log.info('new mail ...')
				self.mails.append(mail)
		
		self.mailboxes = mailboxes
		# cleanup
		for mail in self.mails:
			if mail.subject not in [m.subject for m in mails]:
				self.mails.remove(mail)
				if self.style == 2:
					self.indicators[self.prefix + mail.subject].hide()
					del self.indicators[self.prefix + mail.subject]
	
	def indicate(self):		
		if self.style == 1:
			#### STYLE 1 ####
			for m in self.mailboxes:
				n = self.prefix + m
				if n in self.indicators:
					self.indicators[n].update(str(self.mailboxes[m]['count']))
				else:
					i = IndicatorItem(
						self.mailboxes[m]['link'],
						n,
						str(self.mailboxes[m]['count'])
					)
					self.indicators[n] = i
		elif self.style == 2:			
			#### STYLE 2 ####
			for m in self.mails:
				n = self.prefix + m.subject
				if not n in self.indicators:
					i = IndicatorItem(
						m.link,
						n,
						m.time
					)
					self.indicators[n] = i
					
	def clear(self):
		for i in self.indicators:
			self.indicators[i].hide()
		self.mails		= []
		self.mailboxes 	= {}
		self.indicators = {}
		
class IndicatorItem(indicate.Indicator):
	def __init__(self, link, subject, timeOrCount):
		'''
		indicator for IndicatorItems		
		'''
		log.debug('new IndicatorItem ...')
		indicate.Indicator.__init__(self)
		self.link = link
		self.set_property('name', subject)
		if type(timeOrCount) == type(float()):
			self.set_property_time('time', timeOrCount)
		elif type(timeOrCount) == type(str()):
			self.set_property('count', timeOrCount)
		self.connect('user-display', self.click)
		self.set_property('draw-attention', 'true')
		self.show()
		
	def click(self, server, something):
		server.set_property('draw-attention', 'false')
		subprocess.call(['gnome-open', self.link])
		
	def stress(self):
		self.set_property('draw-attention', 'true')
	
	def unstress(self):
		self.set_property('draw-attention', 'false')
		
	def update(self, timeOrCount):
		if type(timeOrCount) == type(float()):
			self.set_property_time('time', timeOrCount)
		elif type(timeOrCount) == type(str()):
			self.set_property('count', timeOrCount)
		self.set_property('draw-attention', 'true')
	
