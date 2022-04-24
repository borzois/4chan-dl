#!/usr/bin/python

from bs4 import BeautifulSoup
import requests
import os
import re
import sys

# whatever im gonna make it a 4chan scraper now

if len(sys.argv) == 1:
	url = input("Thread: ")
else:
	url = sys.argv[1]

html_get = requests.get(url).text
soup = BeautifulSoup(html_get, 'html.parser')

# make a directory using the post id
dl_dir = url.split('/')[-1]
os.makedirs(dl_dir, exist_ok=True)

for post in soup.find_all(class_='postContainer'):
	post_id = post.get('id')[2:]
	img = post.find('img')
	if img is not None:
		img_name = post.find(class_="fileText").a.text
		img_link = "http:" + post.find(class_="fileThumb").get('href')

		# archived posts will have a gif that fucks everything up
		if img_link.split('/')[-1] != "archived.gif":
			print('Downloading post', post_id, '-', img_name)

			# download:
			file_location = dl_dir + "/" + img_name
			img_get = requests.get(img_link)
			with open(file_location, 'wb') as file:
				file.write(img_get.content)