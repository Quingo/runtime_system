

# Introduction

 Quingo is an external domain-specific language for quantum computing with NISQ features.

 In the NISQ era and the foreseeable future, most of the qubit time is occupied by quantum experiments used to calibrate qubits and quantum operations. Running quantum algorithms is only possible after qubits and operations are well characterized. On the one hand, few high-level QPLs can be connected to the quantum hardware, and fully reveal the capability of the quantum hardware. It is inconceivable that a QPL can get popular in the future without controlling any hardware. On the other hand, current quantum experiments are usually controlled with a paradigm different from any existing high-level QPLs. There is ample space to optimize such a paradigm regarding the control complexity. 

 On this background, We provide Quingo language that supports explicit timing control and using opaque operations at the language level. Quingo also introduces two modes for programming. In the algorithm mode, the wait function and operation definitions without matrices are forbidden in the program. Before generating instructions for execution, The compiler can perform optimization in all degrees of freedom, such as combine/decompose operations, schedule the timing and generate pulses for operations when required. In the experiment mode, programmers can use wait and opaque operations defined by pulses, but the compiler is not allowed to perform timing scheduling, quantum gate optimization, etc. You can use Quingo easily design your Quantum Program and simulate it either in simulators or real quantum chips we offered.

# Installation Manual

 It is recommended to use Quingo in a Windows environment. You can start your quantum programming with either a Quingo runtime system or a Quingo plugin.

 ## Develop with Runtime System
 To develop a Quingo project with runtime system, a Quingo development kit is required. The Quingo development kit consists of :
 
 - Quingo runtime system development kit `qgrtsys`
 - Quantum circuit simulator `QuantumSim`
 
 ### Dependencies
 - [Python](https://www.python.org/downloads/)
 - [JRE](https://www.java.com/zh_CN/download/)

 ## Quingo Runtime System Development Kit
 Quingo runtime system development kit `qgrtsys` consists of runtime system, Quingo compiler, and a quantum control architecture simulator `Cactus`. The runtime system development kit `qgrtsys` can realize the data interaction of kernel, host, and compiler. It can also call compiler to compile your Quingo program and call `Cactus` to verify your project. You can get `qgrtsys` from [Quingo repository](https://git.pcl.ac.cn/CQC-QCA/Quingo/src/branch/hotfix_organize_dir)

 To set up `qgrtsys`, enter the root directory of Quingo, and execute the following command:
 ```
 python setup.py develop
 ``` 
 or
 ```
 pip install -e .
 ```
 To verify the installation, execute the following command:
 ```
 pip show qgrtsys
 ```
 
 ### Quantum Computing Simulator
 Quantum computing simulator `QuantumSim` is a GPU-accelerated full density matrix simulator of quantum circuits and is optional for Quingo simulation.

 A stable version of `QuantumSim` can be fetched from [QuantumSim repository](https://gitlab.com/quantumsim/quantumsim/tree/stable/v0.2).

 To setup QuantumSim, enter the root directory of QuantumSim and install simulator using the command as follows:
 ```
 python setup.py develop
 ```
 To verify the installation of QuantumSim type the following command in the root directory of QuantumSim:
 ```
 py.test
 ```

 ## Develop with Quingo plugin
 Quingo plugin can help you developing Quingo project using VS Code. It should be noted that using Quingo plugin you can only compile your project and generate eQASM file, if you want to check the results, please use `Cactus` and `Quantumsim` to execute your eQASM file.

 ### Dependencies
 - [Visual Studio Code](https://code.visualstudio.com/)

 ### Quingo Plugin
 Quingo plugin is a VS Code plugin that can used to help you write and compile your Quingo project. The latest version of Quingo plugin can be found in [website](https://git.pcl.ac.cn/CQC-QCA/Quingo_plugin/src/branch/master).

 To setup Quingo plugin, download `vsix` plugin file in the above website, then follow these steps to install it in VS Code::
 1. Open VS Code and select `Extensions` in sidebar(or press `Ctrl + Shift + X`).
 2. In `Extensions` bar, click `More actions...` button and select `install from VSIX...`.
 3. Select the Quingo plugin file in the pop-up window.
 4. If the installation is completed, you can find Quingo plugin in your installed extensions.


 Now start your first Quingo project!

# Quick Starts

In this part, we will implement a simple algorithm of quantum random number generator to help you quickly understand some features of our language. This algorithm uses quantum mechanical properties to generate a random number.

The workflow of using Quingo consists of three steps:
1. Give host program
2. Give kernel program
3. Compile and execute the project

We will explain each step in detail in subsequent sections.
## Create a New Quantum Project
To create a new quantum project, you should first select a directory for the program, and add three types of files:
1. Create a file named `config.qfg` that will contain your opaque gates' definition.
2. Create a file named `host.py` that will contain your host program code.
3. Create a file named `kernel.qu` that will contain your kernel program code.

## Add User Configuration
In a new quantum project, you need to define opaque operations in the user-configure file. Here are the opaque operations of quantum random number generator:
```JSON
{
"H": {
	        "duration": 40,
	        "type": "single-qubit",
	        "eqasm": "H"
	   	   },
"measure": {
	        "duration": 600,
	        "type":"meas",
	        "eqasm":"Meas"
	       }
}
```
The user-configure file is written in a `qfg` file. In the file we defined an opaque operation `Hadamard gate` as follows:

`"H"`: The name of Hadamard gate in Quingo is `H`.

`"duration": 40`: The execution time of Hadamard gate is 40 clock cycles.

`"type": "single-qubit"`: The Hadamard gate is a single qubit gate.

`"eqasm": "H"`: The name of Hadamard gate in eQASM, for compilation.

A "measure" operation for measurement is also defined in the configure file. You can copy the code above in our user configure file `config-quingo.qfg`, the name of the configure file should not be changed. In a Quingo project, if no configure file is defined by users, the runtime system will call a default configure file.

## Give Host Program
The host program is given in Python, and it can call a kernel program and get kernel execution results to implement quantum computation. Here is the host program of our quantum random number generator:
```python
from qgrtsys.if_host.python import *

if_quingo = If_Quingo()

if_quingo.call_quingo("kernel.qu",'random')

print(if_quingo.read_result())
```
In the host program, we call the quantum kernel to run the quantum random number generator and read back the kernel execution result.you can copy code above in your host program file `host.py`. Now we will explain the host program in steps:

### Step 1: Import the interface library in the host language
The elements of Quingo runtime system should be imported as follows:
```python
from qgrtsys.if_host.python import *
```

### Step 2: Call the quantum kernel
The `call_quingo` function of `If_Quingo()` can be used to call a Quingo kernel. In this example, we call the "random" function of the kernel as follows:
```python
if_quingo = If_Quingo()

if_quingo.call_quingo("kernel.qu",'random')
```

### Step 3: Read back the kernel execution result
The `read_result` function of `If_Quingo()` can be used to read simulation results of your kernel program. In this example, we print the results in the terminal.
```python
print(if_quingo.read_result())
```

## Give Kernel Program
The kernel program is written in the Quingo language. We use it to implement quantum computing. Here is the kernel program of our quantum random number generator:
```
opaque H(q:qubit): unit;
opaque measure(c:qubit): bool;

operation random(): bool{
    bool result;
    using (q0: qubit){
        H(q0);
        result = measure(q0);
    }
    return result;
}
```
In the program above, we declared a qubit `q0`, add a Hadamard gate on this qubit, then measure the qubit and save the result in a bool variable. You can copy the code above in your kernel program file `kernel.qu`. Now we will explain the kernel program in steps:

### Step 1: Import operations
In the Quingo language, all opaque operations should be defined in the user-configure file. In this project, the Hadamard gate and measure are defined in `config.json`, the compiler can find the user configure file in the compilation, but operations should be declared before they are used in kernel program, so you need to declare operations in your kernel program as follows:
```
opaque H(q:qubit): unit;
opaque measure(c:qubit): bool;
```
After you declare operations, you can use the opaque operations in the kernel program.

### Step 2: Declare qubit
In Quingo language, we declare the qubit variable as follows:
```
using (q0: qubit){

}
```
In Quingo language, you can add operations on qubits only in using statement, and operated qubits should be declared as `q0: qubit`. In the expression, `q0` is the name of the variable, `qubit` means `q0` is a single qubit.

### Step 3: Add operations to qubit
We add Hadamard gate on q0 as follows:
```
H(q0);
```
`H` is the name of the Hardmard gate.

### Step 4: Measure the qubit and read results
We use `measure` expression to measure qubit and save the result in a bool variable as follows:
```
result = measure(q0);
```

### Step 5: Return result
The `random` function has the type of `bool` means the function has return type bool, so you should add a return statement as follows:
```
return result;
```

## Compile and Execute Your Project
After completing the above steps, you can try to compile and execute your project in the Visual Studio Code. If the Quingo development kit has been properly installed, the project can be compiled and executed by entering the directory of host.py and executing the following commands:
```
python host.py
```

## Result Presentation
After executing the above steps, you can wait for the Quingo project to complete, and the result will show in the terminal. For our quantum random number generator, the result should be either 0 or 1. You can execute the project several times and observe the result.



# Quingo Programming Language

## Quingo Program Execution
A Quingo program undergoes the following stages:

1. **Edit time**: Quantum programmers describe the quantum application using Python (for the host) and Quingo (for the kernel).
   - Possible configuration (such as defining what primitive operations can be used by the hardware) is also done at this stage.

2. **Classical compile-time**: A conventional compiler that compiles the host program and outputs a classical binary.

3. **Pre classical execution time**: A `classical computer` executes the classical binary up to the moment when the quantum function defined in the quantum kernel is called.
   - The result of this step: all parameters required to invoke the quantum kernel have been determined. From this moment on, the classical binary pauses until the quantum execution finishes.

4. **Quantum compile-time**: When the classical host calls the quantum function, the quantum compiler is triggered to compile the quantum kernel.
   - All parameters used to invoke the quantum function (called the `interface parameters`) will be known at this moment.
   - The quantum compiler can perform aggressive optimization by partial execution. The output is a quantum binary.

5. **Quantum execution time**: This quantum binary is uploaded to and executed by the quantum control microarchitecture (QCM).
   - The result of executing this binary is to apply quantum gates on qubits and perform measurement over qubits (i.e., controlled quantum state evolution performing computation).
   - Required measurement results are stored as the computation result in the shared memory between the quantum co-processor and the host.

6. **Post-classical execution time**: The classical binary continues execution.
   - It reads the quantum computation result and performs the following post-processing.

7. **Possible repetition**: In some algorithms like VQE, steps 3 to 6 form an iteration and should be repeated several times to reach a good enough result.

## File Structure

In a Quingo program, the host program, kernel program, and user configure file are required. Their functions are as follows:

**host program**: Written in Python, implements classical computation and calls kernel program. It reads the execution results of the kernel program from the shared memory between the quantum co-processor and the host. Any file with the extension of `.py` is considered as host program.

**Kernel program**: Written in Quingo, realizes quantum computation and measurements. Any file with the extension of `.qu` is considered as kernel program.

**User configuration file**: A `qfg` file, defines all the opaque operations. Any file with the extension of `qfg` is considered as a user configuration file.

To realize the interaction between host, quantum compiler, and kernel, we provide a runtime system. You can call the runtime system in a host program as follows:
```
rsm = Runtime_system_manager()
```

### Import a File
If you write your own configure file, your kernel program and configure file need to be in the same directory, or default config file will be used. During compilation, the compiler will find the user config file. If you want to import functions in other Quingo file, use import statements. For example, the following is part of a Quingo file `standard.qu`:
```
package operations

opaque X(q:qubit): unit;
opaque Y(q:qubit): unit;
opaque Z(q:qubit): unit;
```
You can import the file as follows:
```
import operations.*
```

After you install Quingo runtime system development kit `qgrtsys`, you can compose a host program in Python to call the kernel program. To call the kernel program in a host, you can use `call_quingo` functions in the host program in the following form: `call_quingo(<name of Quingo file>,<called function>,<parameters of the function>)`. We give an example as follows:

```python
rsm = If_Quingo()
a = [1, 2, 3, 4]
b = 10

rsm.call_quingo("t1.quingo","t1",a,b)
```
### Function Declarations
Quingo has two types of functions: operation and opaque. Operations are roughly analogous to functions in other languages, and opaques are opaque quantum operations. Functions' names must be unique within a project and may not conflict with any keyword. Declared opaque should be defined in a configuration file.

An operation declaration consists of a keyword `operation`, a name of the operation (can not be "main"), a typed identifier tuple that defines the arguments to the operation, a colon `:`, a type annotation that describes the operation’s result type, and a block statement. The block statement contains the realization of the operation. For example:
```
operation op1(array: int[], integer: int): bool {
	bool result;
    result = (array[1] == integer);
	return results;
}
```
If you define an opaque operation in the configuration file, you still need to declare it in a Quingo file before you use it. An opaque declaration consists of a keyword `opaque`, a name of the opaque, a typed identifier tuple that defines the arguments to the opaque (arguments must be qubit or qubit array), parameters that define parameters of this operation(if the operation is opaque with parameters), a result type annotation and a terminating semicolon `;`. The following example declared an opaque operation named `H`:
```
opaque H(q:qubit): unit;
opaque X(q:qubit, par:double):unit;
```

## Types
This part will introduce Quingo types in detail. Quingo is a strongly-typed language, so we recommend that you carefully use these types. Quingo provides primitive types, tuple types, array types, and function types. In the rest of this section, all the types of Quingo will be described.

### Primitive Types
Quingo language provides several primitive types that can be used directly.
- The `int` type represents a 32-bit signed integer, e.g., 1, 100, -3
- The `double` type represents a double-precision floating-point number, e.g., 1.1, 9.99
- The `bool` type represents a Boolean value that can be either true or false
- The `unit` type represents a null value (). This type is used to indicate function returns no information
- The `qubit` type represents a quantum bit or qubit for short. Qubits are opaque to the user.

### Tuple Type
We can denote a tuple type as (type 1, type 2, type 3, etc.). The types used to construct a tuple type can themselves be tuple types. For example, a tuple type can be (int, bool, int), (int,(int, bool)), etc. Note that a tuple type must contain at least two elements. For example, (int) is illegal.

Tuples can collect values together into a single value, making it easier to pass them around.

### Array Type
For any Quingo type `T`, an array type exist, which can represent an array of values of type `T`. The array Type can be defined with type and `[]`. For example "int[]" represents one-dimensional int array, "qubit[][]" represents two-dimensional qubit array.

We gave some examples as follows:
```
int a;

int[3] x;  // define a one-dimensional int array, number of elements of the array is 3
bool[][] y;   // define a two-dimensional bool array

x[0] = a; // assign "a" to the first element of array "x"
x = {1,2,a} // assign {1, 2, a} to array "x"

```
### Function Type
The input and output type of each function is specified by its function type. The function type has form of `(<input type> -> <return type>)`. `<input type>` indicates the input type of the function, `<return type>` indicates the return type of the function. All functions are considered to take a single value as input and return a single value, both input and return values may be tuples. If there are no returned results, the return type is a unit type. If there are no input parameters, the input type is an empty tuple type.

Some matching examples of function types can referred to the following code:
```
operation func1(a: int, b: int): bool{
    ...
}   // function type of func1 is (int,int) -> bool

operation func2(c: (int,int)->bool): bool{
    ...
}   // type of input parameter "c" is (int,int) -> bool

operation func3():bool{
    ...
}   // function type of "func3" is unit -> bool

operation main():unit{
    int x;
    int y;
    bool z;
    ...
    z = func2(func1); //function type of "func1" matches the parameter type of "func2"
}

opaque H(q0:qubit):unit; //function type of "H" is qubit -> unit
```
## Expression

### Variable Expression
If the name of an identifier equal to the name of a variable of type `T`, the identifier is a variable expression of type `T`. For example, if we have ```int a``` statement. Then "a" is a variable of type `int`.

### Literal Expression
Literal expressions can be divided into three parts: boolean literal, int literal, and double literal. A boolean literal expression is either `true` or `false`, and the type of it is `bool`, an int literal expression is an integer and its type is `int`, a double literal expression is a floating-point number and its type is `double`.

### Boolean Expression
We provide boolean and relation operators for logical operations. The value of a Boolean expression is either `true` or `false`. For two expressions with the same primitive type, you can use binary operators to construct a boolean expression that indicates the relationship of two expressions. For single expression with bool type, a unary operator can ben used to construct a boolean expression.

### Array Expression
An array expression is a sequence of one or more element expressions separated by commas and enclosed in `{}`. All elements must be compatible with the same type. For instance, members of array `{1, 2, 3}` has an `int` type. Type of members in an array can be `array`, `int`, `bool`, `double`, `qubit`, `tuple`. Empty array `{}` is not allowed, the addition of array is not allowed either.

### Array Access Expression
Given an array type variable, array access can be constructed by the name of the variable and some `[]`. The array access expression has the same type of given array variable type. For instance, if "a" is bound to an int type array, then `a[1]` is an expression with `int` type. Especially, `length` is a function that returns the number of elements of array access, with the return type of int. For array `bool[10] b`, type of `b.length` is `int`.

### Tuple Expression
A Tuple expression is a sequence of element expressions separated by commas and enclosed in `()`. It has a tuple type, and the tuple type consists of the types of each tuple element in the expression. For instance, `(1, 2, True)` is an `(int, int, bool)` type expression. Noted that number of elements in a tuple expression should more than one.

### Function Call Expression
A function call expression can be constructed by a given a declared function and a tuple expression of the input type of the function's function type. The type of function call is the output type of the given function.

For example, if "func1" is an operation with function type `(int, int) -> bool`, then "func1(1,2)" is a function call expression and type of this expression is `bool`.

### Arithmetic Expression
For arithmetic expressions, unary operators are right-associative, and binary operators are left-associative. We list Quingo operators below, in the order of precedence, from highest to lowest:
- Operators

| Operator | Arity | Parameter type | Description |
| :------: | :--: | :------------: | :------: |
| ! | Unary | Bool | Logical Not |
| -, + | Unary | Int,Double | Hold or reverse value |
| *, / | Binary | Int,Double | Multiplication, division |
| % | Binary | Int | integer modulus|
| -, + | Binary | Int, Double | Addition, subtraction |
| <, <=, >, >= | Binary | Int, Double | Less-than, less-than-or-equal, greater-than, and greater-than-or-equal comparisons |
| ==, != | Binary | Int, Double, Bool | equal and not-equal comparisons |
| && | Binary | Bool | Logical AND |
| \|\| | Binary | Bool | Logical OR |

### Type Conversion Expression
Quingo supports explicit type conversion of int and double type. Use `toInt()` transfer expression from double type to int type and `toDouble()` transfer expression from int type to double type. for example, `toInt(1.0)`, `toDouble(10)`.

## Statements

### Empty Statement
A statement with only a terminating semicolon `;` is an empty statement. An empty statement does nothing in compilation and execution.

### Variable Declaration Statement
A variable declaration statement is used to declare a variable with a specified type. The statement is consists of the specified type and referred name of the variable, the definition of this variable can also be done ins the statement. Some examples are shown as follows:
```
int a;
double b = 1.1;
(bool, double) c;
```

### Block Statement
Quingo statements are grouped into statement blocks. A block statement starts with a `{` and ends with a `}`. A block statement that is lexically enclosed within another block statement is considered to be a sub-block of the containing block statement.

### Assignment Statement
The form of an assignment is ```<variable> = <right expression>;```. It has a symbol `=` and ends with a terminating semicolon `;`. The function of an assignment is to bind the value of the right expression to the variable. The variable can be in the form of array access, tuples, or normal variables, while the right expression can be all types of expressions.

In an assignment, the variable and right expression should have the same type. 

For an array access assignment, the dimension of left and right should equal. Some examples are shown as follows:
```
int[2][2] array;

array = {{1, 2}, {3, 4}};

array[1] = {1, 2, 3};

array[2] = {1};

array[1][2] = 1;
```
For some right arithmetic expressions, a simplified assignment rule is available, for example, ``` a += b``` is equal to ```a = a + b```. In Quingo language, add("+"), minus("-"), multiple("*"), division("\") and modulo("%") are allowed to combine with `=` to realize the simplified assignment operation. Some examples are shown as follows：
```
int a = 0; 

a += 3; 

a %= 2;

a *= 2;
```

### Control Statements

#### If Statement
An if statement consists of the keyword `if`, an open parenthesis `(`, a condition (i.e., a Boolean expression), a close parenthesis `)`, and a block statement. The block statement is executed once if the condition evaluates to true. The statement may optionally finish with an else clause, which is consists of the keyword `else`, and a block statement, if the condition of the condition evaluates to false, the block statement bounded to "else" is executed. Some examples are shown as follows：
```
bool a = true;

if(a){
    
}else{
    
}//if block will be executed once

if (false){

}// if block will not be executed
```

#### While Statement
A while statement consists of the keyword `while`, an open parenthesis `(`, a condition (i.e., a Boolean expression), a close parenthesis `)`, and a block statement. The block statement (the body of the loop) is executed as long as the condition evaluates to true. Some examples are shown as follows：
```
int a = 0;

while (a < 10>){
    a += 1;
}   //while loop will be executed 10 times

while(false){

} // while loop will not be executed

``` 

#### For Statement
A for statement consists of the keyword `for`, an open parenthesis `(`, a singular statement, a condition (i.e., a Boolean expression), an end cycle statement, a close parenthesis `)`, and a block statement. The block statement (the body of the loop) is executed as long as the condition evaluates to true, at the end of each loop the end cycle statement will execute one time. Some examples are shown as follows：
```
for(int i=0; i < 10; i += 1){
    //for loop will be executed 10 times
}
```

#### Switch-case Statement
A Switch-case statement is available when there are limited options. A switch-case statement consists of the keyword `switch`, an open parenthesis `(`, a condition expression, a close parenthesis `)`, and a switch block.

A switch block consists of an open parenthesis `{`, group of case statements, an optional default statement, and a close parenthesis `}`.

A case statement consists of a keyword `case`, a case expression, a colon `:`, and a block statement.

A default statement consists of a keyword `default`, a colon `:`, and a block statement.

If the value of a conditional expression equals to the value of one of the case statements' case expressions, the block statement bounded to the corresponding case statement is executed. If there is no matching case statement and a default statement exists, the block statement bounded to the default statement is executed. Therefore, we strongly suggest you add a default statement in every switch-case statement. Some examples are shown as follows：
```
int a;
	
switch(a){
    case 1:{}
    case 2:{}
    default:{}
}
```

#### Break Statement
A break statement consists of a keyword `break` and a terminating semicolon `;`. This statement can only be used in a while or switch-case statements. When a break statement is executed, the current loop or switch-case will be skipped. The statement group of every block statement bounded to a case statement should contain a break statement. Some examples are shown as follows：
```
while(true){
	break;  //break out of while loop
}

for(int i=0; i < 3; i+=1){
    break; //break out of for statement
}

int a = 2;
switch(a){
    case 1 : {break;} //break out of switch statement
    default:{break;}
}
```

#### Continue Statement
A continue statement consists of a keyword `continue` and a terminating semicolon `;`. This statement can only be used on a while or for statements. When a continue statement is executed, the remaining unexecuted statements in the body of the loop will be skipped, and the condition of the next loop will be evaluated. Some examples are shown as follows：
```
while(true){
    continue;
    a = b + c; // this statement will not be executed
}

for(int i=0; i < 3; i+=1){
    continue;
}
```

#### Return Statement
The return statement ends the execution of an operation whose type is not `unit` and returns a value to the caller. It consists of the keyword `return`, an expression, and a terminating semicolon `;`.

The type of expression bounded to a return statement equals to the output type of the operation that contains the return statement. When the output type of operation is `unit`, the operation statement should not contain any return statements or return nothing in a return statement. Some examples are shown as follows：
```
operation syntax_return_test1(): unit{

	return;
}

operation syntax_return_test2(): (int,double){

	return (1,1.0);
}

operation syntax_return_test3(): bool[]{

	return {true,false,false};
}
```

### Using Statement
A using statement consists of a keyword `using`, an open parenthesis `(`, a qubit binding,  a close parenthesis `)`, and a block statement.

In Quingo language, qubits are only allocated and used within a using statement. A qubit binding consists of either a single symbol or a tuple of symbols, a colon `:`, and types. Types of qubits can be `qubit` for a single qubit and `qubit[]` for qubit array. If there are tuples of symbols, the type should be a tuple type. Some examples are shown as follows:
```
using(target: qubit){
    // "target" is a single qubit symbol 
}

using((query, answer): (qubit[10], qubit)){
    // "query" is a qubit array symbol and "answer" is a single qubit symbol
}
```

###  Wait Statement
A wait statement is a timing control statement. A wait statement consists of a keyword `wait`, an open parenthesis `(`, a list of qubit type expression, an int type expression, a close parenthesis `)`, and a terminating semicolon `;`. When the wait statement is executed, the qubits in the list of qubit type expressions will wait a while before it is allowed to operate. The waiting time is the product of the value of the int type expression and the hardware clock cycle. Some examples are shown as follows:
```
using((q1,q2):(qubit,qubit[])){
    wait(q1,2);
    wait(q2,3);
    wait(q1,q2,4);
}
```

###  Function Call Statement
The function call statement consists of a function call expression and a terminating semicolon `;`. Some examples are shown as follows:
```
operation syntax_functioncall_test(): unit{

	int a = 1;
	
	test1(a);

}

operation test1(a:int):unit{
	
}
```
```
operation high(fun: qubit->unit, q2: qubit): unit
{
	fun(q2);
}
 
operation higher(q: qubit, caller: (qubit->unit, qubit) -> unit, callee: qubit->unit): unit
{
	caller(callee,q);
}

operation main(): unit
{
	using (q0 : qubit) {
		high(H, q0);
		higher(q0, high, H);
		bool a = measure(q0);
	}
}

```

##  Timing Control
Quingo allows users to control the time of applying quantum operations explicitly. We first introduce the time model used in Quingo, and thereafter how to specify the timing control.

###  Time Model
Quingo recodes and controls the time of applying `quantum` operations. The timeline of classical operations is ignored. The global timer starts when qubits are allocated and increases along with the program execution. By default, one operation starts after the last one finishes. The duration of the operations is specified in Quingo configuration files. Below is a naive example shows the value of the global timer *gt* in the execution process of a piece of Quingo program:
```c
using((q0, q1):(qubit, qubit)){
                    <- gt = 0 ns, when the timer start
    init(q0);
                    <- gt = 200,000 ns, the init operation finishes
    X(q0);
                    <- gt = 200,020 ns, the X gate has been applied
    if (a == 8 * 5) {
                    <- gt = 200,020 ns, the execution of classical codes does not affect the timeline of qubits
        CNOT(q0,q1);
                    <- gt = 200,100 ns, the CNOT gate takes 80 ns
    }
}
```

###  Timer label
Quingo uses two structures to indicate timing control, i.e., *timer labels* and *timing constraints*. A timer label is written as `<Identifier> :` before a statement. The timer starts when the statement executes. You can specify many timers in a program. All of these timers increase at the same pace as the global timer. The only difference between them is the starting moment. We use the same example as the previous to illustrate this idea:
```c
using((q0, q1):(qubit, qubit)){
                    <- gt = 0 ns
    init(q0);
t1:                 <- gt = 200,000 ns, t1 = 0 ns
    X(q0);
                    <- gt = 200,020 ns, t1 = 20 ns
    if (a == 8 * 5) {
t2:                 <- gt = 200,020 ns, t1 = 20 ns, t2 = 0 ns
        CNOT(q0,q1);
                    <- gt = 200,100 ns, t1 = 100 ns, t2 = 80 ns
    }
}
```
We write the labels in different lines from the statements for a better understanding. However, you can also write it in the same line as the statement, i.e., `t1: X(q0);` without changing its semantics.

The timer labels do not change the scheduling of quantum operations. They only act as baselines of the timing constraints.

###  Timing Constraints
Timing constraints are specified at the end of statements: `<Function call> @<constraint>;`. It forces the execution of the `<function call>` to happen under the `<constraint>`. The `<constraint>` is equality or inequality of the timer labels. For example, `@t1<=80` means that the `<function call>` should happen while the value of timer `t1` is no more than 80 ns. Multiple equality or inequality can be combined by `&` or `|` for the AND and OR semantics. We add a timing constraint to the previous example, and it will execute as follows:
```c
using((q0, q1):(qubit, qubit)){
                    <- gt = 0 ns
    init(q0);
t1:                 <- gt = 200,000 ns, t1 = 0 ns
    X(q0);
                    <- gt = 200,020 ns, t1 = 20 ns
    if (a == 8 * 5) {
                    <- gt = 200,020 ns, t1 = 20 ns
                    <- gt = 200,080 ns, t1 = 80 ns
        CNOT(q0,q1) @t1=80;
                    <- gt = 200,160 ns, t1 = 160 ns
    }
}
```
Note that for equality, we use `=` instead of `==`. The constraint requires `t1` to be 80 ns when `CNOT` is applied. However, we know from previous examples that the default value of `t1` would be 20 ns at that point. Therefore, the scheduler forces an idle period of 60 ns to meet the constraint. If the scheduler fails to meet some constraints, it will raise an error, and the compilation will be aborted.

One operation can be scheduled at the same time as its previous operation, but not earlier than that. For example,
```c
using((q0, q1):(qubit, qubit)){
    init(q0);
t1: X(q0);
    X(q1) @t1=0; // X(q1) operates at the same time as X(q0)
    H(q0);
    if (a == 8 * 5) {
        CNOT(q0,q1) @t1=0; // not possible
    }
}
```
In this example, `X` gate applies to `q0` and `q1` at the same time. Then, `H` gate applies to `q0` when `t1` equals  20 ns following the default schedule. Since `CNOT` is after `H` in the program, it cannot be scheduled earlier.

###  Scope
A timing constraint can only refer to timer labels that are defined **before**. The following example will lead to an error:
```c
using((q0, q1):(qubit, qubit)){
    init(q0);
    X(q0) @t1=0; // error
t1: H(q0);
}
```

The timing constraint in a block statement can refer to the timer label outside. Except that, the timer labels defined in other blocks are not allowed to refer to. For example,
```c
using((q0, q1):(qubit, qubit)) {
    init(q0);
t1: H(q0);
    if (a == 8 * 5) {
        X(q0) @t1=100; // correct
t2:     X(q1);
    }
    else {
        H(q1) @t2=100; // error
    }
    H(q1) @t2=200; // error
}
```
###  Timing Constraints in Loops
When referring to a timer label outside the loop, the loop must be unrolled. For example,
```c
using(q:qubit[3]) {
t1: for (int i=0; i<3; ++i) {
        H(q[i]) @t1=0;
    }
}
```
It is equivalent to
```c
t1: {
        H(q[0]) @t1=0;
        H(q[1]) @t1=0;
        H(q[2]) @t1=0;
    }
```
It requires that all the three qubits be applied with an `H` gate together.

If the loop is not intended to be unrolled, then the constraints can only refer to the timer labels defined inside the loop. For example,
```c
using(q:qubit[3]) {
    for (int i=0; i<3; ++i) {
t1:     X(q[i]);
        H(q[i]) @t1=100;
    }
}
```
In each iteration, the `H` gate will apply after the `X` gate with a gap of 80 ns.

# Quingo Library

In a Quingo project, opaque operations need to be defined in a configure file. Quingo library consists of different useful opaque operations. You can create a config file with an extension `qfg` and define opaque operations in it. If there are no configure files in Quingo project, the runtime system will call default lib when executing the project. In a config file operations are defined as follows:
```JSON
{
    "X": {
        "duration": 20,
        "type": "single-qubit-param",
        "eqasm": "x"
    },
    "Y": {
        "duration": 20,
        "type": "single-qubit-param",
        "eqasm": "y"
    },
    "Z": {
        "duration": 20,
        "type": "single-qubit-param",
        "eqasm": "z"
    },
    "T": {
        "duration": 20,
        "type": "single-qubit",
        "eqasm": "t"
    },
    "Tdg": {
        "duration": 20,
        "type": "single-qubit",
        "eqasm": "tdg"
    },
    "S": {
        "duration": 20,
        "type": "single-qubit",
        "eqasm": "S"
    },
	"H": {
		"duration": 40,
		"type": "single-qubit",
		"eqasm": "H"
	},
	"CZ": {
		"duration": 40,
		"type": "two-qubit",
		"eqasm": "CZ"
	},
	"measure": {
		"duration": 600,
		"type":"meas",
		"eqasm":"MeasZ"
	}
}

```
Each opaque has three parameters:
1. duration : The execution time(unit is clock cycles).
2. type: four types of opaque are supported: single-qubit gate without parameters(type is `single-qubit`), single-qubit gate with parameters(type is `single-qubit-param`), two-qubits gate without parameters(type is `two-qubit`), two-qubits gate with parameters(type is `two-qubit-param`).
3. eqasm: The name of the opaque operation in eQASM, for compilation.
The defined opaque operations need to be declared in Quingo project before it can be used. The corresponding operation declaration file has the form of:
```

opaque measure(c:qubit): bool;
opaque X(q:qubit, v:double): unit;
opaque Y(q:qubit, v:double): unit;
opaque Z(q:qubit, v:double): unit;
opaque T(q:qubit): unit;
opaque Tdg(q:qubit): unit;
opaque S(q:qubit): unit;
opaque H(q:qubit): unit;
opaque CZ(c:qubit, t:qubit): unit;

```

# Quingo Command-line Compiler
You can use Quingo compiler with a terminal command. This command-line version compiler is an executable .jar file, which will be referred to as *quingo.jar* in this document.

## Prerequisite
Before using the compiler, you should install the latest version of [Java Development ToolKit](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html). You may need to add or modify a few environmental  variables as well. After a success installation, you should be able to execute this command: `java -version`.

## Usage
The general usage of Quingo command-line compiler is as follows:
```sh
java -jar quingo.jar <Quingo_files> <configuration_file> [options]
```

`java -jar quingo.jar` is calling the compiler with a Java virtual machine. It is followed by one or more Quingo source files (.qu). Note that the file containing the `main` operation should be placed as the first one. Then, you specify the configuration file (.qfg). Some options are available if you want to tweak some parameters of the compiler.

## Options
### Output file name
By default, the generated eQASM file (.eqasm) is placed in a subfolder *build* with the same name as the source file containing the `main` operation. However, you can alter this using the option `-o` or `--output` and the **relative** path of the new file. In this path, "/" is used to indicate the file system's hierarchy, including in Windows OS. For example, `-o src-gen/my.eqasm` means generating *my.eqasm* under the subfolder *src-gen*. If a subfolder does not exist, it will be created automatically. You can even access the parent folder with "../".

### Shared memory address
After the execution of a Quingo program, the `main` operation writes its return values to a memory region that is shared with the host processor. The beginning address of this region is configurable with the option `-s` or `--shared-addr`. The default value is 0.

### Static memory address
By default, the compiler stores variable on memory starting from 0x10000. You can alter this address via the option `-t` or `--static-addr`.

### Dynamic memory address
For an array whose length is not known during the compilation time, it is stored in a different memory region from the other variables. This region starts from 0x20000 by default. You can change this address via the option `-d` or `--dynamic-addr`.

### Maximum unrolling number
Quingo compiler will unroll loops up to a small number, e.g., 100 by default. You can change this number with the option `-u` or `--max-unroll`. The rest of the loop will be implemented using eQASM branch instructions.

### Help
`-h` or `--help` option will print the usage of the Quingo compiler.

### Version
The version of the Quingo compiler can be printed with `-v` or `--version`.

## Examples
The following examples are all correct ways of invoking the Quingo compiler.
```
java -jar quingo.jar t1.qu config-quingo.qfg
java -jar quingo.jar t1.qu config-quingo.qfg -o my.eqasm
java -jar quingo.jar t1.qu config-quingo.qfg -s 4096 --static-addr 9192
java -jar quingo.jar -u 1000 t1.qu config-quingo.qfg
java -jar quingo.jar -h
```