import importlib
import os
import re
from functools import reduce

import click

from common import *


def main_function():
    colorama.init(autoreset=True)

    dir = os.path.dirname(sys.argv[0])

    out = []

    for f in os.listdir(dir):
        if not f.endswith(".py"):
            continue

        #  try to find line with starts with ### and use it as help
        lines = []
        with open(os.path.join(dir,f)) as reader:
            for l in reader.readlines():
                l = l.rstrip()
                m = re.match("### ?(.*)", l)
                if not m:
                    continue
                l = m.group(1)
                lines.append(l)
        f = f.rstrip('.py')

        i = importlib.import_module(f)
        for k,v in sorted(i.__dict__.items()):
            if isinstance(v, click.core.Command):
                help = v.__dict__.get("help")
                if help:
                    lines = [help.split('\n')[0]]

        out.append((f, lines))

    w = reduce(max, map(lambda o:len(o[0]), out))

    for f, lines in out:
        if len(lines)==0:
            continue
        print(colorama.Fore.LIGHTYELLOW_EX + f"%-{w}s " % f, end="")
        print(colorama.Fore.LIGHTCYAN_EX + "\n".join(lines))

if __name__ == "__main__":
    main_function()