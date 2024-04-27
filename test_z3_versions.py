#!/home/uu613/.virtualenvs/bisection/bin/python
import os
import subprocess

workspace_path = "/home/uu613/workspace/"
basic_path = "/home/uu613/workspace/z3_versions/"
versions = ['z3-4.7.1-x64-ubuntu-16.04',
            'z3-4.8.1.016872a5e0f6-x64-ubuntu-16.04',
            'z3-4.8.3.7f5d66c3c299-x64-ubuntu-16.04',
            'z3-4.8.4.d6df51951f4c-x64-ubuntu-16.04',
            'z3-4.8.5-x64-ubuntu-16.04']


def main():
    # 遍历所有版本
    for version in versions:
        z3_path = basic_path + version + '/bin/z3'
        if os.path.isfile(z3_path):
            # 构建yinyang命令
            yinyang_cmd = (f"/home/uu613/.virtualenvs/bisection/bin/python "
                           f"/home/uu613/workspace/yinyang/build/scripts-3.10/typefuzz "
                           f"\"{z3_path} model_validate=true;"
                           f"cvc5-Linux --check-models -m -i -q\" "
                           f"benchmark2")

            # 在后台并行执行命令
            print(f"在后台执行：{yinyang_cmd}")

            subprocess.Popen(yinyang_cmd, shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=workspace_path, text=True)


if __name__ == "__main__":
    main()
