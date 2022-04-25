#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import os
from os.path import exists
import re
import sys

# whatever im gonna make it a 4chan scraper now

def download_post(post, dl_dir):
	img = post.find('img')
	if img is None:
		return False

	img_name = post.find(class_="fileText").a.text
	img_link = "http:" + post.find(class_="fileThumb").get('href')

	# archived posts will have a gif that messes everything up
	if img_link.split('/')[-1] == "archived.gif":
		return False

	# download:
	file_location = dl_dir + "/" + img_name
	if not exists(file_location):
		img_get = requests.get(img_link)
		if img_get.ok:
			with open(file_location, 'wb') as file:
				file.write(img_get.content)
			return True
	else:
		return False

def print_stats(dl_count, skip_count, dl_dir):
	if dl_count != 0:
		print("Downloaded", dl_count, "images to", dl_dir, "\nSkipped", skip_count, "images")
	else:
		print("Nothing to download")

def main():
	if len(sys.argv) == 1:
		url = input("Thread: ")
	else:
		url = sys.argv[1]

	html_get = requests.get(url)
	if not html_get.ok:
		print("Invalid url")
		return
	soup = BeautifulSoup(html_get.text, 'html.parser')

	# make a directory using the post id
	dl_dir = url.split('/')[-1]
	os.makedirs(dl_dir, exist_ok=True)

	dl_count = 0
	skip_count = 0

	for post in soup.find_all(class_='postContainer'):
		download_successful = download_post(post, dl_dir)

		if download_successful:
			print('Downloaded post', post.get('id')[2:], '-', post.find(class_="fileText").a.text)
			dl_count += 1
		else:
			print('Skipped post', post.get('id')[2:], '-', post.find(class_="fileText").a.text)
			skip_count += 1
	
	print_stats(dl_count, skip_count, dl_dir)
	
if __name__ == "__main__":
	main()