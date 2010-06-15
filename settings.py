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

# own imports
from includes.settings import Settings

LOGFILE = './log'
LOGFORMAT = '%(levelname)s\t%(name)-20s\t%(relativeCreated)d\t%(message)s'
PLUGINDIR = './plugins'
CONFIGFILE = '~/.config/mailnotify/settings.conf'

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

class MailNotifySettings:
	def __init__(self):
		gladeFile = 'data/settings.glade'
		self.ui = gtk.Builder()	
		self.ui.add_from_file(gladeFile)	
		self.ui.connect_signals({
			'on_buttonClose_clicked': 				self.quit,
			'on_settingsDialog_destroy': 			gtk.main_quit,
			'on_accountView_cursor_changed':		self.select,
			'on_buttonDelete_clicked':				self.delete,
			'on_buttonAdd_clicked':					self.a,
		})
		
		self.window = self.ui.get_object('settingsDialog')			
		self.accountView = self.ui.get_object('accountView')
		self.entryUsername = self.ui.get_object('entryUsername')
		self.entryPassword = self.ui.get_object('entryPassword')
		
		self.addColumn('Accounts', 0)
		self.addColumn('Id', 1, False)
		
		self.accountList = gtk.ListStore(str, str)
		self.accountView.set_model(self.accountList)	
				
		self.load()
		
	def addColumn(self, title, columnId, visible=True):
		"""
			adds column to account view
		"""
		column = gtk.TreeViewColumn(
			title, 
			gtk.CellRendererText(), 
			text			= columnId,
		)
		column.set_resizable(True)		
		column.set_sort_column_id(columnId)
		column.set_visible(visible)
		
		self.accountView.append_column(column)

	def quit(self, widget):
		"""
			save settings and close window 
		"""
		self.save()
		print 'quit settings dialog'
		gtk.main_quit()
	
	def select(self, w):
		"""
			fills input fields with current values
		"""
		c = w.get_selection().get_selected()
		p = self.config['plugins'][c[0].get_value(c[1], 1)]
		self.entryUsername.set_text(p['username'])
		self.entryPassword.set_text(p['password'])
		
	def load(self):
		"""
			loads initial config
		"""
	
		#TODO receive config
		a = {
			'refreshtimeout': 60, 
			'plugins': {
				'Gmail-1': {
					'username': 'morris.jobke', 
					'password': 'asdasd', 
					'enableprefix': False, 
					'plugin': 'Gmail'
				},
				'Gmail-2': {
					'username': 'morris.jobke2', 
					'password': 'asdasd', 
					'enableprefix': False, 
					'plugin': 'Gmail'
				},
				'Gmail-3': {
					'username': 'morris.jobke3', 
					'password': 'asdasd', 
					'enableprefix': False, 
					'plugin': 'Gmail'
				}
			}
		}
		self.config = a
		self.reloadAccountView()
			
	def reloadAccountView(self):
		"""
			reloads account view
		"""
		self.accountList.clear()
		a = self.config
		for i in a['plugins']:
			title = '%s (%s)'%(
				a['plugins'][i]['plugin'], 
				a['plugins'][i]['username']
			)
			self.accountList.append([title, i])
			
	def delete(self, w):
		"""
			deletes account
		"""
		c = self.accountView.get_selection().get_selected()
		del self.config['plugins'][c[0].get_value(c[1], 1)]
		self.reloadAccountView()
		self.entryUsername.set_text('')
		self.entryPassword.set_text('')
		
	def a(self, w):
		pass
		
	def save(self):
		pass
		
	def main(self):
		self.window.show()
		gtk.main()
		
		
		



if __name__ == '__main__':
	# initialize log	
	logging.basicConfig(filename=LOGFILE, filemode='w', format=LOGFORMAT)
	log = logging.getLogger('Log')
	level = logging.NOTSET
	if len(sys.argv) > 1:
		level = LEVELS.get(sys.argv[1], logging.NOTSET)
	log.setLevel(level)
	
	a = MailNotifySettings()
	a.main()
