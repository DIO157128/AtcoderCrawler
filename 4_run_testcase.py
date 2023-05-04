import glob
import os
import subprocess

import pandas as pd


def cleanFiles(name):
    java_files = glob.glob('{}.*'.format(name))
    # 删除所有文件
    for file_path in java_files:
        os.remove(file_path)


# 返回的是一个字典，内容是关键字+信息
# CE：编译错误，信息为编译时的报错信息，不运行测试用例
# AC 通过，信息为通过的测试用例数/总共测试用例数
# WA 有错误答案，信息为通过的测试用例数/总共测试用例数
# RE 运行时错误,信息为运行时报错信息
# TLE 超时
# MLE 内存不够
# NT 没有测试用例，信息为0/0
# memory限制了执行时运行的内存使用大小，以mb为单位，只要数字
def run_test_case(code, task, memory, time):
    path_to_test_case = "AtCoderTestCasesOfficial/" + task
    input_files = os.listdir(path_to_test_case + "/in")
    output_files = os.listdir(path_to_test_case + "/out")
    f_java = open("Main.java", 'a', encoding='utf-8')
    f_java.write(code)
    f_java.close()
    compile_result = subprocess.run(['javac', '-J-Dfile.encoding=UTF8', 'Main.java'], capture_output=True, text=True,
                                    encoding='utf-8')
    assert len(input_files) == len(output_files)
    if compile_result.returncode != 0:
        print("Compilation Error!")
        cleanFiles("Main")
        return {'CE': compile_result.stderr}
    if len(input_files) == 0:
        print("No testcase to run!")
        cleanFiles("Main")
        return {'NT': "0/0"}
    else:
        num_test_case = (int)(len(input_files))
        count = 0
        for input_file, output_file in zip(input_files, output_files):
            input_path = path_to_test_case + "/in/" + input_file
            output_path = path_to_test_case + "/out/" + output_file
            input = open(input_path, 'r').read()
            expect_output = open(output_path, 'r').read()
            # 运行Java代码并向标准输入流中传递数据
            process = subprocess.Popen(['java', '-Xmx{}m'.format(memory), 'Main'], stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            try:
                actual_output, errors = process.communicate(input=input.encode('utf-8'), timeout=time)
            except subprocess.TimeoutExpired:
                print("Time Limit Exceed Error!")
                cleanFiles("Main")
                return {'TLE': 'Timeout!'}
            if errors.decode('utf-8') != '':
                if 'Invalid maximum heap size' in errors.decode('utf-8'):
                    print('Memory Limit Exceed')
                    cleanFiles("Main")
                    return {'MLE': errors.decode('utf-8')}
                else:
                    print("Runtime Error!")
                    cleanFiles("Main")
                    return {'RE': errors.decode('utf-8')}
            if actual_output.decode(encoding='utf-8').strip() == expect_output.strip():
                count += 1
            else:
                print("One testcase failed!")
                print(expect_output)
                print(actual_output.decode(encoding='utf-8'))
        if count == num_test_case:
            print("All testcases passed!")
            cleanFiles("Main")
            return {'AC': "{}/{}".format(count, count)}
        else:
            print("Passed {}/{} testcases".format(count, num_test_case))
            cleanFiles("Main")
            return {'WA': "{}/{}".format(count, num_test_case)}


if __name__ == '__main__':
    code = '''
import java.util.HashMap;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);
        HashMap<Integer,Character> map = new HashMap<>();
        map.put(8,'h');
        map.put(7,'g');
        map.put(6,'f');
        map.put(5,'e');
        map.put(4,'d');
        map.put(3,'c');
        map.put(2,'b');
        map.put(1,'a');
        for (int i =8; i >0; i--) {
            String s = in.nextLine();
            for (int j = 0; j < s.length() ; j++) {
                char c = s.charAt(j);
                if(c=='*') {
                    System.out.print(map.get(j+1));
                    System.out.print(i);
                }
            }
        }
    }
}


'''
    task = "abc296/B"
    print(run_test_case(code, task, 1,0.00001))
