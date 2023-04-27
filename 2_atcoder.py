import json
import datetime
import json
import os
import random
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
from fake_useragent import UserAgent
import logging

#手动设置
required_language = "Java"
query = ""
if required_language !="":
    query = "?f.Task=&f.LanguageName={}&f.Status=&f.User=".format(required_language)
due_time = "2023-01-01 00:00:00"
process = 0
num_split = 4
contest_id = ""


def signIn():
    user_agent = UserAgent().chrome
    options = Options()
    # options.add_argument('--headless')  # 设置chrome浏览器无界面模式
    options.add_argument('--disable-images')
    options.add_argument('--disable-javascript')
    # options.add_argument('--proxy-server=http://127.0.0.1:7890')
    options.add_argument(f'user-agent={user_agent}')
    # 初始化浏览器

    driver = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=options)


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


def getSubmissionRecordHtml(s):
    sub_1 = s.find('div', {'class': 'row'})
    sub_2 = sub_1.contents[5]
    sub_3 = sub_2.contents[9]
    sub_4 = sub_3.contents[3]
    sub_table = sub_4.find('table', {'class': 'table table-bordered table-striped small th-center'})
    sub_tbody = sub_table.find("tbody")
    sub_trs = sub_tbody.find_all("tr")
    return sub_trs


def getSubmissionHtml(s):
    try:
        sub_1 = s.find('div', {'class': 'row'})
        sub_2 = sub_1.contents[3]
        sub_3 = sub_2.find('pre', {'id': 'submission-code'})
        code_snippets = sub_3.contents[0].contents
        code = ""
        for li in code_snippets:
            code += li.text + "\n"

        return code.replace(" ", "")
    except Exception:
        return ""


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
    span = sub_1.contents[1].contents[3]
    for i in span.contents:
        title = i.find("h3")
        if title != -1 and title is not None:
            pattern_input = r"Sample Input (\d+)"
            pattern_output = r"Sample Output (\d+)"
            if re.search(pattern_input, title.next):
                id = title.next.strip().split(" ")[-1]
                f1 = open(task_path + "/Input_{}.txt".format(id), 'a')
                f1.write(getSampleHtml(i))
                f1.close()
            elif re.search(pattern_output, title.next):
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


def getAllSubmissions(href, driver):
    submission_href = "https://atcoder.jp{}/submissions".format(href)+query
    submission_href_code = "https://atcoder.jp{}/submissions".format(href)
    driver.get(submission_href)
    page_source = BeautifulSoup(driver.page_source, "html.parser")
    try:
        sub_text_center = page_source.find('div', {'class': 'text-center'})
        sub_li = sub_text_center.find_all('li')
        # 获取最大页码
        max_page = (int)(sub_li[-1].string)
    except Exception:
        logging.error(submission_href)
        return []
    submission_list = []
    for i in tqdm.tqdm(range(1, max_page + 1)):
        page_href = submission_href + "&page={}".format(i)
        driver.get(page_href)
        s = BeautifulSoup(driver.page_source, "html.parser")
        try:
            sub_trs = getSubmissionRecordHtml(s)
        except Exception:
            logging.error(page_href)
            continue
        for tr in sub_trs:
            tds = tr.find_all('td')
            time_td = tds[0]
            time = time_td.text
            time_obj = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            time = time_obj.strftime('%Y-%m-%d %H:%M:%S')
            task = contest_id + "/" + tds[1].text.strip().split(" ")[0]
            user = tds[2].text
            language = tds[3].text.split("(")[0].strip()
            status = tds[6].text
            href = tds[-1].find("a").attrs["href"]
            submit_id = href.split("/")[-1]
            code_href = submission_href_code + "/" + submit_id
            driver.get(code_href)
            code_page = BeautifulSoup(driver.page_source, "html.parser")
            code = getSubmissionHtml(code_page)
            submission = Submission(time, task, user, language, status, code)
            submission_list.append(submission)

    return submission_list

