# py-web-crawler

```log
python crawler.py https://mikhail-yudin.ru/notes/ -d 2 -t 50
[200]  14496 B  936 ms /notes/
[200]  27782 B 1429 ms /notes/vim-poisk-po-tekstu-i-zamena/
[200]  44000 B 1336 ms /notes/mikrorazmetka-dlya-sayta/
[200]  26081 B 2835 ms /notes/dinamicheskaya-ikonka-sayta/
[200]  28785 B 2804 ms /notes/drebezg-kontaktov-klaviatury/
[200]  35107 B 2562 ms /notes/web-tipografika-dlya-razrabotchikov/
[200]  99694 B 1571 ms /notes/symbols-font-check/
[200] 321666 B 2803 ms /notes/emmet/
Total: 9 url(s)
```

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
