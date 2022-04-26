#!/usr/bin/python

from bs4 import BeautifulSoup
import os.path
import os
import sys
import requests
import argparse
import json
import time


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
        # self._dl_dir = self.get_directory()

    def prepare_soup(self):
        html_get = requests.get(self._url)
        if not html_get.ok:
            sys.exit("Invalid url")
        return BeautifulSoup(html_get.text, 'html.parser')

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

    def process_format(self, post):
        # full path: path / img_name . extension
        extension = "." + post.find(class_="fileText").a.text.split('.')[-1]

        path_format = self._format
        path_format = path_format.replace("%filename", post.find(class_="fileText").a.text.replace(extension, ''))
        path_format = path_format.replace("%id", post.get('id')[2:])
        path_format = path_format.replace("%count", str(self._dl_count + self._skip_count + 1))
        op = self._soup.find(class_='opContainer')
        path_format = path_format.replace("%opid", op.get('id')[2:])
        path_format = path_format.replace("%opname", op.find(class_="subject").text.replace('/', ' '))
        if "%name" in path_format:
            try:
                path_format = path_format.replace("%name", self._name)
            except TypeError:
                sys.exit("Name must be set (use -n)")
        return path_format + extension

    def run(self):
        for post in self._soup.find_all(class_='postContainer'):
            if post.find('img') is not None:
                download_successful = self.download_post(post)

                if download_successful:
                    if not self._args.quiet:
                        print('Downloaded post', post.get('id')[2:], 'to', self.process_format(post))
                    self._dl_count += 1
                else:
                    if not self._args.quiet:
                        print('Skipped post', post.get('id')[2:], '-', self.process_format(post))
                    self._skip_count += 1

    def download_post(self, post):
        img_path = os.path.expanduser(self.process_format(post))
        img_link = "http:" + post.find(class_="fileThumb").get('href')

        # will make a folder if it doesn't exist
        os.makedirs('/'.join(img_path.split('/')[:-1]) + '/', exist_ok=True)

        # archived posts will have a gif that messes everything up
        if img_link.split('/')[-1] == "archived.gif":
            return False

        # download:
        if not os.path.exists(img_path):
            img_get = requests.get(img_link)
            if img_get.ok:
                with open(img_path, 'wb') as file:
                    file.write(img_get.content)
                return True
        else:
            return False

    def print_stats(self):
        if self._dl_count != 0:
            print("Downloaded", self._dl_count, "images\nSkipped", self._skip_count, "images")
        elif not self._args.quiet:
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
    parser.add_argument("-f", "--format", type=str, help="File naming")
    parser.add_argument("-n", "--name", type=str, help="Set the name variable")
    parser.add_argument("-q", "--quiet", action=argparse.BooleanOptionalAction, help="Less verbose")
    parser.add_argument("-w", "--watch", type=int, default=0, help="Time between retries. 0 will run the program once")
    parser.add_argument("--set-default-format", action=argparse.BooleanOptionalAction,
                        help="Set the current directory format as default")
    parser.add_argument("url", type=str, help="Thread URL")

    return parser.parse_args()


def main():
    args = get_args()
    default_config = {
        "format": "%filename"
    }

    config = load_config()
    if config == {}:
        print("No config file found. Creating default config")
        config = default_config

    while True:
        dl = FourchanDL(args, config)

        dl.run()
        dl.print_stats()
        if args.watch == 0:
            break
        time.sleep(args.watch)

    export_config(config)


if __name__ == "__main__":
    main()
