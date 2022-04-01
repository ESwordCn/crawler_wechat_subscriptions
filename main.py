import json
import os

import requests
from bs4 import BeautifulSoup
import PIL.Image as Image
from io import BytesIO


def write_img(file_path,img): #写文件
    with open(file_path, 'wb') as fd:
        fd.write(img)

def write_img_from_list(img_url_list,song_name): #根据url批量写入图片文件
    num=0
    for idx,img_url in enumerate(img_url_list,1):
        img = requests.get(img_url).content
        im = Image.open(BytesIO(img))
        if im.width < im.height:
            num += 1
            file_path = os.path.join(key, song_name + '_' + str(num) + '.jpg', )
            write_img(file_path,img)
    print(song_name+'：已爬取' + str(num) + '张图：')


def get_img_url(web_url): #从网页中获取图片url
    html = requests.get(web_url).text
    soup = BeautifulSoup(html, 'html.parser')

    imgs = soup.find_all(lambda x:x.has_attr('data-src') and x.has_attr('data-w') and x.name=='img' and x['data-w']!='' and int(x['data-w'])>1000)

    imgs_url_list = [imgs[i]['data-src'] for i in range(len(imgs))]
    return imgs_url_list


def get_article_list(web_url):#获取所有文章列表
    json_file_name = 'article_list.json'
    if os.path.exists(json_file_name):
        with open('article_list.json','r') as fp:
            return json.load(fp)

    ans = {}
    html = requests.get(web_url).text

    soup = BeautifulSoup(html, 'html.parser')
    result_set = soup.find_all('section', attrs={
        'style': 'padding-right: 0.6em;padding-bottom: 1em;padding-left: 0.6em;box-sizing: border-box;'})
    for result in result_set:
        category = result.find('span').text
        sub_result_set = result.find_all('a')
        article_list=[]
        for sub_result in sub_result_set:
            article_url = sub_result['href']
            song_name = sub_result.text
            song_name = song_name.split('》')[0].replace('《','')
            article_list.append({'name':song_name,'url':article_url})

        if len(article_list)!=0: ans[category] = article_list

    with open(json_file_name,'w') as fp:
        json.dump(ans,fp)

    return ans

if __name__ == '__main__':

    url = 'https://mp.weixin.qq.com/s/RQKeWQuOgtCnml-prMXC5w' #曲谱目录
    article_list = get_article_list(url)
    for key in article_list.keys():
        for article in article_list[key]:
            if not os.path.exists(key):os.mkdir(key)
            article_url = article['url']
            img_url_list = get_img_url(article_url)
            write_img_from_list(img_url_list,article['name'])



