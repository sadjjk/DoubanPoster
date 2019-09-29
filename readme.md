# 豆瓣书单分享海报(仿电影海报)

[Github](https://github.com/sadjjk/DoubanPoster) 

### 0x00前言

之前看到一张 豆瓣分享海报 感觉很不错

![哪吒之魔童降世.png](https://i.loli.net/2019/08/25/Vc72z9JuxgkKyEY.png)

应该是豆瓣官方的设计的 但是没找到分享的地方  
*PS:手机APP端分享的海报不是这样的*   
于是就想自己用Python画一个  
![哪吒之魔童降世_poster.png](https://i.loli.net/2019/08/25/F3vnwIjSNs6EKkM.png)

 自己画的是这样的  没有阴影 没有半圆分割 字体略不同 其他基本是一样的 基本满意   
等实现完所有细节 自我陶醉时  
在豆瓣网页端找到这张官方分享海报的地方  
评分右上角 点击 **引用** 即可导出官方分享海报图  
当场吐血 功能白做了 
好在 豆瓣书单是没有引用导出海报功能   
临时加需求 按照电影海报的亚子 绘制书单的分享海报
![房思琪的初恋乐园_poster.png](https://i.loli.net/2019/09/29/fh3KVSa8TECBIkD.png)

### 0x01 豆瓣爬虫

豆瓣电影/书单提供了相应的官方接口 但好像不够满足海报所需的数据 比如星星数
就写相应的爬虫获取相应的数据 这里不是详细阐述爬虫过程 具体见源码
假设相应的数据都已获得

### 0x02 开始绘图

Python画图主要使用的是PIL
二维码绘制使用 qrcode
海报主要分为3部分：①区背景图、 ②区标题和描述、③区评分及详情

#### **0.加载模板素材**

模板素材在imgs文件夹中 
一张豆瓣海报空白底版 三张不同状态的星星

```python
from PIL import Image

class DouBanPoster:

    def __init__(self):
        self.template_image = Image.open('imgs/template.jpg')
        self.star_yes_image = Image.open('imgs/star_yes.jpg')
        self.star_no_image = Image.open('imgs/star_no.jpg')
        self.star_mid_image = Image.open('imgs/star_mid.jpg')
```

之后所有信息都在template_image上进行绘制添加

#### 1. ①区背景图

自定义函数backgroundImg
参数 : bgImg (type:dict)
			 bgImgPath：背景图路径
			 postition：粘贴位置 默认(0,0)
			 size: 重置尺寸 默认(450,684)

把背景图放在在底版图上 `paste`即可

```python
def backgroudImg(self,bgImg):

  bgImgPath = bgImg.get('bgImgPath')
  postition = bgImg.get('postition')
  postition = postition if postition else (0,0)
  size = bgImg.get('size')
  size = size if size else  (450,684)
  if bgImgPath:
    bg_image = Image.open(bgImgPath).resize((size[0],size[1])) #重置大小
    self.template_image.paste(bg_image, postition)

```



#### 2.②区标题和描述

文本的绘制 使用`draw.text`
唯一要注意的是长文本
标题或描述可能会过长 超出绘制区域 无法自动换行
因此需要定义一个自动换行的函数
所有的可能过长的文本都调用此函数
自动换行功能使用textwrap.wrap
它会根据width自动换行
将换好的行 逐行绘制即可
PS:还有一个细节 一行一行绘制
累计高度可能会超过模板图片的高度
因此累计高度超出模板图片高度 break退出 不在绘制文本

```python
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
```

#### 3.③区评分及详情

- 评分数值 及评分人数 指定大小指定位置绘制即可
- 评分星星数 `star_rate` 35代表3.5颗星 40代表4颗星

```
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
```

- 好于XX% XX片 依然是文本 指定大小 指定位置 指定颜色 绘制即可

- 二维码 

  使用qrcode生成地址二维码
  因为模板非纯白色 所以在二维码边框增加模板颜色

  ```python
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
  ```

  将生成好的二维码 放在模板图片上
  处理逻辑和背景图一致

### 0x03 总结

run.py 传入豆瓣相应地址 即可一键生成海报

PS:因数据是按照网页结构即时抓取的 若豆瓣html相应结构发生变化 则会失效 故不保证永远有效

