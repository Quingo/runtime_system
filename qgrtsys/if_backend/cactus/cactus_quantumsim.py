import os
import platform
import subprocess
from pathlib import Path
from qgrtsys.if_backend.if_backend import If_backend
import qgrtsys.global_config as gc
from qgrtsys.core.utils import *

logger = get_logger((__name__).split('.')[-1])


def format_cmd(cmd):
    split_cmd_lines = cmd.split('--')
    formatted_str = ''
    for i, line in enumerate(split_cmd_lines):
        if i == 0:
            formatted_str = line
            continue
        group = line.split(' ', 1)
        formatted_str += '\n'
        if len(group) == 1:
            formatted_str += "\t--{:15s}".format(group[0])
        else:
            formatted_str += "\t--{:15s} {}".format(
                group[0], ' '.join(group[1:]))
    return formatted_str


class Cactus_quantumsim(If_backend):
    """A simulation backend using CACTUS and QuantumSim."""

    def __init__(self, verbose=False, log_level=logging.WARNING, **kwargs):
        super().__init__("CACTUS_QuantumSim", verbose, log_level)
        self.eqasm_file = None
        self.cactus_dir = gc.qgrtsys_root_dir / "if_backend" / "cactus"
        self.cactus_prog_file_opt = ""
        self.cactus_exe_path = None
        self.ret_file_path = ""
        self.set_verbose(verbose)
        self.set_log_level(log_level)
        self.config()

    def available(self):
        return True

    def set_log_level(self, log_level):
        self.log_level = log_level
        logger.setLevel(self.log_level)

    def set_verbose(self, v):
        self.verbose = v

    def config(self, **kwargs):
        """This function performs various configuration for the simulator."""

        cactus_bin_dir = self.cactus_dir / "bin"

        if platform.system() == "Linux":
            self.cactus_exe_path = cactus_bin_dir / "cactus"

        elif platform.system() == "Windows":
            self.cactus_exe_path = cactus_bin_dir / "cactus.exe"

        else:
            raise NotImplementedError(
                "Currently, CACTUS can only run on Windows and Linux.")

        self.config_dict = {
            "num_sim_cycles":   ['--run',           2000000],
            "vliw_width":       ['--vliw_width',    2],
            "num_qubit":        ['--q_num',         7],
            "data_memory_size": ['--dm_size',       '1M'],
            "sim_output_dir":   ['--output',        'sim_output'],
            "log_levels":       ['--log_level',     'log_levels.json'],
            "gate_config":      ['--gate_config',   'qubit_gate_config.json'],
            "topology_config":  ['--tp_config',     'cclight_config.json'],
            "store":            ['--store',         '{} {}'.format(gc.shared_mem_start_addr,
                                                                   gc.shared_mem_size)]
        }

    def cmd_config(self):
        self.opt_str = ""
        for key, value in self.config_dict.items():
            if value[0][2:] in ["log_level", "gate_config", "tp_config"]:
                opt_value_path_str = self.cactus_dir / "config" / value[1]
                opt_value_str = '"{}"'.format(opt_value_path_str)
            else:
                opt_value_str = "{}".format(value[1])

            self.opt_str += " {} {}".format(value[0], opt_value_str)

        if self.verbose:
            self.opt_str += ' --debug_on'  # put this option on to enable cactus output

    def upload_program(self, prog_fn, is_binary=False):
        """
        Upload assembly or binary program to the simulator.

        Args:
            prog_fn: the name of the assembly or binary file.
            is_binary: True when the uploaded program is in binary format.
        """
        if not isinstance(prog_fn, Path):
            prog_fn = Path(prog_fn)

        prog_dir = prog_fn.parent

        if is_binary:
            self.cactus_prog_file_opt = ' --bin "{}"'.format(prog_fn)

        else:
            self.cactus_prog_file_opt = ' --asm "{}"'.format(prog_fn)

        self.ret_file_path = prog_dir / ("res_" + prog_fn.stem + '.bin')
        self.cactus_ret_file_opt = ' --file "{}"'.format(self.ret_file_path)

        qubit_num = self.count_qubits(prog_fn)

        if(qubit_num > self.config_dict['num_qubit'][1]):
            self.config_dict['num_qubit'][1] = qubit_num
            quingo_msg('The number of qubits in use is ' + str(qubit_num))

        self.cmd_config()
        return True

    def execute(self):
        cactus_cmd = str(self.cactus_exe_path) + self.cactus_prog_file_opt +\
            self.cactus_ret_file_opt + self.opt_str

        logger.debug(format_cmd(cactus_cmd))

        ret_value = subprocess.run(cactus_cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True, shell=True)

        if self.verbose and ret_value.stdout != '':
            # the following is a workaround for the progressbar of cactus.
            for line in ret_value.stdout.split('\n'):
                if line.startswith('[>') or line.startswith('[='):
                    continue
                quingo_msg(line)

        if ret_value.stderr != '':
            quingo_err("Error message from cactus:")
            quingo_err("\t" + ret_value.stderr)

        if (ret_value.returncode != 0):  # failure
            return False
        else:  # success
            return True

    def read_result(self):
        """This function tries to read the computation result of the quantum kernel.
        """
        with open(self.ret_file_path, 'rb') as f:
            return(f.read())
