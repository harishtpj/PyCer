# Commandline Interface for PyCer Compiler

import argparse, os, re
from io import StringIO
from py2c.bytecode_walker import translate
from py2c.translator_c import TranslatorC

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

from io import StringIO
from typing import Any

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
    pattern = r"([ ]*)\"c\s*(.*?)\";"
    replacement = r"\1\2;"
    result = re.sub(pattern, replacement, py2c_src, count=0)
    return result

if __name__ == "__main__":
    args = gen_arg_parser().parse_args()
    cfname = args.File[:-3] + '.c'
    cflags = ' '.join(args.cflags)
    cfname = f"_{cfname}" if not args.source else cfname

    with open(args.File) as f:
        source_code = f.read()

    with open(cfname, 'w') as f:
        py2c_src = translate2C(source_code)
        f.write(post_process(py2c_src))

    if not args.source:
        if os.system(f"gcc {cfname} -o {args.File[:-3]} {cflags}") != 0:
            os.remove(cfname)
            exit(-1)
        os.remove(cfname)


