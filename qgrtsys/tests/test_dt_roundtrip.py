from pydata2bin import *
import qgrtsys.core.data_transfer as dt
from qgrtsys.core.utils import *

logger = get_logger(__name__)
logger.setLevel(logging.INFO)


def roundtrip(type_str, value):
    logger.debug("The value to convert is: \n{}".format(value))
    logger.debug("The expected type is: {}".format(type_str))

    res = conv_arg_to_qg_bin(value)

    data_trans = dt.Data_transfer()
    data_trans.set_data_block(res)
    r = data_trans.bin_to_pydata(type_str, 0)

    logger.debug("The decoded data is:\n{}".format(r))
    assert(r == value)

################################################################################
# test case 1
################################################################################

#  3, pA, pB, pC, vA, vB, vC
# vA = [(1, False), (2, False)]
#   2, pa, pb, va, vb
#       va = (1, False): 0x00000001, 0x00
#       vb = (2, False): 0x00000002, 0x00
#       pa = 4 x 2 = 8
#       pb = 4 x 1 + 5 = 9
#   vA: 0x00000002, 0x00000008, 0x00000009, 0x00000001, 0x00, 0x00000002, 0x00  (22 bytes)
#
# vB = [(4, True)]
#   1, pa, va
#       va = (4,  True): 0x00000004, 0x01
#       pa = 4
#   vB: 0x00000001, 0x00000004, 0x00000004, 0x01 (13 bytes)
#
# vC = [(3, False), (4, True), (6, True)]
#   3, pa, pb, pc, va, vb, vc
#       va = (3, False): 0x00000003, 0x00
#       vb = (4,  True): 0x00000004, 0x01
#       vb = (6,  True): 0x00000006, 0x01
#       pa = 4 x 3 = 12
#       pb = 4 x 2 + 5 x 1 = 13
#       pc = 4 + 5 x 2 = 14
#   0x00000003, 0x0000000C, 0x0000000D, 0x0000000E,
#               0x00000003, 0x00,
#               0x00000004, 0x01,
#               0x00000006, 0x01 (31 bytes)
#
#  pA = 4 x 3 = 12
#  pB = 4 x 2 + len(vA) = 30
#  pC = 4 x 1 + len(vA + vB) = 39
#
# 0x00000003, 0x0000000C, 0x0000001E, 0x00000027, 0x00000002, 0x00000008, 0x00000009, 0x00000001, 0x00, 0x00000002, 0x00, 0x00000001, 0x00000004, 0x00000004, 0x01, 0x00000003, 0x0000000C, 0x0000000D, 0x0000000E, 0x00000003, 0x00, 0x00000004, 0x01, 0x00000006, 0x01

# 00, 00, 00, 03, 00, 00, 00, 0C, 00, 00, 00, 1E, 00, 00, 00, 27, 00, 00,
# 00, 02, 00, 00, 00, 08, 00, 00, 00, 09, 00, 00, 00, 01, 00, 00, 00, 00,
# 02, 00, 00, 00, 00, 01, 00, 00, 00, 04, 00, 00, 00, 04, 01, 00, 00, 00,
# 03, 00, 00, 00, 0C, 00, 00, 00, 0D, 00, 00, 00, 0E, 00, 00, 00, 03, 00,
# 00, 00, 00, 04, 01, 00, 00, 00, 06, 01


#0, 0, 0, 3, 0, 0, 0, 12, 0, 0, 0, 30, 0, 0, 0, 39, 0, 0, 0, 2, 0, 0, 0, 8,
#  0, 0, 0, 9, 0, 0, 0, 1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1, 0, 0, 0, 4,
#  0, 0, 0, 4, 1, 0, 0, 0, 3, 0, 0, 0, 12, 0, 0, 0, 13, 0, 0, 0, 14,
#  0, 0, 0, 3, 0, 0, 0, 0, 4, 1, 0, 0, 0, 6, 1,

# value = [(1, False), (2, False)]
# value = (2, False)
# value = [1, 2]
# value = [True, True]
# value = [True]
# value = [(3, False), (4, True), (6, True)]


################################################################################
# test case 2
################################################################################


def test_roundtrip():
    # test case 1
    type_str = '(int, bool)[][]'
    value = [[(1, False), (2, False)],
             [(4, True)],
             [(3, False), (4, True), (6, True)]]

    roundtrip(type_str, value)

    # test case 2
    type_str = '(int, bool, int[][][])'
    value = (128, True, [
        [[1, 2, 3], [-10, -9, -8]],
        [[1, 2, 3], [10, 9, 8]],
        [[1, 2, 3], [-10, -9, -8], [-10, -9, -8], [-10, -9, -8], [-10, -9, -8]]
    ])

    roundtrip(type_str, value)


if __name__ == '__main__':
    test_roundtrip()
