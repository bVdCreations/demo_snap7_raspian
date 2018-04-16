import sqlite3
import os

"""
{'DB2':
{'DB_VAR': {'Adress': '0.0', 'Name': 'DB_VAR', 'Type': 'INT', 'Initial value': 0, 'Comment': 'Temporary placeholder variable'},
'DB_Real': {'Adress': '2.0', 'Name': 'DB_Real', 'Type': 'REAL', 'Initial value': 0, 'Comment': 'bla'},
 'teststring': {'Adress': '6.0', 'Name': 'teststring', 'Type': 'STRING[254]', 'Initial value': "'talking'", 'Comment': 'blablabla'},
  'DB_BOOL': {'Adress': '262.0', 'Name': 'DB_BOOL', 'Type': 'BOOL', 'Initial value': True, 'Comment': '0010101'}},

   'DB1':
   {'STAT0': {'Adress': '0.0', 'Name': 'STAT0', 'Type': 'BOOL', 'Initial value': 'FALSE'},
    'STAT1': {'Adress': '2.0', 'Name': 'STAT1', 'Type': 'REAL', 'Initial value': '0.000000e+000'},
     'STAT2': {'Adress': '6.0', 'Name': 'STAT2', 'Type': 'BYTE', 'Initial value': 'B#16#0'}}}
"""

class store_data():
    """
    http://www.sqlitetutorial.net/sqlite-cheat-sheet/

    """

    def __init__(self, name, file_dir=''):
        self._name_sqlite = name
        self._tables = dict()
        self._file_dir = file_dir

    def connect():
        return sqlite3.connect(self._file_dir + self._name_sqlite)

    def create_tables(self, variables_dict):

        for db_name, var_dict in variables_dict.items():
            variables_string = ''
            for variable_name, variables_details in var_dict.items():
                variables_string = variables_string + str(variable_name)+' ' +\
                 self.get_sqlite_type(variables_details['Type'])

            sqlite3_command = "CREATE TABLE {} (\
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\
            {}\
            sqltime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL\
            )".format(db_name, variables_string)

            self.connect().cursor().execute(sqlite3_command)

    @staticmethod
    def get_sqlite_type(Type_name):
        case = {'BOOL': 'INTEGER',

                    }
        return case[Type_name]

    def update_data_row(self, dbname):
        pass

    def read_row(self):
        pass

    def read_all(self):
        pass

    def delete_row(self):
        pass

# DBs = connection.cursor()
