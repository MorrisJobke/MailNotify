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
import os
import gobject

# own imports
from includes.settings import SettingsSaver
from includes.settings import Settings

LOGFILE = '/tmp/mailnotify-settings-log'
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
			'on_buttonAdd_clicked':					self.add,
			'on_setting_changed':					self.changed,
		})
		
		self.timeouts = 0
		self.currentIndex = ''
		
		self.window = self.ui.get_object('settingsDialog')			
		self.accountView = self.ui.get_object('accountView')
		self.entryUsername = self.ui.get_object('entryUsername')
		self.entryPassword = self.ui.get_object('entryPassword')
		self.cbPlugin = self.ui.get_object('comboboxPlugin')
		self.setSensitiveInput(False)
		
		# plugin combobo
		self.pluginList = gtk.ListStore(str)
		self.cbPlugin.set_model(self.pluginList)	
		c = gtk.CellRendererText()
		self.cbPlugin.pack_start(c, True)
		self.cbPlugin.add_attribute(c, 'text', 0)
		self.loadPlugins()		
		
		# account view
		self.addColumn(self.accountView, 'Accounts', 0)
		self.addColumn(self.accountView, 'Id', 1, False)
		self.accountList = gtk.ListStore(str, str)
		self.accountView.set_model(self.accountList)	
		self.loadAccounts()
		
		
	def loadPlugins(self):
		'''
			read all plugins in PLUGINDIR
		'''
		files = os.listdir(PLUGINDIR)
		f = []
		for i in files:
			if not i[-3:] == 'pyc' and not i == "__init__.py":
				f.append(i[:-3])	
		self.plugins = f
		
		i = 0
		for p in self.plugins:
			self.pluginList.insert(i, [p])
			i += 1
	
	def setSensitiveInput(self, b):	
		'''
			activate/deactivate all inputs
		'''	
		self.entryUsername.set_sensitive(b)
		self.entryPassword.set_sensitive(b)
		self.cbPlugin.set_sensitive(b)
		
	def addColumn(self, view, title, columnId, visible=True):
		'''
			adds column to account view
		'''
		column = gtk.TreeViewColumn(
			title, 
			gtk.CellRendererText(), 
			text			= columnId,
		)
		column.set_resizable(True)		
		column.set_sort_column_id(columnId)
		column.set_visible(visible)
		
		view.append_column(column)

	def quit(self, widget):
		'''
			save settings and close window 
		'''
		self.save()
		gtk.main_quit()
	
	def select(self, w):
		'''
			fills input fields with current values
		'''
		c = w.get_selection().get_selected()
		if not c[1] == None:
			self.currentIndex = c[0].get_value(c[1], 1)
			p = self.config['plugins'][self.currentIndex]
			self.entryUsername.set_text(p['username'])
			self.entryPassword.set_text(p['password'])
			a = 0
			index = -1
			for i in self.plugins:
				if not i == p['plugin']:
					a += 1
				else:
					index = a
					break
			self.cbPlugin.set_active(index)
			self.setSensitiveInput(True)
		
		
	def loadAccounts(self):
		'''
			loads initial config
		'''
		self.config = Settings(CONFIGFILE).config
		self.reloadAccountView()
			
	def reloadAccountView(self):
		'''
			reloads account view
		'''
		self.accountList.clear()
		cursor = -1
		a = self.config['plugins']
		b = 0
		for i in a:
			if a[i]['username'] == None:
				self.config['plugins'][i]['username'] = ''
			if a[i]['password'] == None:
				self.config['plugins'][i]['password'] = ''
			title = '%s (%s)'%(
				a[i]['plugin'], 
				a[i]['username']
			)
			self.accountList.append([title, i])
			if i == self.currentIndex:
				cursor = b
			b += 1
		if cursor >= 0:
			self.accountView.set_cursor(cursor)
			
	def delete(self, w):
		'''
			deletes account
		'''
		c = self.accountView.get_selection().get_selected()
		del self.config['plugins'][c[0].get_value(c[1], 1)]
		self.reloadAccountView()
		self.entryUsername.set_text('')
		self.entryPassword.set_text('')
		self.setSensitiveInput(False)
		self.currentIndex = ''
		
	def add(self, w):
		'''
			adds new account
		'''
		self.setSensitiveInput(True)
		
		self.currentIndex = self.getPluginId()
						
		self.config['plugins'][self.currentIndex] = {
			'username': '',
			'password': '',			
			'plugin': 'Unknown',
			'enableprefix':	False
		}
		self.reloadAccountView()	
		
	def getPluginId(self, plugin='Unknown'):
		'''
			creates a unique id for a plugin
			format: PLUGINNAME-NUMBER
		'''
		pluginId = plugin + '-1'
		while pluginId in self.config['plugins']:
			if pluginId[-1].isdigit():
				tmp = pluginId.split('-')
				pluginId = tmp[0] + '-' + str(int(tmp[1]) + 1)
			else:
				pluginId += '-1'
		return pluginId
		
	def save(self):
		'''
			save settings
		'''
		s = SettingsSaver(CONFIGFILE, self.config)
		s.save()
		
	def changed(self, w):	
		'''
			something is changed, but may there are soon more changes, so this function waits a little bit (10ms)
		'''
		self.timeouts += 1
		gobject.timeout_add(10, self.change)
		
	def change(self):
		'''
			apply changes temporarly
		'''
		self.timeouts -= 1
		if self.timeouts > 0:
			return
		
		if not self.currentIndex == '':			
			p = self.cbPlugin.get_active()
			if not p == -1 and p < len(self.plugins):
				plugin = self.plugins[p]
				if not self.currentIndex[:len(plugin)] == plugin:
					tmpIndex = self.getPluginId(plugin)
					self.config['plugins'][tmpIndex] = \
						self.config['plugins'][self.currentIndex]
					del self.config['plugins'][self.currentIndex]
					self.currentIndex = tmpIndex
				self.config['plugins'][self.currentIndex]['plugin'] = plugin

			self.config['plugins'][self.currentIndex]['username'] = \
				self.entryUsername.get_text()
			self.config['plugins'][self.currentIndex]['password'] = \
				self.entryPassword.get_text()
		
			self.reloadAccountView()
		
	def main(self):
		self.window.show()
		gtk.main()

if __name__ == '__main__':
	# initialize log	
	logging.basicConfig(filename=LOGFILE, filemode='w', format=LOGFORMAT)
	log = logging.getLogger('Log')
	level = logging.NOTSET
	level = logging.DEBUG # tmp
	if len(sys.argv) > 1:
		level = LEVELS.get(sys.argv[1], logging.NOTSET)
	log.setLevel(level)
	
	a = MailNotifySettings()
	a.main()
