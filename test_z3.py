import os
import subprocess
import pandas as pd

csv_path = "/home/uu613/workspace/bugs/new_folder/z3_bugs.csv"
basic_path = "/home/uu613/workspace/z3_versions/"
case_path = "/home/uu613/workspace/bugs/new_folder/"
versions = ['z3-4.7.1-x64-ubuntu-16.04',
            'z3-4.8.1.016872a5e0f6-x64-ubuntu-16.04',
            'z3-4.8.3.7f5d66c3c299-x64-ubuntu-16.04',
            'z3-4.8.4.d6df51951f4c-x64-ubuntu-16.04',
            'z3-4.8.5-x64-ubuntu-16.04']

df = pd.read_csv(csv_path)

for version in versions:
    df[version] = ''
    z3_path = basic_path + version + '/bin/z3'
    for index, row in df.iterrows():
        case_filename = row['Case-Filename']
        expected_result = row['result']
        try:
            result = subprocess.run([z3_path, case_path + case_filename],
                                    cwd=basic_path, capture_output=True, text=True)
            output = result.stdout.strip()
            df.at[index, version] = output
        except Exception as e:
            print(f"Unexpected error: {e}")

df.to_csv(case_path + 'tested_' + os.path.basename(csv_path), index=False)
