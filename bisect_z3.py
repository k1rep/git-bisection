"""
This script is used to find the BIC and BFC of Z3 bugs.
The input is a csv file containing the information of Z3 bugs.
The output is a csv file containing the information of Z3 bugs and the BIC and BFC of each bug.
"""
import subprocess
import pandas as pd
import logging
from utils.constants import VERSIONS_TO_COMMIT

logging.basicConfig(level=logging.INFO)

repo_path = "/home/uu613/workspace/z3"
csv_path = "/home/uu613/workspace/bugs/new_folder/tested_z3_bugs.csv"
result_path = "/home/uu613/workspace/bugs/new_folder/tested_z3_bugs_result.csv"


def run_test(case_filename, bug_result, bic):
    """运行测试。"""
    """获取当前commit的哈希值，并截取前9位。"""
    completed_process = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=repo_path)
    commit_hash = completed_process.stdout.strip()[:9]
    test_case = '/home/uu613/workspace/bugs/new_folder/' + case_filename
    test_command = f"/home/uu613/workspace/z3_commits/z3-{commit_hash} {test_case}"
    logging.info(f"Running test commit: z3-{commit_hash}")
    result = subprocess.run(test_command, shell=True, capture_output=True, text=True)
    # 对于寻找BIC，测试结果不是bug的结果，则返回True
    # 对于寻找BFC，测试结果是bug的结果，则返回True
    if bic:
        if result.stdout.strip() != bug_result:
            return True
        elif result.stdout.strip() == bug_result:
            return False
    else:
        if result.stdout.strip() == bug_result:
            return True
        elif result.stdout.strip() != bug_result:
            return False


def git_bisect_start(good, bad):
    """初始化git bisect会话。"""
    subprocess.run(['git', 'bisect', 'start'], cwd=repo_path)
    subprocess.run(['git', 'bisect', 'bad', bad], cwd=repo_path)
    subprocess.run(['git', 'bisect', 'good', good], cwd=repo_path)


def git_bisect_reset():
    """结束git bisect会话，恢复到开始前的状态。"""
    subprocess.run(['git', 'bisect', 'reset'], cwd=repo_path)


def find_bad_commit(case_filename, bug_result, bic):
    """找到引入错误的提交。"""
    while True:
        # 运行测试
        if run_test(case_filename, bug_result, bic):
            # 如果测试通过，则当前提交是好的
            output = subprocess.check_output(['git', 'bisect', 'good'], text=True, cwd=repo_path)
        else:
            # 如果测试失败，则当前提交是坏的
            output = subprocess.check_output(['git', 'bisect', 'bad'], text=True, cwd=repo_path)

        if 'is the first bad commit' in output:
            # 保留第一个is前面的内容
            output = output[:output.find('is the first bad commit') - 1]
            return output


if __name__ == '__main__':
    df = pd.read_csv(csv_path)
    df['target_bic'] = '-1'
    df['target_bfc'] = '-1'
    for index, row in df.iterrows():
        bug_version = row[df.columns[1]]
        bug_version = bug_version[:bug_version.find('/')]
        induced_version = row['induced_version']
        fixed_version = row['fixed_version']
        if induced_version != '-1':
            good_version = VERSIONS_TO_COMMIT[induced_version]
            bad_version = VERSIONS_TO_COMMIT[bug_version]
            bug_result = row['result']
            logging.info(f"[finding BIC]Start bisecting {good_version}..{bad_version}")
            git_bisect_start(good_version, bad_version)
            target = find_bad_commit(row['Case-Filename'], bug_result, bic=True)
            git_bisect_reset()
            df.at[index, 'target_bic'] = target
        if fixed_version != '-1':
            # 把引入错误的版本作为好的版本，把修复错误的版本作为坏的版本
            # 这样可以定位到修复的commit
            good_version = VERSIONS_TO_COMMIT[bug_version]
            bad_version = VERSIONS_TO_COMMIT[fixed_version]
            bug_result = row['result']
            logging.info(f"[finding BFC]Start bisecting {good_version}..{bad_version}")
            git_bisect_start(good_version, bad_version)
            target = find_bad_commit(row['Case-Filename'], bug_result, bic=False)
            git_bisect_reset()
            df.at[index, 'target_bfc'] = target
    df.to_csv(result_path, index=False)
