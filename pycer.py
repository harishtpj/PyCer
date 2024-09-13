# Commandline Interface for PyCer Compiler

import argparse, os, re
from io import StringIO
from py2c.bytecode_walker import translate
from py2c.translator_c import TranslatorC
from py2c.chelpers import cpprelude

def gen_arg_parser() -> argparse.ArgumentParser:
    """
    Generate an argument parser for the 'pycer' command-line tool.

    Returns:
        An instance of the ArgumentParser class.
    """
    parser = argparse.ArgumentParser(
        prog='pycer',
        description='Python to C Compiler'
    )
    parser.add_argument(
        'File',
        metavar='file',
        type=str,
        help="The File to compile"
    )
    parser.add_argument(
        "-S",
        "--source",
        action="store_true",
        help="only Compiles Python to C source code"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="v1.0.0",
        help="shows version info of PyCer"
    )
    parser.add_argument(
        "cflags",
        nargs=argparse.REMAINDER,
        help="Flags to the C compiler"
    )
    return parser


def translate2C(source_code: str) -> str:
    """
    Translates the given source code using a TranslatorC object.

    Args:
        source_code: The source code to be translated.

    Returns:
        The translated code as a string.
    """
    file_stdout = StringIO()
    translator = TranslatorC(save_to=file_stdout)
    translate(translator, source_code)
    return file_stdout.getvalue()


def post_process(py2c_src: str) -> str:
    """
    Remove the leading whitespace before the string "c" in the given Python to C source code.

    Args:
        py2c_src (str): The Python to C source code.

    Returns:
        str: The modified Python to C source code.
    """
    pattern = r"([ ]*)\"c\s*(.*?)\";"
    result = re.sub(pattern, r"\1\2;", py2c_src, count=0)

    pattern = r"/\*\s*c\s*(.*?)\s*\*/"
    result = re.sub(pattern, r"\1\n", result, flags=re.DOTALL, count=0)
    result = "extern \"C\" {\n" + result + "\n}\n"

    return cpprelude + result

if __name__ == "__main__":
    args = gen_arg_parser().parse_args()
    cfname = args.File[:-3] + '.cpp'
    cflags = ' '.join(args.cflags)
    cfname = f"_{cfname}" if not args.source else cfname

    with open(args.File) as f:
        source_code = f.read()

    with open(cfname, 'w') as f:
        py2c_src = translate2C(source_code)

        py2c_src = py2c_src.replace("PTR", "*")

        f.write(post_process(py2c_src))

    if not args.source:
        if os.system(f"g++ {cfname} -o {args.File[:-3]} {cflags}") != 0:
            os.remove(cfname)
            exit(-1)
        os.remove(cfname)


