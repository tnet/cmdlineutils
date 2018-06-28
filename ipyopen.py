from os.path import abspath

import click

from common import *


@click.command()
@click.argument('f', metavar="IPYNB_FILE")
def main_function(f):
    """
    Opens the jupyter notebook in localhost browser
    e.g. python ipyopen.py %P%N
    """
    server_root = os.environ['JupyterNotebookRoot']
    server_url = "http://localhost/tree/"

    f = sys.argv[1]
    f = abspath(f)
    server_root = abspath(server_root)
    f2 = f[len(server_root) + 1:]

    docurl = server_url + f2
    docurl = docurl.replace("\\", "/")

    import webbrowser
    webbrowser.open(docurl, new=2)


if __name__ == "__main__":
    script_handler(main_function)
