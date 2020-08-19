import re
import struct

import qgrtsys.global_config as gc
from qgrtsys.core.utils import *

logger = get_logger(__name__)
logger.setLevel(logging.WARNING)


def check_if_param_type(arg) -> str:
    arg_type = type(arg).__name__

    if arg_type not in gc.allowed_python_types:
        raise ValueError("Unsupported type ({}) of argument ({}) has been"
                         " passed to Quingo.".format(arg_type, arg))

    if isinstance(arg, float):
        arg_type = 'double'

    return arg_type


def get_list_type_str(arg) -> str:
    assert(isinstance(arg, list))

    # TODO: currently, we cannot infer the type of a list with zero elements
    #       This should be fixed in the future.
    if len(arg) == 0:
        raise NotImplementedError(
            "Currently cannot pass a list with a length of zero to Quingo.")

    # Quingo only accepts a list of elements with the same type
    if not all(isinstance(x, type(arg[0])) for x in arg):
        raise ValueError("Interface parameter error: a list ({}) of elements of"
                         " different types is passed to Quingo.".format(arg))

    list_elem_type = check_if_param_type(arg[0])

    if (list_elem_type == 'list'):
        type_str = get_list_type_str(arg[0]) + '[]'
    elif (list_elem_type == 'tuple'):
        type_str = get_tuple_type_str(arg[0]) + '[]'
    else:
        type_str = list_elem_type + '[]'

    return type_str


def get_tuple_type_str(arg) -> str:
    assert(isinstance(arg, tuple))

    type_str = '('

    for elem in arg:
        tuple_elem_type = check_if_param_type(elem)

        if (tuple_elem_type == 'list'):
            type_str += get_list_type_str(elem) + ', '
        elif (tuple_elem_type == 'tuple'):
            type_str += get_tuple_type_str(elem) + ', '
        else:
            type_str += tuple_elem_type + ', '

    type_str = type_str[:-2] + ')'

    return type_str


def conv_arg_to_qg_str(i: int, arg) -> (str, str):

    arg_def_str = ""

    var_prefix = "var"

    arg_type = check_if_param_type(arg)

    if arg_type in gc.allowed_primitive_types:
        # Give a name to this Quingo variable
        var_name = "{}{}_{}".format(var_prefix, i, arg_type)
        # Quingo variable declaration
        arg_def_str = "{} {};\n".format(arg_type, var_name)
        # assign the value
        arg_def_str += "{} = {};\n".format(var_name, str(arg).lower())

    elif arg_type == 'list':

        concrete_list_type = get_list_type_str(arg)

        # Give a name to this Quingo variable
        var_name = "{}{}_arr".format(var_prefix, i)
        # Quingo variable declaration
        arg_def_str = "{} {};\n".format(concrete_list_type, var_name)
        # assign the value
        array_content = str(arg).lower().replace(
            '[', '{').replace(']', '}')
        arg_def_str += "{} = {};\n".format(var_name, array_content)

    elif arg_type == 'tuple':

        concrete_tuple_type = get_tuple_type_str(arg)

        # Give a name to this Quingo variable
        var_name = "{}{}_tpl".format(var_prefix, i)
        # Quingo variable declaration
        arg_def_str = "{} {};\n".format(concrete_tuple_type, var_name)
        # assign the value
        array_content = str(arg).replace('[', '{').replace(']', '}')
        arg_def_str += "{} = {};\n".format(var_name, array_content)

    return var_name, arg_def_str


def get_tuple_ele_type(tuple_str):
    tuple_str = tuple_str.replace(' ', '')

    if len(tuple_str) < 2 or tuple_str[0] != '(' or tuple_str[-1] != ')':
        raise ValueError(
            "Provided type string ({}) is not a tuple!".format(tuple_str))

    return split_comma_sep_types(tuple_str[1:-1])


def get_end_square_addr(type_str, start_addr):

    end_addr = start_addr

    while (end_addr < len(type_str) - 1):
        if (type_str[end_addr: end_addr + 1] != '[]'):
            break

    return end_addr


def split_comma_sep_types(comma_sep_types):
    comma_sep_types = comma_sep_types.replace(' ', '')

    type_list = []

    end_square_addr = 0

    if (comma_sep_types[0] == '('):  # tuple
        right_brace_addr = get_paired_brace(comma_sep_types, 0)
        end_square_addr = get_end_square_addr(
            comma_sep_types, right_brace_addr)
    else:
        if comma_sep_types.startswith('int'):
            end_square_addr = get_end_square_addr(
                comma_sep_types, len('int') - 1)
        elif comma_sep_types.startswith('bool'):
            end_square_addr = get_end_square_addr(
                comma_sep_types, len('bool') - 1)

    comma_addr = comma_sep_types.find(',', end_square_addr)

    if comma_addr == -1:
        type_list.append(comma_sep_types)
    else:
        type_list.append(comma_sep_types[0: comma_addr])

        new_string = comma_sep_types[comma_addr+1:]

        type_list.extend(split_comma_sep_types(new_string))

    return type_list


