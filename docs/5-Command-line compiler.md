- [Quingo Command-line Compiler](#quingo-command-line-compiler)
  - [1. Prerequisite](#1-prerequisite)
  - [2. Usage](#2-usage)
  - [3. Options](#3-options)
    - [3.1. Output file name](#31-output-file-name)
    - [3.2. Shared memory address](#32-shared-memory-address)
    - [3.3. Static memory address](#33-static-memory-address)
    - [3.4. Dynamic memory address](#34-dynamic-memory-address)
    - [3.5. Maximum unrolling number](#35-maximum-unrolling-number)
    - [3.6. Help](#36-help)
    - [3.7. Version](#37-version)
  - [4. Examples](#4-examples)

# Quingo Command-line Compiler
You can use Quingo compiler with a terminal command. This command-line version compiler is an executable .jar file, which will be referred to as *quingo.jar* in this document.

## 1. Prerequisite
Before using the compiler, you should install the latest version of [Java Development ToolKit](https://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html). You may need to add or modify a few environmental  variables as well. After a success installation, you should be able to execute this command: `java -version`.

## 2. Usage
The general usage of Quingo command-line compiler is as follows:
```sh
java -jar quingo.jar <Quingo_files> <configuration_file> [options]
```

`java -jar quingo.jar` is calling the compiler with a Java virtual machine. It is followed by one or more Quingo source files (.qu). Note that the file containing the `main` operation should be placed as the first one. Then, you specify the configuration file (.qfg). Some options are available if you want to tweak some parameters of the compiler.

## 3. Options
### 3.1. Output file name
By default, the generated eQASM file (.eqasm) is placed in a subfolder *build* with the same name as the source file containing the `main` operation. However, you can alter this using the option `-o` or `--output` and the **relative** path of the new file. In this path, "/" is used to indicate the file system's hierarchy, including in Windows OS. For example, `-o src-gen/my.eqasm` means generating *my.eqasm* under the subfolder *src-gen*. If a subfolder does not exist, it will be created automatically. You can even access the parent folder with "../".

### 3.2. Shared memory address
After the execution of a Quingo program, the `main` operation writes its return values to a memory region that is shared with the host processor. The beginning address of this region is configurable with the option `-s` or `--shared-addr`. The default value is 0.

### 3.3. Static memory address
By default, the compiler stores variable on memory starting from 0x10000. You can alter this address via the option `-t` or `--static-addr`.

### 3.4. Dynamic memory address
For an array whose length is not known during the compilation time, it is stored in a different memory region from the other variables. This region starts from 0x20000 by default. You can change this address via the option `-d` or `--dynamic-addr`.

### 3.5. Maximum unrolling number
Quingo compiler will unroll loops up to a small number, e.g., 100 by default. You can change this number with the option `-u` or `--max-unroll`. The rest of the loop will be implemented using eQASM branch instructions.

### 3.6. Help
`-h` or `--help` option will print the usage of the Quingo compiler.

### 3.7. Version
The version of the Quingo compiler can be printed with `-v` or `--version`.

## 4. Examples
The following examples are all correct ways of invoking the Quingo compiler.
```
java -jar quingo.jar t1.qu config-quingo.qfg
java -jar quingo.jar t1.qu config-quingo.qfg -o my.eqasm
java -jar quingo.jar t1.qu config-quingo.qfg -s 4096 --static-addr 9192
java -jar quingo.jar -u 1000 t1.qu config-quingo.qfg
java -jar quingo.jar -h
```