import pandas as pd
import re
import javalang
import json

from transformers import RobertaTokenizer


def remove_comments(code):
    # 删除单行注释
    code = re.sub(r'//.*', '', code)
    # 删除多行注释
    code = re.sub(r'/\*(.*?)\*/', '', code, flags=re.DOTALL)
    return code
def removespace(code):
    lines = code.split('\n')

    # 去除每行代码开头的空格
    trimmed_lines = [line.lstrip() for line in lines]

    # 将处理后的代码连接成一个字符串
    trimmed_code = '\n'.join(line for line in trimmed_lines if line.strip() != '')
    return trimmed_code
def tokenize(code):
    tokens = javalang.tokenizer.tokenize(code)

    tokenized_code = ''
    for token in tokens:
        tokenized_code += token.value + ' '
    return tokenized_code
def transToken():
    df = pd.read_csv("latest_contests_new.csv")
    source = df["source"]
    target = df["target"]
    s = []
    t = []
    for i in source:
        s.append(removespace(remove_comments(i)))
    for i in target:
        s.append(removespace(remove_comments(i)))
    df["source"] = s
    df["target"] = t
    df.to_csv("atcoder.csv", index=False)
def tokenlenstat():
    tokenizer = RobertaTokenizer.from_pretrained("Salesforce/codet5-base")
    df = pd.read_csv("atcoder.csv")
    sources = df['source']
    tokenlen = []
    over = []
    for source in sources:
        s = tokenizer.encode(source, truncation=True,return_tensors='pt').numpy().tolist()[0]
        tokenlen.append(len(s))
        if len(s)>=512:
            over.append(1)
    print(sum(tokenlen)/len(tokenlen))
    print(len(over))
if __name__ == '__main__':
    with open('../raw_predictions/codet5.json') as file:
        data = json.load(file)
    print(data)
    # tokenlenstat()


