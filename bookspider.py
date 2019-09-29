import traceback
import requests
import logging
import random
import re


class BookInfo():

    def __init__(self, url, show_detail_error=False):

        self._UserAgents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:21.0) Gecko/20100101 Firefox/21.0",
            "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0"
        ]
        self.url = url
        self.show_detail_error = show_detail_error

        self.check_url()

        self.get_title()
        self.get_describe()
        self.get_bgimg_content()
        self.get_rate_star()

    def check_url(self):

        r = requests.get(self.url)

        if r.status_code != 200:
            logging.error("该网页访问失败！请检查网址")
            exit(1)
        else:
            self._text = r.text

    def get_title(self):

        self.title_name = ''
        try:
            self.title_name = ''.join(
                re.findall(r"property=\"v:itemreviewed\">(.*?)</span>.*?</h1>",
                           self._text,
                           re.S)[0])

        except BaseException:
            logging.warning('标题获取失败 默认为空')
            if self.show_detail_error:
                logging.warning('错误信息:' + traceback.format_exc())

    def get_describe(self):

        self.describe = ''
        self.alias_name = ''


        try:
            info_pattern = re.compile(r'<div id="info"(.*?)</div>', re.S)

            book_info = re.search(info_pattern, self._text).group(0)

            book_publish = re.search(r"<span class=\"pl\">出版社:</span>(.*?)<br/>", book_info)

            book_publish_time = re.search(r"<span class=\"pl\">出版年:</span>(.*?)<br/>", book_info)

            book_price = re.search(r"<span class=\"pl\">定价:</span>(.*?)<br/>", book_info)

            book_layout = re.search(r"<span class=\"pl\">装帧:</span>(.*?)<br/>", book_info)

            book_page = re.search(r"<span class=\"pl\">页数:</span>(.*?)<br/>", book_info)

            book_ISBN = re.search(r"<span class=\"pl\">ISBN:</span>(.*?)<br/>",book_info)

            describe = [i.group(1).strip() for i in [book_publish,
                                          book_publish_time,
                                          book_price,
                                          book_layout] if i]
            if book_page:
                    book_page = book_page.group(1).strip() + ' 页'

            if book_ISBN:
                    book_ISBN = 'ISBN-' + book_ISBN.group(1).strip()

            describe.extend([book_page,book_ISBN])

            self.describe = '  /  '.join(describe)
            book_authors = re.search(r"class=\"pl\".*?作者.*?</span>(.*?)</span>", book_info, re.S).group(1)

            book_author = [i.strip() for i in re.findall(r"<a .*?>(.*?)</a>", book_authors, re.S)]

            self.alias_name = ' / '.join(book_author)

        except BaseException:
            logging.warning('别名和概述获取失败 默认为空')
            if self.show_detail_error:
                logging.warning('错误信息:' + traceback.format_exc())

    def get_bgimg_content(self):

        self.bgimg_content = ''
        try:
            bgimg_url = re.search(r"<a class=\"nbg\".*?href=\"(.*?)\" title",
                                  self._text,
                                  re.S).group(1)
            # 增加UserAgent
            headers = {
                "user-agent": random.choice(self._UserAgents)}

            self.bgimg_content = requests.get(bgimg_url, headers=headers).content
        except BaseException:
            logging.warning('背景图获取失败 默认为空')
            if self.show_detail_error:
                logging.warning('错误信息:' + traceback.format_exc())

    def get_rate_star(self):
        self.rate = ''
        self.star_rate = 00
        self.rating_people = ''
        self.star_rate_details = ''
        self.betterthan = ''
        try:
            rate_star_pattern = re.compile(r"<div id=\"interest_sectl\" class=\"\">(.*?)<div id=", re.S)
            rate_star_content = re.search(rate_star_pattern, self._text).group(1)
            self.rate = re.search(r"property=\"v:average\">(.*?)</strong>", rate_star_content, re.S).group(1).strip()

            self.star_rate = re.search(r"<div class=\"ll bigstar(\d+)\"></div>", rate_star_content).group(1)
            self.rating_people = re.search(r"<span property=\"v:votes\">(\d+)</span>人评价", rate_star_content).group(1)

            self.star_rate_details = re.findall(r"<span class=\"rating_per\">(.*?)%</span>", rate_star_content)

        except BaseException:
            logging.warning('评分获取失败 默认为空')
            if self.show_detail_error:
                logging.warning('错误信息:' + traceback.format_exc())


if __name__ == '__main__':

    book_url = "https://book.douban.com/subject/33446318"
    bookinfo = BookInfo(book_url)
