from qgrtsys import If_Quingo

if_quingo = If_Quingo(backend='PyCACTUS_QuantumSim')

if if_quingo.call_quingo("kernel.qu", 'gen_ran'):
    res = if_quingo.read_result()
    print("res: ", res)
else:
    print("failed to call the quantum kernel qrng@kernel.qu.")
