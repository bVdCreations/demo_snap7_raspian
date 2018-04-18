import snap7

from snap7.util import *


if '__main__' == __name__ :
    plc = snap7.client.Client()
    plc.connect('10.34.0.95', 0, 2)
    alldata = plc.db_read(1,0,1)
    print(alldata)
    snap7.util.set_bool(alldata, 0, 0 , True)
    plc.db_write(1, 0, alldata)
    plc.disconnect()