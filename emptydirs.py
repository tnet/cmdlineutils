import click

from common import *

colorama.init(autoreset=True)


def walkdirectory(rootdirectory):
    root_subdirs_files = list()
    for root, subdirs, files in os.walk(rootdirectory):
        root_subdirs_files.append((root, subdirs, files))
    i = 0
    n = len(root_subdirs_files)
    for root, subdirs, files in sorted(root_subdirs_files):
        yield i, n, root, subdirs, files
        i += 1


@click.command()
@click.argument('rootdirectory', metavar="ROOT_DIRECTORY")
def main_function(rootdirectory):
    """Finds empty directories"""

    verify_path(rootdirectory)

    print(colorama.Fore.CYAN + "Walking directory '%s'" % rootdirectory)

    empty_directories = []

    for i, n, root, subdirs, files in walkdirectory(rootdirectory):
        if len(files) == 0 and len(subdirs) == 0:
            empty_directories.append(root)

        print_terminal_line(colorama.Fore.LIGHTMAGENTA_EX + "%5i/%5i " % (i + 1, n), "Directory ", root,
                            alignment="LLR")
        print(end='\r')

        for j, f in enumerate(files):
            ff = os.path.join(root, f)
            size = os.path.getsize(ff)
    print()

    if len(empty_directories) > 0:
        print(colorama.Fore.LIGHTMAGENTA_EX + "Empty Directories: ")
        for ed in empty_directories:
            print(colorama.Fore.YELLOW + ed)


if __name__ == "__main__":
    script_handler(main_function)
