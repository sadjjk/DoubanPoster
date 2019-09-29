import traceback
import requests
import logging
import random
import re


class MovieInfo():

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
        self.get_rate_detail()

    def check_url(self):

        r = requests.get(self.url)

        if r.status_code != 200:
            logging.error("该网页访问失败！请检查网址")
            exit(1)
        else:
            self._text = r.text

    def get_title(self):

        self.title_name = ''
        self.alias_name = ''
        try:
            self.title_name = ''.join(
                re.findall(r"property=\"v:itemreviewed\">(.*?)</span>.*?\"year.*?</h1>",
                           self._text,
                           re.S)[0])

            if len(self.title_name.split(' ',1)) > 1 :

                self.alias_name = self.title_name.split(' ',1)[1]
                self.title_name = self.title_name.split(' ', 1)[0]

        except BaseException:
            logging.warning('标题获取失败 默认为空')
            if self.show_detail_error:
                logging.warning('错误信息:' + traceback.format_exc())

    def get_describe(self):

        self.describe = ''

        try:
            info_pattern = re.compile(r'<div id="info">(.*?)</div>', re.S)

            movie_info = re.search(info_pattern, self._text).group(0)
            movie_time = re.search(r"片长:</span>.*?<span .*?>(.*?)</span><br/>",
                                   movie_info,
                                   re.S).group(1)

            movie_type = re.findall(r"<span property=\"v:genre\">(.*?)</span>", movie_info)

            directors = re.findall(r"<a href=.*? rel=\"v:directedBy\">(.*?)</a>", movie_info, re.S)

            actors = re.findall(r"<a href=.*? rel=\"v:starring\">(.*?)</a>", movie_info, re.S)

            releasedate = re.findall(r"<span property=\"v:initialReleaseDate\" content=.*?>(.*?)</span>", movie_info, re.S)

            self.describe = ' / '.join([movie_time,
                                        ' / '.join(movie_type),
                                        ' / '.join(['%s(导演)' % director for director in directors]),
                                        ' / '.join(actors[:5]),
                                        ' / '.join(releasedate)])
        except BaseException:
            logging.warning('别名和概述获取失败 默认为空')
            if self.show_detail_error:
                logging.warning('错误信息:' + traceback.format_exc())

    def get_bgimg_content(self):

        self.bgimg_content = ''
        try:
            bgimg_url = re.search(r"<a class=\"nbgnbg\".*?<img src=\"(.*?)\" title=\"点击看更多海报\".*?</a>",
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

        try:
            rate_star_pattern = re.compile(r"<div class=\"rating_self clearfix\" typeof=\"v:Rating\">(.*?)<div class=\"ratings-on-weight\">", re.S)
            rate_star_content = re.search(rate_star_pattern, self._text).group(1)
            self.rate = re.findall(r"property=\"v:average\">(.*?)</strong>", rate_star_content, re.S)[0]

            self.star_rate = re.findall(r"<div class=\"ll bigstar bigstar(\d+)\"></div>", rate_star_content)[0]
            self.rating_people = re.findall(r"<span property=\"v:votes\">(\d+)</span>人评价", rate_star_content)[0]
        except BaseException:
            logging.warning('评分获取失败 默认为空')
            if self.show_detail_error:
                logging.warning('错误信息:' + traceback.format_exc())

    def get_rate_detail(self):

        self.star_rate_details = []
        self.betterthan = []

        try:
            rate_detail_pattern = re.compile(r"<div class=\"ratings-on-weight\">(.*?)<div id=\"interest_sect_level\"", re.S)

            rate_detail_content = re.search(rate_detail_pattern, self._text).group(1)

            self.star_rate_details = re.findall(r"<span class=\"rating_per\">(.*?)%</span>", rate_detail_content)

            self.betterthan = re.findall(r"<a href=\"/typerank?.*?\">(.*?)</a><br/>", rate_detail_content)
            if self.betterthan:
                self.betterthan = ["好于 %s" % i for i in self.betterthan]
        except BaseException:
            logging.warning('评分详情获取失败 默认为空')
            if self.show_detail_error:
                logging.warning('错误信息:' + traceback.format_exc())



if __name__ == '__main__':

    movie_url = "https://movie.douban.com/subject/33383770/"
    # movie_url ="https://movie.douban.com/subject/27010768"
    movieinfo = MovieInfo(movie_url)

