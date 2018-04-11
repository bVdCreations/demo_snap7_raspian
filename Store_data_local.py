import sqlite3
import os


class store_data():
    """
    http://www.sqlitetutorial.net/sqlite-cheat-sheet/

    """

    def __init__(self, name, max_values):
        if os.path(name) is False:
            self._connection = sqlite3.connect('name')
        self._max_values = max_values

    def update_data_row(self):
        pass

    def read_row(self):
        pass

    def read_all(self):
        pass

    def delete_row(self):
        pass

# DBs = connection.cursor()
