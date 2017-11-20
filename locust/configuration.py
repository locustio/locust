import json
import pandas as pd

def get_nested_record(grouped_data_key, grouped_data, array_column, regular_column):
    """
    Set a record which is consist of regular column and column which has array type value.

    :param list grouped_data_key: data key of grouped data
    :param list grouped_data: data of grouped data
    :param list array_column: column's name which value's data type is list
    :param list regular_column: column's name which value's data type is numbers or string
    :returns: a data in the shape of dictionary
    """

    record = {}
    # assign key and value which come from regular column
    for i in range(len(grouped_data_key)):
        print(regular_column[i])
        record[regular_column[i]] = grouped_data_key[i]

    # assign key and value which come from column which has array type value
    for field in array_column:
        record[field] = list(grouped_data[field].unique())

    return record

def get_array_record(array_column, df):
    """
    Set a record which is consist of column and its value data type is array.

    :param list array_column: column's name which value's data type is list
    :param dataframe df: raw data which want to be processed
    :returns: a data in the shape of dictionary
    """

    record = {}
    for field in array_column:
        record[field] = list(df[field].unique())

    return record

def convert_csv_to_json(csv_path, array_column):
    """
    Convert csv data into json data with only 1 depth level.

    :param string csv_path: path of csv which want to be converted into json format
    :param list array_column: column's name which value's data type is list
    :returns: string in json formatting
    """

    df = pd.read_csv(csv_path)

    # collect column's name which is not having array as its value
    regular_column = []
    for column in df.keys():
        if column not in array_column: regular_column.append(column)

    records = []
    # if csv contains only one column and the column act as array
    if not regular_column:
        records.append(get_array_record(array_column, df))
    # group csv data by regular column data
    else:
        for grouped_data_key, grouped_data in df.groupby(regular_column):
            record = get_nested_record(grouped_data_key, grouped_data, array_column, regular_column)
            records.append(record)

    return json.dumps(records, indent=2)
