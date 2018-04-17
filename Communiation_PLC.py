import snap7

from snap7.util import *
from Read_DB_Data_Excell import ReadDB_Data


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

        for key, values in ReadDB_Data(file_name=file_name, file_dir=file_dir).read_data().items():
            self._db_list.update({key: self.DB_PLC(key, values)})

    def read_db(self, *args):
        self.connect()
        if len(args) == 0:

            dbs = self._db_list.keys()
        else:
            dbs = args

        db_values = dict()
        for db in dbs:
            db_instance = self._db_list[db]
            db_instance.set_read_data(self._plc.db_get(int(db[2::])))
            db_values.update({db: db_instance.read_variable()})
        self.disconnect()
        return db_values

    def read_variable(self, **kwargs):
        pass

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
            self._list_variables = dict()
            self._create_variables(dict_varia)
            self._db_read_data = bytearray()
            self._db_write_data = bytearray()

        def _create_variables(self, dict_varia):
            for key, items in dict_varia.items():
                if 'Comment' in items.keys():
                    comment = items['Comment']
                else:
                    comment = ''
                self._list_variables.update(
                    {key: self.DBvariables(items['Name'], items['Adress'], items['Type'],
                                      items['Initial value'], comment)}
                )

        def get_name(self):
            return self._db_name

        def get_read_data(self):
            return self._db_read_data

        def set_read_data(self, read_data):
            self._db_read_data = read_data

        def get_write_data(self):
            return self._db_write_data

        def set_write_data(self, write_data):
            self._db_write_data = write_data

        def update_variables(self, update_dict):
            for key , value in update_dict.items():
                self._list_variables.update({key:value})

        def read_variable(self, *args):

            if len(args) == 0:
                variables = self._list_variables.keys()
            else:
                variables = args

            var_values = dict()
            for variable in variables:
                if variable in self._list_variables.keys():
                    var_inst = self._list_variables[variable]
                    var_inst.set_var_read(self.get_read_data())
                    variable_value = var_inst.read_var()
                else:
                    variable_value = \
                        'This variable {} is not in the variable list of the DB {}'.format(variable, self._db_name)
                var_values.update({variable:variable_value})
            return var_values

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
                self._offset = 0

            def convert_init_value(self, init_value_string):

                if self._variable_type == "BOOL":

                    if init_value_string == 'true':
                        return True
                    else:
                        return False
                if self._variable_type =="REAL":
                    return float(init_value_string)

                if self._variable_type =="BYTE":

                    hex_string = (init_value_string.split('#')[-1])
                    if len(hex_string) == 1:
                        hex_string = '0' + hex_string

                    return bytearray.fromhex(hex_string)

                if self._variable_type =="WORD":
                    return init_value_string

                if self._variable_type =="DWORD":
                    return init_value_string

                if self._variable_type =="INT":
                    return int(init_value_string)

                if self._variable_type =="DINT":
                    return init_value_string

                if self._variable_type =="S5TIME":
                    return init_value_string

                if self._variable_type =="TIME":
                    return init_value_string

                if self._variable_type =="DATE":
                    return init_value_string

                if self._variable_type =="TIME _OF_DAY":
                    return init_value_string

                if self._variable_type =="CHAR":
                    return init_value_string

            def read_var(self):

                if self._variable_type == "BOOL":
                    var = snap7.util.get_bool(self.get_var_read(), self._variable_adress[0], self._variable_adress[1])

                if self._variable_type =="REAL":

                    var = snap7.util.get_real(self.get_var_read(), self._variable_adress[0])

                if self._variable_type =="BYTE":

                    var = 'under constrution'

                if self._variable_type =="WORD":
                    var = 'under constrution'

                if self._variable_type =="DWORD":
                    var = snap7.util.get_dword(self.get_var_read(), self._variable_adress[0])

                if self._variable_type =="INT":
                    var = snap7.util.get_int(self.get_var_read(), self._variable_adress[0])

                if self._variable_type =="DINT":
                    var = 'under constrution'

                if self._variable_type =="S5TIME":
                    var = 'under constrution'

                if self._variable_type =="TIME":
                    var = 'under constrution'

                if self._variable_type =="DATE":
                    var = 'under constrution'

                if self._variable_type =="TIME _OF_DAY":
                    var = 'under constrution'

                if self._variable_type =="CHAR":
                    var = 'under constrution'

                if self._variable_type[:6:] =="STRING":
                    if self._variable_type[7:-1:]:
                        var = snap7.util.get_string(self.get_var_read(), self._variable_adress[0],
                                                 int(self._variable_type[7:-1:]))
                    else:
                        var = 'under constrution'

                self._variable_value = var

                return var

            def get_var_read(self):
                return self._variable_read_bytearray

            def set_var_read(self, var_bytearray):
                self._variable_read_bytearray= var_bytearray

            def get_var_write(self):
                return self._variable_write_bytearray

            def set_var_write(self, var_bytearray):
                self._variable_write_bytearray = var_bytearray


def convert_adress(adress_string):
    split = adress_string.strip().split('.')
    adress_tuple = (int(split[0]), int(split[1]))

    return adress_tuple



if __name__ == '__main__':
    plc = PLC('10.34.0.95', rack=0, slot=2)
    print(plc.read_db())
