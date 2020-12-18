from qgrtsys import if_quingo
import time

if_quingo.call_quingo("qft.qu", 'qft4')
res = if_quingo.read_result()
print(res)
