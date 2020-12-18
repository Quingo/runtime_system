# Quingo Runtime System

The Quingo runtime system.

**NOTE**:
- The code in the `master` branch is currently unstable.
- The more stable version can be found in the `develop` branch.

## Prerequisites
- Python 3.7
  - **NOTE**: Python **3.7** is required.
  - Python 3.6 **cannot** work.
  - Python 3.8 has not been tested.
- Java Development ToolKit (JDK)
  - you should install the latest version of [Java Development ToolKit](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html). You may need to add or modify a few environmental  variables as well.
  - If you are using Ubuntu, you can install JDK8 with the following command: `sudo apt-get install openjdk-8-jdk`.
  - After a success installation, you should be able to execute this command: `java -version`.
- PyCACTUS
  - Please clone from this [repo](https://github.com/gtaifu/PyCACTUS) and install it.

## Installation
Enter the root directory of this project, and simply run either one of the two following commands:
```
python setup.py develop
```
or
```
pip install -e .
```


## File Structure
The directory `qgrtsys` includes the code implementing the runtime system support the Quingo programming framework, which comprises of three parts:
- `core`: it implements the _phase manager_, which controls the framework to undergo the _pre-execution_, _quantum compilation_, _quantum execution_, and _post-execution_ phase. It also provides a set of APIs to enable the definition of APIs for different host languages.
- `if_interface`: it provides programming interface to the host language based on the APIs provided by the core.
- `if_backend`: it is defines an interface (`If_backend`)to call different quantum backends. Drivers for actual backends should be implemented by inheriting this interface, like the interface `Cactus_quantumsim`, which calls the CACTUS + QuantumSim simulator for execution.

The correspondence between some modules and files:
- Parameter converter: the function `gen_main_func_file` of the module `Runtime_system_manager` in the file `core/manager.py`;
- Data Decoder: the module `Data_transfer` in the file `core/data_transfer.py`;
- JIT compiler: the file `core/quingo.jar`;
- Q. Backend Driver: the interface `If_backend` defined in `if_backend/if_backend.py` and its children modules;
- Pulse Generator: not implemented yet;
- Configurator: some `set_xxx` functions in the `Runtime_system_manager`.

The file `core/quingo.jar` implements a prototype compiler, which takes the quantum kernel with parameters as input, and generate eQASM instructions as output. It can perform partial execution to optimize the quantum kernel based on the given parameters during classical runtime.