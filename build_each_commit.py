"""
This script is used to build the Z3 and CVC5 solver from commits between different versions.
"""
import concurrent.futures
import os
import shutil
import subprocess
from datetime import datetime
import logging
from utils.constants import Z3_VERSIONS_TO_COMMIT, CVC5_VERSIONS_TO_COMMIT

logging.basicConfig(level=logging.INFO, filename='build_log.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')


def build_from_tag(repo_src, tag, solver):
    log_file = 'build_tag.log'
    password = '123123'
    command = 'make install'
    with open(log_file, 'a') as log:
        git_result = subprocess.check_output(f'git checkout {tag}', shell=True, cwd=repo_src)
        log.write(f'git checkout {tag} output:\n{git_result.decode()}\n')

        if solver == 'z3':
            # 运行 mk_make.py 脚本并记录输出
            result1 = subprocess.run(['python3', 'scripts/mk_make.py'], cwd=repo_src, capture_output=True, text=True)
            log.write(f'Running mk_make.py output:\n{result1.stdout}\n{result1.stderr}\n')
        else:
            result1 = subprocess.run(['./configure.sh'], cwd=repo_src, capture_output=True, text=True)
            log.write(f'Running configure.sh output:\n{result1.stdout}\n{result1.stderr}\n')

        make_result = subprocess.run(['make', '-j32'], cwd=f'{repo_src}/build', capture_output=True, text=True)
        log.write(f'make output:\n{make_result.stdout}\n{make_result.stderr}\n')

        make_install_result = subprocess.run(['sudo', '-S'] + command.split(), input=password, text=True,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=repo_src)
        log.write(f'make install output:\n{make_install_result.stdout}\n{make_install_result.stderr}\n')


def build_from_commit(repo_src, commit_hash, worktree_path, solver):
    password = '123123'
    command = 'make install'
    try:
        subprocess.run(["git", "worktree", "add", worktree_path, commit_hash], check=True, cwd=repo_src)
        # Clean previous build directory safely
        shutil.rmtree(os.path.join(worktree_path, 'build'), ignore_errors=True)
        make_clean = subprocess.run(f"echo {password} | sudo -S rm -rf build", shell=True, cwd=worktree_path,
                                    capture_output=True, text=True)
        logging.info(f'make clean output:\n{make_clean.stdout}\n{make_clean.stderr}\n')

        # # reset
        # reset_result = subprocess.run(f'echo {password} | sudo -S git reset --hard', shell=True, cwd=repo_src,
        #                               capture_output=True,
        #                               text=True)
        # logging.info(f'Reset output:\n{reset_result.stdout}\n{reset_result.stderr}\n')

        # # clean
        # clean_result = subprocess.run(f'echo {password} | sudo -S git clean -fd', shell=True, cwd=repo_src,
        #                               capture_output=True,
        #                               text=True)
        # logging.info(f'Clean output:\n{clean_result.stdout}\n{clean_result.stderr}\n')

        # make_clean1 = subprocess.run(f"echo {password} | sudo -S rm -rf build", shell=True, cwd=repo_src,
        #                             capture_output=True, text=True)
        # logging.info(f'make clean1 output:\n{make_clean1.stdout}\n{make_clean1.stderr}\n')

        # # 检出指定的提交
        # checkout_result = subprocess.run(f'echo {password} | sudo -S git checkout {commit_hash}',
        #                                  shell=True,
        #                                  cwd=repo_src,
        #                                  capture_output=True,
        #                                  text=True)
        # logging.info(f'Checkout commit {commit_hash} output:\n{checkout_result.stdout}\n{checkout_result.stderr}\n')

        # # reset1
        # reset_result1 = subprocess.run(f'echo {password} | sudo -S git reset --hard', shell=True, cwd=repo_src,
        #                               capture_output=True,
        #                               text=True)
        # logging.info(f'Reset1 output:\n{reset_result1.stdout}\n{reset_result1.stderr}\n')
        if solver == 'z3':
            # 运行 mk_make.py 脚本并记录输出
            result1 = subprocess.run(f"echo {password} | sudo -S python3 scripts/mk_make.py", shell=True,
                                     cwd=worktree_path, capture_output=True, text=True)
            logging.info(f'Running z3 mk_make.py output:\n{result1.stdout}\n{result1.stderr}\n')
        else:
            result1 = subprocess.run(f"echo {password} | sudo -S ./configure.sh", shell=True, cwd=worktree_path,
                                     capture_output=True, text=True)
            logging.info(f'Running cvc5 configure.sh output:\n{result1.stdout}\n{result1.stderr}\n')
        # 执行 make 并记录输出
        make_result = subprocess.run(f"echo {password} | sudo -S make", shell=True, cwd=f'{worktree_path}/build',
                                     capture_output=True, text=True)
        logging.info(f'make output:\n{make_result.stdout}\n{make_result.stderr}\n')
        # 重命名
        if solver == 'z3':
            subprocess.run(f"echo {password} | sudo -S mv z3 /home/uu613/workspace/z3_commits/z3-{commit_hash}",
                           shell=True, cwd=f'{worktree_path}/build', capture_output=True, text=True)
        else:
            subprocess.run(f"echo {password} | sudo -S mv cvc5 /home/uu613/workspace/cvc5_commits/cvc5-{commit_hash}",
                           shell=True, cwd=f'{worktree_path}/build', capture_output=True, text=True)
        # 执行 make install 并记录输出
        make_install_result = subprocess.run(['sudo', '-S'] + command.split(), input=password, text=True,
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                             cwd=f'{worktree_path}/build')
        logging.info(f'make install output:\n{make_install_result.stdout}\n{make_install_result.stderr}\n')
    except subprocess.CalledProcessError as e:
        logging.error(f"Build failed for commit: {commit_hash}, Error: {str(e)}")
    finally:
        # 清理工作树
        subprocess.run(['sudo', '-S'] + ["git", "worktree", "remove", worktree_path], input=password,
                       check=True, cwd=repo_src)
        if os.path.exists(worktree_path):
            shutil.rmtree(worktree_path)


