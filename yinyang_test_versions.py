"""
For each version of Z3 and CVC5, run Yinyang on the benchmark2 folder.
"""
import os
import subprocess
import logging

from utils.constants import Z3_VERSIONS, CVC5_VERSIONS

logging.basicConfig(level=logging.INFO)
workspace_path = "/home/uu613/workspace/"
z3_basic_path = "/home/uu613/workspace/z3_versions/"
cvc5_basic_path = "/home/uu613/workspace/cvc5_versions/"


def yinyang_test_z3_versions():
    # 遍历所有版本
    for version in Z3_VERSIONS:
        z3_path = z3_basic_path + version + '/bin/z3'
        if os.path.isfile(z3_path):
            # 权限
            os.chmod(z3_path, 0o755)
            # 构建yinyang命令
            yinyang_cmd = (f"/home/uu613/.virtualenvs/bisection/bin/python "
                           f"/home/uu613/workspace/yinyang/build/scripts-3.10/typefuzz "
                           f"\"{z3_path} model_validate=true;"
                           f"cvc5-Linux --check-models -m -i -q\" "
                           f"benchmark2")

            # 在后台并行执行命令
            logging.info(f"在后台执行：{yinyang_cmd}")

            subprocess.Popen(yinyang_cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=workspace_path, text=True)


def yinyang_test_cvc5_versions():
    # 遍历所有版本
    for version in CVC5_VERSIONS:
        if version == 'cvc5-1.1.1' or version == 'cvc5-1.1.2':
            cvc5_path = cvc5_basic_path + version + '/bin/cvc5'
        else:
            cvc5_path = cvc5_basic_path + version
        if os.path.isfile(cvc5_path):
            # 权限
            os.chmod(cvc5_path, 0o755)
            # 构建yinyang命令
            yinyang_cmd = (f"/home/uu613/.virtualenvs/bisection/bin/python "
                           f"/home/uu613/workspace/yinyang/build/scripts-3.10/typefuzz "
                           f"/home/uu613/workspace/z3_versions/z3-4.13.0-x64-glibc-2.35/bin/z3 model_validate=true;"
                           f"\"{cvc5_path} --check-models -m -i -q\" "
                           f"benchmark2")

            # 在后台并行执行命令
            logging.info(f"在后台执行：{yinyang_cmd}")

            subprocess.Popen(yinyang_cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=workspace_path, text=True)


if __name__ == "__main__":
    # yinyang_test_z3_versions()
    yinyang_test_cvc5_versions()
