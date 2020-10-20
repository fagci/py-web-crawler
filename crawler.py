import argparse, re, requests
from urllib.parse import urlparse
from queue import Queue
from threading import Thread, Lock

class Crawler:
    def __init__(self, base_url, deep = 5, threads = 10):
        self.base_url = base_url
        self.deep = deep
        self.threads = threads
        self.urls = set()
        self.lock = Lock()
        self.queue = Queue()

        base_parsed = urlparse(base_url)

        self.base_scheme = base_parsed.scheme
        self.base_netloc = base_parsed.netloc

        self.link_compiled_regexp = re.compile(r'href="?([^" >]+)[" >]')

    def get_links_from_page(self, url):
        try:
            response = requests.get(url, timeout = 10)
            elapsed_ms = round(response.elapsed.microseconds / 1000)
            html = response.content.decode('utf-8')
            p_url = urlparse(url)
            print(f'[{response.status_code}]({len(html):>6}) {elapsed_ms}ms: {p_url.path}')
            return map(self.normalize_url,self.link_compiled_regexp.findall(html))
        except Exception as e:
            # print('exception:', e)
            return []

    def normalize_url(self, url):
        if url.startswith('//'):
            url = f'{self.base_scheme}:{url}'
        elif url.startswith('/'):
            url = '{self.base_scheme}://{self.base_netloc}{url}'
        return url

    def manage_url(self, url, level):
        if level > self.deep or not url.startswith(self.base_url):
            return False
        self.lock.acquire()
        if url in self.urls:
            self.lock.release()
            return False
        self.urls.add(url)
        self.lock.release()
        self.queue.put((url, level))
        return True

    def crawl(self, i, q):
        while True:
            url, level = q.get()

            for link_from_page in self.get_links_from_page(url):
                self.manage_url(link_from_page, level + 1)

            q.task_done()

    def start(self):
        for i in range(self.threads):
            worker = Thread(target=self.crawl, args=(i,self.queue,))
            worker.setDaemon(True)
            worker.start()
        self.urls.add(self.base_url)
        self.queue.put((self.base_url,1))
        self.queue.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Web crawler.')

    parser.add_argument('url', metavar='URL', help='address to start crawl from')
    parser.add_argument('-d', type=int, default=5, help='crawl depth (default: 5)')
    parser.add_argument('-t', type=int, default=10, help='threads count (default: 10)')

    args = parser.parse_args()

    crawler = Crawler(args.url, args.d, args.t)
    crawler.start()

    print(f'Total: {len(crawler.urls)} url(s)')

