import openpyxl
from openpyxl.utils import get_column_letter


class ReadDB_Data:
    """
    this reads the db files in an excell and stores it in a multi level dict

    """

    def __init__(self, file_name='DBs_PLC_300.xlsx', file_dir=''):
        """

        :param file_name: the name of the excell file (standard 'DBs_PLC_{}.xlsx'.format plcName
        :param file_dir: the directory of the excell file
        """
        self._fileName = file_name
        self._file_dire = file_dir
        self._workbook = openpyxl.load_workbook(self._file_dire+self._fileName)

    def read_data(self):
        """ returns a dict with the als key the DB names and as value:
         a directory with all the variables of the db
        """
        returndict = dict()
        for sheetname in self._workbook.get_sheet_names():
            if 'DB' in sheetname:
                returndict.update({sheetname: dict()})
                sheet_object = self._workbook.get_sheet_by_name(sheetname)
                for rowOfCellObjects in sheet_object['A3':self.get_last_entry_timesheet(sheet_object)]:
                    namerow = rowOfCellObjects[1].value
                    returndict[sheetname].update({namerow: dict()})
                    for cellObj in rowOfCellObjects:

                        if cellObj.value is not None:
                            returndict[sheetname][namerow].update(
                                {sheet_object.cell(column=cellObj.col_idx, row=1).value: cellObj.value})

        return returndict

    def get_last_entry_timesheet(self, sheet_object: openpyxl):
        # find the maximum range of data in the sheet
        return self.get_last_entry_column(sheet_object, row=1) + \
               str(self.get_last_entry_row(sheet_object, start_row=1)-1)

    @staticmethod
    def get_last_entry_row(sheet_object: openpyxl, start_row=1, column=1):
        # find the row number of the last entry in the given column
        row = start_row
        last_entry_row = row
        while sheet_object.cell(column=column, row=row).value is not None:
            last_entry_row = row
            row += 1
        return last_entry_row

    @staticmethod
    def get_last_entry_column(sheet_object: openpyxl, start_column=1, row=1):
        # find the column number of the last entry the given row
        column = start_column
        last_entry_column = column
        while sheet_object.cell(column=column, row=row).value is not None:
            last_entry_column = column
            column += 1
        return get_column_letter(last_entry_column)


if '__main__' == __name__:
    pass
