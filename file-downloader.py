import sublime
import sublime_plugin
import webbrowser as web
import _thread

from .constant import *
from .util import *


class InsertDownloadTextCommand(sublime_plugin.TextCommand):

	def run(self, edit, text):
		file = sublime.active_window().new_file()
		file.insert(edit, 0, text)


class DownloadReplaceCommand(sublime_plugin.TextCommand):

	def run(self, edit, a, b, file):
		self.view.replace(edit, sublime.Region(a, b), file)


class DownloadEvents(sublime_plugin.EventListener):

	def download_in_path(self, index):
		if index != -1:
			url, file, region, path = self.info
			v = self.v
			if index == 0:
				return _thread.start_new_thread(
					download, (v, url, path, self.relative, file, region)
				)
			if index:
				self.info[3] = path + self.directory[index]
				self.relative += self.directory[index] + '/'
			self.directory = list_directory(self.info[3])
			v.window().show_quick_panel(self.directory, self.download_in_path, selected_index=0)

	def on_browser(self, v, url, file, region):
		web.open(url)

	def on_download(self, v, url, file, region):
		self.relative = ''
		self.directory = list_directory(self.info[1])
		self.download_in_path(None)

	def on_memory(self, v, url, file, region):
		_thread.start_new_thread(memory, (v, url))

	def action(self, path):
		action, url = path.split('://', 1)
		url, file, region, path = self.info
		fns = [self.on_download, self.on_memory, self.on_browser]
		switch(action, fns)(self.v, url, file, region)

	def on_hover(self, v, point, hover_zone):
		self.v = v
		info = obtain_info(v, point)
		url, file, region, path = info
		if url and sublime.HOVER_TEXT == hover_zone:
			self.info = info
			popup(v, url, file, path, point, self.action)

	def on_modified(self, view):
		gutter_update("download", view, view.find_all(URL))

	def on_activated(self, view):
		gutter_update("download", view, view.find_all(URL))
