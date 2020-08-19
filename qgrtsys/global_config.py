from pathlib import Path

compiler_fn = 'quingo.jar'
qgrtsys_root_dir = Path(__file__).absolute().parent
xtext_compiler_path = qgrtsys_root_dir / 'core' / compiler_fn


std_op_fn = 'standard_operations.qu'
std_qfg_fn = 'config-quingo.qfg'
std_op_full_path = qgrtsys_root_dir / 'lib' / std_op_fn
std_qfg_full_path = qgrtsys_root_dir / 'lib' / std_qfg_fn

quingo_suffix = ".qu"
eqasm_suffix = '.eqasm'
res_bin_suffix = '.bin'
build_dirname = 'build'

shared_mem_start_addr = 0x000
shared_mem_size = 0x100000

QU_BOOL_SIZE = 1
QU_INT_SIZE = 4
QU_PTR_SIZE = 4
QU_DOUBLE_SIZE = 4

allowed_primitive_types = ['int', 'bool', 'double']
allowed_python_types = ['int', 'bool', 'float', 'list', 'tuple']

endian = 'little'
