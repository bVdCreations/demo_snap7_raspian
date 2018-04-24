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

    def __init__(self, ip_adress, rack=None, slot=None, file_location=''):
        """
        :param ip_adress: ip adress in string
        :param rack: rack number
        :param slot: slot number
        """
        self._plc = snap7.client.Client()
        self._ip = ip_adress
        self._rack = rack
        self._slot = slot
        self._db_list = dict()
        self.create_db_inst_from_excell(file_name=file_location)
        self._connect = self.connect()
        self.disconnect()

    def get_ip(self):
        """
        :return: the IP adress of the PLC
        """
        return self._ip

    def set_ip(self, ip_adress, rack=None, slot=None):
        """disconnect the plc
        set new Ip adress
        make a new connection
        if the connection is made return True otherwise False
        :param ip_adress: string
        :param rack: rack number
        :param slot: slot number
        """

        if rack is None:
            rack = self._rack

        if slot is None:
            slot = self._slot

        try:
            self._plc.disconnect()
            self._connect = self._plc.connect(ip_adress, rack, slot)
            self.disconnect()
            self._ip = ip_adress
            self._rack = rack
            self._slot = slot
            return True
        except :
            return False

    def create_db_inst_from_excell(self, file_name='', file_dir=''):
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
            # assert args in self._db_list, 'one or more arguments do not exits'
            dbs = args

        db_values = dict()
        # empty dict for storing the read values

        for db_name in dbs:
            db_instance = self._db_list[db_name]
            _bytearray_db =(self._plc.db_get(db_instance.db_number()))
            # read the complete db byte array
            db_values.update({db_name: dict()})

            for variable_name, variable_inst in db_instance.variable_dict().items():
                variable_value = variable_inst.read_var(offset_on=True, read_bytearray=_bytearray_db)
                db_values[db_name].update({variable_name: variable_value})

        self.disconnect()
        return db_values

    def read_variable(self, dict_read):

        if self._check_input(dict_read):
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

        if self._check_input(dict_write):
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
    def _check_input(self, dict_input):
        if len(dict_input) == 0:
            return False
        else:
            return True

    def connect(self):
        if self._plc.get_connected():
            print("already connected")
        else:
            try:
                return self._plc.connect(self._ip, self._rack, self._slot)
            except ConnectionError:
                raise ConnectionError("Can not connect to the PLC")

    def disconnect(self):
        self._plc.disconnect()

    class DB_PLC:

        def __init__(self, db_name, dict_varia):

            self._db_name = db_name
            self._db_number = int(db_name[2::])
            self._dict_variables = dict()
            self._create_variables(dict_varia)


        def _create_variables(self, dict_varia):
            """
            create variable instances and updates it in _dict_variables
            :param dict_varia: {variable_name : {'Name': variable_name , 'Ardess': '5.3' ,
                                                'Type': 'BOOL', 'Initial value': False , 'Comment': comment string} }
            :return: None
            """
            for variable_name, variables_data in dict_varia.items():
                if 'Comment' in variables_data.keys():
                    comment = variables_data['Comment']
                else:
                    comment = ''
                self._dict_variables.update(
                    {variable_name: self.DBvariables(variables_data['Name'], variables_data['Adress'],
                                                     variables_data['Type'], variables_data['Initial value'], comment)}
                )

        def get_name(self):
            return self._db_name

        def db_number(self):
            return self._db_number

        def update_variables(self, update_dict):
            for key, value in update_dict.items():
                self._dict_variables.update({key: value})

        def variable_dict(self):
            """:return: the variable dict of the db """
            return self._dict_variables

        def variable(self, variable_name):
            """
            :param variable_name: the name of the variable (str)
            :return: the variable instance of the the variable in the db list
            """
            assert variable_name in self._dict_variables.keys(), 'variable_name does not exits'
            return self._dict_variables[variable_name]

        class DBvariables:

            def __init__(self, variable_name, variable_adress, variable_type,
                         variable_init_value_string, variable_value=None, variable_comment=''):

                self._variable_name = variable_name
                self._variable_adress = convert_adress(variable_adress)
                self._variable_type = variable_type
                self._variable_value = variable_value
                self._variable_comment = variable_comment
                self._variable_init_value = None
                self._size = None
                self.convert_input(variable_init_value_string)

            def convert_input(self, init_value_string):
                """
                sets the size of the the variable
                sets the initial value
                :param init_value_string:
                :return:
                """

                if self._variable_type == "BOOL":

                    self._size = 1

                    if init_value_string == 'true':
                        self._variable_init_value = True
                    else:
                        self._variable_init_value = False

                if self._variable_type == "REAL":

                    self._size = 4
                    self._variable_init_value = float(init_value_string)

                if self._variable_type == "BYTE":

                    hex_string = (init_value_string.split('#')[-1])
                    self._size = int(init_value_string.split('#')[1])/8

                    if len(hex_string) == 1:
                        hex_string = '0' + hex_string

                    self._variable_init_value = bytearray.fromhex(hex_string)

                if self._variable_type == "WORD":
                    self._size = 2
                    self._variable_init_value = init_value_string

                if self._variable_type == "DWORD":
                    self._size = 4
                    self._variable_init_value = init_value_string

                if self._variable_type == "INT":
                    self._size = 2
                    self._variable_init_value = int(init_value_string)

                if self._variable_type == "DINT":
                    self._size = 2
                    self._variable_init_value = init_value_string

                if self._variable_type == "S5TIME":
                    self._size = 2
                    self._variable_init_value = init_value_string

                if self._variable_type == "TIME":
                    self._size = 4
                    self._variable_init_value = init_value_string

                if self._variable_type == "DATE":
                    self._size = 2
                    self._variable_init_value = init_value_string

                if self._variable_type == "TIME _OF_DAY":
                    self._size = 4
                    self._variable_init_value = init_value_string

                if self._variable_type == "CHAR":
                    self._size = 2
                    self._variable_init_value = init_value_string

                if "STRING[" in self._variable_type:
                    # String type are stored as STRING[254] for example with 254 as size of the string
                    # That size has to be added with 2

                    self._size = int(self._variable_type[7:-1:]) + 2
                    self._variable_init_value = init_value_string

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

                if self._variable_type == "CHAR":
                    var = util.get_char(_bytearray_read, offset)

                if self._variable_type[:6:] == "STRING":
                    if self._variable_type[7:-1:]:
                        var = snap7.util.get_string(_bytearray_read, offset,
                                                    self.get_size())
                    else:
                        var = 'under constrution'

                self._variable_value = var

                return var

            def write_var(self, value , offset_on=False, write_bytearray=None):
                """

                :param value: the value that needs to be written in the db
                :param offset_on: if True the offset = get_offset if false offset=0
                                  this depend if the bytearray is a full db or only the variable part of the db
                :param write_bytearray: if = bytearray this byttearray will be used to write the value in
                                        other wise an empty bytearray will be created
                :return:the bytearray with the written value inside
                """

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
                    util.set_bool(_bytearray_write, offset,
                                              self.get_bit_offset(), value)
                    return _bytearray_write

                if self._variable_type == "REAL":
                    util.set_real(_bytearray_write, offset, value)
                    return _bytearray_write

                if self._variable_type == "BYTE":
                    util.set_byte(_bytearray_write, offset, value)
                    return _bytearray_write

                if self._variable_type == "WORD":
                    util.set_word(_bytearray_write, offset, value)
                    return _bytearray_write

                if self._variable_type == "DWORD":
                    util.set_dword(_bytearray_write, offset, value)
                    return _bytearray_write

                if self._variable_type == "INT":
                    util.set_int(_bytearray_write, offset, value)
                    return _bytearray_write

                if self._variable_type == "DINT":
                    util.set_dint(_bytearray_write, offset, value)
                    return _bytearray_write

                if self._variable_type == "S5TIME":
                    util.set_s5time(_bytearray_write, offset, value)
                    return _bytearray_write

                if self._variable_type == "TIME":
                    util.set_time(_bytearray_write, offset, value)
                    return _bytearray_write

                if self._variable_type == "DATE":
                    util.set_date(_bytearray_write, offset, value)
                    return _bytearray_write

                if self._variable_type == "TIME_OF_DAY":
                    util.set_time_of_day(_bytearray_write, offset, value)
                    return _bytearray_write

                if self._variable_type == "CHAR":
                    util.set_char(_bytearray_write, offset, value)
                    return _bytearray_write

                if self._variable_type[:6:] == "STRING":
                    util.set_string(_bytearray_write, offset, value, self.get_size())
                    return _bytearray_write

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

            def get_size(self):
                return self._size






if __name__ == '__main__':
    plc = PLC('10.34.0.95', rack=0, slot=2, file_location='I_O_info_plc//DBs_PLC_300.xlsx')
    print(plc.read_db('DB3'))
    print('-' * 10)
    print(plc.read_variable({'DB3': ['DB_CHAR']}))
    print('-'*10)
    print('here')
    plc.write_variable({'DB3': {'DB_CHAR': 'C'}})
    print('-' * 10)
    print(plc.read_variable({'DB3': ['DB_CHAR']}))

