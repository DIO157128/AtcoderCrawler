import json
import datetime
import json
import os
import re

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import requests
import tqdm
from bs4 import BeautifulSoup
from structures import Contest, Submission
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

due_time = "2023-01-01 00:00:00"
contest_id = ""


def signIn():
    service = Service(executable_path='chromedriver.exe')
    options = Options()
    # options.add_argument('--headless')  # 设置chrome浏览器无界面模式
    # 初始化浏览器
    driver = webdriver.Chrome(service=service, chrome_options=options)

    # 打开登录页面
    driver.get("https://atcoder.jp/login")

    # 输入用户名和密码
    username_field = driver.find_element(By.NAME, "username")
    username_field.clear()
    username_field.send_keys("ste1la")

    password_field = driver.find_element(By.NAME, "password")
    password_field.clear()
    password_field.send_keys("ybw064289")

    # 提交登录表单
    password_field.send_keys(Keys.RETURN)

    # 等待页面加载完成
    time.sleep(5)

    # 打印当前页面标题
    print(driver.title)
    return driver


def filterTime(due_time, given_time):
    if given_time >= due_time:
        return True
    else:
        return False


def getUrlContent(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, "
                      "like Gecko) Version/15.5 Safari/605.1.15",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200:
        s = BeautifulSoup(response.content, "html.parser")
        return s
    else:
        print("Error getting contests list!")


def getTestCaseListHtml(s):
    sub_1 = s.find('div', {'class': 'row'})
    sub_2 = sub_1.contents[3]
    tbody = sub_2.find('tbody')
    # 找到tbody中的所有tr标签
    trs = tbody.find_all('tr')
    href_list = []
    for tr in trs:
        tds = tr.find_all('td')
        href_list.append(tds[0].find("a").attrs["href"].split("/")[-1].strip())
    return href_list


def getSampleHtml(s):
    return s.contents[1].contents[3].text


def getTestCaseHtml(s, task_path):
    sub_1 = s.find('div', {'id': 'task-statement'})
    try:
        span = sub_1.contents[1].contents[3]
    except IndexError:
        return
    for i in span.contents:
        title = i.find("h3")
        if title != -1 and title is not None:
            pattern_input = r"Sample Input (\d+)"
            pattern_output = r"Sample Output (\d+)"
            pattern_input_jp = r"入力例 (\d+)"
            pattern_output_jp = r"入力例 (\d+)"
            if re.search(pattern_input, title.next) or re.search(pattern_input_jp, title.next):
                id = title.next.strip().split(" ")[-1]
                f1 = open(task_path + "/Input_{}.txt".format(id), 'a')
                f1.write(getSampleHtml(i))
                f1.close()
            elif re.search(pattern_output, title.next) or re.search(pattern_output_jp, title.next):
                id = title.next.strip().split(" ")[-1]
                f2 = open(task_path + "/Output_{}.txt".format(id), 'a')
                f2.write(getSampleHtml(i))
                f2.close()


def getContests():
    contest_list_url = "https://atcoder.jp/contests/archive"
    s = getUrlContent(contest_list_url)
    tbody = s.find('tbody')
    # 找到tbody中的所有tr标签
    trs = tbody.find_all('tr')
    contest_list = []
    for tr in trs:
        # 找到tr中的所有td标签
        tds = tr.find_all('td')
        # 遍历每个td标签，获取其中的文本内容
        time_td = tds[0]
        time = time_td.text
        time_obj = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S%z')
        time = time_obj.strftime('%Y-%m-%d %H:%M:%S')
        href_td = tds[1]
        href = href_td.find("a").attrs["href"]
        single_contest = Contest(time, href)
        contest_list.append(single_contest)
    filtered_list = list(filter(lambda x: filterTime(due_time, x.time), contest_list))
    return filtered_list


def getAllTestCases(href, driver):
    task_href = "https://atcoder.jp{}/tasks".format(href)
    driver.get(task_href)
    page_source = BeautifulSoup(driver.page_source, "html.parser")
    task_list = getTestCaseListHtml(page_source)
    contest_path = "AtCoderTestCases/" + href.split("/")[-1]
    os.mkdir(contest_path)
    for t in task_list:
        page_href = task_href + "/" + t
        driver.get(page_href)
        s = BeautifulSoup(driver.page_source, "html.parser")
        title = s.find('span', {'class': 'h2'}).text.strip().split("\n\t\t\t")[0]
        task_path = contest_path + "/" + title.split(" ")[0]
        os.mkdir(task_path)
        getTestCaseHtml(s, task_path)




if __name__ == "__main__":
    # 登录OJ
    driver = signIn()
    # #获取比赛列表
    contest_list = getContests()
    for c in contest_list:
        href = c.href
        contest_id = href.split("/")[-1].strip()
        getAllTestCases(href, driver)
