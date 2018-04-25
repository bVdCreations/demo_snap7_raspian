import snap7
import util
from datetime import datetime, time, timedelta, date


# from snap7.util import *
from Read_DB_Data_Excell import ReadDB_Data


class PLC:

    def __init__(self, file_name, file_location='I_O_info_plc//'):
        """
        :param ip_adress: ip adress in string
        :param rack: rack number
        :param slot: slot number
        """
        self._plc = snap7.client.Client()

        self._plc_info = dict()
        self._db_dict = dict()

        self._input_dict = dict()
        self._output_dict = dict()

        self.read_all_info_excell(file_name=file_name, file_dir=file_location)
        self._connect = self.connect()
        self.disconnect()

    def get_ip(self):
        """
        :return: the IP adress of the PLC
        """
        return self._plc_info['IP_adress']

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
            rack = self._plc_info['rack']

        if slot is None:
            slot = self._plc_info['slot']

        try:
            self._plc.disconnect()
            self._connect = self._plc.connect(ip_adress, rack, slot)
            self.disconnect()
            self._plc_info['IP_adress'] = ip_adress
            self._plc_info['rack'] = rack
            self._plc_info['slot'] = slot
            return True
        except :
            return False

    def connect(self):
        if self._plc.get_connected():
            print("already connected")
        else:
            try:
                return self._plc.connect(self._plc_info['IP_adress'], self._plc_info['rack'], self._plc_info['slot'])
            except ConnectionError:
                raise ConnectionError("Can not connect to the PLC")

    def disconnect(self):
        self._plc.disconnect()

    def read_all_info_excell(self, file_name='', file_dir=''):
        """
        this function files in the dict _plc_info and _db_dict
        by reading the datat from an excell file

        _db_dict
        the data is structured in a multi level dictionary
        {DB_NAME:{variable name : {variable_info : 'info', ... }   , variable name2: {...} } ,
         DB_NAME2:{... }  }
        from that dict it updates
        a dictionary with the names of the db's as keys and an instance of the class DB_PLC as value

        _plc_info
        a dict with the keys IP_adress, rack and slot with it's values
        """

        read_file = ReadDB_Data(file_name=file_name, file_dir=file_dir)

        # _db_dict
        for db_name, variables_dict in read_file.read_data_dbs().items():
            self._db_dict.update({db_name: self.DB_PLC(db_name, variables_dict)})

        # _plc_info
        self._plc_info = read_file.read_info_plc()


    def read_all_db(self, *args):

        """
        This method read the complete DB from the PLC
        :param args: db_names (if None it will read all the db's)
        :return: dict with the read values
        """
        self.connect()
        if len(args) == 0:
            dbs = self._db_dict.keys()
        else:
            # assert args in self._db_list, 'one or more arguments do not exits'
            dbs = args

        db_values = dict()
        # empty dict for storing the read values

        for db_name in dbs:
            db_instance = self._db_dict[db_name]
            _bytearray_db =(self._plc.db_get(db_instance.db_number()))
            # read the complete db byte array
            db_values.update({db_name: dict()})

            for variable_name, variable_inst in db_instance.variable_dict().items():
                variable_value = variable_inst.read_var(offset_on=True, read_bytearray=_bytearray_db)
                db_values[db_name].update({variable_name: variable_value})

        self.disconnect()
        return db_values


    def read_db_variables(self, dict_read):


        if self._check_input(dict_read):
            self.connect()
            dict_value = dict()
            for db_name, variables in dict_read.items():
                db = self._db_dict[db_name]
                dict_value.update({db_name: dict()})
                for variable_name in variables:
                    variable_inst = db.variable(variable_name)
                    _bytearray = self._plc.db_read(db.db_number(), variable_inst.get_offset(), variable_inst.get_size())

                    # util.test_time(_bytearray)


                    value = variable_inst.read_var(read_bytearray=_bytearray)
                    dict_value[db_name].update({variable_name: value})

            self.disconnect()
            return dict_value

    def write_variable(self, dict_write):

        if self._check_input(dict_write):
            self.connect()
            for db_name, variables in dict_write.items():
                db = self._db_dict[db_name]
                for variable_name, value in variables.items():
                    variable_inst = db.variable(variable_name)
                    _bytearray = self._plc.db_read(db.db_number(), variable_inst.get_offset(), variable_inst.get_size())

                    variable_inst.write_var(value, write_bytearray=_bytearray)


                    self._plc.db_write(db.db_number(), variable_inst.get_offset(), _bytearray)

            self.disconnect()


    # To do
    def _check_input(self, dict_input):
        pass



    def read_input(self, input_name):
        """
        this method read the value of the given input
        :param input_name: the name of the input
        :return: value of the input
        """
        # check if input name exits in the input dict
        assert input_name in self._input_dict, \
            ('the input "{}" is not in the input dict = {}'.format(input_name, self._input_dict.keys()))

        # connect to the plc
        self.connect()
        input_instance = self._input_dict[input_name]
        # read the bytearray
        _bytearray = self._plc.read_area(areas['PA'], 0, input_instance.get_byte(), input_instance.get_size())

        # get the value from the bytearray
        value = input_instance.read_bytearray(_bytearray)

        # discoonect from the plc
        self.disconnect()
        return value

    def write_input(self, input_name, value):
        """
        this method writes a value into a given input
        :param input_name: the name of the input
        :param value: the value that needs to written into the input
        :return: value of the input
        """
        # check if input name exits in the input dict
        assert input_name in self._input_dict, \
            ('the input "{}" is not in the input dict = {}'.format(input_name, self._input_dict.keys()))

        # connect to the plc
        self.connect()
        input_instance = self._input_dict[input_name]
        # read the bytearray
        _bytearray = self._plc.read_area(areas['PA'], 0, input_instance.get_byte(), input_instance.get_size())

        # write the value in the bytearray
        input_instance.write_bytearray(_bytearray, value)

        # write the nex bytearray in the plc
        self._plc.write_area(areas['PA'], 0, input_instance.get_byte(), _bytearray)

        # disconnect from the plc
        self.disconnect()


    # To do
    def _check_input_db(self, dict_input):

        if len(dict_input) == 0:
            return False
        else:
            return True

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

        # def update_variables(self, update_dict):
        #     for key, value in update_dict.items():
        #         self._dict_variables.update({key: value})


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
                self._variable_adress = util.convert_adress(variable_adress)
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

            def get_offset(self):
                return self._variable_adress[0]

            def get_bit_offset(self):
                return self._variable_adress[1]

            def get_size(self):
                return self._size


    class IO_PLC:

        def __init__(self, symbol_name, adress_string, data_type, comment=''):
            """

            :param symbol_name: the name off the io
            :param adress_string: the adress of the io (example : I  4.0 )
            :param data_type: type of the data of the IO
            :param comment: the comment that is given in the symbol table
            """
            self._synbol_name = symbol_name
            self._type = adress_string[0:2:].strip()
            self._adress_byte, self._ardess_bit = util.convert_adress(adress_string)
            self._size = util.size(data_type)
            self._data_type = data_type
            self._comment = comment

        def read_bytearray(self, _read_bytearry, offset_on=False):

            if offset_on is True:
                offset = self.get_offset()
            else:
                offset = 0

            if self._type == "BOOL":
                return util.get_bool(_read_bytearry, offset, self.get_bit_offset())

            if self._type == "BYTE":
                return util.get_byte(_read_bytearry, offset)

            if self._type == "WORD":
                return util.get_word(_read_bytearry, offset)

            if self._type == "DWORD":
                return snap7.util.get_dword(_read_bytearry, offset)

        def write_bytearray(self, write_bytearray, value, offset_on=False):
            """

            :param value: the value that needs to be written in the db
            :param offset_on: if True the offset = get_offset if false offset=0
                              this depend if the bytearray is a full db or only the variable part of the db
            :param write_bytearray: this byttearray will be used to write the value in
            :return:the bytearray with the written value inside
            """

            if offset_on is True:
                offset = self.get_offset()
            else:
                offset = 0

            if self._variable_type == "BOOL":
                util.set_bool(write_bytearray, offset,
                              self.get_bit_offset(), value)
                return write_bytearray

            if self._variable_type == "BYTE":
                util.set_byte(write_bytearray, offset, value)
                return write_bytearray

            if self._variable_type == "WORD":
                util.set_word(write_bytearray, offset, value)
                return write_bytearray

            if self._variable_type == "DWORD":
                util.set_dword(write_bytearray, offset, value)
                return write_bytearray


areas = {
    'PE': 0x81,
    'PA': 0x82,
    'MK': 0x83,
    'DB': 0x84,
    'CT': 0x1C,
    'TM': 0x1D,
}



if __name__ == '__main__':
    plc = PLC('DBs_PLC_300.xlsx')
    print(plc.read_db('DB3'))
    print('-' * 10)
    print(plc.read_variable({'DB3': ['DB_CHAR']}))
    print('-'*10)
    print('here')
    plc.write_variable({'DB3': {'DB_CHAR': 'C'}})
    print('-' * 10)
    print(plc.read_variable({'DB3': ['DB_CHAR']}))
