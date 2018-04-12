import snap7
from snap7.util import *


class CommunicationPLC:

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
        try:
            self._connect = self._plc.connect(self._IP, rack, slot)
        except ConnectionError:
            raise ConnectionError("Can not connect to the PLC")

    def get_ip(self):
        return self._IP

    def set_IP(self, ip_adress, rack=None, slot=None):
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


    def set_DB_List(self, *args ):

        for args
        pass

# class DataBasePLC (CommunicationSiemens):
#
#
#
#     def get_db_row(db, start, size):
#         """
#         Here you see and example of readying out a part of a DB
#         Args:
#             db (int): The db to use
#             start (int): The index of where to start in db data
#             size (int): The size of the db data to read
#         """
#         type_ = snap7.snap7types.wordlen_to_ctypes[snap7.snap7types.S7WLByte]
#         data = client.db_read(db, start, type_, size)
#         # print_row(data[:60])
#         return data
#
#     def set_db_row(db, start, size, _bytearray):
#         """
#         Here we replace a piece of data in a db block with new data
#         Args:
#            db (int): The db to use
#            start(int): The start within the db
#            size(int): The size of the data in bytes
#            _butearray (enumerable): The data to put in the db
#         """
#         client.db_write(db, start, size, _bytearray)
#
