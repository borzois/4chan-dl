#!/usr/bin/python

from bs4 import BeautifulSoup
import os.path
import os
import sys
import requests
import argparse
import json

# whatever im gonna make it a 4chan scraper now

class FourchanDL:
	def __init__(self, args, config):
		self._args = args
		self._config = config
		self._url = args.url
		self._soup = self.prepare_soup()
		self._dl_count = 0
		self._skip_count = 0
		self._name = args.name
		self._format = self.get_format()
		self._dl_dir = self.get_directory()

	def prepare_soup(self):
		html_get = requests.get(self._url)
		if not html_get.ok:
			sys.exit("Invalid url")
		return BeautifulSoup(html_get.text, 'html.parser')

	def get_directory(self):
		dl_subdir = '/'.join(self._format.split('/')[:-1])
		if "%name" in dl_subdir:
			try:
				dl_subdir = dl_subdir.replace("%name", self._name)
			except TypeError:
				sys.exit("Name must be set (use -n)")
		op = self._soup.find(class_='opContainer')
		dl_subdir = dl_subdir.replace("%opid", op.get('id')[2:])
		dl_subdir = dl_subdir.replace("%opname", op.find(class_="subject").text.replace('/', ' '))
		print(dl_subdir)

		# download directory is chosen based on the following order of priorities
		if self._args.directory is not None:
			# 1. -d argument
			dl_dir = os.path.join(self._args.directory, dl_subdir)
			if self._args.set_default_directory is True:
				self._config['path'] = self._args.directory
				print("Set", self._args.directory, "as default download directory")
		elif self._config['path'] is not None:
			# 2. default directory
			dl_dir = os.path.join(self._config['path'], dl_subdir)
		else:
			# 3. current directory (where the script is being run from)
			dl_dir = dl_subdir
		os.makedirs(dl_dir, exist_ok=True)
		print(dl_dir)
		return dl_dir

	def get_format(self):
		# format is chosen based on the following order of priorities
		if self._args.format is not None:
			# 1. -f argument
			form = self._args.format
			if self._args.set_default_format is True:
				self._config['format'] = self._args.format
				print("Set", self._args.format, "as default format")
		else:
			# 2. default directory
			form = self._config['format']
		return form

	def get_img_name(self, post):
		extension = "." + post.find(class_="fileText").a.text.split('.')[-1]
		img_name = self._format.split('/')[-1]
		img_name = img_name.replace("%filename", post.find(class_="fileText").a.text.replace(extension, ''))
		img_name = img_name.replace("%id", post.get('id')[2:])
		img_name = img_name.replace("%count", str(self._dl_count + self._skip_count + 1))
		op = self._soup.find(class_='opContainer')
		img_name = img_name.replace("%opid", op.get('id')[2:])
		img_name = img_name.replace("%opname", op.find(class_="subject").text.replace('/', ' '))
		if "%name" in img_name:
			try:
				img_name = img_name.replace("%name", self._name)
			except TypeError:
				sys.exit("Name must be set (use -n)")
		
		img_name = img_name + extension
		return img_name

	def run(self):
		for post in self._soup.find_all(class_='postContainer'):
			if post.find('img') is not None:
				download_successful = self.download_post(post)

				if download_successful:
					if not self._args.quiet:
						print('Downloaded post', post.get('id')[2:], 'as', self.get_img_name(post))
					self._dl_count += 1
				else:
					if not self._args.quiet:
						print('Skipped post', post.get('id')[2:], '-', self.get_img_name(post))
					self._skip_count += 1

	def download_post(self, post):
		img_name = self.get_img_name(post)
		img_link = "http:" + post.find(class_="fileThumb").get('href')

		# archived posts will have a gif that messes everything up
		if img_link.split('/')[-1] == "archived.gif":
			return False

		# download:
		file_location = os.path.join(self._dl_dir, img_name)
		if not os.path.exists(file_location):
			img_get = requests.get(img_link)
			if img_get.ok:
				with open(file_location, 'wb') as file:
					file.write(img_get.content)
				return True
		else:
			return False

	def print_stats(self):
		if self._dl_count != 0:
			print("Downloaded", self._dl_count, "images to", self._dl_dir, "\nSkipped", self._skip_count, "images")
		else:
			print("Nothing to download\nSkipped", self._skip_count, "images")


def load_config():
	config_path = os.path.expanduser("~/.config/4chan-dl/config.json")
	config = {}
	if os.path.isfile(config_path):
		with open(config_path, 'r') as file:
			config = json.load(file)
	return config

def export_config(config):
	config_path = os.path.expanduser("~/.config/4chan-dl/config.json")
	if not os.path.exists(os.path.expanduser("~/.config/4chan-dl/")):
		os.makedirs(os.path.expanduser("~/.config/4chan-dl/"))
	with open(config_path, 'w') as file:
		json.dump(config, file)

def get_args():
	parser = argparse.ArgumentParser(description="4chan image downloader")
	parser.add_argument("-d", "--directory", type=str, help="Directory to save images to")
	parser.add_argument("-f", "--format", type=str, help="File naming")
	parser.add_argument("-n", "--name", type=str, help="Set the %name variable")
	parser.add_argument("-q", "--quiet", action=argparse.BooleanOptionalAction, help="Less verbose")
	parser.add_argument("--set-default-directory", action=argparse.BooleanOptionalAction, help="Set the current directory argument as default")
	parser.add_argument("--set-default-format", action=argparse.BooleanOptionalAction, help="Set the current directory format as default")
	parser.add_argument("url", type=str, help="Thread URL")

	return parser.parse_args()

def main():
	args = get_args()
	default_config = {
		"path": None,
		"format": "%filename"
	}

	config = load_config()
	if config == {}:
		print("No config file found. Creating default config")
		config = default_config

	dl = FourchanDL(args, config)

	dl.run()	
	dl.print_stats()

	export_config(config)
	
if __name__ == "__main__":
	main()