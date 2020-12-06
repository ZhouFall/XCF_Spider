


1.查看最后的输出文件，json只有743个数据，少了7个，排查思路如下
2.网站链接是25页，一页是30个，一共750个，从保存的html文件里搜索div，数量相符
3.排查res部分，加上打印，每个foods打印count
4.排除掉这部分之后，怀疑是zip函数的问题，内存不够用，丢数据了
5.换成itertools额izip，报错找不到izip，查看源码，方法换成了zip_longest
6.打印之后，发现还是少了几位
7.怀疑是list变成dict的时候，有重复数据，怎么找出这个重复数据？
8.>>> from collections import Counter
    >>> Counter([1,2,2,2,2,3,3,3,4,4,4,4])
    Counter({1: 5, 2: 3, 3: 2})
9.真相大白
    Counter({'鸡蛋汉堡': 3, '红茶芝士蛋糕': 2, '香菇鸡腿焖饭': 2, '圆白菜蟹棒烩豆腐': 2, '烂蒜肥肠': 2, '快手番茄锅': 2, '鲜虾干蒸烧卖': 1,

print(len(title))
print(len(link))
# xyz = itertools.zip(title, link)
# print(xyz)
d = dict(itertools.zip_longest(title, link))
# print(d)
print(len(d))

word常用的方法有add_heading, add_paragraph,add_table

##### 在替换word中图片时遇到问题，总是报错图片找不到，学会解析docx的xml文件很有用
1.使用的方法为：document.replace_pic('图片 1',r'../output/word/{}.jpg'.format(title))
2.删除原来模板里的图片，重新上传pic.jpg图片，图片名字使用pic.jpg不行
3.参考网上的教程，将docx文件后缀名改为.zip，然后解压，查看xml文件，发现word,media下面有image1.jpg
  尝试使用image1.jpg作为文件名，还是失败
4.查看document.xml文件，找到  <w:drawing>标签，发现图片名字是'图片 1'
  使用图片 1.jpg/jpeg，都不行
5.最后直接使用图片 1，成功。

##### 合并所有文件到一个文件的时候，先打开一个模板文件，这样格式不会乱
