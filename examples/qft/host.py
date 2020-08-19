from qgrtsys.if_host.python import *
import time
if_quingo = If_Quingo()

if_quingo.call_quingo("qft.qu", 'qft4')
res = if_quingo.read_result()
print(res)
