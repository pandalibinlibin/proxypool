import requests
import re
from proxypool.db import RedisClient
import logging
from parsel import Selector


class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        # Initialize an empty list to store crawl function names
        __CrawlFunc__ = []
        for key, value in attrs.items():
            if key.startswith("crawl_"):
                __CrawlFunc__.append(key)
        # Add the list of crawl function names to the class attributes
        attrs["__CrawlFunc__"] = __CrawlFunc__
        # Add the count of crawl functions to the class attributes
        attrs["__CrawlFuncCount__"] = len(__CrawlFunc__)
        return super().__new__(cls, name, bases, attrs)


class Getter(object, metaclass=ProxyMetaclass):
    def __init__(self):
        self.redis = RedisClient()

    def is_over_threshold(self):
        """
        Check if the number of proxies in the proxy pool exceeds the threshold
        to prevent infinite crawling.
        """
        # Assume the threshold is 100, you can adjust it according to your needs
        threshold = 5000
        count = self.redis.count()
        return count >= threshold

    def run(self):
        """
        Traverse and call all crawler methods starting with 'crawl_',
        and add the obtained proxies to Redis.
        """
        if not self.is_over_threshold():
            for func in self.__CrawlFunc__:
                logging.info(f"Running {func}...")
                proxies = getattr(self, func)()
                if proxies:
                    for proxy in proxies:
                        self.redis.add(proxy)

    def crawl_kuaidaili(self, pages=3):
        """
        Crawl free proxies from https://www.kuaidaili.com/free/inha
        :param pages: Number of pages to crawl
        :return: Generator of proxies in the format 'ip:port'
        """
        base_url = "https://www.kuaidaili.com/free/inha/{}/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        for page in range(1, pages + 1):
            url = base_url.format(page)
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    selector = Selector(text=response.text)
                    trs = selector.css("#list table tbody tr")
                    for tr in trs:
                        ip = tr.css("td:nth-child(1)::text").get()
                        port = tr.css("td:nth-child(2)::text").get()
                        if ip and port:
                            yield f"{ip}:{port}"
            except requests.RequestException as e:
                logging.info(f"Error crawling {url}: {e}")

    def crawl_ip3366(self, pages=3):
        """
        Crawl free proxies from http://www.ip3366.net/free/
        :param pages: Number of pages to crawl
        :return: Generator of proxies in the format 'ip:port'
        """
        base_url = "http://www.ip3366.net/free/?stype=1&page={}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        for page in range(1, pages + 1):
            url = base_url.format(page)
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    selector = Selector(text=response.text)
                    trs = selector.css("#list table tbody tr")
                    for tr in trs:
                        ip = tr.css("td:nth-child(1)::text").get()
                        port = tr.css("td:nth-child(2)::text").get()
                        if ip and port:
                            yield f"{ip}:{port}"
            except requests.RequestException as e:
                logging.info(f"Error crawling {url}: {e}")

    def crawl_89ip(self, pages=3):
        """
        Crawl free proxies from https://www.89ip.cn/
        :param pages: Number of pages to crawl
        :return: Generator of proxies in the format 'ip:port'
        """
        base_url = "https://www.89ip.cn/index_{}.html"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        for page in range(1, pages + 1):
            url = base_url.format(page) if page > 1 else "https://www.89ip.cn/"
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    selector = Selector(text=response.text)
                    trs = selector.css("table.layui-table tr:not(:first-child)")
                    for tr in trs:
                        ip = tr.css("td:nth-child(1)::text").get().strip()
                        port = tr.css("td:nth-child(2)::text").get().strip()
                        if ip and port:
                            yield f"{ip}:{port}"
            except requests.RequestException as e:
                logging.info(f"Error crawling {url}: {e}")

    def crawl_freeserial(self, pages=3):
        """
        Crawl free proxies from https://free-proxy-list.net/zh-cn/
        :param pages: Number of pages to crawl
        :return: Generator of proxies in the format 'ip:port'
        """
        base_url = "https://free-proxy-list.net/zh-cn/?page={}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        for page in range(1, pages + 1):
            url = base_url.format(page)
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    selector = Selector(text=response.text)
                    trs = selector.css("#proxylisttable tbody tr")
                    for tr in trs:
                        ip = tr.css("td:nth-child(1)::text").get()
                        port = tr.css("td:nth-child(2)::text").get()
                        if ip and port:
                            yield f"{ip}:{port}"
            except requests.RequestException as e:
                logging.info(f"Error crawling {url}: {e}")


if __name__ == "__main__":
    # Initialize and run the getter
    getter = Getter()
    getter.run()
