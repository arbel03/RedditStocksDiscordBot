import os
import csv
import json


def is_test_mode():
    return os.environ["test"].lower() == "true" if "test" in os.environ else False


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


def get_data_file_path(name):
    this_dir, _ = os.path.split(__file__)
    return os.path.join(this_dir, "data", name)


def read_config():
    return json.load(open(get_data_file_path(("config.json"))))
