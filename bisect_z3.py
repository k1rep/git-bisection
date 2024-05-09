"""
This script is used to find the BIC and BFC of Z3 and cvc5 bugs.
The input is a csv file containing the information of Z3 and cvc5 bugs.
The output is a csv file containing the information of Z3 and cvc5 bugs and the BIC and BFC of each bug.
"""
import os.path
import subprocess
import pandas as pd
import logging
from utils.constants import Z3_VERSIONS_TO_COMMIT, CVC5_VERSIONS_TO_COMMIT

logging.basicConfig(level=logging.INFO)

z3_repo_path = "/home/uu613/workspace/z3"
z3_csv_path = "/home/uu613/workspace/bugs/new_folder/tested_z3_bugs.csv"
z3_result_path = "/home/uu613/workspace/bugs/new_folder/tested_z3_bugs_result.csv"
z3_case_path = "/home/uu613/workspace/bugs/new_folder"
cvc5_repo_path = "/home/uu613/workspace/cvc5"
cvc5_csv_path = "/home/uu613/workspace/cvc5_bugs/new_folder/tested_cvc5_bugs.csv"
cvc5_result_path = "/home/uu613/workspace/cvc5_bugs/new_folder/tested_cvc5_bugs_result.csv"
cvc5_case_path = "/home/uu613/workspace/cvc5_bugs/new_folder"


def run_test(case_filename, bug_result, bic, solver):
    """运行测试。"""
    """获取当前commit的哈希值，并截取前9位。"""
    repo_path = z3_repo_path if solver == 'z3' else cvc5_repo_path
    completed_process = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=repo_path)
    commit_hash = completed_process.stdout.strip()[:9]
    test_case = os.path.join(z3_case_path, case_filename) if solver == 'z3' \
        else os.path.join(cvc5_case_path, case_filename)
    test_command = f"/home/uu613/workspace/z3_commits/z3-{commit_hash} {test_case}" if solver == 'z3' \
        else f"/home/uu613/workspace/cvc5_commits/cvc5-{commit_hash} {test_case}"
    logging.info(f"Running test commit: z3-{commit_hash}") if solver == 'z3' \
        else logging.info(f"Running test commit: cvc5-{commit_hash}")
    result = subprocess.run(test_command, shell=True, capture_output=True, text=True)
    # 对于寻找BIC，测试结果不是bug的结果，则返回True
    # 对于寻找BFC，测试结果是bug的结果，则返回True
    output = result.stdout.strip() if solver == 'z3' else result.stdout.strip().split('\n')[-1]
    if bic:
        if output != bug_result:
            return True
        elif output == bug_result:
            return False
    else:
        if output == bug_result:
            return True
        elif output != bug_result:
            return False


def git_bisect_start(good, bad, solver):
    """初始化git bisect会话。"""
    repo_path = z3_repo_path if solver == 'z3' else cvc5_repo_path
    subprocess.run(['git', 'bisect', 'start'], cwd=repo_path)
    subprocess.run(['git', 'bisect', 'bad', bad], cwd=repo_path)
    subprocess.run(['git', 'bisect', 'good', good], cwd=repo_path)


def git_bisect_reset(solver):
    """结束git bisect会话，恢复到开始前的状态。"""
    repo_path = z3_repo_path if solver == 'z3' else cvc5_repo_path
    subprocess.run(['git', 'bisect', 'reset'], cwd=repo_path)


def find_bad_commit(case_filename, bug_result, bic, solver):
    """找到引入错误的提交。"""
    repo_path = z3_repo_path if solver == 'z3' else cvc5_repo_path
    while True:
        # 运行测试
        if run_test(case_filename, bug_result, bic, solver):
            # 如果测试通过，则当前提交是好的
            output = subprocess.check_output(['git', 'bisect', 'good'], text=True, cwd=repo_path)
        else:
            # 如果测试失败，则当前提交是坏的
            output = subprocess.check_output(['git', 'bisect', 'bad'], text=True, cwd=repo_path)

        if 'is the first bad commit' in output:
            # 保留第一个is前面的内容
            output = output[:output.find('is the first bad commit') - 1]
            return output


def find_bic_and_bfc(solver):
    csv_path = z3_csv_path if solver == 'z3' else cvc5_csv_path
    result_path = z3_result_path if solver == 'z3' else cvc5_result_path
    df = pd.read_csv(csv_path)
    df['target_bic'] = '-1'
    df['target_bfc'] = '-1'
    for index, row in df.iterrows():
        bug_version = row[df.columns[1]]
        bug_version = bug_version[:bug_version.find('/')]
        induced_version = row['induced_version']
        fixed_version = row['fixed_version']
        if induced_version != '-1':
            good_version = Z3_VERSIONS_TO_COMMIT[induced_version] if solver == 'z3' \
                else CVC5_VERSIONS_TO_COMMIT[induced_version]
            bad_version = Z3_VERSIONS_TO_COMMIT[bug_version] if solver == 'z3' else CVC5_VERSIONS_TO_COMMIT[bug_version]
            bug_result = row['result']
            logging.info(f"[finding BIC]Start bisecting {good_version}..{bad_version}")
            git_bisect_start(good_version, bad_version, solver=solver)
            target = find_bad_commit(row['Case-Filename'], bug_result, bic=True, solver=solver)
            git_bisect_reset(solver=solver)
            df.at[index, 'target_bic'] = target
        if fixed_version != '-1':
            # 把引入错误的版本作为好的版本，把修复错误的版本作为坏的版本
            # 这样可以定位到修复的commit
            good_version = Z3_VERSIONS_TO_COMMIT[bug_version] if solver == 'z3' \
                else CVC5_VERSIONS_TO_COMMIT[bug_version]
            bad_version = Z3_VERSIONS_TO_COMMIT[fixed_version] if solver == 'z3' \
                else CVC5_VERSIONS_TO_COMMIT[fixed_version]
            bug_result = row['result']
            logging.info(f"[finding BFC]Start bisecting {good_version}..{bad_version}")
            git_bisect_start(good_version, bad_version, solver=solver)
            target = find_bad_commit(row['Case-Filename'], bug_result, bic=False, solver=solver)
            git_bisect_reset(solver=solver)
            df.at[index, 'target_bfc'] = target
    df.to_csv(result_path, index=False)


if __name__ == '__main__':
    # find_bic_and_bfc(solver='z3')
    find_bic_and_bfc(solver='cvc5')
