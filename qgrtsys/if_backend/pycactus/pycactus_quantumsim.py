import os
import platform
import subprocess
from pathlib import Path
from qgrtsys.if_backend.if_backend import If_backend
import qgrtsys.global_config as gc
from qgrtsys.core.utils import *
from pycactus.quantum_coprocessor import Quantum_coprocessor

logger = get_logger((__name__).split('.')[-1])


class Pycactus_quantumsim(If_backend):
    """A functional eQASM simulation backend using PyCACTUS and QuantumSim."""

    def __init__(self, **kwargs):
        super().__init__("PyCACTUS_QuantumSim")
        self.sim = Quantum_coprocessor()
        self.pycactus_dir = gc.qgrtsys_root_dir / "if_backend" / "pycactus"
        self.verbose = kwargs.pop('verbose', False)
        self.loglevel = kwargs.pop('loglevel', logging.INFO)
        logger.setLevel(self.loglevel)

    def available(self):
        return True

    def set_log_level(self, log_level):
        self.log_level = log_level
        logger.setLevel(self.log_level)

    def set_verbose(self, v):
        self.verbose = v

    def set_max_exec_cycle(self, num_cycle: int):
        self.sim.set_max_exec_cycle(num_cycle)

    def upload_program(self, prog_fn, is_binary=False):
        """
        Upload assembly or binary program to the simulator.

        Args:
            prog_fn: the name of the assembly or binary file.
            is_binary: True when the uploaded program is in binary format.
        """
        if not isinstance(prog_fn, Path):
            prog_fn = Path(prog_fn)

        qubit_num = self.count_qubits(prog_fn)

        try:
            success = self.sim.upload_program(prog_fn, qubit_num)
            return success
        except Exception as e:
            quingo_err("Error in uploading program to PyCACTUS: {}".format(e))

        return False

    def execute(self):
        try:
            success = self.sim.execute()
            return success
        except Exception as e:
            quingo_err("Error in PyCACTUS Simulation: {}".format(e))

        return False

    def read_result(self):
        """This function tries to read the computation result of the quantum kernel.
        """
        return self.sim.read_result()
