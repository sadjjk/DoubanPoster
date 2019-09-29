from moviespider import MovieInfo
from bookspider import  BookInfo
from poster import DouBanPoster
from io import BytesIO
import  logging
import  re


def main(url):

    if re.search(r"https://movie.douban.com/subject/.+?",url):

        doubaninfo = MovieInfo(url)
    elif re.search(r"https://book.douban.com/subject/.+?",url):
        doubaninfo = BookInfo(url,show_detail_error=True)

    else:
        logging.error("网址不符合要求 请输入如下样式:\n"
                      "电影:https://movie.douban.com/subject/xxxxx\n"
                      "书籍:https://book.douban.com/subject/xxxxx")
        exit(1)

    dbposter = DouBanPoster()

    dbposter.backgroundImg({"bgImgPath": BytesIO(doubaninfo.bgimg_content)}
                          )

    dbposter.titleAndDescribe({
        "title": {"name": doubaninfo.title_name},
        "alias": {"name": doubaninfo.alias_name},
        "describe": doubaninfo.describe
    })

    dbposter.rateAndDescribe({"rate": doubaninfo.rate,
                              "rating_people": doubaninfo.rating_people,
                              "star_rate": doubaninfo.star_rate,
                              "star_rate_details": doubaninfo.star_rate_details,
                              "betterthan": doubaninfo.betterthan
                              })

    dbposter.urlQRimg({"url": doubaninfo.url})

    # dbposter.template_image.show()

    dbposter.savePoster(doubaninfo.title_name)


if __name__ == '__main__':

    # main('https://movie.douban.com/subject/26794435/?from=playing_poster')
    main('https://book.douban.com/subject/27614904/')



