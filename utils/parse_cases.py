import csv
import os
from difflib import SequenceMatcher
import logging

logging.basicConfig(level=logging.DEBUG)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def find_most_similar_file(target, folder_path):
    highest_similarity = 0
    most_similar_filename = None

    for filename in os.listdir(folder_path):
        if filename == target or filename.endswith('.output'):
            continue
        similarity = similar(target, filename)
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_similar_filename = filename

    return most_similar_filename, highest_similarity


def list_logs(path):
    logs = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):
                logs.append(file_path)
    return logs


def log2case(filepath, output):
    statements = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        statements = lines[4:]
    file.close()

    with open(output, 'w') as f:
        for statement in statements:
            f.write(statement)
    f.close()


def logs2cases(input_path, output_path):
    count = 0
    logs = list_logs(input_path)
    for log in logs:
        output_file = f'{output_path}/case_{count}.log'
        log2case(log, output_file)
        count += 1


def find_z3_version(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if len(lines) >= 2:
                second_line = lines[1]
                index = second_line.find('z3-')
                if index != -1:
                    start_index = index
                    end_index = second_line.find(' ', start_index)
                    if end_index == -1:
                        end_index = len(second_line)
                    return second_line[start_index:end_index]
    except Exception as e:
        return f"读取文件时发生错误: {str(e)}"


def get_test_result(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if len(lines) >= 5:
                result_line = lines[4]
                start_index = 0
                end_index = result_line.find('\n', start_index)
                if end_index == -1:
                    end_index = len(result_line)
                return result_line[start_index:end_index]
    except Exception as e:
        return f"读取文件时发生错误: {str(e)}"


if __name__ == "__main__":
    # input_path = '/root/code/logs/3.28.0'
    # output_path = '/root/code/cases/3.28.0'
    # logs2cases(input_path, output_path)
    folder_path = "/home/uu613/workspace/bugs/new_folder"
    csv_path = "/home/uu613/workspace/bugs/new_folder/z3_bugs.csv"
    target_filenames = [filename for filename in os.listdir(folder_path) if filename.endswith('.output')
                        and os.path.isfile(os.path.join(folder_path, filename))]
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Case-Filename", "Z3 Version", "result"])
        # 对于所有的output文件
        for filename in target_filenames:
            # 找到与之配对的case-smt2文件
            most_similar_file, similarity_score = find_most_similar_file(filename, folder_path)
            logging.info(f"Most similar file to {filename} is {most_similar_file} "
                         f"with similarity score {similarity_score}")
            # 找到这个output文件对应的z3版本
            version = find_z3_version(os.path.join(folder_path, filename))
            logging.critical(f"Version of {filename} is {version}")
            # 找到这个output文件的测试结果
            result = get_test_result(os.path.join(folder_path, filename))
            logging.critical(f"Result of {filename} is {result}")
            if version is None and result is None:
                continue
            writer.writerow([most_similar_file, version, result])
