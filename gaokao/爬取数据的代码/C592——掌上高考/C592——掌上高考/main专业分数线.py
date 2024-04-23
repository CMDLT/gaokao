import time

import execjs
import requests
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
}


with open('掌上高考.js', 'r', encoding='utf-8') as fp:
    js_file = fp.read()
ctx = execjs.compile(js_file)

batch_dict = {
    '北京': '14',
}
pro_dict = {
    '北京': '11',
}
type_dict = {
    '北京': '3',
}
nameList = [
    '北京'
]

# local_batch_idList = [1570,]
# local_province_idList = [37,]
# local_type_idList = [3]
#
#

# 基本参数
page = 146
f = "D23ABC@#56"
data_dict = {
    "SIGN": f
}
size = 10
for name in nameList:
    print(name)
    years = [2019, 2020, 2021, 2022, 2023]
    for year in years:
        with open(f"Data2/{name}--{year}.csv", "w", newline="", encoding="UTF-8") as csvfile:
            writer = csv.writer(csvfile)
            # 先写入columns_name
            writer.writerow(["年份","学校", "专业名称", "录取批次", "平均分", "最低分/最低位次", "选科要求"])
        local_batch_id = batch_dict[name]
        local_province_id = pro_dict[name]
        # 都变成列表用于循环
        if year == 2019:
            local_type_id_list = [1, 2]
        else:
            local_type_id_list = [type_dict[name]]
        for local_type_id in local_type_id_list:
            for pn in range(1, page):
                print(pn)
                # 列表页参数
                j = f"api.zjzw.cn/web/api/?keyword=&page={pn}&province_id=&ranktype=&request_type=1&size=20&top_school_id=[3238]&type=&uri=apidata/api/gkv3/school/lists"
                signsafe = ctx.call('v', data_dict, j)
                url = f'https://api.zjzw.cn/web/api/?keyword=&page={pn}&province_id=&ranktype=&request_type=1&size=20&top_school_id=[3238]&type=&uri=apidata/api/gkv3/school/lists&signsafe={signsafe}'
                # 要是没有请求成功 就继续请求到成功为止
                while True:
                    try:
                        response = requests.get(url=url, headers=headers).json()
                        break
                    except:
                        print('重连')
                        time.sleep(3)
                items = response['data']['item']
                for item in items:
                    school_id = item['school_id']
                    hightitle = item['hightitle']
                    print("开始爬取id 为{} 学校名字为{}.... ".format(school_id,hightitle), end="\n")
                    # 详情页加密
                    ItemPage = 1
                    writerData = []
                    while True:
                        j = f'api.zjzw.cn/web/api/?local_batch_id={local_batch_id}&local_province_id={local_province_id}&local_type_id={local_type_id}&page={ItemPage}&school_id={school_id}&size=10&special_group=&uri=apidata/api/gk/score/special&year={year}'
                        numNowFound = ItemPage * size
                        signsafe = ctx.call('v', data_dict, j)
                        itemUrl = f'https://api.zjzw.cn/web/api/?local_batch_id={local_batch_id}&local_province_id={local_province_id}&local_type_id={local_type_id}&page={ItemPage}&school_id={school_id}&size=10&special_group=&uri=apidata/api/gk/score/special&year={year}&signsafe={signsafe}'
                        while True:
                            try:
                                itemResponse = requests.get(itemUrl, headers=headers).json()
                                break
                            except:
                                print('重连')
                                time.sleep(3)
                        numFound = itemResponse['data']['numFound']
                        if numFound == 0:
                            break
                        else:
                            sourceItems = itemResponse['data']['item']
                            for sourceItem in sourceItems:
                                # 年份
                                d0 = year
                                # 专业名称
                                d1 = sourceItem['spname']
                                # 录取批次
                                d2 = sourceItem['local_batch_name']
                                # 平均分
                                d3 = sourceItem['average']
                                # 最低分/最低位次
                                d4 = f"{sourceItem['min']}/{sourceItem['min_section']}"
                                # 选科要求 如果没有就是在sp里面
                                if year == 2019 and local_type_id == 1:
                                    d5 = '理科'
                                elif year == 2019 and local_type_id == 2:
                                    d5 = '文科'
                                else:
                                    d5 = f"{sourceItem['sg_info']}"
                                    if d5 == "":
                                        d5 = sourceItem['sp_info']
                                d = [d0,hightitle, d1, d2, d3, d4, d5]
                                writerData.append(d)
                            if numNowFound >= numFound:
                                break
                            ItemPage += 1
                    with open(f"Data2/{name}--{year}.csv", "a", newline="", encoding="UTF-8") as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerows(writerData)