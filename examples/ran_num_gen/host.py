from qgrtsys.if_host.python import *

# to get all information, use these parameters: loglevel=logging.DEBUG, verbose=True
if_quingo = If_Quingo()


def gen_ran_num(nr_rand_num):

    if if_quingo.call_quingo("kernel.qu", 'gen_ran_seq', nr_rand_num):
        res = if_quingo.read_result()
        print("nr_rand_num: ", nr_rand_num)
        print(res)


nr_rand_num = 10
gen_ran_num(nr_rand_num)
