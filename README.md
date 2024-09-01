# 🧮 PyCer
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

PyCer, a Python to C++ compiler written in Python. Heavily based on Polyakov Konstantin's [py2c](https://github.com/syeysk/tool_py2c_translator) project.

# ℹ About
**PyCer** is a Python transpiler which **syntatically** transpiles Python code to Pure C++ code.  Note that it does not **semantically** transpile. Instead it compiles the Python's syntatic constructs to C++'s equivalent.
This project is not intended to be a pure Python compiler like Cython or Nutika(with lots of optimisations). But to be a lightweight transpiler. This projects intends to give a good API and a frontend for the base Transpiler.

# Things to note

As previously stated, this project syntatically transpiles Python code to C++ code.

For example:

```python
# python
i: int = int(input("Hola"))
```

would be translated to:

```c
// c++
int i = int(input("Hola"));
```

Think this project as a extension to existing C++ where the user can write C++ code using Python's syntax.

Restrictions:
- Types must always be declared through annotation during initialization.
- Type annotation will work if it is specified before the assignment. If it is specified at or after the assignment, the annotation will be ignored.
- All arguments are mandatory (there are plans to add the ability to specify default arguments).
- By default, all positive integers have the C-type `int`.
- Strings have the default type of `std::string`.
- Arrays of pointers are currently impossible
- The string `PTR` will get replaced with `*` after translation, so may not be used in variable names

## Required additions to Python syntax

Obviously, C++ has some different features to Python, and so some extra features have had to have been added to extend the syntax:

### Pointers and references
To declare a pointer, add the text `PTR` to the end of the type, and to use a reference, use the REF(value) macro:
```python
# python
myStr: str = "Hello, world!"
myPtr: strPTR = REF(str)
print(myPtr)
```
Gets translated to:
```c++
// c++
std::string myStr = "Hello, world!";
std::string *myPtr = &myStr;
print(myPtr); // this goes to a function defined in the preamble
```

### Array types
To define an array you can just use the standard non-array type with a python list, however when you need to access the array type for functions, you should add the string `_ARRx` to the end of the type, where `x` is the amount of elements. `x` can be omitted if wanted.

```python
# python
def example(arr: strPTR) -> strPTR:
    result: strPTR = ptr(string, malloc(2 * sizeof(string))) # macro: ((type *) (value))

    if result == NULL: # memory safety is important!
        print("Memory allocation failed!")
        return NULL

    result[0] = arr[1]
    result[1] = arr[0]

    return result

def main() -> int:
    arr1: str = ["hello, world", "element 2.1"]
    arr2: str_ARR2 = ["hello, world again", "element 2.2"]
    arr3: str_ARR = ["hello, world again again", "element 2.3"]

    retArr: strPTR = example(arr1)
    for i in range(2):
        print("Element",str(i)+":",retArr[i])
```

Translated to:

```c++
// C++
string* example(string* arr) {
    string* result = ptr(string, malloc(2 * sizeof(string)));
    if (result == NULL) {
        print("Memory allocation failed!");
        return NULL;
    }
    result[0] = arr[1];
    result[1] = arr[0];
    return result;
}
int main(void) {
    string arr1[] = {"hello, world", "element 2.1"};
    string arr2[2] = {"hello, world again", "element 2.2"};
    string arr3[] = {"hello, world again again", "element 2.3"};
    string* retArr = example(arr1);
    for (int i=0; i<2; i++) {
        print("Element", str(i) + ":", retArr[i]);
    }
}
```

# 📃 Requirements
- Python >= 3.6
- Any C++ compiler, to compile the produced C++ code to native binary
    - When executed with Pycer, `g++` is used, and is recommended, but any C++ compiler will do

# ✍🏻 Authors and acknowledgment
I would like to thank [Polyakov Konstantin](https://github.com/syeysk) for his work on [py2c](https://github.com/syeysk/tool_py2c_translator) project.

This project is currently edited and maintained by [Harish Kumar](https://github.com/harishtpj). Some features such as pointers, references and arrays have been implemented by [develop331](https://github.com/iwl-lyam).

<!-- Thanking the contributors -->

# ⏳ Project Status
This project is currently in development.

# 📝 License
#### This project is [GPLv3](https://github.com/harishtpj/PyCer/blob/master/LICENSE) licensed.