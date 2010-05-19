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
import pynotify
# own imports

class Mail:
	def __init__(self, mailbox, subject, author, link, time):
		self.mailbox 	= mailbox
		self.subject 	= subject
		self.author 	= author
		self.link		= link
		self.time		= time
		self.icon 		= 'applications-email-panel'
		self.new 		= True
		
	def setIcon(self, icon):
		self.icon = icon
		
	def notify(self):
		if self.new:
			n = pynotify.Notification(
				self.subject, 
				'%s <%s>'%(self.author['name'],self.author['mail']), 
				self.icon
			)
			n.show()
			self.new = False
