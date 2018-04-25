import struct

from datetime import datetime, time, timedelta, date


def test_time(_bytearray):
    data = _bytearray

    print('-' * 20)
    print(_bytearray)
    print('-' * 20+ 'Raw')
    for i, byte in enumerate(data):
        b ='{0:b}'.format(byte)
        b = '0'*(8-len(b))+b
        b = b[0:4]+' '+b[4:8]
        print('raw data[{2}] int = {0}  b= {1}'.format(byte, b, i))

    # print('-' * 20)
    #
    # value = struct.unpack('>i', struct.pack('4B', *data))[0]
    # print(value)
    # timevalue = timedelta(microseconds=value*1000)
    # print(timevalue)
    # print('-' * 20)
    # print(timevalue.microseconds)
    # print('-' * 20)


def convert_adress(adress_string):

    if adress_string[0] == ('I' or 'Q'):
        adress_string = adress_string[2::]

    split = adress_string.strip().split('.')
    adress_tuple = (int(split[0]), int(split[1]))

    return adress_tuple


def get_bool(_bytearray, byte_index, bool_index):
    """
    Get the boolean value from location in bytearray
    """
    index_value = 1 << bool_index
    byte_value = _bytearray[byte_index]
    current_value = byte_value & index_value
    return current_value == index_value


def set_bool(_bytearray, byte_index, bool_index, value):
    """
    Set boolean value on location in bytearray
    """
    assert value in [0, 1, True, False]
    current_value = get_bool(_bytearray, byte_index, bool_index)
    index_value = 1 << bool_index

    # check if bool already has correct value
    if current_value == value:
        return

    if value:
        # make sure index_v is IN current byte
        _bytearray[byte_index] += index_value
    else:
        # make sure index_v is NOT in current byte
        _bytearray[byte_index] -= index_value


def set_int(_bytearray, byte_index, _int):
    """
    Set value in bytearray to int
    """
    # make sure were dealing with an int
    _int = int(_int)
    _bytes = struct.unpack('2B', struct.pack('>h', _int))
    _bytearray[byte_index:byte_index + 2] = _bytes


def get_int(_bytearray, byte_index):
    """
    Get int value from bytearray.
    int are represented in two bytes
    """
    data = _bytearray[byte_index:byte_index + 2]
    value = struct.unpack('>h', struct.pack('2B', *data))[0]
    return value


def set_real(_bytearray, byte_index, real):
    """
    Set Real value
    make 4 byte data from real
    """
    real = float(real)
    real = struct.pack('>f', real)
    _bytes = struct.unpack('4B', real)
    for i, b in enumerate(_bytes):
        _bytearray[byte_index + i] = b


def get_real(_bytearray, byte_index):
    """
    Get real value. create float from 4 bytes
    """
    x = _bytearray[byte_index:byte_index + 4]
    real = struct.unpack('>f', struct.pack('4B', *x))[0]
    return real


def set_string(_bytearray, byte_index, value, max_size):
    """
    Set string value
    :params value: string data
    :params max_size: max possible string size
    """
    if six.PY2:
        assert isinstance(value, (str, unicode))
    else:
        assert isinstance(value, str)

    size = len(value)
    # FAIL HARD WHEN trying to write too much data into PLC
    if size > max_size:
        raise ValueError('size %s > max_size %s %s' % (size, max_size, value))
    # set len count on first position
    _bytearray[byte_index + 1] = len(value)

    i = 0
    # fill array which chr integers
    for i, c in enumerate(value):
        _bytearray[byte_index + 2 + i] = ord(c)

    # fill the rest with empty space
    for r in range(i + 1, _bytearray[byte_index]):
        _bytearray[byte_index + 2 + r] = ord(' ')


def get_string(_bytearray, byte_index, max_size):
    """
    parse string from bytearray
    """
    size = _bytearray[byte_index + 1]

    if max_size < size:
        print("the string is to big for the size encountered in specification")
        print("WRONG SIZED STRING ENCOUNTERED")
        size = max_size

    data = map(chr, _bytearray[byte_index + 2:byte_index + 2 + size])
    return "".join(data)


def get_dword(_bytearray, byte_index):
    """
    Get word value from bytearray.
    double word are represented in four bytes
    (word = unsigned int)
    """
    data = _bytearray[byte_index:byte_index + 4]
    dword = struct.unpack('>I', struct.pack('4B', *data))[0]
    return dword


def set_dword(_bytearray, byte_index, dword):
    """
    Set value in bytearray to double word
    """
    dword = int(dword)
    _bytes = struct.unpack('4B', struct.pack('>I', dword))
    for i, b in enumerate(_bytes):
        _bytearray[byte_index + i] = b


def get_word(_bytearray, byte_index):
    """
    Get word value from bytearray.
    word are represented in two bytes
    (word = unsigned int)
    """
    data = _bytearray[byte_index:byte_index + 2]
    value = struct.unpack('>H', struct.pack('2B', *data))[0]
    return value


def set_word(_bytearray, byte_index, _word):
    """
    Set value in bytearray to word
    """
    # make sure were dealing with an word
    _word = int(_word)
    assert _word > 0, 'a word can only be a positive value'
    _bytes = struct.unpack('2B', struct.pack('>H', _word))
    _bytearray[byte_index:byte_index + 2] = _bytes


