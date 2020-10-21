# py-web-crawler

## Dependencies installation

```sh
pip install -r requirements.txt
```

## Usage

### Basic

```sh
python crawler.py https://mikhail-yudin.ru
```

### With options

```sh
usage: crawler.py [-h] [-d DEPTH] [-t THREADS_COUNT] [-u USER_AGENT] URL

Web crawler.

positional arguments:
  URL               address to start crawl from

optional arguments:
  -h, --help        show this help message and exit
  -d DEPTH          crawl depth (default: 5)
  -t THREADS_COUNT  threads count (default: 10)
  -u USER_AGENT     user agent (default: Mozilla/5.0 (compatible;
                    pycrawlbot/1.0))
```

Dependencies: [requirements.txt](https://github.com/fagcinsk/py-web-crawler/blob/main/requirements.txt)
