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
		self._url = args.url
		self._soup = self.prepare_soup()
		self._dl_count = 0
		self._skip_count = 0

		dl_subdir = self._url.split('/')[-1]
		# download directory is chosen based on the following order of priorities
		if args.directory is not None:
			# 1. -d argument
			self._dl_dir = os.path.join(args.directory, dl_subdir)
			if args.set_default is True:
				config['default_path'] = args.directory

		elif config['default_path'] is not None:
			# 2. default directory
			self._dl_dir = os.path.join(config['default_path'], dl_subdir)
		else:
			# 3. current directory (where the script is being run from)
			self._dl_dir = dl_subdir
		os.makedirs(self._dl_dir, exist_ok=True)

	def prepare_soup(self):
		html_get = requests.get(self._url)
		if not html_get.ok:
			print("Invalid url")
			return
		return BeautifulSoup(html_get.text, 'html.parser')

	def run(self):
		for post in self._soup.find_all(class_='postContainer'):
			if post.find('img') is not None:
				download_successful = self.download_post(post)

				if download_successful:
					print('Downloaded post', post.get('id')[2:], '-', post.find(class_="fileText").a.text)
					self._dl_count += 1
				else:
					print('Skipped post', post.get('id')[2:], '-', post.find(class_="fileText").a.text)
					self._skip_count += 1

	def download_post(self, post):
		img_name = post.find(class_="fileText").a.text
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
	with open(config_path, 'w') as file:
		json.dump(config, file)

def main():
	parser = argparse.ArgumentParser(description="4chan image downloader")
	parser.add_argument("-d", "--directory", type=str, help="Directory to save images to")
	parser.add_argument("--set-default", action=argparse.BooleanOptionalAction, help="Set the current directory argument as default")
	parser.add_argument("url", type=str, help="Thread URL")

	args = parser.parse_args()
	config = load_config()
	if config == {}:
		print("No config file found")

	dl = FourchanDL(args, config)

	dl.run()	
	dl.print_stats()

	export_config(config)
	
if __name__ == "__main__":
	main()