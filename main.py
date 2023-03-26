"""
Project: Parse Coins (on aiohttp 3.8.3, Python 3.10)

File: main
"""

import asyncio
import aiohttp
import time
import random

from lxml.html import HtmlElement, document_fromstring
from decimal import Decimal, getcontext

# 6 digits precision
getcontext().prec = 6


class App:
    HEADERS = [{'User-Agent':
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:45.0) Gecko/20100101 '
                    'Firefox/45.0'},
               {'User-Agent':
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/51.0.2704.103 Safari/537.36'},
               {'User-Agent':
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36 OPR/38.0.2220.41'},
               {'User-Agent':
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'},
               {'User-Agent':
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 '
                    '(KHTML, like Gecko) Version/13.1.1 Safari/604.1'}]

    def __init__(self, web_sites_labels: tuple | list,
                 to_find_on_web_site: tuple | list, urls: tuple | list) -> None:
        """
        Object initializer
        """

        self.connector: aiohttp.TCPConnector | None = None
        self.data: dict = {key: [] for key in web_sites_labels}
        self.session: aiohttp.ClientSession | None = None
        self.web_sites: list = list(zip(web_sites_labels, to_find_on_web_site, urls))

    @staticmethod
    async def parser(html: str, to_find: str) -> list[HtmlElement]:
        """

        :param html: str
        :param to_find: str,
        :return: list
        """

        tree: HtmlElement = document_fromstring(html)
        objects: list[HtmlElement] = tree.xpath(to_find)

        return objects

    async def fetch(self, url: str) -> str:
        """

        :param url: str of URL to parse
        :return: str of response – HTML page
        """

        # Let's try and avoid caching, which is a huge problem
        new_url = f"{url}?timestamp={int(time.time())}?random={random.randint(0, 100)}"
        # --------------------------------------------

        async with self.session.get(new_url) as response:
            return await response.text()

    async def pages(self, url: str, to_find: str) -> list:
        """
        Collect data and parse html

        :return: None
        """

        html: str = await self.fetch(url)

        return await self.parser(html, to_find)

    async def get_hourly_max(self, current_time: int, data_key: str) -> Decimal | bool:
        out = False
        try:

            # Only keep last hour data to save memory, since no other instructions available
            self.data[data_key] = list(filter(lambda x: x[0] > current_time - 3600,
                                              self.data[data_key]))
            # ------------------------------------------------------------------------------

            out = max(map(lambda x: x[1], self.data[data_key]))

        except ValueError:
            pass

        finally:
            return out

    @staticmethod
    async def strip_string_by_separator(string: str, sep: str) -> str:
        return string.split(sep)[0]

    async def main(self) -> None:
        """
        Main function

        :return: tuple of two sets – for each key listed in self.__init__
        """

        self.connector = aiohttp.TCPConnector(use_dns_cache=False, force_close=True)

        async with aiohttp.ClientSession(headers=random.choice(self.HEADERS),
                                         connector=self.connector,
                                         connector_owner=False) as session:

            print("[START] Started collecting data")
            self.session = session

            while True:
                for web_site, to_find_tag, this_url in self.web_sites:
                    result = await self.pages(to_find=to_find_tag,
                                              url=this_url)
                    to_show_result = Decimal(await self.strip_string_by_separator(result[0].text_content(), " |"))
                    current_t = int(time.time())
                    self.data[web_site].append((current_t, to_show_result))

                    if m := await self.get_hourly_max(current_t, web_site):
                        if (m - to_show_result) / m > 0.01:
                            print("[MESSAGE] Current price is 1% lower than hourly max")

                    print(f"[+] Last price: {to_show_result} for {web_site} at {current_t} UTC")


if __name__ == "__main__":
    # To test multiple
    # new_app_instance_dict = {"web_sites_labels": ("binance_futures", "binance_futures2",),
    #                          "to_find_on_web_site": ("//head/title", "//head/title",),
    #                          "urls": ("https://www.binance.com/en/futures/XRPUSDT",
    #                                   "https://www.binance.com/en/futures/BNBUSDT",)}
    new_app_instance_dict = {"web_sites_labels": ("XRP/USDT",),
                             "to_find_on_web_site": ("//head/title",),
                             "urls": ("https://www.binance.com/en/futures/XRPUSDT",)}

    new_app_instance = App(**new_app_instance_dict)
    try:
        asyncio.run(new_app_instance.main())

    except (KeyboardInterrupt,
            RuntimeError) as error:
        print(error)

    finally:
        print("[+] Closing loop")
        print("[END]")
