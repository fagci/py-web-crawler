#!/usr/bin/env python
import re
import requests
import dns_cache
from sys import stdout
from argparse import ArgumentParser
from urllib.parse import urlparse, unquote
from queue import Queue
from collections import namedtuple
from threading import Thread, Lock

dns_cache.override_system_resolver()

class Crawler:
    def __init__(self, base_url, deep=5, threads=10, output_file=None, user_agent='Mozilla/5.0 (compatible; pycrawlbot/1.0)'):
        self.base_url = base_url
        self.deep = deep
        self.threads = threads
        self.file = None
        if output_file == '-':
            self.file = stdout
        elif output_file:
            self.file = open(output_file, 'w')
        self.ua = user_agent
        self.urls = set()
        self.lock = Lock()
        self.queue = Queue()

        p = urlparse(base_url)

        self.scheme = p.scheme
        self.netloc = p.netloc

        self.link_regexp = re.compile(r'href=["\']?([^"\'> ]+?)["\'> ]', re.I)
        self.QueueItem = namedtuple('QueueItem', ['url', 'level'])

    def get_links(self, url):
        try:
            headers = {'User-Agent': self.ua}
            response = requests.get(url, timeout=10, headers=headers)
            elapsed_ms = round(response.elapsed.total_seconds() * 1000)
            if 'text/html' not in response.headers['Content-Type']:
                return []
            html = response.content.decode()
            links = self.link_regexp.findall(html)
            if self.file is not stdout:
                print(f'[{response.status_code}] {len(html):>6} B {elapsed_ms:>4} ms {unquote(url[len(self.base_url):])}')
            return map(self.normalize_url, links)
        except Exception as e:
            print(f'[ERR] {e} for {url}')
            return []

    def normalize_url(self, url):
        if url.startswith('//'): return f'{self.scheme}:{url}'
        if url.startswith('/'): return f'{self.scheme}://{self.netloc}{url}'
        return url

    def manage_url(self, url, level):
        if level > self.deep or not url.startswith(self.base_url):
            return False
        with self.lock:
            if url in self.urls:
                return False
            self.urls.add(url)
            if self.file:
                self.file.write(f'{url}\n')
                self.file.flush()
        self.queue.put(self.QueueItem(url=url, level=level))
        return True

    def crawl(self, queue):
        while True:
            url, level = queue.get()

            for link in self.get_links(url):
                self.manage_url(link, level + 1)

            queue.task_done()

    def start(self):
        for _ in range(self.threads):
            worker = Thread(target=self.crawl, args=(self.queue,))
            worker.setDaemon(True)
            worker.start()
        self.urls.add(self.base_url)
        self.queue.put(self.QueueItem(self.base_url, 1))
        self.queue.join()

if __name__ == "__main__":
    try:
        parser = ArgumentParser(description='Web crawler.')

        parser.add_argument('url', metavar='URL', help='address to start crawl from')
        parser.add_argument('-d', metavar='DEPTH', type=int, default=5, help='crawl depth (default: 5)')
        parser.add_argument('-t', metavar='THREADS_COUNT', type=int, default=10, help='threads count (default: 10)')
        parser.add_argument('-o', metavar='OUTPUT_FILE', default=None, help='output file')
        parser.add_argument(
                '-u',
                metavar='USER_AGENT',
                default='Mozilla/5.0 (compatible; pycrawlbot/1.0)',
                help='user agent (default: Mozilla/5.0 (compatible; pycrawlbot/1.0))')

        args = parser.parse_args()

        crawler = Crawler(args.url, args.d, args.t, args.o, args.u)
        crawler.start()

        if crawler.file is not stdout:
            print(f'Total: {len(crawler.urls)} url(s)')

    except KeyboardInterrupt:
        print('bye')
