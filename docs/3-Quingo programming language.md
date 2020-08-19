

# Quingo Programming Language

<!-- TOC -->

- [Quingo Programming Language](#quingo-programming-language)
  - [1. Quingo Program Execution](#1-quingo-program-execution)
  - [2. File Structure](#2-file-structure)
    - [2.1. Import a File](#21-import-a-file)
    - [2.2. Function Declarations](#22-function-declarations)
  - [3. Types](#3-types)
    - [3.1. Primitive Types](#31-primitive-types)
    - [3.2. Tuple Type](#32-tuple-type)
    - [3.3. Array Type](#33-array-type)
    - [3.4. Function Type](#34-function-type)
  - [4. Expression](#4-expression)
    - [4.1. Variable Expression](#41-variable-expression)
    - [4.2. Literal Expression](#42-literal-expression)
    - [4.3. Boolean Expression](#43-boolean-expression)
    - [4.4. Array Expression](#44-array-expression)
    - [4.5. Array Access Expression](#45-array-access-expression)
    - [4.6. Tuple Expression](#46-tuple-expression)
    - [4.7. Function Call Expression](#47-function-call-expression)
    - [4.8. Arithmetic Expression](#48-arithmetic-expression)
    - [4.9. Type Conversion Expression](#49-type-conversion-expression)
  - [5. Statements](#5-statements)
    - [5.1. Empty Statement](#51-empty-statement)
    - [5.2. Variable Declaration Statement](#52-variable-declaration-statement)
    - [5.3. Block Statement](#53-block-statement)
    - [5.4. Assignment Statement](#54-assignment-statement)
    - [5.5. Control Statements](#55-control-statements)
      - [5.5.1. If Statement](#551-if-statement)
      - [5.5.2. While Statement](#552-while-statement)
      - [5.5.3. For Statement](#553-for-statement)
      - [5.5.4. Switch-case Statement](#554-switch-case-statement)
      - [5.5.5. Break Statement](#555-break-statement)
      - [5.5.6. Continue Statement](#556-continue-statement)
      - [5.5.7. Return Statement](#557-return-statement)
    - [5.6. Using Statement](#56-using-statement)
    - [5.7. Wait Statement](#57-wait-statement)
    - [5.8. Function Call Statement](#58-function-call-statement)
  - [6. Timing Control](#6-timing-control)
    - [6.1. Time Model](#61-time-model)
    - [6.2. Timer label](#62-timer-label)
    - [6.3. Timing Constraints](#63-timing-constraints)
    - [6.4. Scope](#64-scope)
    - [6.5. Timing Constraints in Loops](#65-timing-constraints-in-loops)

<!-- /TOC -->
<!-- vscode-markdown-toc-config
	numbering=true
	autoSave=true
	/vscode-markdown-toc-config -->
<!-- /vscode-markdown-toc -->

## 1. Quingo Program Execution
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

## 2. File Structure

In a Quingo program, the host program, kernel program, and user configure file are required. Their functions are as follows:

**host program**: Written in Python, implements classical computation and calls kernel program. It reads the execution results of the kernel program from the shared memory between the quantum co-processor and the host. Any file with the extension of `.py` is considered as host program.

**Kernel program**: Written in Quingo, realizes quantum computation and measurements. Any file with the extension of `.qu` is considered as kernel program.

**User configuration file**: A `qfg` file, defines all the opaque operations. Any file with the extension of `qfg` is considered as a user configuration file.

To realize the interaction between host, quantum compiler, and kernel, we provide a runtime system. You can call the runtime system in a host program as follows:
```
rsm = Runtime_system_manager()
```

### 2.1. Import a File
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
### 2.2. Function Declarations
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

## 3. Types
This part will introduce Quingo types in detail. Quingo is a strongly-typed language, so we recommend that you carefully use these types. Quingo provides primitive types, tuple types, array types, and function types. In the rest of this section, all the types of Quingo will be described.

### 3.1. Primitive Types
Quingo language provides several primitive types that can be used directly.
- The `int` type represents a 32-bit signed integer, e.g., 1, 100, -3
- The `double` type represents a double-precision floating-point number, e.g., 1.1, 9.99
- The `bool` type represents a Boolean value that can be either true or false
- The `unit` type represents a null value (). This type is used to indicate function returns no information
- The `qubit` type represents a quantum bit or qubit for short. Qubits are opaque to the user.

### 3.2. Tuple Type
We can denote a tuple type as (type 1, type 2, type 3, etc.). The types used to construct a tuple type can themselves be tuple types. For example, a tuple type can be (int, bool, int), (int,(int, bool)), etc. Note that a tuple type must contain at least two elements. For example, (int) is illegal.

Tuples can collect values together into a single value, making it easier to pass them around.

### 3.3. Array Type
For any Quingo type `T`, an array type exist, which can represent an array of values of type `T`. The array Type can be defined with type and `[]`. For example "int[]" represents one-dimensional int array, "qubit[][]" represents two-dimensional qubit array.

We gave some examples as follows:
```
int a;

int[3] x;  // define a one-dimensional int array, number of elements of the array is 3
bool[][] y;   // define a two-dimensional bool array

x[0] = a; // assign "a" to the first element of array "x"
x = {1,2,a} // assign {1, 2, a} to array "x"

```
### 3.4. Function Type
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
## 4. Expression

### 4.1. Variable Expression
If the name of an identifier equal to the name of a variable of type `T`, the identifier is a variable expression of type `T`. For example, if we have ```int a``` statement. Then "a" is a variable of type `int`.

### 4.2. Literal Expression
Literal expressions can be divided into three parts: boolean literal, int literal, and double literal. A boolean literal expression is either `true` or `false`, and the type of it is `bool`, an int literal expression is an integer and its type is `int`, a double literal expression is a floating-point number and its type is `double`.

### 4.3. Boolean Expression
We provide boolean and relation operators for logical operations. The value of a Boolean expression is either `true` or `false`. For two expressions with the same primitive type, you can use binary operators to construct a boolean expression that indicates the relationship of two expressions. For single expression with bool type, a unary operator can ben used to construct a boolean expression.

### 4.4. Array Expression
An array expression is a sequence of one or more element expressions separated by commas and enclosed in `{}`. All elements must be compatible with the same type. For instance, members of array `{1, 2, 3}` has an `int` type. Type of members in an array can be `array`, `int`, `bool`, `double`, `qubit`, `tuple`. Empty array `{}` is not allowed, the addition of array is not allowed either.

### 4.5. Array Access Expression
Given an array type variable, array access can be constructed by the name of the variable and some `[]`. The array access expression has the same type of given array variable type. For instance, if "a" is bound to an int type array, then `a[1]` is an expression with `int` type. Especially, `length` is a function that returns the number of elements of array access, with the return type of int. For array `bool[10] b`, type of `b.length` is `int`.

### 4.6. Tuple Expression
A Tuple expression is a sequence of element expressions separated by commas and enclosed in `()`. It has a tuple type, and the tuple type consists of the types of each tuple element in the expression. For instance, `(1, 2, True)` is an `(int, int, bool)` type expression. Noted that number of elements in a tuple expression should more than one.

### 4.7. Function Call Expression
A function call expression can be constructed by a given a declared function and a tuple expression of the input type of the function's function type. The type of function call is the output type of the given function.

For example, if "func1" is an operation with function type `(int, int) -> bool`, then "func1(1,2)" is a function call expression and type of this expression is `bool`.

### 4.8. Arithmetic Expression
For arithmetic expressions, unary operators are right-associative, and binary operators are left-associative. We list Quingo operators below, in the order of precedence, from highest to lowest:
- Operators

|   Operator   | Arity  |  Parameter type   |                                    Description                                     |
| :----------: | :----: | :---------------: | :--------------------------------------------------------------------------------: |
|      !       | Unary  |       Bool        |                                    Logical Not                                     |
|     -, +     | Unary  |    Int,Double     |                               Hold or reverse value                                |
|     *, /     | Binary |    Int,Double     |                              Multiplication, division                              |
|      %       | Binary |        Int        |                                  integer modulus                                   |
|     -, +     | Binary |    Int, Double    |                               Addition, subtraction                                |
| <, <=, >, >= | Binary |    Int, Double    | Less-than, less-than-or-equal, greater-than, and greater-than-or-equal comparisons |
|    ==, !=    | Binary | Int, Double, Bool |                          equal and not-equal comparisons                           |
|      &&      | Binary |       Bool        |                                    Logical AND                                     |
|     \|\|     | Binary |       Bool        |                                     Logical OR                                     |

### 4.9. Type Conversion Expression
Quingo supports explicit type conversion of int and double type. Use `toInt()` transfer expression from double type to int type and `toDouble()` transfer expression from int type to double type. for example, `toInt(1.0)`, `toDouble(10)`.

## 5. Statements

### 5.1. Empty Statement
A statement with only a terminating semicolon `;` is an empty statement. An empty statement does nothing in compilation and execution.

### 5.2. Variable Declaration Statement
A variable declaration statement is used to declare a variable with a specified type. The statement is consists of the specified type and referred name of the variable, the definition of this variable can also be done ins the statement. Some examples are shown as follows:
```
int a;
double b = 1.1;
(bool, double) c;
```

### 5.3. Block Statement
Quingo statements are grouped into statement blocks. A block statement starts with a `{` and ends with a `}`. A block statement that is lexically enclosed within another block statement is considered to be a sub-block of the containing block statement.

### 5.4. Assignment Statement
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

### 5.5. Control Statements

#### 5.5.1. If Statement
An if statement consists of the keyword `if`, an open parenthesis `(`, a condition (i.e., a Boolean expression), a close parenthesis `)`, and a block statement. The block statement is executed once if the condition evaluates to true. The statement may optionally finish with an else clause, which is consists of the keyword `else`, and a block statement, if the condition of the condition evaluates to false, the block statement bounded to "else" is executed. Some examples are shown as follows：
```
bool a = true;

if(a){

}else{

}//if block will be executed once

if (false){

}// if block will not be executed
```

#### 5.5.2. While Statement
A while statement consists of the keyword `while`, an open parenthesis `(`, a condition (i.e., a Boolean expression), a close parenthesis `)`, and a block statement. The block statement (the body of the loop) is executed as long as the condition evaluates to true. Some examples are shown as follows：
```
int a = 0;

while (a < 10>){
    a += 1;
}   //while loop will be executed 10 times

while(false){

} // while loop will not be executed

```

#### 5.5.3. For Statement
A for statement consists of the keyword `for`, an open parenthesis `(`, a singular statement, a condition (i.e., a Boolean expression), an end cycle statement, a close parenthesis `)`, and a block statement. The block statement (the body of the loop) is executed as long as the condition evaluates to true, at the end of each loop the end cycle statement will execute one time. Some examples are shown as follows：
```
for(int i=0; i < 10; i += 1){
    //for loop will be executed 10 times
}
```

#### 5.5.4. Switch-case Statement
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

#### 5.5.5. Break Statement
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

#### 5.5.6. Continue Statement
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

#### 5.5.7. Return Statement
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

### 5.6. Using Statement
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

### 5.7. Wait Statement
A wait statement is a timing control statement. A wait statement consists of a keyword `wait`, an open parenthesis `(`, a list of qubit type expression, an int type expression, a close parenthesis `)`, and a terminating semicolon `;`. When the wait statement is executed, the qubits in the list of qubit type expressions will wait a while before it is allowed to operate. The waiting time is the product of the value of the int type expression and the hardware clock cycle. Some examples are shown as follows:
```
using((q1,q2):(qubit,qubit[])){
    wait(q1,2);
    wait(q2,3);
    wait(q1,q2,4);
}
```

### 5.8. Function Call Statement
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

## 6. Timing Control
Quingo allows users to control the time of applying quantum operations explicitly. We first introduce the time model used in Quingo, and thereafter how to specify the timing control.

### 6.1. Time Model
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

### 6.2. Timer label
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

### 6.3. Timing Constraints
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

### 6.4. Scope
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
### 6.5. Timing Constraints in Loops
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