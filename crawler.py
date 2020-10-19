import re, requests
from time import sleep
from sys import argv

class Crawler:
    def __init__(self, start_url, deep = 3):
        self.start_url = start_url
        self.urls = set()
        self.deep = deep
        self.link_compiled_regexp = re.compile(r'href="?([^" >]+)[" >]')

    def get_links(self, url):
        try:
            response = requests.get(url)
            elapsed_ms = round(response.elapsed.microseconds / 1000)
            print('[{}] {}ms: {}'.format(response.status_code,elapsed_ms,url))
            html = response.content.decode('utf-8')
            return self.link_compiled_regexp.findall(html)
        except:
            return []

    def crawl(self, url, level = 1):

        if url in self.urls:
            return

        if level > self.deep:
            return


        sleep(0.025)
        self.urls.add(url)

        links = self.get_links(url)

        for link in links:
            if link.startswith(self.start_url):
                self.crawl(link)
            elif (not link.startswith('//')) and link.startswith('/'):
                self.crawl(self.start_url + link, level + 1)

    def start(self):
        self.crawl(self.start_url)

if __name__ == "__main__":
    crawler = Crawler(argv[1])
    crawler.start()

