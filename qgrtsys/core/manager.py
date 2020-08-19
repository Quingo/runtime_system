
import os
import re
import platform
import subprocess
import logging
from pathlib import Path
from qgrtsys.core.utils import quingo_err, quingo_msg, get_logger
from qgrtsys.if_backend.cactus.cactus_quantumsim import Cactus_quantumsim
import qgrtsys.core.data_transfer as dt
import qgrtsys.global_config as gc

logger = get_logger(__name__)


def remove_comment(qu_src):
    search_annotation_string = r'\/\/.*\n'
    return re.sub(search_annotation_string, '', qu_src)


def get_ret_type(qg_filename: str, qg_func_name: str):
    """This function read the Quingo source file to retrieve the return
    type of called Quingo operation.

    Args:
        qg_filename (path) :  the name of the Quingo file which contains the
            quantum function called by the host program.
        qg_func_name (str) : the name of the Quingo function.
    """
    with open(qg_filename, 'r', encoding='utf-8') as qu_src_file:
        qu_src = qu_src_file.read()

    qu_src = remove_comment(qu_src)

    search_string = r'\boperation\b\s+' + \
        qg_func_name + r'\s*\((.*)\)\s*:(.*)\s*\{'

    op_def_components = re.search(search_string, qu_src)
    if op_def_components is None:
        raise ValueError("Cannot find the operation ({}) in the given Quingo source "
                         "file ({}).".format(qg_func_name, qg_filename))

    ret_type = re.sub(r'\d', '', op_def_components.groups()[1].strip())
    return ret_type


