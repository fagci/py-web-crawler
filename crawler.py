import re, requests
from time import sleep
from sys import argv
from urllib.parse import urlparse
from queue import Queue
from threading import Thread, Lock

class Crawler:
    def __init__(self, start_url, deep = 5, threads = 10):
        self.start_url = start_url
        self.deep = deep
        self.threads = threads
        self.lock = Lock()
        self.start_url_parsed = urlparse(start_url)
        self.urls = set()
        self.queue = Queue()
        self.link_compiled_regexp = re.compile(r'href="?([^" >]+)[" >]')

    def get_links(self, url):
        try:
            response = requests.get(url, timeout = 10)
            elapsed_ms = round(response.elapsed.microseconds / 1000)
            # print('--[{}] {}ms: {}'.format(response.status_code,elapsed_ms,url))
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
        while True:
            url, level = q.get()
            print(f'-T{i} {url}')
            # print('--thr:{},lv:{},{}'.format(i,level,url))

            links = self.get_links(url)

            for link in links:
                link = self.normalize_url(link)
                if not link.startswith(self.start_url):
                    continue #todo: show as external for ex.

                self.lock.acquire()
                if  level > self.deep or link in self.urls:
                    self.lock.release()
                    continue

                self.urls.add(link)
                self.lock.release()
                print(f'+T{i} {link}')
                self.queue.put((link, level+1))
            if q.empty():
                break
        print('q for {} is empty'.format(i))
        q.task_done()

    def start(self):
        for i in range(self.threads):
            worker = Thread(target=self.crawl, args=(i,self.queue,))
            worker.setDaemon(True)
            worker.start()
        print(f'+TX {self.start_url}')
        self.urls.add(self.start_url)
        self.queue.put((self.start_url,0))
        print('waiting for q')
        self.queue.join()

if __name__ == "__main__":
    crawler = Crawler(argv[1])
    crawler.start()

