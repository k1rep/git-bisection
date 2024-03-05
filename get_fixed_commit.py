import csv
import os
import subprocess
import test as t
import build_sqlite as b


# TODO: remove to utils
def filter_cases(input_file, cases_path, output_src='/root/code/kept_cases'):
    cases_kept = []
    with open(input_file, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            cases_kept.append(str(row[0]).replace('\ufeff', ''))
    file.close()
    count = 0
    for c in cases_kept:
        os.system(f'mv {cases_path}/{c} {output_src}/{count}.log')
        count += 1


def get_commits(version_old, version_new, repo_src):
    git_log_cmd = f"git -C {repo_src} log --pretty=format:'%H' --ancestry-path {version_old}...{version_new}"
    output = subprocess.check_output(git_log_cmd, shell=True).decode('utf-8')
    commit_ids = output.strip().split("\n")
    # Sort in ascending time order
    commit_ids.reverse()
    return commit_ids


# store csv after each execution, in order to avoid crash
def get_fixed_commit(cases_path, commit_ids, out_csv, repo_src='/root/sqlite'):
    test_cases = t.get_cases(cases_path)
    fixed_commits = [[''] for _ in range(len(test_cases))]
    count = 331
    for commit_id in commit_ids:
        if commit_ids.index(commit_id) < 330:
            continue
        b.build_from_tag(repo_src, commit_id)
        for test_case in test_cases:
            i = test_cases.index(test_case)
            # TODO: reuse
            out, err, code = t.exec_case(test_case)
            if err != '<error>':
                res = t.compare(out)
            else:
                res = 'execute_error'
            if res == 'pass':
                fixed_commits[i] = [commit_id]
        t.write_csv(fixed_commits, ['fixed_commit'], [os.path.basename(c) for c in test_cases],
                    f'{out_csv}/{count}.csv')
        count += 1
        b.make_clean(repo_src)


if __name__ == "__main__":
    # z3-4.7.1
    version_old = '3b1b82bef05a1b5fd69ece79c80a95fb6d72a990'
    version_new = '1a3220ace68c3889c875120120497d4c7b78e714'
    repo_src = '/home/uu613/workspace/z3'
    commit_ids = get_commits(version_old, version_new, repo_src)
    reverse_commit_ids = commit_ids[::-1]
    cases_path = '/root/code/kept_cases'
    # out_csv = '/root/code/fixed_commit.csv'
    out_csv = '/root/code/fixed_commits'
    get_fixed_commit(cases_path, commit_ids[::-1], out_csv)
