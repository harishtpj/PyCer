# 🧮 PyCer
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

PyCer, a Python to C compiler written in Python. Heavily based on Polyakov Konstantin's [py2c](https://github.com/syeysk/tool_py2c_translator) project.

# ℹ About
**PyCer** is a Python transpiler which **syntatically** transpiles Python code to Pure C code.  Note that it does not **semantically** transpile. Instead it compiles the Python's syntatic constructs to C's equivalent.
This project is not intended to be a pure Python compiler like Cython or Nutika(with lots of optimisations). But to be a lightweight transpiler. This projects intends to give a good API and a frontend for the base Transpiler.

# Things to note

As previously stated, this project syntatically transpiles Python code to C code.

For example:

```python
i: int = int(input("Hola"))
```

would be translated to:

```c
int i = int(input("Hola"));
```
Where `int()` and `input()` are intended to be predefined somewhere by the user. except for the print function

```python
print("Hello, World!")
``` 

```c
#include "stdio.h"

printf("Hello, World!\n");
```

Think this project as a extension to existing C where the user can write C code using Python's syntax.

The following operations are supported:
- Assignment of constant values to variables: positive integers and strings.

Restrictions:
- Types must always be declared through annotation during initialization.
- Type annotation will work if it is specified before the assignment. If it is specified at or after the assignment, the annotation will be ignored.
- All arguments are mandatory (there are plans to add the ability to specify default arguments).
- A function always returns only one value (there are plans to enable returning an array for multiple values).
- By default, all positive integers have the C-type `int`.
- Strings have the default type of `unsigned char`.

# 📃 Requirements
- Python >= 3.6
- Any C compiler, to compile the produced C code to native binary

# ✍🏻 Authors and acknowledgment
I would like to thank [Polyakov Konstantin](https://github.com/syeysk) for his work on [py2c](https://github.com/syeysk/tool_py2c_translator) project.

This project is currently edited and maintained by [Harish Kumar](https://github.com/harishtpj).

<!-- Thanking the contributors -->

# ⏳ Project Status
This project is currently in development.

# 📝 License
#### This project is [GPLv3](https://github.com/harishtpj/PyCer/blob/master/LICENSE) licensed.