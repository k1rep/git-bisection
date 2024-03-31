import logging
import subprocess
from datetime import datetime

import pandas as pd

logging.basicConfig(level=logging.INFO)


def build_from_tag(repo_src, tag):
    log_file = 'build_tag.log'
    password = '123123'
    command = 'make install'
    with open(log_file, 'a') as log:
        git_result = subprocess.check_output(f'git checkout {tag}', shell=True, cwd=repo_src)
        log.write(f'git checkout {tag} output:\n{git_result.decode()}\n')

        result1 = subprocess.run(['python3', 'scripts/mk_make.py'], cwd=repo_src, capture_output=True, text=True)
        log.write(f'Running mk_make.py output:\n{result1.stdout}\n{result1.stderr}\n')

        make_result = subprocess.run(['make', '-j32'], cwd=f'{repo_src}/build', capture_output=True, text=True)
        log.write(f'make output:\n{make_result.stdout}\n{make_result.stderr}\n')

        make_install_result = subprocess.run(['sudo', '-S'] + command.split(), input=password, text=True,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=repo_src)
        log.write(f'make install output:\n{make_install_result.stdout}\n{make_install_result.stderr}\n')


def build_from_commit(repo_src, commit_hash):
    password = '123123'
    command = 'make install'
    try:
        make_clean = subprocess.run(f"echo {password} | sudo -S rm -rf build", shell=True, cwd=repo_src,
                                    capture_output=True, text=True)
        logging.info(f'make clean output:\n{make_clean.stdout}\n{make_clean.stderr}\n')

        # reset
        reset_result = subprocess.run(f'echo {password} | sudo -S git reset --hard', shell=True, cwd=repo_src,
                                      capture_output=True,
                                      text=True)
        logging.info(f'Reset output:\n{reset_result.stdout}\n{reset_result.stderr}\n')

        # 检出指定的提交
        checkout_result = subprocess.run(f'echo {password} | sudo -S git checkout {commit_hash}',
                                         shell=True,
                                         cwd=repo_src,
                                         capture_output=True,
                                         text=True)
        logging.info(f'Checkout commit {commit_hash} output:\n{checkout_result.stdout}\n{checkout_result.stderr}\n')

        # 运行 mk_make.py 脚本并记录输出
        result1 = subprocess.run(f"echo {password} | sudo -S python3 scripts/mk_make.py", shell=True, cwd=repo_src,
                                 capture_output=True, text=True)
        logging.info(f'Running mk_make.py output:\n{result1.stdout}\n{result1.stderr}\n')

        # 执行 make 并记录输出
        make_result = subprocess.run(f"echo {password} | sudo -S make", shell=True, cwd=f'{repo_src}/build',
                                     capture_output=True, text=True)
        logging.info(f'make output:\n{make_result.stdout}\n{make_result.stderr}\n')
        # 重命名
        subprocess.run(f"echo {password} | sudo -S mv z3 /home/uu613/workspace/z3_commits/z3-{commit_hash}", shell=True,
                       cwd=f'{repo_src}/build', capture_output=True, text=True)

        # 执行 make install 并记录输出
        make_install_result = subprocess.run(['sudo', '-S'] + command.split(), input=password, text=True,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=f'{repo_src}/build')
        logging.info(f'make install output:\n{make_install_result.stdout}\n{make_install_result.stderr}\n')
    except Exception as e:
        logging.error(f"Error: {e}")


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


def mark_buggy_version():
    df = pd.read_csv(csv_path)

    df['induced_version'] = '-1'
    df['fixed_version'] = '-1'

    # 遍历DataFrame的每一行
    for index, row in df.iterrows():
        # 前5个字符
        bug_version = row[df.columns[1]][3:8]
        # 遍历列标题，找到含有bug_version的列
        for column in df.columns[3:8]:
            if bug_version in column:
                # 向前遍历找到第一个不同的列
                for i in range(df.columns.get_loc(column) - 1, 2, -1):
                    if row[df.columns[i]] != row[df.columns[2]]:
                        df.at[index, 'induced_version'] = df.columns[i]
                        break
                # 向后遍历找到第一个不同的列
                for i in range(df.columns.get_loc(column) + 1, len(df.columns)):
                    # 不以z3开头
                    if not df.columns[i].startswith('z3'):
                        break
                    if row[df.columns[i]] != row[df.columns[2]]:
                        df.at[index, 'fixed_version'] = df.columns[i]
                        break

    df.to_csv(csv_path, index=False)


def get_commits_between_versions(repo_src, old_version, new_version):
    # 构建命令
    command = f"git log --oneline {old_version}..{new_version}"

    # 执行命令
    result = subprocess.run(command, shell=True, check=True,
                            cwd=repo_src, stdout=subprocess.PIPE, universal_newlines=True)

    # 拆分输出以获取每一行
    lines = result.stdout.split('\n')

    # 提取每行的第一个词（commit hash）
    commit_hashes = [line.split(' ')[0] for line in lines if line]

    return commit_hashes


def build_each_commit():
    repo_src = '/home/uu613/workspace/z3'
    old_version_hash = versions_to_commit.get('z3-4.7.1-x64-ubuntu-16.04')
    new_version_hash = versions_to_commit.get('z3-4.8.5-x64-ubuntu-16.04')
    commit_list = get_commits_between_versions(repo_src, old_version_hash, new_version_hash)
    logging.info(f"Total commits: {len(commit_list)}")
    for commit in commit_list:
        # 如果已经构建过了，就跳过
        if f'z3-{commit}' in subprocess.run('ls', shell=True, cwd='/home/uu613/workspace/z3_commits',
                                            capture_output=True, text=True).stdout:
            logging.info(f"Exists, Skipped {commit}, Time: {datetime.now()}")
            continue
        build_from_commit(repo_src, commit)
        logging.info(f"Built {commit}, Time: {datetime.now()}")


if __name__ == '__main__':
    # mark_buggy_version()
    build_each_commit()
