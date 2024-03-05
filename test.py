import csv
import logging
import os
import psutil
import signal
import subprocess

import build_sqlite as b

TAGs_before = ['version-3.24.0', 'version-3.25.0', 'version-3.25.1', 'version-3.25.2', 'version-3.25.3',
               'version-3.26.0', 'version-3.27.0', 'version-3.27.1', 'version-3.27.2']
TAGs_after = ['version-3.29.0', 'version-3.30.0', 'version-3.30.1', 'version-3.31.0', 'version-3.31.0',
              'version-3.31.1', 'version-3.32.0', 'version-3.32.1', 'version-3.32.2', 'version-3.32.3',
              'version-3.33.0']


def read_sql_statements(sql_file):
    statements = []
    with open(sql_file, 'r') as file:
        lines = file.readlines()
        for l in lines:
            statement = l.rstrip().split(";")[0] + ";"
            if statement:
                statements.append(statement)
    file.close()
    return statements


def exec_case(test_case):
    """
    execute the test case
    :param test_case: absolute path of test case
    :return: -1: timeout
    """
    p = subprocess.Popen("sqlite3 < " + os.path.abspath(test_case), shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    pid = p.pid
    try:
        p.wait(timeout=60)
        stdout = p.stdout.read().decode().strip()
        stderr = p.stderr.read().decode().strip()
        retcode = p.returncode
    except Exception as ex:
        print('Error')
        print(f'{test_case}')
        '''
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        pids = [child.pid for child in children]
        for p in pids:
            os.kill(p, signal.SIGUSR1)
        '''
        stdout = ''
        stderr = '<error>'
        retcode = -1
    return stdout, stderr, retcode


def compare(stdout):
    results = stdout.split('\n')
    try:
        res = 'pass' if results[0] == results[1] else 'fail'
    except Exception as ex:
        print('======')
        print(stdout)
        res = 'compare_error'
    return res


def get_cases(cases_path):
    cases = []
    for root, dirs, files in os.walk(cases_path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                cases.append(file_path)
    return cases


def run(cases_path, versions, output_csv):
    test_cases = get_cases(cases_path)
    test_result = [[None] * len(versions) for _ in range(len(test_cases))]
    for version in versions:
        b.make_clean(REPO_SRC)
        b.build_from_tag(REPO_SRC, version)
        j = versions.index(version)
        for test_case in test_cases:
            i = test_cases.index(test_case)
            out, err, code = exec_case(test_case)
            if err != '<error>':
                res = compare(out)
            else:
                res = 'execute_error'
            test_result[i][j] = res
    write_csv(test_result, versions, [os.path.basename(c) for c in test_cases], output_csv)


def write_csv(data, row_header, column_header, output_file):
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([''] + row_header)
        for i in range(len(column_header)):
            row = [column_header[i]] + data[i]
            writer.writerow(row)
    file.close()


if __name__ == "__main__":
    REPO_SRC = '/root/sqlite'
    cases_path = '/root/code/cases/3.28.0/'
    versions = ['version-3.28.0']
    output_csv = '/root/code/3.28.0.csv'
    run(cases_path, versions, output_csv)
