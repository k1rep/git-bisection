import subprocess


csv_path = "/home/uu613/workspace/bugs/new_folder/tested_z3_bugs.csv"
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


def run_test():
    """运行测试脚本并返回测试是否通过。"""
    try:
        subprocess.check_output(['./test_script.sh'], stderr=subprocess.STDOUT)
        return True  # 测试通过
    except subprocess.CalledProcessError:
        return False  # 测试失败


def git_bisect_start(bad, good):
    """初始化git bisect会话。"""
    subprocess.run(['git', 'bisect', 'start'])
    subprocess.run(['git', 'bisect', 'bad', bad])
    subprocess.run(['git', 'bisect', 'good', good])


def git_bisect_reset():
    """结束git bisect会话，恢复到开始前的状态。"""
    subprocess.run(['git', 'bisect', 'reset'])


def find_bad_commit():
    """找到引入错误的提交。"""
    while True:
        # 运行测试
        if run_test():
            # 如果测试通过，则当前提交是好的
            subprocess.run(['git', 'bisect', 'good'])
        else:
            # 如果测试失败，则当前提交是坏的
            subprocess.run(['git', 'bisect', 'bad'])

        # 检查是否已经找到坏的提交
        output = subprocess.check_output(['git', 'bisect', 'visualize'], text=True)
        if 'is the first bad commit' in output:
            return output


if __name__ == '__main__':
    import pandas as pd
    df = pd.read_csv(csv_path)
    df['target_bic'] = '-1'
    df['target_bfc'] = '-1'
    for index, row in df.iterrows():
        bug_version = row[df.columns[1]]
        induced_version = row['induced_version']
        fixed_version = row['fixed_version']
        if induced_version != '-1':
            good_version = versions_to_commit[induced_version]
            bad_version = versions_to_commit[bug_version]
            git_bisect_start(bad_version, good_version)
            target = find_bad_commit()
            git_bisect_reset()
            df.at[index, 'target_bic'] = target
        if fixed_version != '-1':
            good_version = versions_to_commit[bug_version]
            bad_version = versions_to_commit[fixed_version]
            git_bisect_start(bad_version, good_version)
            target = find_bad_commit()
            git_bisect_reset()
            df.at[index, 'target_bfc'] = target
