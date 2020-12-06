import requests
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime
import json
import os
from docx import Document
#导入尺寸类,颜色，字体大小
from docx.shared import Inches,Pt,RGBColor
#d对齐方式
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docxtpl import DocxTemplate
from docxcompose.composer import Composer
# from collections import Counter    #查找重复数据

url = 'https://www.xiachufang.com/cook/126271064/created/?page='
root_path = r'C:\Users\Administrator\Desktop\Python学习\Spider\food'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3823.400 QQBrowser/10.7.4307.400',
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'www.xiachufang.com',
    'Referer': 'https://www.xiachufang.com/cook/126271064/created/'
}
simple_header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
}

class xiachufang():
    def __init__(self,link,root_path):
        self.link = link
        self.headers = headers
        self.path = root_path    #root path
        self.html_path = r'../output/html'
        # print(self.html_path)
    
    def get_page_content(self):
        print('开始爬下厨房菜单\n')
        title = []
        link = []
        homepage = 'https://www.xiachufang.com'
        for i in range(1, 26):
            self.link = url + str(i)
            res = requests.get(self.link, headers=self.headers)
            print('网站链接为：{0}\n爬到的返回状态为{1}\n'.format(self.link, res.status_code))
            print("开始解析数据\n")
            content = BeautifulSoup(res.text, parser='html.parser', features="lxml")
            foods = content.find_all(class_="cover")  # 使用cover更精准
            for food in foods:
                title.append(food.find('a')['title'])
                link.append(homepage+food.find('a')['href'])
            #爬完一个网站后,等0.2s再爬下一个网站
            sleep(0.2)
            with open(r'../data/food.html', 'ab+') as f:
                f.write(res.content)
            print('write success\n')
        # print(Counter(title))    #可用于检验重复的菜名
        d = dict(zip(title, link))
        j = json.dumps(d,ensure_ascii=False,indent=4)
        with open(r'../data/link.json','w',encoding='utf-8') as f:
            f.write(j)
        print('write json success\n')
        print('下厨房菜单爬取完毕')
        print("菜名和对应的网页链接解析完毕\n")
        sleep(1)

    def download_one_page(self,title,link):
        self.headers['Referer'] = link
        res = requests.get(link,headers=self.headers)
        with open(self.path+'\output\html\{}.html'.format(title),'wb') as f:
            f.write(res.content)
            print('{}下载成功'.format(title))

    def download_all_page(self):
        with open('../data/link.json', 'rb') as f:
            filejson = json.load(f)
        # print(type(filejson))
        # print(filejson)
        for k,v in filejson.items():
            self.download_one_page(k,v)
            sleep(0.5)  # 延时0.2s,可以成功，不会封
        print('所有页面下载成功')

    def walkFile(self):
        for root, dirs, files in os.walk(self.html_path):
            for f in files:
                if f.endswith('.html'):
                    fullname = os.path.join(root, f)
                    yield fullname

    def parser_one_page(self,file):
        with open(file,'rb') as f:
            soup = BeautifulSoup(f,parser='html.parser',features="lxml")
        title = soup.find('h1',class_='page-title').text
        title = title.strip()
        sub_food = soup.find(class_="ings")
        des = sub_food.find_all('a')
        weight = sub_food.find_all(class_="unit")
        steps = soup.find_all('p',class_="text")
        picture = soup.find(class_="cover image expandable block-negative-margin")
        picture_link = picture.find('img')['src']
        #图片下载到本地并保存
        pic = requests.get(picture_link, headers=simple_header)
        with open(self.path+'\output\word\{}.jpg'.format(title),'wb') as f:
            f.write(pic.content)
        name = []
        unit = []
        step = ''
        table_str = ''
        for n in des :
            name.append(n.text)
        for w in weight:
            unit.append(w.text.strip())
        table = dict(zip(name, unit))
        #对字典的访问，请加上items
        for k,v in table.items():
            if k in list(table.items())[-1]:
                table_str = table_str + k + v + '。'
            else:
                table_str = table_str+k+v+'、'
        #添加操作步骤
        count = 0
        for item in steps:
            count = count + 1
            step = step +str(count)+'.'+ item.text +'\n'
        #写入单个world里面
        data_dic = {'t1':title,'t2':table_str,'t3':step}
        document = DocxTemplate(r'../data/菜谱模板.docx')
        document.render(data_dic)    #替换这类文字{{title}}
        #不需要加上后缀名，只需要填写图片 1就行
        document.replace_pic('图片 1',r'../output/word/{}.jpg'.format(title))
        document.save(self.path+'\output\word\{}.docx'.format(title))

    def parser_all_page(self):
        for i in self.walkFile():
            print('当前解析文件为:'+i)
            self.parser_one_page(i)

class docx_handler():
    def __init__(self,path,filetype,final_docx):
        self.path = path
        self.filetype = filetype
        self.final_docx = final_docx

    def get_filename(self):
        file_name = []
        for root, dirs, files in os.walk(self.path):
            for f in files:
                if self.filetype + ' ' in f + ' ':
                    fullname = os.path.join(root, f)
                    file_name.append(fullname)
        return file_name

    def merge_all_docx(self):
        files = self.get_filename()
        print(files)
        #打开鸡公煲文件，这样复制粘贴的时候发型不会乱！！！
        new_document = Document(r'../data/“佛跳墙”土鸡煲.docx')
        composer = Composer(new_document)
        for fn in files:
            composer.append(Document(fn))
            print('成功添加 {}'.format(fn))
        composer.save(self.final_docx)

if __name__ == '__main__':
    print('下厨房爬虫开始运行,开始时间:')
    print(datetime.now())
    xcf = xiachufang(url,root_path)
    xcf.get_page_content()
    xcf.download_all_page()
    xcf.parser_all_page()
    doc = docx_handler(r'../output/word','docx',r'../output/下厨房懒饭菜谱合集.docx')
    doc.merge_all_docx()
    print('下厨房爬虫运行结束,结束时间:')
    print(datetime.now())
