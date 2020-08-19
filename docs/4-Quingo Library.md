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