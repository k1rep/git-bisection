"""
This script is used to build the Z3 solver from commits between different versions.
"""
import subprocess
from datetime import datetime
import logging
from utils.constants import VERSIONS_TO_COMMIT

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
        logging.error(f"Error: {e}, commit: {commit_hash}")


csv_path = "/home/uu613/workspace/bugs/new_folder/tested_z3_bugs.csv"


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
    old_version_hash = VERSIONS_TO_COMMIT.get('z3-4.4.0-x64-ubuntu-14.04')
    new_version_hash = VERSIONS_TO_COMMIT.get('z3-4.13.0-x64-glibc-2.35')
    commit_list = get_commits_between_versions(repo_src, old_version_hash, new_version_hash)
    logging.critical(f"Total commits: {len(commit_list)}")
    for commit in commit_list:
        # 如果已经构建过了，就跳过
        if f'z3-{commit}' in subprocess.run('ls', shell=True, cwd='/home/uu613/workspace/z3_commits',
                                            capture_output=True, text=True).stdout:
            logging.info(f"Exists, Skipped {commit}, Time: {datetime.now()}")
            continue
        build_from_commit(repo_src, commit)
        logging.info(f"Built {commit}, Time: {datetime.now()}")


if __name__ == '__main__':
    build_each_commit()
