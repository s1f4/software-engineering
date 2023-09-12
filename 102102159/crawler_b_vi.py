"""
102102159 李璐璐
日本核污染水排海视频弹幕分析挖掘
任务要求:
 数据获取
1.利用爬虫B站爬取所需弹幕数据，搜索关键词“日本核污染水排海”，爬取综合排序前300的所有视频弹幕

 数据统计
1.统计每种弹幕数量，并输出数量排名前20的弹幕
2.将统计的数据利用编程工具或开发包自动写入Excel表中

数据可视化
1.对采集的数据集进行可视化表示，制作词云图，越美观越好

数据结论
1.通过统计数据得出当前B站用户对于日本核污染水排海的主流看法

"""

import requests
import json
import re # 正则
import openpyxl # 实现所有的 Excel 功能
from collections import Counter# 统计弹幕
import matplotlib.pyplot as plt # 绘制并显示词云图
from wordcloud import WordCloud,STOPWORDS # 制作词云图
from PIL import Image # 添加蒙版图片需要使用PIL，numpy库
import numpy as np
import logging
import jieba

# 弹幕列表
danmu_list = []

url = "https://api.bilibili.com/x/web-interface/wbi/search/type?page_size=50&keyword=%E6%97%A5%E6%9C%AC%E6%A0%B8%E6%B1%A1%E6%9F%93%E6%B0%B4%E6%8E%92%E6%B5%B7&search_type=video"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69"
}
cookies = {
    "LIVE_BUVID": "AUTO4016261546844610",
    "dy_spec_agreed": "1",
    "i-wanna-go-back": "-1",
    "buvid_fp_plain": "undefined",
    "CURRENT_BLACKGAP": "0",
    "buvid3": "DB924180-3BD8-42B5-8BA2-4C8E6CD0802A148811infoc",
    "blackside_state": "0",
    "is-2022-channel": "1",
    "buvid4": "7FDFFDBD-4A05-CE5B-36F8-65644EF23BAA01057-022012119-AriTOoXUlusyf%2FPJFVaFQQ%3D%3D",
    "fingerprint3": "a5079b7c6bbff612db4a71d0b5309f09",
    "_uuid": "1895FF54-38108-F76E-425C-67F7D2649F2D79892infoc",
    "b_nut": "100",
    "rpdid": "|(k|ul)))|)J0J'uYY)l~~uku",
    "b_ut": "5",
    "CURRENT_PID": "6064c9b0-cd27-11ed-9166-4964fac53142",
    "nostalgia_conf": "-1",
    "hit-new-style-dyn": "1",
    "hit-dyn-v2": "1",
    "CURRENT_FNVAL": "4048",
    "FEED_LIVE_VERSION": "V8",
    "buvid_fp": "fa328c199106d855c503e19e77cfd2e5",
    "PVID": "5",
    "header_theme_version": "CLOSE",
    "CURRENT_QUALITY": "120",
    "fingerprint": "df225497cabdc8de8b5d4ffa4c5f3b07",
    "home_feed_column": "5",
    "b_lsid": "12946BB1_18A6F60043F",
    "browser_resolution": "1456-797",
    "sid": "4x0efj2f",
    "bp_video_offset_457472714": "838573964930318341"
}

# 获取弹幕
def get_danmu(bvid,headers):
    cid_url = "https://api.bilibili.com/x/web-interface/view?bvid=" + bvid
    cid_req = requests.get(cid_url, headers=headers) # 根据bvid获取cid请求
    cid_res = json.loads(cid_req.text)# 通过json.loads转换为对象
    cid = cid_res['data']['cid']

    danmu_url = "https://comment.bilibili.com/" + str(cid) + ".xml" # 弹幕链接
    danmu_req = requests.get(danmu_url, headers=headers)
    danmu_req.encoding = 'utf-8'
    danmu_list = re.findall('<d p=".*?">(.*?)</d>',danmu_req.text)# 正则表达式

    for index in danmu_list:
            print(index)
    return danmu_list

# 一个页面有30个视频，需要爬取300个视频，所以需要10页
for i in range(10):
    sess = requests.session()# requests.session()复用TCP
    req = sess.get(url + "&page=" + str(i+1), headers=headers, cookies=cookies)# 请求每一页的视频
    res = json.loads(req.text)# 通过json.loads转换为对象
    for video in res['data']['result']:
        danmu_list = danmu_list + get_danmu(video['bvid'],headers)

# 统计弹幕数量
danmu_count = Counter(danmu_list)
# 创建新的Excel表，写入统计结果
workbook = openpyxl.Workbook()
sheet = workbook.active
# 写入表头
sheet['A1'] = '弹幕'
sheet['B1'] = '数量'

# 写入数据
row = 2
for danmu,count in danmu_count.items():
    sheet[f'A{row}'] = danmu
    sheet[f'B{row}'] = count
    row += 1
# 获取数量排名前20的弹幕
top_20_count = danmu_count.most_common(20)
# 打印输出数量排名前20的弹幕
print("数量排名前20的弹幕：")
for danmu, count in top_20_count:
    print(f"{danmu}: {count}")
# 保存Excel表
workbook.save('danmu_statistics.xlsx')

# 将弹幕列表转换为字符串
text = ' '.join(danmu_list)

# 对文本进行中文分词
wc_list = jieba.lcut(text)

# 将分词结果转换为字符串
wc_text = ' '.join(wc_list)

# 设置停用词
stopwords = set(STOPWORDS)
stopwords.update(["的", "了", "和", "是", "在", "我", "你", "他", "她"])

# 加载背景图片
mask = np.array(Image.open("background_image.png")) # 打开遮罩图片,将图片转换为数组

# 创建词云对象
wc = WordCloud(width=800,height=400,font_path="C:\Windows\Fonts\STXINGKA.ttf",background_color='white', stopwords=stopwords, mask=mask, contour_width=1, contour_color='steelblue').generate(text)

# 绘制词云图


jieba.setLogLevel(logging.WARNING)
plt.figure(figsize=(10, 10))
plt.imshow(wc, interpolation='bilinear') # 用plt显示图片
plt.axis('off') # 不显示坐标轴
plt.show()
wc.to_file("wc_image.png")





