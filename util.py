import csv


def read_csv_files(filename, data=None, **kwargs):
    """
    :param filename (str): name of file to be read
    :param data (list): initial list, should be empty
    :param kwargs: additional formatting arguments for csv.reader
    :return: data(list) = list of parsed rows in a column
    """
    data = data or []
    with open(filename, 'r', errors='ignore') as File:
        file_reader = csv.reader(File, **kwargs)
        for row in file_reader:
            data.append(row[0])

    return data
