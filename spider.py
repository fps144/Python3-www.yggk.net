
# 中国校花网的爬虫脚本(校花部分)
'''
1. 可以爬取校花模块的图，截止2017/9/13，可以爬到约950张
2. 下载路径在项目的根目录下
3. 分文件夹，按类存储图片
'''


# TODO 1. 单线程爬虫 -> 多线程爬虫
# TODO 2. 规范化代码格式
# TODO 3. 生成图片目录到 Excel 表格或 txt 文档中


import re
import requests
import os
import time
from bs4 import BeautifulSoup


BASE_URL = 'http://www.yggk.net'
img_count = 0

http_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
    'Upgrade-Insecure-Requests': 1,
    'Proxy-Connection': 'close',
    'Accept-Encoding': 'gzip, deflate',
    'Host': 'www.yggk.net'
}


def get_data(page):
    girl_url = 'http://www.yggk.net/xiaohua/xiaohua/list{}.html'
    data = requests.get(girl_url.format(page), stream=False).content.decode('gbk')
    return data


def image_downloader(url) -> list:
    base_url_str = url + 'index_{}.html'
    soup = BeautifulSoup(requests.get(url, stream=False).content.decode('gbk', 'ignore'), 'lxml')
    li_tag = soup.find_all('li')

    if len(li_tag) != 0 and len(li_tag[0].text) != 0 and len(re.findall(r'\d+', soup.find_all('li')[0].text)) != 0:
        total_page = re.findall(r'\d+', soup.find_all('li')[0].text)[0]
    else:
        total_page = str(1)
    result_list = []

    for index in range(1, int(total_page) + 1):
        url_a = ''
        if index == 1:
            url_a = url + 'index.html'
        else:
            url_a = base_url_str.format(str(index))
        content = requests.get(url_a, http_header, stream=False).content.decode('gbk', 'ignore')
        img_tag = BeautifulSoup(content, 'lxml').img

        if 'src' in str(img_tag):
            real_url = img_tag['src']
        else:
            continue
        # real_url = img_tag['src']
        # img_url = ''
        if BASE_URL not in real_url:
            img_url = BASE_URL + real_url
        else:
            img_url = real_url
        if BASE_URL + r'/' in img_url:
            result_list.append(requests.get(img_url).content)

        global img_count
        img_count += 1
        print(img_count)

        # print(img_url)
        # time.sleep(3)

    return result_list


def spider():
    try:
        s = requests.session()
        s.keep_alive = False
        s.mount(BASE_URL, adapter=5)
        total_page = int(re.findall(r'<strong>(.*?)</strong>',
                                requests.get('http://www.yggk.net/xiaohua/xiaohua/list1.html').content.decode(
                                    'gbk'))[0])
        for index in range(1, int(total_page) + 1):
            data = get_data(str(index))

            if data == None:
                break

            ul_str = re.findall(r'<ul class="product01 show">.*?</ul>', data, re.S)[0]
            name_list = re.findall(r'<p><b>(.*?)</b></p>|<p>(.*?)</p>', ul_str)
            real_name_list = []

            for name in name_list:
                if name[0] == '':
                    real_name_list.append(name[1])
                else:
                    real_name_list.append(name[0])

            url_list = re.findall(r"(?<=href=\").+?(?=\")", ul_str)
            datas = dict(zip(real_name_list, url_list))

            for data in datas:
                if not os.path.exists(r"./{}".format(data)):
                    os.mkdir(r'./{}'.format(data))

                images = image_downloader(datas[data])
                # print(data, '-', len(images), '-', datas[data])

                for index1 in range(1, len(images) + 1):
                    if data[-1] == ' ':
                        data = data[:-1]

                    file_path = r'./{}\{}.jpg'.format(data, str(index1))
                    # print(file_path)
                    open(file_path, 'wb').write(images[index1 - 1])

    except Exception as e:
        print(e)
