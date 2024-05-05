import subprocess
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

repo_path = "/home/uu613/workspace/z3"
csv_path = "/home/uu613/workspace/bugs/new_folder/tested_z3_bugs.csv"
result_path = "/home/uu613/workspace/bugs/new_folder/tested_z3_bugs_result.csv"
versions = ['z3-4.7.1-x64-ubuntu-16.04',
            'z3-4.8.1.016872a5e0f6-x64-ubuntu-16.04',
            'z3-4.8.3.7f5d66c3c299-x64-ubuntu-16.04',
            'z3-4.8.4.d6df51951f4c-x64-ubuntu-16.04',
            'z3-4.8.5-x64-ubuntu-16.04']
versions_to_commit = {'z3-4.7.1-x64-ubuntu-16.04': '3b1b82bef05a1b5fd69ece79c80a95fb6d72a990',
                      'z3-4.8.1.016872a5e0f6-x64-ubuntu-16.04': 'b301a59899ff401dc1a98dd522b8a8df19471dee',
                      'z3-4.8.3.7f5d66c3c299-x64-ubuntu-16.04': 'f9f83040278cdda4a92c69385387ff2a49799548',
                      'z3-4.8.4.d6df51951f4c-x64-ubuntu-16.04': 'c99a06a0bcb349eebf11fb147c8f3ccec3ecabf1',
                      'z3-4.8.5-x64-ubuntu-16.04': 'e79542cc689d52ec4cb34ce4ae3fbe56e7a0bf70'}


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
            output = output[:output.find('is the first bad commit')-1]
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
            good_version = versions_to_commit[induced_version]
            bad_version = versions_to_commit[bug_version]
            bug_result = row['result']
            logging.info(f"[finding BIC]Start bisecting {good_version}..{bad_version}")
            git_bisect_start(good_version, bad_version)
            target = find_bad_commit(row['Case-Filename'], bug_result, bic=True)
            git_bisect_reset()
            df.at[index, 'target_bic'] = target
        if fixed_version != '-1':
            # 把引入错误的版本作为好的版本，把修复错误的版本作为坏的版本
            # 这样可以定位到修复的commit
            good_version = versions_to_commit[bug_version]
            bad_version = versions_to_commit[fixed_version]
            bug_result = row['result']
            logging.info(f"[finding BFC]Start bisecting {good_version}..{bad_version}")
            git_bisect_start(good_version, bad_version)
            target = find_bad_commit(row['Case-Filename'], bug_result, bic=False)
            git_bisect_reset()
            df.at[index, 'target_bfc'] = target
    df.to_csv(result_path, index=False)
