import os
import subprocess
import pandas as pd

csv_path = "/home/uu613/workspace/bugs/new_folder/z3_bugs.csv"
tested_csv_path = "/home/uu613/workspace/bugs/new_folder/tested_z3_bugs.csv"
basic_path = "/home/uu613/workspace/z3_versions/"
case_path = "/home/uu613/workspace/bugs/new_folder/"
versions = [str(version) for version in os.listdir(basic_path) if version.startswith('z3-')]


def mark_buggy_version():
    df = pd.read_csv(tested_csv_path)
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
    df.to_csv(tested_csv_path, index=False)


if __name__ == '__main__':
    df = pd.read_csv(csv_path)

    for version in versions:
        df[version] = ''
        z3_path = basic_path + version + '/bin/z3'
        # 授权
        os.chmod(z3_path, 0o755)
        for index, row in df.iterrows():
            case_filename = row['Case-Filename']
            expected_result = row['result']
            try:
                result = subprocess.run([z3_path, case_path + case_filename],
                                        cwd=basic_path, capture_output=True, text=True, timeout=60)
                output = result.stdout.strip()
                df.at[index, version] = output
                print(f"Case: {case_filename}, Version: {version}, Result: {output}")
            except subprocess.TimeoutExpired:
                df.at[index, version] = 'Timeout'
                print(f"Case: {case_filename}, Version: {version}, Result: Timeout")
            except Exception as e:
                print(f"Unexpected error: {e}")

    df.to_csv(case_path + 'tested_' + os.path.basename(csv_path), index=False)
    mark_buggy_version()
