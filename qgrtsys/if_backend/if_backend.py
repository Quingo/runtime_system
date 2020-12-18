import re
from qgrtsys.core.utils import *
import logging


class If_backend():
    """The interface class for Quingo backends.

    Any actual backend (including hardware such as CCLight, simulators)
    should inherit from this interface.
    """

    def __init__(self, name, verbose=False, log_level=logging.WARNING):
        self.__name__ = name
        self.set_verbose(verbose)
        self.set_log_level(log_level)

    def name(self):
        return self.__name__

    def set_verbose(self, v):
        raise NotImplementedError

    def set_log_level(self, log_level):
        raise NotImplementedError

    def available(self):
        return False

    def execute(self):

        raise NotImplementedError

    def read_result(self):
        raise NotImplementedError

    def upload_program(self, program):
        raise NotImplementedError

    def count_qubits(self, eqasm_fn):

        with Path(eqasm_fn).open('r') as f:
            lines = f.readlines()

        qubit_list_s = r'{\d+(,\d+)*}'
        qubit_pair = r'\(\d+,\d+\)'
        qubit_list_t = (r'{{{pair}(,{pair})*}}').format(pair=qubit_pair)
        smis = r's\d+,' + qubit_list_s
        smit = r't\d+,' + qubit_list_t

        regex_dict = {'smis': smis,
                      'smit': smit}

        tran_dict = {'smis': str.maketrans(r"{,}", "   "),  # replace these charactors '{,}' with space
                     'smit': str.maketrans(r",{}()", "     ")}

        num_list = []
        for lineno, line in enumerate(lines):
            line = line.lower().strip()

            if line.startswith('smis ') or line.startswith('smit '):
                smi = line[:4]  # get 'smis' or 'smit'
                # get the following part in the instruction, e.g., 's0,{1,2}'
                line = line[4:].replace(' ', '')

                # validate the format of this SMIS/SMIT instruction
                m = re.match(regex_dict[smi], line)
                if m is None or m.group() != line:
                    raise ValueError(
                        "Errors found at line {}: {}.".format(lineno + 1, lines[lineno]))

                # get all qubit numbers in the instruction
                qubit_list = [int(q) for q in re.findall(
                    r' \d+', line.translate(tran_dict[smi]))]

                num_list.extend(qubit_list)

        return len(set(num_list))
