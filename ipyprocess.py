import click
import io
import nbformat
import os
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor, ClearOutputPreprocessor

from common import *


def execute(input, to_html, to_self, to_clear):
    print('Processing ' + Fore.LIGHTGREEN_EX + input)
    with open(input, 'rb') as f:
        notebook = nbformat.read(f, as_version=4)

    if to_html or to_self:
        print("    Executing")
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(notebook, {'metadata': {'path': './'}})

    if to_html:
        html_output = input + ".html"
        print("    Saving to HTML")
        exportHTML = HTMLExporter()
        (body, resources) = exportHTML.from_notebook_node(notebook)
        with open(html_output, 'wt') as f:
            f.write(body)

    if to_clear:
        print("    Clearing")
        ep = ClearOutputPreprocessor()
        ep.preprocess(notebook, {'metadata': {'path': './'}})

    if to_self or to_clear:
        stringio = io.StringIO()
        nbformat.write(notebook, stringio)
        self_output = input
        print("    Saving to self")
        with open(self_output, 'wb') as f:
            s = stringio.getvalue().encode('utf-8')
            f.write(s)


@click.command()
@click.argument('files', nargs=-1)
@click.option('flag_html', '-h', '--html', help='Executes notebook and writes to file.ipynb.html', is_flag=True)
@click.option('flag_self', '-s', '--self', help='Executes notebook and writes to file.ipynb (self)', is_flag=True)
@click.option('flag_clear', '-c', '--clear', help='Clears output cells in notebook and writes to self', is_flag=True)
def main_function(files, flag_html, flag_self, flag_clear):
    """
    Processes Jupyter notebook

    Use "*" instead of files to process all ipynb files in the current working directory

    Options are not mutually exclusive
    """
    if '*' in files:
        files = list()
        for f in filter(lambda s: s.endswith('.ipynb'), os.listdir('.')):
            files.append(f)

    for f in files:
        try:
            execute(f, flag_html, flag_self, flag_clear)
        except BaseException as ex:
            raise ex
            print(Fore.LIGHTRED_EX + f"Unable to convert file '{f}':\n" + str(ex))


if __name__ == "__main__":
    script_handler(main_function)
