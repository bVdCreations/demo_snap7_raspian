import snap7
import util
from datetime import datetime, time, timedelta, date


# from snap7.util import *
from Read_DB_Data_Excell import ReadDB_Data


def convert_adress(adress_string):
    split = adress_string.strip().split('.')
    adress_tuple = (int(split[0]), int(split[1]))

    return adress_tuple


class PLC:

    def __init__(self, ip_adress, rack=None, slot=None):
        """
        :param ip_adress: string
        :param rack: int_
        :param slot: int
        """
        self._plc = snap7.client.Client()
        self._IP = ip_adress
        self._rack = rack
        self._slot = slot
        self._db_list = dict()
        self.create_db_inst_from_excell()
        self._connect = self.connect()
        self.disconnect()

    def get_ip(self):
        """

        :return: the Ip adress of the PLC
        """
        return self._IP

    def set_ip(self, ip_adress, rack=None, slot=None):
        """disconnect the plc
        set new Ip adress
        make a new connection
        if the connection is made return True otherwise False"""

        if rack is None:
            rack = self._rack

        if slot is None:
            slot = self._slot

        try:
            self._plc.disconnect()
            self._connect = self._plc.connect(ip_adress, rack, slot)
            return True
        except ConnectionError:
            return False

    def create_db_inst_from_excell(self, file_name='DBs_PLC_300.xlsx', file_dir=''):
        """
        reads in the DB data from an excell file
        the data is structured in a multi level dictionary
        {DB_NAME:{variable name : {variable_info : 'info', ... }   , variable name2: {...} } ,
         DB_NAME2:{... }  }
        from that dict it updates
        a dictionary with the names of the db's as keys and an instance of the class DB_PLC as value
        """

        for db_name, variables_dict in ReadDB_Data(file_name=file_name, file_dir=file_dir).read_data().items():
            self._db_list.update({db_name: self.DB_PLC(db_name, variables_dict)})

    def read_db(self, *args):
        """
        This method read the complete DB from the PLC
        :param args: db_names (if None it will read all the db's)
        :return: dict with the read values
        """
        self.connect()
        if len(args) == 0:

            dbs = self._db_list.keys()
        else:
            print(self._db_list.keys())
            # assert args  in self._db_list.keys(), 'one or more arguments do not exits'
            dbs = args

        db_values = dict()
        # empty dict for storing the read values

        for db in dbs:
            db_instance = self._db_list[db]
            db_instance.set_read_data(self._plc.db_get(db_instance.db_number()))
            # read the complete db and store that bytearray in self._db_read_data
            db_values.update({db: db_instance.read_variable()})
            # read the variables from the stored bytearray and update that to the value dict
        self.disconnect()
        return db_values

    def read_variable(self, dict_read):

        if self.check_input(dict_read):
            self.connect()
            dict_value = dict()
            for db_name, variables in dict_read.items():
                db = self._db_list[db_name]
                dict_value.update({db_name: dict()})
                for variable_name in variables:
                    variable_inst = db.variable(variable_name)
                    _bytearray = self._plc.db_read(db.db_number(), variable_inst.get_offset(), variable_inst.get_size())
                    print('read {}'.format(_bytearray))
                    util.test_time(_bytearray)


                    value = variable_inst.read_var(read_bytearray=_bytearray)
                    dict_value[db_name].update({variable_name: value})

            self.disconnect()
            return dict_value

    def write_variable(self, dict_write):

        if self.check_input(dict_write):
            self.connect()
            for db_name, variables in dict_write.items():
                db = self._db_list[db_name]
                for variable_name, value in variables.items():
                    variable_inst = db.variable(variable_name)
                    _bytearray = self._plc.db_read(db.db_number(), variable_inst.get_offset(), variable_inst.get_size())
                    variable_inst.write_var(value , write_bytearray=_bytearray)

                    self._plc.db_write(db.db_number(), variable_inst.get_offset(), _bytearray)

            self.disconnect()

    # To do
    def check_input(self, dict_input):
        if len(dict_input) == 0:
            return False
        else:
            return True

    def connect(self):
        if self._plc.get_connected():
            print("already connected")
        else:
            try:
                return self._plc.connect(self._IP, self._rack, self._slot)
            except ConnectionError:
                raise ConnectionError("Can not connect to the PLC")

    def disconnect(self):
        self._plc.disconnect()

    class DB_PLC:

        def __init__(self, db_name, dict_varia):

            self._db_name = db_name
            self._db_number = int(db_name[2::])
            self._list_variables = dict()
            self._create_variables(dict_varia)
            self._db_read_data = bytearray()
            self._db_write_data = bytearray()

        def _create_variables(self, dict_varia):
            for variable_name, variables_data in dict_varia.items():
                if 'Comment' in variables_data.keys():
                    comment = variables_data['Comment']
                else:
                    comment = ''
                self._list_variables.update(
                    {variable_name: self.DBvariables(variables_data['Name'], variables_data['Adress'],
                                                     variables_data['Type'], variables_data['Initial value'], comment)}
                )

        def get_name(self):
            return self._db_name

        def db_number(self):
            return self._db_number

        def get_read_data(self):
            return self._db_read_data

        def set_read_data(self, read_data):
            self._db_read_data = read_data

        def get_write_data(self):
            return self._db_write_data

        def set_write_data(self, write_data):
            self._db_write_data = write_data

        def update_variables(self, update_dict):
            for key, value in update_dict.items():
                self._list_variables.update({key: value})

        def read_variable(self, *args):

            if len(args) == 0:
                variables = self._list_variables.keys()
            else:
                variables = args

            var_values = dict()
            for variable in variables:
                if variable in self._list_variables.keys():
                    var_inst = self._list_variables[variable]
                    var_inst.set_bytearray_read(self.get_read_data())
                    variable_value = var_inst.read_var(offset_on=True)
                else:
                    variable_value = \
                        'This variable {} is not in the variable list of the DB {}'.format(variable, self._db_name)
                var_values.update({variable: variable_value})
            return var_values

        def variable_list(self):
            """:return: the variable dict of the db """
            return self._list_variables

        def variable(self, variable_name):
            """
            :param variable_name: the name of the variable (str)
            :return: the variable instance of the the variable in the db list
            """
            assert variable_name in self._list_variables.keys(), 'variable_name does not exits'
            return self._list_variables[variable_name]

        class DBvariables:

            def __init__(self, variable_name, variable_adress, variable_type,
                         variable_init_value, variable_value=None, variable_comment=''):

                self._variable_name = variable_name
                self._variable_adress = convert_adress(variable_adress)
                self._variable_type = variable_type
                self._variable_init_value = variable_init_value
                self._variable_value = variable_value
                self._variable_comment = variable_comment
                self._variable_read_bytearray = bytearray()
                self._variable_write_bytearray = bytearray()
                self._size = self.set_size()

            def convert_init_value(self, init_value_string):

                if self._variable_type == "BOOL":

                    if init_value_string == 'true':
                        return True
                    else:
                        return False
                if self._variable_type == "REAL":
                    return float(init_value_string)

                if self._variable_type == "BYTE":

                    hex_string = (init_value_string.split('#')[-1])
                    if len(hex_string) == 1:
                        hex_string = '0' + hex_string

                    return bytearray.fromhex(hex_string)

                if self._variable_type == "WORD":
                    return init_value_string

                if self._variable_type == "DWORD":
                    return init_value_string

                if self._variable_type == "INT":
                    return int(init_value_string)

                if self._variable_type == "DINT":
                    return init_value_string

                if self._variable_type == "S5TIME":
                    return init_value_string

                if self._variable_type == "TIME":
                    return init_value_string

                if self._variable_type == "DATE":
                    return init_value_string

                if self._variable_type == "TIME _OF_DAY":
                    return init_value_string

                if self._variable_type == "CHAR":
                    return init_value_string

            def read_var(self, offset_on=False, read_bytearray=None):

                if offset_on is True:
                    offset = self.get_offset()
                else:
                    offset = 0

                if read_bytearray is None:
                    _bytearray_read = self.get_bytearray_read()
                else:
                    _bytearray_read = read_bytearray

                if self._variable_type == "BOOL":
                    var = snap7.util.get_bool(_bytearray_read, offset, self.get_bit_offset())

                if self._variable_type == "REAL":

                    var = snap7.util.get_real(_bytearray_read, offset)

                if self._variable_type == "BYTE":
                    var = util.get_byte(_bytearray_read, offset)

                if self._variable_type == "WORD":
                    var = util.get_word(_bytearray_read, offset)

                if self._variable_type == "DWORD":
                    var = snap7.util.get_dword(_bytearray_read, offset)

                if self._variable_type == "INT":
                    var = snap7.util.get_int(_bytearray_read, offset)

                if self._variable_type == "DINT":
                    var = util.get_dint(_bytearray_read, offset)

                if self._variable_type == "S5TIME":
                    var = util.get_s5time(_bytearray_read, offset)

                if self._variable_type == "TIME":
                    var = util.get_time(_bytearray_read, offset)

                if self._variable_type == "DATE":
                    var = util.get_date(_bytearray_read, offset)

                if self._variable_type == "TIME_OF_DAY":
                    var = util.get_time_of_day(_bytearray_read, offset)

                if self._variable_type =="CHAR":
                    var = util.get_char(_bytearray_read, offset)

                if self._variable_type[:6:] =="STRING":
                    if self._variable_type[7:-1:]:
                        var = snap7.util.get_string(_bytearray_read, offset,
                                                    self.get_size())
                    else:
                        var = 'under constrution'

                self._variable_value = var

                return var

            def write_var(self, value , offset_on=False, write_bytearray=None):

                if offset_on == True:
                    offset = self.get_offset()
                else:
                    offset = 0

                if write_bytearray is None:
                    print('underconstrution : feature create bytearray to write')
                    _bytearray_write = self.get_bytearray_write()
                else:
                    _bytearray_write = write_bytearray

                if self._variable_type == "BOOL":
                    snap7.util.set_bool(_bytearray_write, offset,
                                              self.get_bit_offset(), value)
                    return

                if self._variable_type == "REAL":
                    snap7.util.set_real(_bytearray_write, offset, value)
                    return

                if self._variable_type == "BYTE":
                    util.set_byte(_bytearray_write, offset, value)
                    return

                if self._variable_type == "WORD":
                    util.set_word(_bytearray_write, offset, value)
                    return

                if self._variable_type == "DWORD":
                    snap7.util.set_dword(_bytearray_write, offset, value)
                    return

                if self._variable_type == "INT":
                    snap7.util.set_int(_bytearray_write, offset, value)
                    return

                if self._variable_type == "DINT":
                    util.set_dint(_bytearray_write, offset, value)
                    return

                if self._variable_type == "S5TIME":
                    util.set_s5time(_bytearray_write, offset, value)
                    return

                if self._variable_type == "TIME":
                    util.set_time(_bytearray_write, offset, value)
                    return

                if self._variable_type == "DATE":
                    util.set_date(_bytearray_write, offset, value)
                    return

                if self._variable_type == "TIME_OF_DAY":
                    util.set_time_of_day(_bytearray_write, offset, value)
                    return

                if self._variable_type == "CHAR":
                    util.set_char(_bytearray_write, offset, value)
                    return

                if self._variable_type[:6:] == "STRING":
                    snap7.util.set_string(_bytearray_write, offset, value, self.get_size())
                    return

            def get_bytearray_read(self):
                return self._variable_read_bytearray

            def set_bytearray_read(self, var_bytearray):
                self._variable_read_bytearray= var_bytearray

            def get_bytearray_write(self):
                return self._variable_write_bytearray

            def set_bytearray_write(self, var_bytearray):
                self._variable_write_bytearray = var_bytearray

            def get_offset(self):
                return self._variable_adress[0]

            def get_bit_offset(self):
                return self._variable_adress[1]

            def set_size(self):

                if "STRING[" in self._variable_type:
                    # String type are stored as STRING[254] for example with 254 as size of the string
                    # That size has to be added with 2

                    size = int(self._variable_type[7:-1:]) + 2
                else:

                    size_dict = {"BOOL": 1,
                                 "REAL": 4,
                                 "BYTE": 2,
                                 "WORD": 2,
                                 "DWORD": 4,
                                 "INT": 2,
                                 "DINT": 4,
                                 "S5TIME": 2,
                                 "TIME": 4,
                                 "DATE": 2,
                                 "TIME_OF_DAY": 4,
                                 "CHAR": 2,
                                 }
                    size = size_dict[self._variable_type]

                return size

            def get_size(self):
                return self._size


if __name__ == '__main__':
    plc = PLC('10.34.0.95', rack=0, slot=2)
    print(plc.read_db('DB3'))
    print('-' * 10)
    print(plc.read_variable({'DB3': ['DB_CHAR']}))
    print('-'*10)
    print('here')
    plc.write_variable({'DB3': {'DB_CHAR': 'C'}})
    print('-' * 10)
    print(plc.read_variable({'DB3': ['DB_CHAR']}))

