import collections
import hashlib
import re

import click

from common import *

colorama.init(autoreset=True)
cache_saving_frequency = 10


def file_hash(filename):
    h = hashlib.sha256()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda: f.read(128 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def walkdirectory(rootdirectory, regex_search_pattern):
    root_subdirs_files = list()
    for root, subdirs, files in os.walk(rootdirectory):
        if not re.search(regex_search_pattern, root):
            continue
        root_subdirs_files.append((root, subdirs, files))
    i = 0
    n = len(root_subdirs_files)
    for root, subdirs, files in sorted(root_subdirs_files):
        yield i, n, root, subdirs, files
        i += 1


@click.command()
@click.argument('rootdirectory', metavar="ROOT_DIRECTORY")
@click.option('regex_search_pattern', '-r', '--regex', default='x', metavar="REGEX", help='Search pattern for subdirectories. Default is .*')
def main_function(rootdirectory, regex_search_pattern):
    """Finds duplicate files based on exact binary match"""

    verify_path(rootdirectory)

    print(colorama.Fore.CYAN + "Walking directory '%s'" % rootdirectory)

    size_collisions = collections.defaultdict(list)

    for i, n, root, subdirs, files in walkdirectory(rootdirectory, regex_search_pattern):
        print_terminal_line(colorama.Fore.LIGHTMAGENTA_EX + "%5i/%5i " % (i + 1, n), "Directory ", root, alignment='LLR')
        print(end='\r')

        for j, f in enumerate(files):
            ff = os.path.join(root, f)
            size = os.path.getsize(ff)
            size_collisions[size].append(ff)
    print()

    for size, files in sorted(size_collisions.items()):
        if len(files) <= 1:
            continue

        hash_collisions = collections.defaultdict(list)
        for f in files:
            h = file_hash(f)
            hash_collisions[h].append(f)

        for hash, files in sorted(hash_collisions.items()):
            if len(files) <= 1:
                continue

            print(colorama.Fore.LIGHTGREEN_EX + "Duplicate files (hard hash), size %i kB" % (size / 1024))
            for f in files:
                print(f)


if __name__ == "__main__":
    script_handler(main_function)
