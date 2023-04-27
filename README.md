# README
## 数据集爬取
按照顺序运行即可，multi是多进程

AtCoder_data/AtCoder_raw_data.csv是未配对的数据

AtCoder_data/AtCoder_data.csv是配对的数据，即用来测试的数据

## 运行测试用例
程序入口在4_run_testcase.py里，函数传入task名称和具体代码
## 比赛编号说明
在AtCoderTestCases/里有例如abc284的文件夹，这个编号是比赛的代码，如果需要查看详细比赛信息，访问https://atcoder.jp/contests/abc284并将最后一个替换为需要的即可
AtCoderTestCasesOfficial/是从官网上下载的测试用例
## 注意
4_run_testcase.py有时候会在运行fixed时出现CE，但是第二次就可以了，不知道为什么。