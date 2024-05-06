"""
This script is used to test the z3 solver on different versions.
Given a csv file containing the test cases, the script will test each case on each version of z3.
The results will be stored in a new csv file.
mark_buggy_version() will mark the buggy version for each bug.
"""
import os
import subprocess
import pandas as pd
import logging

csv_path = "/home/uu613/workspace/bugs/new_folder/z3_bugs.csv"
tested_csv_path = "/home/uu613/workspace/bugs/new_folder/tested_z3_bugs.csv"
basic_path = "/home/uu613/workspace/z3_versions/"
case_path = "/home/uu613/workspace/bugs/new_folder/"
versions = [str(version) for version in os.listdir(basic_path) if version.startswith('z3-')]
logging.basicConfig(level=logging.INFO)


def version_key(version):
    # Split the version string into its main components
    parts = version.split('-')
    # The main version part (e.g., '4.10.0') is at index 1
    main_version = parts[1]
    # Split the main version on '.' to handle major, minor, and patch as numbers
    version_numbers = [int(num) if num.isdigit() else num for num in main_version.split('.')]
    return version_numbers


# Sort versions using the custom key
sorted_versions = sorted(versions, key=version_key)
logging.info(f"Versions: {sorted_versions}")


def mark_buggy_version(tested_csv_path):
    df = pd.read_csv(tested_csv_path)
    df['induced_version'] = '-1'
    df['fixed_version'] = '-1'

    # 遍历DataFrame的每一行
    for index, row in df.iterrows():
        bug_version = row[df.columns[1]].split('-')[1]
        # 遍历列标题，找到含有bug_version的列
        version_columns = [col for col in df.columns if bug_version in col]
        for column in version_columns:
            # 向前遍历找到第一个不同的列
            for i in range(df.columns.get_loc(column) - 1, 2, -1):
                # 不以z3开头
                if not df.columns[i].startswith('z3'):
                    break
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

    for version in sorted_versions:
        df[version] = ''
        z3_path = os.path.join(basic_path, version, 'bin', 'z3')
        # 授权
        os.chmod(z3_path, 0o755)
        for index, row in df.iterrows():
            case_filename = row['Case-Filename']
            expected_result = row['result']
            try:
                result = subprocess.run([z3_path, os.path.join(case_path, case_filename)],
                                        cwd=basic_path, capture_output=True, text=True, timeout=60)
                output = result.stdout.strip()
                # 寻找sat或unsat
                if output != 'sat' and output != 'unsat':
                    if 'sat' in output or 'unsat' in output:
                        output = output.split('\n')[-1]
                    else:
                        output = 'unknown'
                df.at[index, version] = output
                logging.info(f"Case: {case_filename}, Version: {version}, Result: {output}")
            except subprocess.TimeoutExpired:
                df.at[index, version] = 'Timeout'
                logging.info(f"Case: {case_filename}, Version: {version}, Result: Timeout")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")

    df.to_csv(os.path.join(case_path, 'tested_' + os.path.basename(csv_path)), index=False)
    mark_buggy_version(tested_csv_path)
