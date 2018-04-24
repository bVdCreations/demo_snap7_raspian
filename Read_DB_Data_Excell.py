import openpyxl
from openpyxl.utils import get_column_letter


class ReadDB_Data:
    """
    this reads the db files in an excell and stores it in a multi level dict

    """

    def __init__(self, file_name, file_dir=''):
        """

        :param file_name: the name of the excell file (standard 'DBs_PLC_{}.xlsx'.format plcName
        :param file_dir: the directory of the excell file
        """
        self._fileName = file_name
        self._file_dire = file_dir
        self._workbook = openpyxl.load_workbook(self._file_dire+self._fileName)

    def read_data_dbs(self):
        """ returns a dict with the as key the DB names and as value:
         a dict with all the variables of the db
        """
        returndict = dict()
        for sheetname in self._workbook.sheetnames:
            if 'DB' in sheetname:
                returndict.update({sheetname: dict()})
                sheet_object = self._workbook[sheetname]
                last_entry = self.get_last_entry_sheet(sheet_object)
                
                for rowOfCellObjects in sheet_object['A3':last_entry]:
                    namerow = rowOfCellObjects[1].value
                    returndict[sheetname].update({namerow: dict()})
                    for cellObj in rowOfCellObjects:

                        if cellObj.value is not None:
                            returndict[sheetname][namerow].update(
                                {sheet_object.cell(column=cellObj.col_idx, row=1).value: cellObj.value})

        return returndict

    def read_info_plc(self):
        """ returns a dict with the keys IP_adress, rack and slot with it's values"""
        returndict = dict()
        sheetnames = self._workbook.sheetnames
        if 'info_PLC' in sheetnames:

            sheet_object = self._workbook['info_PLC']
            for rowOfCellObjects in sheet_object['A1':self.get_last_entry_sheet(sheet_object)]:
                # loop through sheet row by row
                returndict.update({rowOfCellObjects[0].value: rowOfCellObjects[1].value})
            return returndict
        else:
            raise FileNotFoundError('"info_PLC" can not be found in the sheetnames : {}'.format(sheetnames))



    def get_last_entry_sheet(self, sheet_object: openpyxl):
        # find the maximum range of data in the sheet
        return self.get_last_entry_column(sheet_object, row=1) + \
               str(self.get_last_entry_row(sheet_object, start_row=2))

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

    for key, value in ReadDB_Data('DBs_PLC_300.xlsx', file_dir='I_O_info_plc//').read_info_plc().items():
        print('key = {}   value = {}'.format(key, value))

    for db, values in ReadDB_Data('DBs_PLC_300.xlsx', file_dir='I_O_info_plc//').read_data_dbs().items():
        print('key ={}'.format(db))

        for keyvar, value in values.items():
            print('\tkeyvar ={}'.format(keyvar))
            print('\ttype ={}'.format(value['Type']))
        print('-'*10)
