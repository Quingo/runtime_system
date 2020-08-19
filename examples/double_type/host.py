from qgrtsys.if_host.python import *

import random


def test_input_float(a, b):
    quingo = If_Quingo()
    if quingo.call_quingo("float_add.qu", 'test_add', a, b) is True:
        res = quingo.read_result()
        print("THe result of {} + {} by Quingo is: {}. Expected: {}".format(a, b, res, a+b))
    else:
        print("Fail to call the kernel.")


values = [[0.0, 0.0],
          [0.0, 1.0],
          [1.0, 0.0],
          [-1.0, 0.0],
          [0.0, -1.0],
          [0.1, -0.1],
          [0.1, 0.0],
          [0.1, 0.1],
          [random.uniform(-1000, 0), random.uniform(-1000, 0)],
          [random.uniform(0, 1000), random.uniform(0, 1000)],
          [random.uniform(1000, 10000000), random.uniform(1000, 10000000)],
          [random.uniform(-10000000, 0), random.uniform(-10000000, 0)]]

for pair in values:
    test_input_float(pair[0], pair[1])
