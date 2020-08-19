import qgrtsys.global_config as gc
import qgrtsys.core.data_transfer as dt
import pysnooper


def conv_prim_type_to_bytes(arg):
    arg_type = type(arg).__name__

    if arg_type == 'int':
        return arg.to_bytes(gc.QU_INT_SIZE, byteorder=gc.endian, signed=True)

    if arg_type == 'bool':
        return arg.to_bytes(gc.QU_BOOL_SIZE, byteorder=gc.endian, signed=True)

    raise ValueError("Found argument ({}) with an undefined primitive type"
                     " ({}).".format(arg, type(arg)))


def conv_list_to_bytes(arr):

    # the first four bytes always correspond to the length of the array
    length = len(arr)
    res = length.to_bytes(gc.QU_INT_SIZE, byteorder=gc.endian, signed=True)

    if length == 0:
        return res

    ptr_bytes = bytes()
    value_bytes = bytes()

    cur_ptr_addr = 0
    value_start_addr = len(arr) * gc.QU_PTR_SIZE

    ele_type = dt.check_if_param_type(arr[0])

    if ele_type != 'list':
        for ele in arr:
            cur_value_bytes = conv_arg_to_qg_bin(ele)
            value_bytes += cur_value_bytes
            value_start_addr += len(cur_value_bytes)

        res += value_bytes

    else:
        for ele in arr:
            # calculate the offset and put it in the bytes
            addr_offset = value_start_addr - cur_ptr_addr
            ptr_bytes += addr_offset.to_bytes(gc.QU_PTR_SIZE,
                                              byteorder=gc.endian, signed=True)
            cur_ptr_addr += gc.QU_PTR_SIZE

            # get the data bytes
            cur_value_bytes = conv_arg_to_qg_bin(ele)
            value_bytes += cur_value_bytes
            value_start_addr += len(cur_value_bytes)

        res = res + ptr_bytes + value_bytes

    return res


def conv_tuple_to_bytes(tup):

    res = bytes()

    for ele in tup:
        res += conv_arg_to_qg_bin(ele)

    return res


def conv_arg_to_qg_bin(arg):

    arg_type = dt.check_if_param_type(arg)

    res = bytes()

    if arg_type in gc.allowed_primitive_types:
        res += conv_prim_type_to_bytes(arg)

    elif arg_type == 'list':
        res += conv_list_to_bytes(arg)

    elif arg_type == 'tuple':
        res += conv_tuple_to_bytes(arg)

    else:
        raise ValueError("Undefined types ({}) found.".format(arg))

    return res