def getAllSubmissionsExtra(href, driver):
    submission_href_code = href.split("?")[0]
    submission_list = []
    page_href = href
    driver.get(page_href)
    s = BeautifulSoup(driver.page_source, "html.parser")
    try:
        sub_trs = getSubmissionRecordHtml(s)
    except Exception:
        logging.error(page_href)
        return []
    for tr in sub_trs:
        tds = tr.find_all('td')
        time_td = tds[0]
        time = time_td.text
        time_obj = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        time = time_obj.strftime('%Y-%m-%d %H:%M:%S')
        task = contest_id + "/" + tds[1].text.strip().split(" ")[0]
        user = tds[2].text
        language = tds[3].text.split("(")[0].strip()
        status = tds[6].text
        href = tds[-1].find("a").attrs["href"]
        submit_id = href.split("/")[-1]
        code_href = submission_href_code + "/" + submit_id
        driver.get(code_href)
        code_page = BeautifulSoup(driver.page_source, "html.parser")
        code = getSubmissionHtml(code_page)
        submission = Submission(time, task, user, language, status, code)
        submission_list.append(submission)
    return submission_list

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

def persistance(submission_list,name):
    df = pd.DataFrame()
    time = []
    user = []
    task = []
    status = []
    language = []
    code = []
    for submit in submission_list:
        time.append(submit.time)
        user.append(submit.user)
        task.append(submit.task)
        status.append(submit.status)
        language.append(submit.language)
        code.append(submit.code)
    df["time"]=time
    df["user"]=user
    df["task"]=task
    df["status"] = status
    df["language"] = language
    df["code"] = code
    df.to_csv(name,encoding='utf-8',index=False)

def main_multi(i,split):
    global contest_id
    # 登录OJ
    # #获取比赛列表
    f = open("contests.txt", 'r')
    contest_list = f.read().splitlines()
    submission_list = []
    single_split = (int)(len(contest_list)/split)
    name = "Atcoder_raw_data_{}.csv".format(i)
    for i in range(single_split*i,single_split*(i+1)):
        href = contest_list[i]
        contest_id = href.split("/")[-1].strip()
        driver = signIn()
        submission_list += getAllSubmissions(href, driver)
        print("finished one contest")
        driver.quit()
        time.sleep(random.randrange(1,5))
    persistance(submission_list,name)
def main():
    global contest_id
    # 登录OJ
    # #获取比赛列表
    f = open("contests.txt", 'r')
    contest_list = f.read().splitlines()
    submission_list = []
    for c in tqdm.tqdm(contest_list):
        href = c
        contest_id = href.split("/")[-1].strip()
        driver = signIn()
        submission_list += getAllSubmissions(href, driver)
        print("finished one contest")
        driver.quit()
        time.sleep(random.randrange(1,5))
    persistance(submission_list,"Atcoder_raw_data.csv")
def extra_contest(href,name):
    global contest_id
    contest_id = href.split("/")[-1].strip()
    driver = signIn()
    submission_list = getAllSubmissions(href, driver)
    print("finished one contest")
    driver.quit()
    persistance(submission_list,name)
    time.sleep(random.randrange(1, 5))
def extra_page(path,name):
    global contest_id
    f= open(path,'r')
    hrefs = []
    for line in f.read().splitlines():
        hrefs.append(line.replace("ERROR:root:",""))
    submission_list = []
    driver = signIn()
    for href in tqdm.tqdm(hrefs):
        contest_id = href.split("/")[4].strip()
        submission_list+= getAllSubmissionsExtra(href,driver)
        print("finished one contest")
        time.sleep(random.randrange(1, 5))
    persistance(submission_list, name)
if __name__ == "__main__":
    #1 进行第一次爬取
    logging.basicConfig(filename='example{}.log'.format(process), level=logging.ERROR)
    main_multi(process,num_split)
    #2 爬取失败的比赛
    hrefs = []
    count = 0
    logging.basicConfig(filename='example{}_contest.log'.format(process), level=logging.ERROR)
    for href in hrefs:
        name = "AtCoder_raw_data_{}_{}.csv".format(process,count)
        count+=1
        extra_contest(href,name)
    #3 爬起失败的页面
    logging.basicConfig(filename='example{}_page.log'.format(process), level=logging.ERROR)
    extra_page("example{}.log","AtCoder_raw_data_XX_{}.csv".format(process,count))
