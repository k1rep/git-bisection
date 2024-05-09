import csv

import test as t

'''
1. read csv to 2D array
2. 2 kinds
    a. before: from end to start
    b. after: from start to end
'''


def parse(csv_file, order, output_file):
    data = []
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row)
    file.close()
    res = [['Non good'] for _ in range(len(data))]
    column_header = ['' for _ in range(len(data) - 1)]
    for i in range(1, len(data)):
        column_header[i - 1] = data[i][0]
        if order == 'p':
            for j in range(1, len(data[i]), 1):
                if data[i][j] == 'pass':
                    res[i][0] = data[0][j]
                    continue
        else:
            for j in range(len(data[i]) - 1, 0, -1):
                if data[i][j] == 'pass':
                    res[i][0] = data[0][j]
                    continue
    row_header = ['before'] if order == 'p' else ['after']
    t.write_csv(res, row_header, column_header, output_file)


if __name__ == "__main__":
    csv_file = '/root/code/before_3.28.0.csv'
    order = 'p'
    output_file = '/root/code/good_before.csv'
    parse(csv_file, order, output_file)
