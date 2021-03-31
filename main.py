import requests
import parsel
import re
import csv

"""
查询参数：
'ssdm': 'xx' 选择省市
dwmc:xx  直接选择单位
'mldm': 'xx' 门类  专科：zyxw
'yjxkdm': 'xxxx'  学科类别
zymc: 选择专业
xxfs: 1 全日制 2 非全日制
"""
first_post_page = 0
with open('data.csv', mode='w', encoding='utf-8', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(
        ['招生单位', '所在地', '研究生院', '自划线院校', '博士点',
         '考试方式', '院系所', '专业', '研究方向', '学习方式', '指导教师', '拟招生人数', '跨专业', '备注',
         '政治', '考试大纲', '英语', '考试大纲', '数学', '考试大纲', '专业课', '考试大纲',
         '政治', '考试大纲', '英语', '考试大纲', '数学', '考试大纲', '专业课', '考试大纲', ])

url = 'https://yz.chsi.com.cn/zsml/queryAction.do'

data = {
    'ssdm': '11',
    'dwmc': '',
    'mldm': '08',
    'mlmc': '',
    'yjxkdm': '0812',
    'zymc': '',
    'xxfs': '1',
    'pageno': str(first_post_page),
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
}

response = requests.post(url=url, data=data, headers=headers)
html_data = response.text
selector = parsel.Selector(html_data)

max_page_num = int(selector.css('.zsml-page-box li:nth-last-child(2) a::text').get())
print(max_page_num)

for page in range(1, max_page_num + 1):
    print(page)
    data = {
        'ssdm': '',
        'dwmc': '',
        'mldm': '08',
        'mlmc': '',
        'yjxkdm': '0801',
        'zymc': '',
        'xxfs': '',
        'pageno': str(page),
    }
    response = requests.post(url=url, data=data, headers=headers)
    html_data = response.text
    selector = parsel.Selector(html_data)
    trs = selector.css('.ch-table tbody tr')

    for tr in trs:
        temp_writer = []
        temp_all = []
        school = tr.css('a::text').get()
        school_url = 'https://yz.chsi.com.cn/' + tr.css('a::attr(href)').get()
        city = tr.css('td:nth-child(2)::text').get()
        statue_1 = tr.css('td:nth-child(3) i::text').get()
        if not statue_1:
            statue_1 = ''
        else:
            statue_1 = '是'
        statue_2 = tr.css('td:nth-child(4) i::text').get()
        if not statue_2:
            statue_2 = ''
        else:
            statue_2 = '是'
        statue_3 = tr.css('td:nth-child(5) i::text').get()
        if not statue_3:
            statue_3 = ''
        else:
            statue_3 = '是'
        print(school, city, statue_1, statue_2, statue_3)

        with open('data.csv', mode='a', encoding='utf-8', newline='') as file:
            file.write(school + ',' + city + ',' + statue_1 + ',' + statue_2 + ',' + statue_3 + ',')

        temp_subject_Information = []

        response = requests.get(url=school_url, headers=headers)
        selector = parsel.Selector(response.text)
        trs = selector.css('.ch-table tbody tr')

        extent = selector.css('.ch-table tbody tr td:nth-child(1)::text').getall()

        Number_of_studies = len(extent)
        control_number = 1

        for tr in trs:
            form = tr.css('td:nth-child(1)::text').get()
            faculty = tr.css('td:nth-child(2)::text').get()
            speciality = tr.css('td:nth-child(3)::text').get()
            Research_Direction = tr.css('td:nth-child(4)::text').get()
            Styles = tr.css('td:nth-child(5)::text').get()
            teacher = tr.css('td:nth-child(6)::text').get().strip()
            people = tr.css('td:nth-child(7) script::text').get()
            transdisciplinary = tr.css('td:nth-child(9) a::text').get()
            remark = tr.css('td:nth-child(10) script::text').get()
            # try:
            #     people = re.findall("专业：.*?',", people, re.S)[0]
            # except:
            #     try:
            #         people = re.findall("研究方向：.*?,", people, re.S)[0]
            #     except:
            #         try:
            #             people = re.findall("一级学科：.*?,", people, re.S)[0]
            #         except:
            #             people = re.findall("院系所：.*?,", people, re.S)[0]
            remark = eval(re.findall("cutString(.*?),", remark, re.S)[0].replace('(', ''))
            people: str
            people = people.split('cutString')[-1].replace("'", '').split(',')[0].strip("(")

            syllabus_url = 'https://yz.chsi.com.cn/' + tr.css('td:nth-child(8) a::attr(href)').get()
            print(form, faculty, speciality, Research_Direction, Styles, teacher, people, transdisciplinary, remark)

            temp_subject_Information.append(
                [form, faculty, speciality, Research_Direction, Styles, teacher, people, transdisciplinary, remark])

            response = requests.get(url=syllabus_url, headers=headers)
            selector = parsel.Selector(response.text)
            tds = selector.css('tbody.zsml-res-items td')
            for td in tds:
                politics = td.css('::text').get().strip()
                detail = td.css('span::text').get()
                print(politics, detail)

                temp_subject_Information.append([politics, detail])

            for i in temp_subject_Information:
                for k in i:
                    temp_writer.append(k)

            temp_subject_Information.clear()

            with open('data.csv', mode='a', encoding='utf-8', newline='') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(temp_writer)

            temp_writer.clear()

            # 决定是否写入新行
            if Number_of_studies == 1:
                pass
            else:
                if control_number == Number_of_studies:
                    pass
                else:
                    with open('data.csv', mode='a', encoding='utf-8', newline='') as file:
                        file.write('' + ',' + '' + ',' + '' + ',' + '' + ',' + '' + ',')
                    control_number += 1

        print('*' * 100)
