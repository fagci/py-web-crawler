import re, requests
from time import sleep
from sys import argv
from urllib.parse import urlparse
from queue import Queue
from threading import Thread

class Crawler:
    def __init__(self, start_url, deep = 5, threads = 10):
        self.start_url = start_url
        self.deep = deep
        self.threads = threads
        self.start_url_parsed = urlparse(start_url)
        self.urls = set()
        self.queue = Queue()
        self.link_compiled_regexp = re.compile(r'href="?([^" >]+)[" >]')

    def get_links(self, url):
        try:
            response = requests.get(url, timeout = 10)
            elapsed_ms = round(response.elapsed.microseconds / 1000)
            print('[{}] {}ms: {}'.format(response.status_code,elapsed_ms,url))
            html = response.content.decode('utf-8')
            return self.link_compiled_regexp.findall(html)
        except Exception as e:
            print('exception:', e)
            return []

    def normalize_url(self, url):
        if url.startswith('//'):
            url = '{}:{}'.format(self.start_url_parsed.scheme, url)
        elif url.startswith('/'):
            url = '{}://{}{}'.format(self.start_url_parsed.scheme,self.start_url_parsed.netloc, url)
        return url


    def crawl(self, i, q):
        while not q.empty():
            url, level = q.get()
            if  level > self.deep or url in self.urls:
                return

            self.urls.add(url)
            print('thr:{},lv:{},{}'.format(i,level,url))

            links = self.get_links(url)

            for link in links:
                link = self.normalize_url(link)
                if link.startswith(self.start_url):
                    q.put((link, level+1))
        print('q for {} is empty'.format(i))

    def start(self):
        self.queue.put((self.start_url,0))
        for i in range(self.threads):
            worker = Thread(target=self.crawl, args=(i,self.queue,))
            worker.setDaemon(True)
            worker.start()
        self.queue.join()

if __name__ == "__main__":
    crawler = Crawler(argv[1])
    crawler.start()

