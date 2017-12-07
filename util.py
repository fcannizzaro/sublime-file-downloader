import sublime
import os
import re
import urllib.request
from .constant import *


def identify(v, point):
	regions = list(filter(lambda r: r.contains(point), v.find_all(URL)))
	if regions:
		region = regions[0]
		url = v.substr(region)
		return [url, url.split('/')[-1], region]
	return [None]*3


def file_path(v):
	path = re.search(DIR, v.file_name()) if v.file_name() else None
	return [path.group(1) if path else None]


def obtain_info(v, point):
	return identify(v, point) + file_path(v)


def gutter_update(tag, view, regions):
		flags = sublime.HIDE_ON_MINIMAP | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_EMPTY | sublime.DRAW_SOLID_UNDERLINE
		view.add_regions(tag, regions, tag, ICON % tag, flags)


def popup(v, url, file, path, point, action):
		resources = sublime.find_resources('template.html')
		html = sublime.load_resource(resources[0])
		html = re.sub(DOWNLOAD, '', html) if not path else html
		html = html.format(file=file, url=url)
		v.show_popup(html, location=point, max_width=600,
                    on_navigate=action, flags=sublime.HIDE_ON_MOUSE_MOVE_AWAY)


def list_directory(path):
		for _, dirnames, _ in os.walk(path):
				return ['./'] + dirnames


def download(v, url, path, relative, file, region):
	v.window().status_message('Downloading %s..' % file)
	urllib.request.urlretrieve(url, path + '/' + file)
	regions = v.find_all(url)
	for reg in regions:
			v.run_command('download_replace', {
			              'a': region.a,
			              'b': region.b,
			              'file': './' + relative + file
			              })
	sublime.message_dialog('"%s" download completed!' % file)


def memory(v, url):
		response = urllib.request.urlopen(url)
		data = response.read().decode('utf-8')
		v.run_command('insert_download_text', {'text': data})


def switch(action, fns):
		return fns[ACTIONS.index(action)]
