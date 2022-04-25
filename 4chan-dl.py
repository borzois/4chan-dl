#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import os
from os.path import exists
import re
import sys

# whatever im gonna make it a 4chan scraper now

class FourchanDL:
	def __init__(self, url):
		self._url = url
		self._soup = self.prepare_soup()
		self._dl_dir = dl_dir = self._url.split('/')[-1]
		self._dl_count = 0
		self._skip_count = 0

		os.makedirs(dl_dir, exist_ok=True)

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
		file_location = self._dl_dir + "/" + img_name
		if not exists(file_location):
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
			print("Nothing to download")

def main():
	if len(sys.argv) == 1:
		url = input("Thread: ")
	else:
		url = sys.argv[1]
	
	dl = FourchanDL(url)

	dl.run()	
	dl.print_stats()
	
if __name__ == "__main__":
	main()