def set_dint(_bytearray, byte_index, _dint):
    """
    Set value in bytearray to int
    """
    # make sure were dealing with an int
    _dint = int(_dint)
    _bytes = struct.unpack('4B', struct.pack('>i', _dint))
    _bytearray[byte_index:byte_index + 4] = _bytes


def get_dint(_bytearray, byte_index):
    """
    Get int value from bytearray.
    int are represented in two bytes
    """

    data = _bytearray[byte_index:byte_index + 4]
    value = struct.unpack('>i', struct.pack('4B', *data))[0]
    return value


def set_byte(_bytearray, byte_index, _byte):
    """
    Set value in bytearray to hex string
    """
    # make sure were dealing with an int

    _int = int(_byte, 0)
    _bytes = struct.unpack('2B', struct.pack('>h', _int))
    _bytearray[byte_index:byte_index + 2] = _bytes
    _bytearray.reverse()


def get_byte(_bytearray, byte_index):
    """
    Get hex value from bytearray.
    hex value is repesented into a string
    """

    data = _bytearray[byte_index:byte_index + 2]
    data.reverse()

    value = struct.unpack('>h', struct.pack('2B', *data))[0]

    value = hex(value)

    return value


def set_time(_bytearray, byte_index, _time: timedelta):
    """
    Set value in bytearray to time
    """

    ms = _time.total_seconds()*1000

    _dint = int(ms)
    print(_dint)
    _bytes = struct.unpack('4B', struct.pack('>i', _dint))
    _bytearray[byte_index:byte_index + 4] = _bytes


def get_time(_bytearray, byte_index):
    """
    Get time value from bytearray.
<<<<<<< HEAD
    time are represented in two bytes
=======
    time are represented in four bytes
>>>>>>> com_PLC
    time are set in ms
    """
    data = _bytearray[byte_index:byte_index + 4]
    value = struct.unpack('>i', struct.pack('4B', *data))[0]
    timevalue = timedelta(milliseconds=value)

    return timevalue

def set_s5time(_bytearray, byte_index, _time: timedelta):
    """
    Set value in bytearray to s5time
    """
    print('S5time under constrution')
    # ms = _time.total_seconds()*1000
    #
    # _dint = int(ms)
    #
    # _bytes = struct.unpack('2B', struct.pack('>h', _dint))
    # _bytearray[byte_index:byte_index + 2] = _bytes


def get_s5time(_bytearray, byte_index):
    """
    Get time value from bytearray.
    time are represented in two bytes
    time are set in 10ms
    """
    print('S5time under constrution')
    return 'S5time under constrution'
    # test_time(_bytearray)
    # data = _bytearray[byte_index:byte_index + 2]
    # value = struct.unpack('>h', struct.pack('2B', *data))[0]
    # print(value)
    # timevalue = timedelta(milliseconds=value*10)
    #
    # return timevalue


def set_date(_bytearray, byte_index, _date: date):
    """
    Set value in bytearray to time
    """

    days = _date-date(year=1990, month=1, day=1)
    _int = int(days.days)
    set_word(_bytearray, byte_index, _int)


def get_date(_bytearray, byte_index):
    """
    Get time value from bytearray.
    time are represented in two bytes
    time are set in ms
    """

    value=get_word(_bytearray,byte_index)

    timevalue = date(year=1990, month=1, day=1) + timedelta(days=value)
    print(type(timevalue))

    return timevalue

def set_time_of_day(_bytearray, byte_index, tod:timedelta):
    """
    Set value in bytearray to int
    """

    # make sure were dealing with an int
    ms = tod.total_seconds() * 1000
    if int(ms // (3600 * 10 ** 3))>23:
        raise ValueError('the value is to high')
    else:
        _int = int(ms)
        set_dword(_bytearray, byte_index, _int)


def get_time_of_day(_bytearray, byte_index):
    """
    Get int value from bytearray.
    int are represented in two bytes
    """
    value = get_dword(_bytearray,byte_index)

    time_value = time(hour=int(value//(3600*10**3)), minute=int(value/1000 % 3600) // 60,
                      second=int(value/1000 % 60), microsecond=(int(value*1000)) % 1000)

    return time_value


def set_char(_bytearray, byte_index, char):
    """
    Set value in bytearray to int
    """

    _int = ord(char)
    _bytes = struct.unpack('2B', struct.pack('h', _int))
    _bytearray[byte_index:byte_index + 2] = _bytes


def get_char(_bytearray, byte_index):
    """
    get char value from bytearray
    """
    data = _bytearray[byte_index:byte_index + 2]
    value = struct.unpack('h', struct.pack('2B', *data))[0]
    return chr(value)


def size(datatype):
    '''
    :param datatype: the datatype as a string
    :return: the byte size of the data type
    '''
    types = {
        'BOOL': 1,
        'BYTE': 2,
        'WORD': 2,
        'DWORD': 4,
        'INT': 2,
        'DINT': 4,
        'REAL': 4,
        'S5TIME': 2,
        'TIME': 2,
        'DATE': 2,
        'TIME_OF_DAY': 4,
        'CHAR': 2,
        'STRING[254]': 256
    }

    assert datatype in types, \
        ('the datatype "{}" does not exits, it must be one of the following {}'.format(datatype, types.keys()))

    return types[datatype]
