import click
from common import *

colorama.init(autoreset=True)


@click.command()
@click.argument('files', nargs=-1)
def main_function(files):
    """Convert tabs to 4 spaces"""
    for file in sys.argv[1:]:
        lines = []
        with open(file) as reader:
            for line in reader.readlines():
                line = line.replace('\t', 4 * ' ')
                lines.append(line)

        with open(file, 'w') as writer:
            print("writing " + Fore.GREEN + file)
            for line in lines:
                print(line, file=writer, end="")


if __name__ == "__main__":
    script_handler(main_function)
