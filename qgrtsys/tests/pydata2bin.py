import qgrtsys.global_config as gc
import qgrtsys.core.data_transfer as dt
import struct


def int2bytes(value):
    '''Convert a Python interger to Quingo binary data.
    '''
    assert(isinstance(value, int))

    return value.to_bytes(gc.QU_INT_SIZE, byteorder=gc.endian, signed=True)


def bool2bytes(value):
    '''Convert a Python boolean value to Quingo binary data.
    '''
    assert(isinstance(value, bool))

    return value.to_bytes(gc.QU_BOOL_SIZE, byteorder=gc.endian, signed=True)


def double2bytes(value):
    '''Convert a Python boolean value to Quingo binary data.
    '''
    assert(isinstance(value, float))
    return struct.pack('<f', value)


class Pydata_2_qg_bin():
    def __init__(self, buf_size: int = 1000):
        # buf is used to store the converted data
        self.buf = bytearray(buf_size)
        # free is the starting point of the free space
        self.heap_head = 0

    def get_result(self):
        return self.buf[:self.heap_head]

    def append_bytes_to_stack(self, bytes, pos: int):

        end_pos = pos + len(bytes)

        self.buf[pos: end_pos] = bytes

        return end_pos

    def write_int(self, int_val: int, pos: int):
        '''Convert the python integer `int_val` into quingo binary and write this binary into buf
        with the starting address being `pos`.

        Args:
          - int_val: the python data to convert
          - pos: the starting address to allocate the binary of the integer

        Return:
          - int: the address of buf to allocate the next binary data
        '''

        int_bytes = int2bytes(int_val)

        return self.append_bytes_to_stack(int_bytes, pos)

    def write_bool(self, bool_val: bool, pos: int):
        '''Convert the python boolean value `int_val` into quingo binary and write this binary into
        buf with the starting address being `pos`.

        Args:
          - bool_val: the python data to convert
          - pos: the starting address to allocate the binary of the boolean value

        Return:
          - int: the address of buf to allocate the next binary data
        '''
        bool_bytes = bool2bytes(bool_val)

        return self.append_bytes_to_stack(bool_bytes, pos)

    def write_double(self, double_val: float, pos: int):
        '''Convert the python float value `double_val` into quingo binary and write this binary
        into buf with the starting address being `pos`.

        Args:
          - double_val: the python data to convert
          - pos: the starting address to allocate the binary of the double value

        Return:
          - int: the address of buf to allocate the next binary data
        '''
        double_bytes = double2bytes(double_val)
        return self.append_bytes_to_stack(double_bytes, pos)

    def write_list(self, list_val: list, pos: int):
        '''Convert the python list `list_val` into quingo binary and write this binary
        into buf with the starting address being `pos`.

        Args:
          - list_val: the python data to convert
          - pos: the starting address to allocate the binary of the double value

        Return:
          - int: the address of buf to allocate the next binary data
        '''
        # the list body, which has the following structure:
        # pointer -> [length, ele0, ele1, ele2, ...]
        # the pointer is written at the stack part, and the body at heap part.

        # the pointer
        end_pos = self.write_int(self.heap_head - pos, pos)

        # list body in the heap part
        # first write the length
        self.heap_head = self.write_int(len(list_val), self.heap_head)

        # list_body_pos indicate the position to write the first level of the list,
        #   i.e., ele0, ele1 ...
        list_body_pos = self.heap_head

        # forward heap_head to reserve space for the first level of the list body
        self.heap_head += self.list_level1_size(list_val)

        # then write the list body
        #  - if the element is not a list, the actual value is written;
        #  - otherwise, the pointer is written at list_body_pos, and the lower level list is
        #    written at the new heap_head
        for ele in list_val:
            list_body_pos = self.convert(ele, list_body_pos)

        return end_pos

    def write_tuple(self, tuple_val: tuple, pos: int):
        '''Convert the python tuple `tuple_val` into quingo binary and write this binary into buf
        with the starting address being `pos`.
        '''
        for ele in tuple_val:
            pos = self.convert(ele, pos)

        return pos

    def list_level1_size(self, list_val):
        if len(list_val) == 0:
            return 0

        return len(list_val) * self.stack_part_size(list_val[0])

    def stack_part_size(self, pydata: str):
        '''The binary converted from the python data contains two parts: the stack part and the
        heap part. This function calculates the size of stack part of the quingo binary converted from the python value `pydata`.
        '''

        data_type = dt.check_if_param_type(pydata)

        res = 0
        if data_type == 'int':
            res = gc.QU_INT_SIZE

        elif data_type == 'bool':
            res = gc.QU_BOOL_SIZE

        elif data_type == 'list':
            res = gc.QU_INT_SIZE

        elif data_type == 'double':
            res = gc.QU_DOUBLE_SIZE

        elif data_type == 'tuple':
            for ele in pydata:
                res += self.stack_part_size(ele)

        else:
            raise ValueError("Found unsupported type: {}.".format(pydata))

        return res

    def convert(self, pydata, pos: int = 0):
        '''Convert the pydata into quingo binary, and write this binary into buf.

        Args:
          - pydata: the python data to convert
          - pos: the starting address to write this binary

        Return:
          - int: the address of buf to allocate the next binary data
        '''

        assert(isinstance(pos, int))

        data_type = dt.check_if_param_type(pydata)

        self.heap_head = max(self.heap_head, pos +
                             self.stack_part_size(pydata))

        if data_type == 'int':
            pos = self.write_int(pydata, pos)

        elif data_type == 'bool':
            pos = self.write_bool(pydata, pos)

        elif data_type == 'double':
            pos = self.write_double(pydata, pos)

        elif data_type == 'list':
            pos = self.write_list(pydata, pos)

        elif data_type == 'tuple':
            pos = self.write_tuple(pydata, pos)

        else:
            raise ValueError("Found undefined types ({}).\n\tSupported types include "
                             "int, bool, double, list, and tuple.".format(pydata))

        return pos
