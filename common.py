import os
import struct
import sys

import colorama
from colorama import Fore

colorama.init(autoreset=True)


def print_terminal_line(*args, alignment):
    w, h = get_terminal_size_windows()
    # for i in range(1,w+1):
    #    print((Fore.RED if i%10==0 else Fore.GREEN) + str(i%10), end='')
    # print()
    for i, arg in enumerate(args):
        a = alignment[i] if i < len(alignment) else 'L'
        assert a in ['L', 'R']
        if a == 'L':
            arg = arg[0:w]
        else:
            arg = arg[len(arg) - w:]
        print(arg, end='')
        w -= len(arg)
    print(w * ' ', end='')


def get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        raise
        pass


class UserInputError(BaseException):
    def __init__(self, error):
        super().__init__(error)


def verify_path(path):
    if not os.path.exists(path):
        raise UserInputError("Path '%s' doesn't exist" % path)


def script_handler(click_function):
    try:
        argv_org = sys.argv.copy()
        if len(sys.argv) == 1:
            sys.argv.append('--help')
        click_function()
        sys.argv = argv_org
    except UserInputError as ex:
        print(Fore.LIGHTRED_EX + str(ex))
    except BaseException as ex:
        raise ex
