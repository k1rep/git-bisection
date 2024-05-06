import subprocess
import logging
logging.basicConfig(level=logging.INFO)

sqlite_configure_flags = '--enable-fts5 --enable-rtree'


def build_from_tag(repo_src, tag):
    subprocess.check_output(f'git checkout {tag}', shell=True, cwd=repo_src)
    output = subprocess.check_output(f'./configure --enable-fts5 --enable-rtree', shell=True, cwd=repo_src,
                                     stderr=subprocess.DEVNULL)
    subprocess.check_output(f'make -j', shell=True, cwd=repo_src, stderr=subprocess.DEVNULL)
    subprocess.check_output(f'make install', shell=True, cwd=repo_src, stderr=subprocess.DEVNULL)


def build_from_commit(repo_src, commit_id):
    pass


def make_clean(repo_src):
    subprocess.check_output('make clean', shell=True, cwd=repo_src)
    subprocess.check_output('rm /usr/local/bin/sqlite3', shell=True, cwd=repo_src)


if __name__ == "__main__":
    sqlite_repo = '/root/sqlite'
    sqlite_tag = 'version-3.28.0'
    build_from_tag(sqlite_repo, sqlite_tag)
    output = subprocess.check_output('sqlite3 --version', shell=True)
    logging.info(output.decode())
    # make_clean(sqlite_repo)