def get_paired_brace(type_str, start_addr):

    assert(type_str[start_addr] == '(')

    level = 0

    i = start_addr
    for i in range(start_addr, len(type_str)):
        if (type_str[i] == '('):
            level += 1

        if (type_str[i] == ')'):
            level -= 1

        if level == 0:
            return i

    raise ValueError(
        "Found unpaired braces in the type string ({}).".format(type_str))


def get_outer_type(type_str):

    type_str = type_str.replace(' ', '')

    length = len(type_str)

    if length > 3 and type_str[length - 2: length] == '[]':
        return 'list'

    elif (len(type_str) > 2 and type_str[0] == '(' and type_str[-1] == ')'):
        return 'tuple'

    elif type_str == 'int' or type_str == 'bool' or type_str == 'double':
        return type_str
    else:
        raise ValueError(
            "Unrecognized type string ({}) is provided.".format(type_str))


class Data_transfer():
    """Data_transfer serves as the backbone module."""

    def __init__(self, **kwargs):
        self.data_block = None
        self.head = 0

    def set_data_block(self, bin_block):
        """This function set the data block to be decoded, and reset the
        decoder pointer.

        Args:
            bin_block (binary) : the binary data block returned by the quantum kernel.
        """
        logger.info("The data block is decode is: ")
        ps = ''
        for i, b in enumerate(bin_block):
            ps += '{:2}, '.format(b)
            if (i+1) % 8 == 0:
                ps += '\n'
        logger.info(ps)
        self.data_block = bin_block
        self.head = 0

    def _byte_2_int(self, byte_data):
        return int.from_bytes(byte_data, byteorder=gc.endian, signed=True)

    def _byte_2_bool(self, byte_data):
        return bool.from_bytes(byte_data, byteorder=gc.endian, signed=True)

    def _byte_2_double(self, byte_data):
        return struct.unpack('<f', byte_data)[0]

    def _check_ptr_range(self, head, tail):
        if head < 0:
            logger.error("Error: found negative pointer ({})!", format(head))

        if tail > len(self.data_block):
            logger.error("The pointer ({}) to the data block exceeds the "
                         "maximum size ({}).".format(tail, len(self.data_block)))

    def _get_int(self, head):
        """This function read an integer from the data block, and move the
        decode pointer forward with a step size equal to the integer size.
        """

        new_head = head + gc.QU_INT_SIZE
        self._check_ptr_range(head, new_head)
        int_data = self.data_block[head: new_head]
        return self._byte_2_int(int_data), new_head

    def _get_bool(self, head):
        """This function read a bool from the data block, and move the decode
        pointer forward with a step size equal to the bool size.
        """

        new_head = head + gc.QU_BOOL_SIZE
        self._check_ptr_range(head, new_head)
        int_data = self.data_block[head: new_head]
        return self._byte_2_bool(int_data), new_head

    def _get_double(self, head):
        """This function read a double from the data block, and move the decode
        pointer forward with a step size equal to the double size.
        """

        new_head = head + gc.QU_DOUBLE_SIZE
        self._check_ptr_range(head, new_head)
        int_data = self.data_block[head: new_head]
        return self._byte_2_double(int_data), new_head

    def _get_pointer(self, head):
        new_head = head + gc.QU_PTR_SIZE
        self._check_ptr_range(head, new_head)
        int_data = self.data_block[head: new_head]
        return self._byte_2_int(int_data), new_head

    def bin_to_pydata(self, type_str, start_addr=0x600):
        logger.debug('The binary data is going to be decoded according to the type: ',
                     type_str)
        res, head = self.conv_qg_bin_to_py_data(type_str, start_addr)
        return res

    def conv_qg_bin_to_py_data(self, type_str, head):
        outer_type = get_outer_type(type_str)

        if outer_type == 'int':
            value, head = self._get_int(head)

        elif outer_type == 'bool':
            value, head = self._get_bool(head)

        elif outer_type == 'double':
            value, head = self._get_double(head)

        elif outer_type == 'tuple':
            value, head = self.conv_qg_bin_to_py_tuple(type_str, head)

        elif outer_type == 'list':
            value, head = self.conv_qg_bin_to_py_array(type_str, head)

        else:
            raise ValueError("Undefined types ({}) found.".format(arg))

        return value, head

    def conv_qg_bin_to_py_tuple(self, type_str, head):
        type_list = get_tuple_ele_type(type_str)

        value = ()
        for ele_type in type_list:
            ele_value, head = self.conv_qg_bin_to_py_data(ele_type, head)
            value += (ele_value,)

        return value, head

    def conv_qg_bin_to_py_array(self, type_str, head):

        assert(get_outer_type(type_str) == 'list')

        arr_length, head = self._get_int(head)

        ele_type = type_str[:-2]

        resolved_arr = []

        if (get_outer_type(ele_type) != 'list'):
            for i in range(arr_length):
                ele, head = self.conv_qg_bin_to_py_data(ele_type, head)
                resolved_arr.append(ele)
        else:
            for i in range(arr_length):
                sub_arr_head_offset, new_head = self._get_pointer(head)
                sub_arr_head = head + sub_arr_head_offset

                sub_arr, head = self.conv_qg_bin_to_py_data(
                    ele_type, sub_arr_head)

                resolved_arr.append(sub_arr)

                head = new_head

        return resolved_arr, head
