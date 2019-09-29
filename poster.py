from PIL import Image, ImageDraw, ImageFont
import textwrap
import qrcode
import os


class DouBanPoster:

    def __init__(self):

        self.template_image = Image.open('imgs/template.jpg')
        self.star_yes_image = Image.open('imgs/star_yes.jpg')
        self.star_no_image = Image.open('imgs/star_no.jpg')
        self.star_mid_image = Image.open('imgs/star_mid.jpg')

        self.draw = ImageDraw.Draw(self.template_image)

        # 圆角图片
        self.circleCorderImage = True

    def getFontSize(self,size,bd=False):

        if bd == True:
                return ImageFont.truetype("font/msyh.ttc", size)
        return ImageFont.truetype("font/msyhl.ttc", size)



    # 长文本换行
    def draw_longtext(self,draw, item_describe, postition, pad_h,font_size,width,text_color = "#000000",bd=False):
        # 换行

        para = textwrap.wrap(item_describe, width=width)

        for line in para:
            w, h = draw.textsize(line, font=self.getFontSize(font_size,bd=bd))

            draw.text(postition, line, text_color, font=self.getFontSize(font_size,bd=bd))
            postition[1] += h + pad_h # 增加行间距

            # 超过模板高度 停止
            if postition[1]+ h+pad_h > self.template_image.size[1]:
                break

        return  postition[1]

    # 二维码
    def make_QR(self,content, sizeW, sizeH):  # 创建二维码

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(data=content)
        qr.make(fit=True)
        img = qr.make_image(back_color="#fafbfc")
        img = img.resize((sizeW, sizeH))
        return img

    # 海报图片圆角
    def circle_corder_image(self,rad = 30):

        circle = Image.new('L', (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
        alpha = Image.new('L', self.template_image.size, 255)
        w, h =self.template_image.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        self.template_image.putalpha(alpha)



    def backgroundImg(self,bgImg):

        bgImgPath = bgImg.get('bgImgPath')
        postition = bgImg.get('postition')
        postition = postition if postition else (0,0)
        size = bgImg.get('size')
        size = size if size else  (450,684)
        if bgImgPath:
            bg_image = Image.open(bgImgPath).resize((size[0],size[1]))
            self.template_image.paste(bg_image, postition)


    def titleAndDescribe(self,titledescribe):

        # 标题
        title_name = titledescribe['title']['name']
        title_postition = titledescribe['title'].get('postition')
        title_postition = title_postition if title_postition else [480,70] # 标题默认位置480,70
        title_H = self.draw_longtext(self.draw, title_name,
                                     postition=title_postition,
                                     pad_h=15, font_size=60,
                                     width=8,bd=True)

        # 别名
        alias = titledescribe.get('alias')
        if alias:
            alias_name = titledescribe['alias'].get('name')
            alias_postition = titledescribe['alias'].get('postition')
            alias_postition = alias_postition if alias_postition else [480, title_H]
            alias_H = self.draw_longtext(self.draw, alias_name,
                                         postition=alias_postition, pad_h=0,
                                         font_size=38,width=20,text_color="#bbb9ba",bd=True)


        # 描述
        describe  = titledescribe.get('describe')
        if describe:
            # self.draw.text((480,alias_H+20),textwrap.fill(self.draw,width=50),"#000000",self.getFontSize(30))
            self.draw_longtext(self.draw, describe,
                               postition=[480,alias_H+20],
                               pad_h=15,font_size=30,width=30)



    def rateAndDescribe(self,ratedescribe):

        # 豆瓣评分文字 固定位置
        self.draw.text((1137, 48), '豆', font=self.getFontSize(27))
        self.draw.text((1190, 48), '豆瓣评分', "#67b967", font=self.getFontSize(27))

        # 评分数值、人数评价

        if ratedescribe:

            rate_index=  1115
            rate = str(ratedescribe.get('rate'))
            if rate:
                self.draw.text((rate_index, 132), rate, "#000000", font=self.getFontSize(90,bd=True))

            rating_people = str(ratedescribe.get('rating_people'))
            # rating_people_index = 1130
            if rating_people:
                rating_people_index = rate_index + 145
                self.draw.text((rating_people_index, 195), '%s人评价' % rating_people, "#000000", self.getFontSize(25))
            else:
                rating_people_index = rate_index + 130
                self.draw.text((rating_people_index, 195), '尚未上映' , "#000000", self.getFontSize(25))
            # 星星数
            star_rate = str(ratedescribe.get('star_rate'))
            if star_rate:
                for i in range(5):
                    if i < int(star_rate) // 10:
                        self.template_image.paste(self.star_yes_image, (rating_people_index + i * 30, 160))
                    elif str(star_rate)[1] == '5' and i == int(star_rate) // 10:
                        self.template_image.paste(self.star_mid_image, (rating_people_index + i * 30, 160))
                    else:
                        self.template_image.paste(self.star_no_image, (rating_people_index + i * 30, 160))


            # 评价详情
            star_rate_details = ratedescribe.get('star_rate_details')
            if star_rate_details:
                for index, score in enumerate(star_rate_details):
                    score = float(score)
                    self.draw.text((1120, 270 + 40 * index), "%d星" % (5 - index), "#000000", self.getFontSize(30))
                    self.draw.rectangle((1180, 283 + 40 * index, 1180 + int(240 * score / 100), 296 + 40 * index), "#f4ae4b")
                    self.draw.text((1180 + int(240 * score / 100) + 10, 272 + 40 * index), str(score) + "%", "#000000",
                              self.getFontSize(26))

            betterthan = ratedescribe.get("betterthan")
            if betterthan:
                for index, betterone in enumerate(betterthan):
                    self.draw.text((1120, 500 + index * 40), betterone.split(" ")[0], "#000000", self.getFontSize(26))
                    self.draw.text((1180, 500 + index * 40), betterone.split(" ")[1], (65,190,87), self.getFontSize(26,bd=True))
                    self.draw.text((1240, 500 + index * 40), betterone.split(" ")[2], "#000000", self.getFontSize(26))

        else:
            self.draw.text((1115, 185), '暂无评分' , "#bbb9ba", self.getFontSize(25))
            for i in range(5):
                self.template_image.paste(self.star_no_image, (1115 + i * 30, 150))


    def urlQRimg(self,urlinfo):

        # 制作二维码

        url  = urlinfo['url']
        size = urlinfo.get('size')
        postition  = urlinfo.get('postiton')
        if size:
            sizeW = size[0],sizeH = size[1]
        else:
            sizeW = 125
            sizeH = 125

        postition = postition if postition else [1360,480]


        QR_img = self.make_QR(url,sizeW, sizeH)
        self.template_image.paste(QR_img, postition)


    def savePoster(self,save_img_name,saveDirPath ='imgs'):

        if self.circleCorderImage:
            self.circle_corder_image()

        if not os.path.exists(saveDirPath):
            os.mkdir(saveDirPath)

        self.template_image.save(os.path.join(saveDirPath,'%s_poster.png' % save_img_name),quality = 100)


if __name__ == '__main__':


    dbposter =DouBanPoster()
    dbposter.backgroundImg({"bgImgPath":"imgs/哪吒之魔童降世(2019)_bgImg.jpg"}
                           )
    dbposter.titleAndDescribe({"title":{"name":"哪吒之魔童降世"},
                               "alias":{"name":"哪吒降世 / Ne Zha"},
                               "describe":"110分钟 /  剧情 / 喜剧 / 动画 / 奇幻 / 饺子(导演) / 吕艳婷 / 囧森瑟夫 / 瀚墨 / 陈浩 / 绿绮  / 2019-07-26(中国大陆) / 2019-07-13(大规模点映) "
                               })
    dbposter.rateAndDescribe({"rate":"8.6",
                              "rating_people":775253,
                              "star_rate":35,
                              "star_rate_details":[45.8,39.1,12.9,1.7,0.5],
                              "betterthan":['好于 89% 动画片','好于 97% 喜剧片']})

    dbposter.urlQRimg({"url":"https://movie.douban.com/subject/26794435/?from=playing_poster"})

    dbposter.template_image.show()