class Runtime_system_manager():
    def __init__(self, **kwargs):

        # possible options for the compilers are:
        #   - "xtext": Xtext-based prototype compiler
        #   - "llvm": LLVM-based compiler, not ready yet.
        self.compiler = kwargs.pop('compiler', "xtext")

        self.loglevel = kwargs.pop('loglevel', logging.INFO)
        logger.setLevel(self.loglevel)

        self.main_func_fn = None  # pathlib.Path

        self.eqasm_file_path = None  # pathlib.Path

        self.data_block = ""

        self.verbose = kwargs.pop('verbose', False)

        self.set_backend(kwargs.pop('backend', "cactus_quantumsim"))

        self.xtext_option = {
            "eqasm_filename": self.set_eqasm_filename,
            "shared_addr": self.set_shared_addr,
            "static_addr": self.set_static_addr,
            "dynamic_addr": self.set_dynamic_addr,
            "max_unroll": self.set_max_unroll
        }

        self.eqasm_filename = ""
        self.shared_addr = 0
        self.static_addr = 0x10000
        self.dynamic_addr = 0x20000
        self.max_unroll = 100

        if self.verbose:
            logger.debug("Python version: {}".format(
                platform.python_version()))

    def set_backend(self, backend: str):
        """This function set the backend to execute the quantum application.
        Allowed backend includes:

        - actual hardware (like CC-Light)
        - Simulator: QArchSim + a qubit state simulator (like QuantumSim)
        """

        allowed_backends = ["cactus_quantumsim", "CCLight"]

        if (backend == "cactus_quantumsim"):
            self.backend = Cactus_quantumsim(verbose=self.verbose)
        else:
            logger.error("Undefined backend is used.")
            raise NotImplementedError

    def set_eqasm_filename(self, tmp_eqasm_filename):
        self.eqasm_filename = tmp_eqasm_filename

    def set_shared_addr(self, tmp_shared_addr):
        self.shared_addr = tmp_shared_addr

    def set_static_addr(self, tmp_static_addr):
        self.static_addr = tmp_static_addr

    def set_dynamic_addr(self, tmp_dynamic_addr):
        self.dynamic_addr = tmp_dynamic_addr

    def set_max_unroll(self, tmp_max_unroll):
        self.max_unroll = tmp_max_unroll

    def call_quingo(self, qg_filename: str, qg_func_name: str, xtext_options, *args):
        """This function triggers the main process."""
        self.parse_xtext_options(qg_func_name, xtext_options)
        return self.main_process(qg_filename, qg_func_name, *args)

    def parse_xtext_options(self, qg_func_name, xtext_options):
        for key in xtext_options:
            self.xtext_option[key](xtext_options[key])
        if(self.eqasm_filename == ""):
            self.eqasm_filename = qg_func_name + ".eqasm"

    def config_path(self, qg_filename: str, qg_func_name: str):

        resolved_qg_filename = Path(qg_filename).resolve()

        # ensure there is a build directory in the same directory as the source file.
        self.prj_root_dir = Path(resolved_qg_filename).parent

        self.build_dir = self.prj_root_dir / gc.build_dirname

        if not self.build_dir.exists():
            self.build_dir.mkdir()

        # the basename of qg_filename without extension
        self.qg_stem = resolved_qg_filename.stem

        self.main_func_fn = (self.build_dir / ('main_' +
                                               self.qg_stem)).with_suffix(gc.quingo_suffix)

        self.eqasm_file_path = self.main_func_fn.with_suffix(gc.eqasm_suffix)

    def main_process(self, qg_filename: str, qg_func_name: str, *args):
        """This function is the main function of the manager, which describes the main process:
          1. prepare the hyper() function
          2. compile the Quingo program including the hyper() function
            - different low-level formats can be generated according to the compilation settings
          3. Upload the assembly code or binary code to the backend for execution

        Args:
            qg_filename (str) :  the name of the Quingo file which contains the
                quantum function called by the host program.
            qg_func_name (str) : the name of the quantum function
            args: a variable length of parameters passed to the quantum function
        """

        self.config_path(qg_filename, qg_func_name)

        if self.verbose:
            quingo_msg("Start compilation ... ", end='')

        # generate the quingo file which contains the main function.
        self.gen_main_func_file(qg_filename, qg_func_name, *args)

        # compile and execute
        if not self.compile(qg_filename):  # compilation failed
            quingo_err("Compilation failed. Abort.")
            return False

        logger.debug("The compiler exited successfully.")

        if(self.eqasm_filename != ""):
            self.eqasm_file_path = self.build_dir / self.eqasm_filename

        eqasm_file = Path(self.eqasm_file_path)
        if not eqasm_file.is_file():
            quingo_err("Error: expected eQASM file ({}) has not been generated. Aborts.".format(
                self.eqasm_file_path))
            return False

        # compilation finished successfully
        logger.debug("The eQASM file has been generated at: {}".format(
            self.eqasm_file_path))

        if self.verbose:
            quingo_msg("Start execution ... ")

        if not self.execute():  # execute the eQASM file
            quingo_err("Execution failed. Abort.")
            return False

        quingo_msg('Execution finished.')

        # read back the results
        self.result = self.backend.read_result()

        return True

    def execute(self):
        """This function upload the quantum computing task to the backend."""

        if self.backend.available is False:
            raise EnvironmentError(
                "The backend{} is not available.".format(self.backend.name()))

        self.backend.upload_program(self.eqasm_file_path, False)
        return self.backend.execute()

    def get_imported_qu_fns(self, prj_dir):
        """This function recursively scans the project root directory, and
        return all Quingo files (with extention `.qu` or `.qfg`) as a list."""
        valid_file_list = []
        for r, d, f in os.walk(prj_dir):
            for file in f:
                file_path = Path(r) / file
                if file_path.suffix in ['.qu', '.qfg']:
                    valid_file_list.append(file_path)

        logger.debug("imported files: ")
        for f in valid_file_list:
            logger.debug('   {}'.format(f))

        return valid_file_list

    def compile(self, qg_filename):
        """This function compiles the project.

        The command compiling the project using the Xtext-based compiler
        is:     java -jar quingo.jar t1.qingo standard_operations.qingo
        config-qingo.json
        """

        quingo_compiler = "java -jar " + \
            ('"{}"'.format(str(gc.xtext_compiler_path)))

        # the Quingo files written by the programmer
        # qgrtsys recursively scans the root directory of the project to get all quingo files.
        # however, qgrtsys will only use the files which are imported by `qg_filename`
        user_files = self.get_imported_qu_fns(self.prj_root_dir)

        # default files that every compilation process should process, including:
        #   - a `stand_operations.qu` file, which contains the declaration of opaque operations
        #   - a `config-quingo.qu/.qfg` file, which contains the implementation of the above
        #     operations.
        #
        # If the project directory contains either one of these two files, qgrtsys will the
        # existing file(s). Otherwise, qgrtsys will use the default files as delivered with qgrtsys.
        default_files = []

        fn_list = [f.name for f in user_files]

        # add the file `standard_operations.qu`
        if not gc.std_op_fn in fn_list:
            default_files.append(gc.std_op_full_path)

        # search the file `config-quingo.qfg` in the project directory
        # if not found, use the default one.
        if not gc.std_qfg_fn in fn_list:
            default_files.append(gc.std_qfg_full_path)

        compile_files = [self.main_func_fn]

        user_files.remove(self.main_func_fn)
        compile_files.extend(user_files)
        compile_files.extend(default_files)

        compile_cmd = quingo_compiler + " " + \
            (" ".join(['"{}"'.format(str(f)) for f in compile_files])) + \
            " -o " + '"{}"'.format(str(self.build_dir / self.eqasm_filename)) + \
            " -s " + str(self.shared_addr) + \
            " -t " + str(self.static_addr) + \
            " -d " + str(self.dynamic_addr) + \
            " -u " + str(self.max_unroll)

        compile_cmd_for_print = quingo_compiler + " " + \
            "<imported files>" + \
            "\n\t -o " + '"{}"'.format(str(self.build_dir / self.eqasm_filename)) + \
            "\n\t -s " + str(self.shared_addr) + \
            "\n\t -t " + str(self.static_addr) + \
            "\n\t -d " + str(self.dynamic_addr) + \
            "\n\t -u " + str(self.max_unroll)

        logger.debug(compile_cmd_for_print)

        ret_value = subprocess.run(compile_cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   text=True, shell=True)
        if ret_value.stdout != '':
            quingo_msg(ret_value.stdout.strip())
        if ret_value.stderr != '':
            quingo_err("Error message from the compiler:")
            quingo_err("\t{}".format(ret_value.stderr))

        if (ret_value.returncode != 0):  # failure
            return False
        else:  # success
            return True

    def gen_main_func_file(self, qg_filename: str, qg_func_name: str, *args):
        """This function generates the main function required to perform
        compilation. A new file named 'main_<qg_filename>' under the
        `<build_dirname>` directory is generated to allocate this main
        function.

        Args:
            qg_filename (str) :  the name of the Quingo file which contains the
                quantum function called by the host program.
            qg_func_name (str) : the name of the Quingo function.
            args (list): a variable length of parameters passed to the quantum function
        """

        main_func_str = self.main_func(qg_filename, qg_func_name, *args)

        try:
            self.main_func_fn.write_text(main_func_str)
        except:
            raise IOError("Cannot write the file: ", self.main_func_fn)

    def main_func(self, qg_filename: str, qg_func_name: str, *args):
        """This function is used to generate string version of the main
        function used to call quingo.

        Args:
            qg_func_name (str) : the name of called Quingo operation._name`.
        """

        var_name_list = []
        arg_str_list = []

        logger.debug("calling function '{}' with parameters: {}".format(
            qg_func_name, args))

        if len(args) != 0:
            for (i, arg) in enumerate(args):
                var_name, var_def_str = dt.conv_arg_to_qg_str(i, arg)
                var_name_list.append(var_name)
                arg_str_list.append(var_def_str)

        self.ret_type = get_ret_type(qg_filename, qg_func_name)
        func_str = "\noperation main(): " + self.ret_type + " {\n"

        for arg_str in arg_str_list:
            func_str += "\n" + arg_str

        if self.ret_type == 'unit':
            func_str += "\n " + qg_func_name + "("
        else:
            func_str += "\nreturn " + qg_func_name + "("

        for var in var_name_list:
            func_str += var + ","

        if func_str[-1] == ',':
            func_str = func_str[:-1]

        func_str += ");\n}"

        return func_str

    def read_result(self, start_addr):
        data_trans = dt.Data_transfer()
        data_trans.set_data_block(self.result)
        pydata = data_trans.bin_to_pydata(self.ret_type, start_addr)
        logger.debug(
            "The data converted from the binary is: \n{}\n".format(pydata))
        return pydata
