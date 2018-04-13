import snap7

from snap7.util import *
from Read_DB_Data_Excell import ReadDB_Data


class PLC:

    def __init__(self, ip_adress, rack=None, slot=None):
        """
        :param ip_adress: string
        :param rack: int
        :param slot: int
        """
        self._plc = snap7.client.Client()
        self._IP = ip_adress
        self._rack = rack
        self._slot = slot
        self._DB_list = dict()
        self.create_db_inst_from_excell()
        try:
            self._connect = self._plc.connect(self._IP, rack, slot)
        except ConnectionError:
            raise ConnectionError("Can not connect to the PLC")

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

        for key, values in ReadDB_Data(file_name=file_name, file_dir=file_dir).read_data():
            self._DB_list.update({key: DB_PLC(key, values)})




class DB_PLC(snap7.util.DB):

    def __init__ (self,db_name, **kwargs):
        self._name = db_name
        self._list_variables = dict()
        self._create__intc_variables(**kwargs)
        self._db_read_data = bytearray()
        self._db_write_data = bytearray()

    def _create_intc_variables(self, **kwargs):
        for key, items in kwargs:
            self._list_variables.update(
                {key: self.DBvariables(items['name'], items['adress'], items['type'],
                                       items['Initial value'], items['comment'])}
            )


class DBvariables:

    def __init__(self, variable_name , variable_adress, variable_type,
                 variable_init_value, variable_value=None, variable_comment=None):

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

    def convert_adress(adress_string):
        split = adress_string.strip().split('.')
        adress_tuple = (int(split[0]), int(split[1]))

        return adress_tuple
    # def ReadMemory(plc,byte,bit,datatype):
    #     result = plc.read_area(areas['MK'],0,byte,datatype)
    #     if datatype==S7WLBit:
    #         return get_bool(result,0,bit)
    #     elif datatype==S7WLByte or datatype==S7WLWord:
    #         return get_int(result,0)
    #     elif datatype==S7WLReal:
    #         return get_real(result,0)
    #     elif datatype==S7WLDWord:
    #         return get_dword(result,0)
    #     else:
    #         return None
    #
    # def WriteMemory(plc,byte,bit,datatype,value):
    #     result = plc.read_area(areas['MK'],0,byte,datatype)
    #     if datatype==S7WLBit:
    #         set_bool(result,0,bit,value)
    #     elif datatype==S7WLByte or datatype==S7WLWord:
    #         set_int(result,0,value)
    #     elif datatype==S7WLReal:
    #         set_real(result,0,value)
    #     elif datatype==S7WLDWord:
    #         set_dword(result,0,value)
    #     plc.write_area(areas["MK"],0,byte,result)





# def ReadMemory(plc,byte,bit,datatype):
#     result = plc.read_area(areas['MK'],0,byte,datatype)
#     if datatype==S7WLBit:
#         return get_bool(result,0,bit)
#     elif datatype==S7WLByte or datatype==S7WLWord:
#         return get_int(result,0)
#     elif datatype==S7WLReal:
#         return get_real(result,0)
#     elif datatype==S7WLDWord:
#         return get_dword(result,0)
#     else:
#         return None
#
# def WriteMemory(plc,byte,bit,datatype,value):
#     result = plc.read_area(areas['MK'],0,byte,datatype)
#     if datatype==S7WLBit:
#         set_bool(result,0,bit,value)
#     elif datatype==S7WLByte or datatype==S7WLWord:
#         set_int(result,0,value)
#     elif datatype==S7WLReal:
#         set_real(result,0,value)
#     elif datatype==S7WLDWord:
#         set_dword(result,0,value)
#     plc.write_area(areas["MK"],0,byte,result)


