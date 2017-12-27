import json
import pandas as pd

class csvToJson:

    def __init__(self, file_path):
        """
        Initialize object's attribute

        :param string file_path: path of csv file
        """
        self.file_path = file_path
        self.df = pd.read_csv(file_path)

    def get_columns_name(self):
        """
        Return column's name which exist in the file

        :returns: column's name in list object type
        """
        return self.df.keys().tolist()

    def _get_nested_record(self, grouped_data_key, grouped_data, array_column, regular_column):
        """
        Set a record which is consist of regular column and column which has array type value.

        :param list grouped_data_key: data key of grouped data
        :param list grouped_data: data of grouped data
        :param list array_column: column's name which value's data type is list
        :param list regular_column: column's name which value's data type is numbers or string
        :returns: a data in the shape of dictionary
        """

        record = {}
        # check whether grouped_data_key tuple or not. if not (only exist one key), turn into tuple
        if not isinstance(grouped_data_key, tuple):
            grouped_data_key = (grouped_data_key,)

        # assign key and value which come from regular column
        for i in range(len(grouped_data_key)):
            record[regular_column[i]] = grouped_data_key[i]

        # assign key and value which come from column which has array type value
        for field in array_column:
            record[field] = list(grouped_data[field].unique())

        return record

    def _get_array_record(self, array_column):
        """
        Set a record which is consist of column and its value data type is array.

        :param list array_column: column's name which value's data type is list
        :param dataframe df: raw data which want to be processed
        :returns: a data in the shape of dictionary
        """

        record = {}
        for field in array_column:
            record[field] = list(self.df[field].unique())

        return record

    def convert(self, array_column):
        """
        Convert csv data into json data with only 1 depth level.

        :param string csv_path: path of csv which want to be converted into json format
        :param list array_column: column's name which value's data type is list
        :returns: list object
        """

        # collect column's name which is not having array as its value
        regular_column = []
        for column in self.get_columns_name():
            if column not in array_column: regular_column.append(column)

        records = None
        # if csv contains only one column and the column definitely acts as array
        if len(self.df.columns)==1:
            records= self._get_array_record(self.get_columns_name())
        # if csv contains more than one columns and all of it act as array
        elif not regular_column:
            records= self._get_array_record(array_column)
        # group csv data by regular column data
        else:
            records = []
            for grouped_data_key, grouped_data in self.df.groupby(regular_column):
                record = self._get_nested_record(grouped_data_key, grouped_data, array_column, regular_column)
                records.append(record)

        return records