def get_commits_between_versions(repo_src, old_version, new_version):
    # 构建命令
    command = f"git log --oneline {old_version}..{new_version}"

    # 执行命令
    result = subprocess.run(command, shell=True, check=True,
                            cwd=repo_src, stdout=subprocess.PIPE, text=True)

    # 拆分输出以获取每一行
    lines = result.stdout.split('\n')

    # 提取每行的第一个词（commit hash）
    commit_hashes = [line.split(' ')[0] for line in lines if line]

    return commit_hashes


def build_each_commit(solver):
    repo_src = '/home/uu613/workspace/z3' if solver == 'z3' else '/home/uu613/workspace/cvc5'
    old_version_hash = Z3_VERSIONS_TO_COMMIT.get('z3-4.4.0-x64-ubuntu-14.04') if solver == 'z3' \
        else CVC5_VERSIONS_TO_COMMIT.get('cvc5-0.0.2')
    new_version_hash = Z3_VERSIONS_TO_COMMIT.get('z3-4.13.0-x64-glibc-2.35') if solver == 'z3' \
        else CVC5_VERSIONS_TO_COMMIT.get('cvc5-1.1.2')
    commit_list = get_commits_between_versions(repo_src, old_version_hash, new_version_hash)
    logging.info(f"Total commits to build: {len(commit_list)}")
    # Cache already built
    built_commits = set(os.listdir('/home/uu613/workspace/z3_commits')) if solver == 'z3' \
        else set(os.listdir('/home/uu613/workspace/cvc5_commits'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # 将每个commit分配给build_from_commit函数
        futures = []
        for i, commit in enumerate(commit_list):
            if f'z3-{commit}' in built_commits or f'cvc5-{commit}' in built_commits:
                logging.info(f"Exists, Skipped {commit}, Time: {datetime.now()}")
                continue
            worktree_path = f"/tmp/{solver}_worktree_{i}"
            futures.append(executor.submit(build_from_commit, repo_src, commit, worktree_path, solver))
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
                logging.info(f"Built {commit}, Time: {datetime.now()}")
            except Exception as e:
                logging.error(f"An error occurred: {e}")

        logging.info(f"Finished building all commits, Time: {datetime.now()}")

    # for commit in commit_list:
    #     # 如果已经构建过了，就跳过
    #     if f'z3-{commit}' in subprocess.run('ls', shell=True, cwd='/home/uu613/workspace/z3_commits',
    #                                         capture_output=True, text=True).stdout:
    #         logging.info(f"Exists, Skipped {commit}, Time: {datetime.now()}")
    #         continue
    #     build_from_commit(repo_src, commit)
    #     logging.info(f"Built {commit}, Time: {datetime.now()}")


if __name__ == '__main__':
    build_each_commit(solver='z3')
    # build_each_commit(solver='cvc5')
