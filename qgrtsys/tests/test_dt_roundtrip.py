from qgrtsys.tests.pydata2bin import Pydata_2_qg_bin
import qgrtsys.core.data_transfer as dt
from qgrtsys.core.utils import *
import pytest
import random

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)


def check_equal(val1, val2):
    """This function check if two values are equal or not.
    Note:
      - val1 and val2 must have exactly the same type to get a True result; currently,
        the following types are supported: int, bool, float, list, tuple.
      - For floating-point values, they are compared approximately.

    Args:
      - val1: the first value
      - val2: the second value

    Return:
      - True on equal, otherwise False.
    """

    if type(val1) is not type(val2):
        return False

    if (isinstance(val1, float) or isinstance(val2, float)):
        return val1 == pytest.approx(val2, rel=1e-7)

    elif(isinstance(val1, int) or isinstance(val1, bool)):
        return val1 == val2

    elif(isinstance(val1, list) or isinstance(val1, tuple)):
        if (len(val1) != len(val2)):
            return False

        return all(map(lambda x, y: check_equal(x, y), val1, val2))

    else:
        raise ValueError("Found unsupported value type ({}). \n\tCurrently only int, bool, float, "
                         "list, and tuple are supported.".format(type(val1)))


def roundtrip(type_str, value):
    logger.debug("The value to convert is: {}".format(value))
    logger.debug("The expected type is: {}".format(type_str))

    # Use `Pydata_2_qg_bin` to convert python data into quingo binary
    converter = Pydata_2_qg_bin()
    converter.convert(value)

    res = converter.get_result()

    logger.debug(res)

    # Use 'data_transfer' to convert binary data into python data
    data_trans = dt.Data_transfer()
    data_trans.set_data_block(res)
    res_py = data_trans.bin_to_pydata(type_str, 0)

    logger.debug("The decoded data is:{}\n".format(res_py))

    assert(check_equal(res_py, value))


def test_roundtrip():
    n = 20
    while n > 0:
        type_str = gen_type_str(weight_list=4, weight_tuple=4,
                                weight_bool=2, weight_int_double=10, layer=0, max_num=5)

        if type_str == None:
            continue

        value = gen_ran_value(type_str)
        roundtrip(type_str, value)
        n -= 1


def gen_type_str(weight_list, weight_tuple, weight_bool, weight_int_double, layer, max_num):
    """This function generates a random string of type.

    Args:
        weight_list (int) : the weight of int which is used to generate
            the string of type.
        weight_tuple (int) : the weight of tuple.
        weight_bool (int) : the weight of bool.
        weight_int_dou (int) : the weight of int and double.
        layer (int) : the number of times in which a tuple or array is nested.
        max_num (int) : the maximum number of the values in a tuple.
    """

    if(layer >= 5):
        return

    tmp_bool = weight_bool
    tmp_int_double = weight_int_double

    # Generate a random value to choose a type.
    index = random.uniform(0, 1)

    # The sum of the weights.
    weight_total = weight_list + weight_tuple + weight_bool + weight_int_double

    # Select the type according to the weight
    if(layer == 0):
        weight_bool = 1
        weight_int_double = 1
    if(index < weight_list / weight_total):
        chosed_type = 'list'
    elif(index < (weight_list + weight_tuple) / weight_total):
        chosed_type = 'tuple'
    elif(index < (weight_list + weight_tuple + weight_bool) / weight_total):
        chosed_type = 'bool'
    elif(index < (weight_list + weight_tuple + weight_bool + 0.25*weight_int_double) / weight_total):
        chosed_type = 'double'
    else:
        chosed_type = 'int'

    weight_bool = tmp_bool
    weight_int_double = tmp_int_double

    # If the tuple is chosen, the function is called to add several elements to the tuple.
    if(chosed_type == 'tuple'):
        res = "("
        num = random.randint(2, max_num)
        cnt = 0
        for i in range(num):
            tmp = gen_type_str(weight_list, weight_tuple-1,
                               weight_bool, weight_int_double, layer+1, max_num)
            if(tmp):
                cnt += 1
                res += tmp + ','
        if(cnt < 2):
            return
        return res[:-1]+')'

    # If the list is chosen, the function is called to genetate a type for the list.
    elif(chosed_type == 'list'):
        tmp = gen_type_str(weight_list-1, weight_tuple,
                           weight_bool, weight_int_double, layer+1, max_num)
        if(tmp):
            return tmp + '[]'
        return

    elif(chosed_type == 'bool'):
        return 'bool'
    elif(chosed_type == 'int'):
        return 'int'
    elif(chosed_type == 'double'):
        return 'double'
    else:
        print("Error: No such a type!")
        exit(0)


def gen_ran_value(type_str, max_num=5):
    """This function generates a data based on the type.

    Args:
        type_str (string) : a string of type.
        max_num (int) : the maximum number of values in an array.
    """

    res = []
    type_str = type_str.replace(' ', '')
    if(type_str[-2:] == '[]'):
        num = random.randint(1, max_num+1)
        for i in range(num):
            res.append(gen_ran_value(type_str[:-2], max_num))
        return res

    elif(type_str[0] == '(' and type_str[-1] == ')'):
        sub = list(type_str[1:-1])
        left = 0

        for i in range(len(sub)):
            if(sub[i] == '('):
                left += 1
            elif(sub[i] == ')'):
                left -= 1
            elif(sub[i] == ','):
                if(left == 0):
                    sub[i] = '$'
        sub = (''.join(sub)).split('$')

        for i in sub:
            res.append(gen_ran_value(i, max_num))
        return tuple(res)

    elif(type_str == 'int'):
        return random.randint(-10000, 10000)

    elif(type_str == 'double'):
        return random.uniform(-10000, 10000)

    elif(type_str == 'bool'):
        if(random.uniform(0, 1) < 0.5):
            return True
        return False
    else:
        print("Error: No such a type!")
        exit(0)


if __name__ == '__main__':
    test_roundtrip()
