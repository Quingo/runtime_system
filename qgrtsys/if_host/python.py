from qgrtsys.core.manager import *
from qgrtsys.core.data_transfer import *


class If_Quingo():
    def __init__(self, **kwargs):
        self.rsm = Runtime_system_manager(**kwargs)
        self.data_transfer = Data_transfer()

    def set_eqasm_filename(self, tmp_eqasm_filename):
        self.rsm.set_eqasm_filename(tmp_eqasm_filename)

    def set_shared_addr(self, tmp_shared_addr):
        self.rsm.set_shared_addr(tmp_shared_addr)

    def set_static_addr(self, tmp_static_addr):
        self.rsm.set_static_addr(tmp_static_addr)

    def set_dynamic_addr(self, tmp_dynamic_addr):
        self.rsm.set_dynamic_addr(tmp_dynamic_addr)

    def set_max_unroll(self, tmp_max_unroll):
        self.rsm.set_max_unroll(tmp_max_unroll)

    def call_quingo(self, qg_filename, qg_func_name, *args, xtext_options={}):
        """This function provides a method in Python to call quantum kernels
        written in Quingo. After the execution of the quantum kernel, the
        result can be read back using the function `read_result`.

        Args:
            qg_filename (str) :  the name of the Qingo file which contains the
                quantum function called by the host program.
            qg_func_name (str) : the name of the quantum function
            args (dict): a variable length of parameters passed to the quantum function
        """
        return self.rsm.call_quingo(qg_filename, qg_func_name, xtext_options, *args)

    def read_result(self, start_addr=0x0):
        """After the execution of the quantum kernel, the result can be read back using
        this function.
        """
        return self.rsm.read_result(start_addr)
