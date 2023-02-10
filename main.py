"""
Project: Parse Coins (on aiohttp 3.8.3, Python 3.10)

File: main

Version: 2.9
"""

import asyncio
import pprint
import aiohttp

from lxml.html import etree
from random import choice


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

        self.data: dict = {}
        self.p: etree.HTMLParser = etree.HTMLParser()
        self.web_sites: zip = zip(web_sites_labels, to_find_on_web_site, urls)

    async def parser(self, html: str, to_find: str) -> list:
        """

        :param html: str
        :param to_find: str,
        :return: list
        """

        tree: etree.HTML = etree.HTML(html, parser=self.p)
        objects: list = tree.xpath(to_find)

        return objects

    @staticmethod
    async def fetch(session: aiohttp.ClientSession, url: str) -> str:
        """

        :param session: new aiohttp.ClientSession,
        :param url: str of URL to parse
        :return: str of response – HTML page
        """

        async with session.get(url) as response:
            return await response.text(encoding="utf-8")

    async def start_session(self, to_find: str, url: str) -> list[str]:
        """
        Instantiate new session

        :param to_find: str,
        :param url: str,
        :return: list of strings
        """

        async with aiohttp.ClientSession(headers=choice(self.HEADERS)) as session:
            html: str = await self.fetch(session, url)

            return await self.parser(html, to_find)

    async def pages(self) -> None:
        """
        Collect data to object property "data"

        :return: None
        """

        for web_site, to_find_XPATH, this_url in self.web_sites:
            self.data[web_site]: list[str] = await self.start_session(to_find=to_find_XPATH,
                                                                      url=this_url)

    @staticmethod
    def convert(arg: bytes, source: str) -> str:
        """

        :param arg: bytes of etree.tostring() to be converted to string value,
        :param source: string value – label of web_site,
        :return: string value
        """

        arg: str = str(arg, encoding="utf-8")
        x: str = arg[arg.find(">") + 1:arg.find("</")]
        to_find: str = """data-bn-type="link" href="/en/trade/"""
        ind: int = x.find(to_find) + len(to_find)

        if "binance" in source:
            return x[ind:x.find("?")] if to_find in x else ""
        else:
            return x

    def main(self) -> dict[str, set]:
        """
        Main function

        :return: tuple of two sets – for each key listed in self.__init__
        """

        asyncio.run(self.pages())

        for key in self.data:
            self.data.update({key: set(map(lambda x: self.convert(etree.tostring(x),
                                                                  source=key),
                                           self.data[key]))})

        return self.data


if __name__ == "__main__":
    # Currently, Coinmarketcap fails to be parsed
    # It is only here as proof-of-concept

    new_app_instance = App(web_sites_labels=("binance_listed", "coinmarketcap"),
                           to_find_on_web_site=("""//div[@class="css-vlibs4"]""",
                                                """//*[@class="sc-1eb5slv-0 gGIpIK coin-item-symbol"]"""),
                           urls=("https://www.binance.com/en/markets/newListing",
                                 "https://coinmarketcap.com/new/"))
    result = new_app_instance.main()

    pprint.pprint(result)
