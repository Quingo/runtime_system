
- [1. Heterogeneous Quantum-Classical Computation](#1-heterogeneous-quantum-classical-computation)
- [2. Build a Quingo Project](#2-build-a-quingo-project)
- [3. Host Program](#3-host-program)
    - [3.1. Import the Interface Library in the Host Language](#31-Import-the-Interface-Library-in-the-Host-Language)
    - [3.2. Call the Quingo Kernel](#32-call-the-quingo-kernel)
    - [3.3. Read back the Kernel Execution Result](#33-read-back-the-kernel-execution-result)
- [4. Quingo Kernel](#4-quingo-kernel)
    - [4.1. Opaque](#41-opaque)
    - [4.2. Operation](#42-operation)
    - [4.3. Qubit Allocation](#43-qubit-allocation)
    - [4.4. Type System](#44-type-system)
- [5. Quantum Operation Configuration](#5-quantum-operation-configuration)
- [6. Compile and Execute Your Project](#6-compile-and-execute-your-project)

# Quick Starts

This document introduces the programming model adopted by Quingo and how to implement a simple quantum algorithm with Quingo, taking the quantum random number generator as an example. This demo should help you quickly understand some basic features of Quingo.

## 1. Heterogeneous Quantum-Classical Computation
Quingo adopts a Heterogeneous Quantum-Classical Computation model, which platform
mainly consists of two parts:
- a  **classical host**, which can be a classical CPU, or a cluster, or even a supercomputer;
  - The classical host is responsible for complex classical computing as well as loading the quantum task on the quantum coprocessor.
- a **quantum coprocessor**, which is used to _accelerate particular classically hard tasks_, and can be further divided into two parts:
  - a classical controller, which can execute a set of instructions (such as eQASM) and generate control signals over qubits;
    - It is in charge of executing instructions in a Quantum Instruction Set Architecture (QISA). It can execute auxiliary classical instructions to update classical registers and control program flow, and quantum instructions of which the execution result applies control signals (quantum operations) on qubits;
  - and a quantum core consisting of multiple qubits,
    -  where quantum state evolution happens.

In this model, a full application utilizing quantum computing contains two parts:
- **A classical host program**, which is
   - written in a classical language, such as Python or C++ (currently only Python is supported);
   - compiled/interpreted and eventually executed on the classical host.
 - **A quantum kernel**, which is
    - written in the Quingo language;
    - compiled into instructions in the supported QISA and eventually executed by the quantum coprocessor.

Note, Quingo is only used to describes the task executed on the quantum coprocessor, complex classical tasks should be described by the classical host language.

## 2. Build a Quingo Project
To create a new Quingo project, you need first select a directory for the project, and add three kinds of content:
1. The host program, which can be a set of Python files.
   - They describes the classical part and calls the quantum kernel.
2. The quantum kernel, which can be a set of Quingo files with the `.qu` suffix.
   - They describe the quantum logic with classical support.
3. The quantum operation configuration with the `.qfg` suffix.
   - It describes the primitive quantum operations as used by this project.

In the rest of this document, we will introduce:
- how to write a host program with the quantum kernel called;
- how to write a quantum kernel;
- the compilation and execution process of a Quingo project.


## 3. Host Program
Since the host program is eventually compiled/interpreted and executed on the classical CPU, the user is allowed to write arbitrary valid code in Python to do any classical computation. This section mainly focuses on how to call the quantum kernel and read the kernel computation results back. Note, the code interacting with Quingo can be arbitrarily interleaved with other Python code.

The quantum kernel in Quingo can be called in the host program using the `call_quingo(<kernel_filename>, <kernel_main_func>, <param1>, <param2>, ...)` method, and the kernel computation result can be read back using the `read_result()` method. These APIs are encapsulated in the `If_Quingo` class.

The following code (say, residing in a file named `qrng_host.py`) illustrates how to use these APIs in Python to call a quantum kernel:

```python {.line-numbers}
# qrng_host.py

from qgrtsys.if_host.python import *

if_quingo = If_Quingo()

no_ran_nums = 5
if if_quingo.call_quingo("kernel.qu", 'gen_ran_seq', no_ran_nums) is True:
    ran_num_list = if_quingo.read_result()
    print(ran_num_list)
else:
    print("Fail to call the kernel.")
```

As shown in the above code, calling a Quingo kernel roughly comprises of three steps, i.e., (1) import the interface library, (2) call the quantum kernel, and (3) read the result back.

### 3.1. Import the Interface Library in the Host Language
The interface library (qgrtsys.if_host.python) provides an interface (`If_Quingo`) in the host language to connect the Quingo Runtime System (qgrtsys). `qgrtsys` is in charge of compiling and executing Quingo and detailed in Section xx. The interface is imported and instantiated in **line 3 and line 5**.

### 3.2. Call the Quingo Kernel
The interface `If_Quingo` encapsulates the `call_quingo(<kernel_filename>, <kernel_main_func>, <param1>, <param2>, ...)` method, which can call the Quingo kernel and is shown in **line 8**.

The `call_quingo` function accepts the following parameters:
1. The first parameter is mandatory and should be the file name of the Quingo file which defines the top-level operation of the quantum kernel. In the above example, it is the string `"kernel.qu"`.
2. The second parameter is mandatory and should be the name of the top-level operation of the quantum kernel. In the above example, it is the string `"gen_ran_seq"`.
3. The following optional parameters are all converted into the corresponding data structure in Quingo and transferred to the top-level kernel operation as parameters. In the above example, only one parameter (the integer `no_ran_nums`) is transferred.

The `call_quingo` will read the corresponding Quingo file(s), call the Quingo compiler to compile the Quingo code, and load the binary or assembly code to the hardware or simulator for execution. If the execution succeeds, `call_quingo` returns `True`; otherwise, `False`.

### 3.3. Read back the Kernel Execution Result
If the kernel execution succeeds, the `read_result` method can be used to read back the execution result of the quantum kernel, as shown in **line 9**.

Note, before calling the quantum kernel and/or after reading the kernel execution result, arbitrary classical computation can be performed, such as preparing the parameter, post-process the kernel execution result, and/or calling another quantum kernel based on the post-process. This is especially useful for NISQ applications where quantum-classical hybrid computing is required, such as Variational Quantum Eigensolver (VQE).



## 4. Quingo Kernel

The Quingo kernel describes the task that should be performed by the quantum processor, i.e., the quantum core qubits and the classical controller (or the control processor) controlling the quantum core. The following code (say, residing in the file `kernel.qu`) illustrates how to generate a list of random numbers (the `gen_ran_seq(N: int)` operation) using Quingo.

``` C++ {.line-numbers}
// kernel.qu

import config.json.*
opaque H(q:qubit): unit;
opaque measure(c:qubit): bool;
opaque X(q:qubit): unit;

operation init(q: qubit) : unit {
    bool a;
    a = measure(q);
    if (a) {
        X(q);
    }
}

operation qrng(): bool {
    bool a = false;

    using(q: qubit) {
        init(q);
        H(q);
        a = measure(q);
    }

    return a;
}

operation gen_ran_seq(N: int): bool[] {
    bool[N] res;
    int i;
    i = 0;
    while (i < N) {
        res[i] = qrng();
        i = i + 1;
    }
    return res;
}
```

The kernel contains two pieces of code. The first part declares a list of **opaque  operations**, including the `init`, `H`, and `measure` operation. The second part utilize the opaque operations to define two composite **operations**, i.e., the `qrng()` operation and the `gen_ran_seq(N: int)` operation. They are explained in details in the following.

Although the programmer is free to use a set of standard gates provided by the `standard_operations.qu` package distributed along the Quingo release, the Quingo language **does not** predefine any quantum operation. Quantum operations in Quingo must be defined in either one of the two methods:
- Define a primitive operation using the `opaque` keyword;
- Define a composite operation using the `operation` keyword.

### 4.1. Opaque
An opaque operation is a primitive operation that can be used at the language level, and all primitive operations must be defined using the `opaque` keyword. Being primitive (or atomic), the language does not know how the underlying hardware deals with this operation. Its behavior is defined by the configuration file as explained later. The definition of an opaque operation contains four parts:
- The keyword `opaque`;
- The name of this opaque operation;
- A list of parameters (surrounded by parentheses `(...)`) accepted by this operation; and
- The type(s) of value(s) returned by this operation (after the colon symbol).

After an opaque operation is declared, it can be applied on qubits in a format the same as calling a function. For example, `a = measure(q)` in **line 13**.

### 4.2. Operation

The `operation` keyword can be used to define composite operations based on:
- primitive operations,
- other composite operations,
- timing control logic, and
- simply classical logic, such as arithmetic/logic operation, and program flow control (including loop, conditional branch, etc.).

Roughly speaking, a composite operation can interleave quantum operations with basic classical logic and timing information, which provides much efficiency when describing a quantum algorithm. Note, since an operation can include classical control logic (such as feedback control) and timing information, the functionality described by it might not be illustrated by a quantum circuit.

After an operation is defined, it can be used by other operation in a format the same as call a function. For example, `res[i] = qrng();` in **line 24**.

### 4.3. Qubit Allocation
Except qubits declared in the parameters, any qubit used in a Quingo program must be allocated using the `using(q0: qubit)` statement, and only be used within the following region surrounded by a pair of curly braces `{...}`. In the expression, `q` is the name of the variable, `qubit` means `q` is a single qubit.

It is assumed that there is a pool of qubits. The qubits declared in the `using` statement are allocated from the pool immediately after this statement, and released back to the pool right before the end of this region.

In addition, all qubits allocated from this pool is assumed in a unknown state and the user is responsible for initializing it.

For example, the qubit `q` is allocated and initialized in **line 10 and line 11**.

### 4.4. Type System
Quingo currently only supports the following types:
- primitive types: `bool`, `int`, `double`, `qubit`, `unit`. The `unit` type is most used by the return type of an operation, which means this operation has no return.
- tuple, which is a collection of types, for example: `(int, bool)` is a tuple with two elements, with the first being `int` and the second being `bool`.
- array, which is a list of any homogeneous types, for example: `(int, bool)[]` is a list of `(int, bool)` tuples;
- function type, which contains the parameter type list and the return type list with a arrow `->` inserted in the between. For example: ((qubit, int[]) -> bool[]).



## 5. Quantum Operation Configuration

In a new quantum project, you need to define opaque operations in the user-configure file. Here are the opaque operations of quantum random number generator:
```JSON
// config-quingo.qfg
// For now, the name of the configure file should not be changed
package  config.json
{
    "H": {
        "duration": 40,
        "type": "single-qubit",
        "eqasm": "H"
    },

    "X": {
        "duration": 20,
        "type": "single-qubit",
        "eqasm": "rx180"
    },

    "measure": {
        "duration": 600,
        "type":"meas",
        "eqasm":"Meas"
    }
}
```
The details of all opaque operations should be defined in a `qfg` file. In the file we defined an opaque operation `Hadamard gate` as follows:

- `"H"`: The name of Hadamard gate in Quingo is `H`.
- `"duration": 40`: The execution time of a Hadamard gate is 40 nanoseconds.
- `"type": "single-qubit"`: The Hadamard gate is a single-qubit gate.
- `"eqasm": "H"`: The name of Hadamard gate in eQASM, for compilation.


A `init` and `measure` operation are also defined in this configuration file.

Note, the name of the configuration file `config-quingo.qfg` should not be changed. Currently, the compiler reads the configuration from this fixed file name. In a Quingo project, if no configuration file is defined by users, the runtime system will call a default config file.



## 6. Compile and Execute Your Project
After completing the above steps, you can try to compile and execute your project. If the Quingo development kit has been properly installed, the project can be compiled and executed with some simple steps:
- Open a terminal, and enter the directory containing `host.py`;
- Run the python file `qrng_host.py` using the command `python qrng_host.py`

After executing the above steps, you can wait for the Quingo project to execute, and the result will show up in the terminal. In our quantum random number generator example, the result should be a list of 5 digits, each being either 0 or 1. You could execute the project several times and observe the result to vary.