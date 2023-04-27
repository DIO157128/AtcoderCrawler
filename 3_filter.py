import difflib
import os

import pandas as pd
import tqdm
import re

def count_token_diff(content1, content2):
    # 将文件1和文件2内容拆分为令牌列表
    tokens1 = content1.split()
    tokens2 = content2.split()

    # 使用SequenceMatcher计算两个文件之间的差异
    matcher = difflib.SequenceMatcher(None, tokens1, tokens2)
    diff_count = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace' or tag == 'delete' or tag == 'insert':
            # 计算差异令牌数量
            diff_count += max(i2 - i1, j2 - j1)

    return diff_count


def filter_comments(java_code):
    pattern = re.compile(r"(\".*?\"|'.*?')|(/\*.*?\*/|//.*?$)", re.DOTALL | re.MULTILINE)
    return pattern.sub(lambda match: match.group(1) or '', java_code)


def filterDf(path):
    df = pd.read_csv(path)
    print(df.shape[0])
    df = df.drop_duplicates(subset=df.columns[2:], keep='first')
    print(df.shape[0])
    df = df.dropna()
    print(df.shape[0])
    tasks = df["task"]
    set_task = set(tasks)
    res_user = []
    res_task = []
    res_language = []
    res_buggy = []
    res_fixed = []
    res_type = []
    for task in tqdm.tqdm(set_task):
        df_task = df[df['task'].str.contains(task)]
        task_users = df_task['user']
        set_task_user = set(task_users)
        for user in set_task_user:
            df_task_user = df_task[df_task['user'].str.contains(user)]
            df_user_AC = df_task_user[df_task_user['status'].str.contains("AC")]
            df_user_NOT_AC = df_task_user[~df_task_user['status'].str.contains("AC")]
            AC_code = df_user_AC["code"]
            NOT_AC_code = df_user_NOT_AC["code"]
            NOT_AC_status = df_user_NOT_AC["status"]
            code_pair = [(filter_comments(buggy), filter_comments(fixed), status) for buggy in NOT_AC_code for fixed in AC_code for status in
                         NOT_AC_status]
            code_pair_score = []
            for cp in code_pair:
                code_pair_score.append([cp, count_token_diff(cp[0], cp[1])])
            code_pair_score.sort(key=lambda x: x[1])
            for s in code_pair_score:
                if s[1] <= 6 and len(s[0][1].split())<=500:
                    res_user.append(user)
                    res_language.append("Java")
                    res_task.append(task)
                    res_buggy.append(s[0][0])
                    res_fixed.append(s[0][1])
                    res_type.append(s[0][2])
    df_res = pd.DataFrame()
    df_res["user"] = res_user
    df_res["task"] = res_task
    df_res["language"] = res_language
    df_res["buggy"] = res_buggy
    df_res["fixed"] = res_fixed
    df_res["type"] = res_type
    df_res.to_csv("Atcoder_data.csv", encoding='utf-8', index=False)
    print(df_res.shape[0])

def filterExistingContests(tests_path,file_path):
    df = pd.read_csv(file_path)
    df = df.drop_duplicates()
    df = df.dropna()
    tasks = df["task"]
    set_task = set(tasks)
    contests = sorted(set([x.split("/")[0] for x in set_task]))
    dirs = [d for d in os.listdir(tests_path) if os.path.isdir(os.path.join(tests_path, d))]
    non_exist = [x for x in contests if x not in dirs]
    for c in non_exist:
        df = df[~df['task'].str.contains(c)]
    df.to_csv("Atcoder_data.csv", encoding='utf-8', index=False)
    print(df.shape[0])
def concat(index, slice):
    df = pd.read_csv("atcoder_multi/AtCoder_raw_data_{}.csv".format(index))
    merge_df = df
    for i in range(slice):
        df_read = pd.read_csv("atcoder_multi/AtCoder_raw_data_{}_{}.csv".format(index, i))
        merge_df = pd.concat([merge_df, df_read], ignore_index=True)
    merge_df.to_csv("AtCoder_raw_data_{}.csv".format(index), encoding='utf-8', index=False)

def countAvTestCase(test_path):
    dirs = [d for d in os.listdir(tests_path) if os.path.isdir(os.path.join(tests_path, d))]
    count = 0
    tasks = 0
    for dir in dirs:
        tasks += len(os.listdir(tests_path+"/"+dir))
        for task in os.listdir(tests_path+"/"+dir):
            count+=len(os.listdir(tests_path+"/"+dir+"/"+task+"/in"))
    print(count/tasks)

if __name__ == '__main__':
    path = "AtCode_data/Atcoder_data.csv"
    # # filterDf(path)
    tests_path = "AtCoderTestCasesOfficial"
    file_path = path
    filterExistingContests(tests_path,file_path)
