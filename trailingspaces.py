import click

from common import *


@click.command()
@click.argument('files', nargs=-1)
def main_function(files):
    """Removes trailing spaces and trailing tabs from any file"""

    if len(files)==0:
        raise UserInputError("At least one file must be provided")

    for file in files:
        lines = []
        with open(file) as reader:
            for line in reader.readlines():
                line = line.rstrip('\n').rstrip('\t').rstrip(' ')
                lines.append(line)

        with open(file, 'w') as writer:
            print("writing " + Fore.GREEN + file)
            for line in lines:
                print(line, file=writer)


if __name__ == "__main__":
    script_handler(main_function)
